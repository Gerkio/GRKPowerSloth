"""
Servicio para monitorizar procesos.
Equivalente a ProcessMonitorService.cs

Responsable de:
1. Monitorear cierre de procesos (ON_EXIT) con verificación de familia y ventanas
2. Detectar fin de descargas (ON_NETWORK_IDLE / Al terminar descarga)
   mediante fusión de 3 señales: familia de procesos, I/O de disco/red y candado de archivos parciales.
3. Health checks periódicos y timeouts de seguridad.
4. Notificación de estado en tiempo real.
"""

import os
import time
from collections import deque
from pathlib import Path
from typing import Dict, List, Optional
import psutil
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from models.enums import MonitoringMode
from managers.localization_manager import LocalizationManager


def _format_speed(bytes_per_sec: float) -> str:
    """Convierte bytes/segundo a cadena legible."""
    if bytes_per_sec < 1024:
        return f"{bytes_per_sec:.0f} B/s"
    elif bytes_per_sec < 1024 * 1024:
        return f"{bytes_per_sec / 1024:.1f} KB/s"
    else:
        return f"{bytes_per_sec / (1024 * 1024):.1f} MB/s"


class ProcessMonitorService(QObject):
    """
    Servicio mejorado para monitorizar procesos, con detección robusta
    tanto por finalización como por fin de descarga.
    """
    
    # Signals
    monitoring_success = pyqtSignal()
    monitoring_error = pyqtSignal(str)
    monitoring_log = pyqtSignal(str)
    monitoring_status = pyqtSignal(str, str)  # (status_detallado, status_mini)
    
    # ===== CONFIGURACIÓN =====
    CHECK_INTERVAL_MS = 2000              # Muestreo constante cada 2 segundos
    HISTORY_WINDOW_SIZE = 15              # Ventana deslizante de 15 muestras (30s)
    IDLE_CONFIRMATION_SECONDS = 40        # 40 segundos de inactividad sostenida para confirmar fin
    
    # Umbrales acotados para evitar falsos positivos y falsos negativos
    IDLE_FLOOR_BYTES_PER_SEC = 35 * 1024       # 35 KB/s piso (ignora telemetría/keep-alive en reposo)
    ACTIVE_CEILING_BYTES_PER_SEC = 150 * 1024   # 150 KB/s techo (actividad garantizada independientemente del pico)
    DISK_ACTIVE_THRESHOLD_BYTES = 250 * 1024    # 250 KB/s disco (detecta descompresión/verificación post-descarga)
    
    MAX_MONITORING_DURATION_HOURS = 24
    
    def __init__(self):
        super().__init__()
        
        # Estado
        self.monitored_pid: Optional[int] = None
        self.monitored_name: Optional[str] = None
        self.monitoring_mode: Optional[MonitoringMode] = None
        self.monitoring_start_time: Optional[float] = None
        
        # Historial y métricas
        self.network_history = deque(maxlen=self.HISTORY_WINDOW_SIZE)
        self.consecutive_idle_seconds = 0.0
        self.consecutive_exit_checks = 0
        self._consecutive_dead_ticks = 0
        
        self._last_proc_io: Dict[int, tuple] = {}  # pid -> (read_bytes, write_bytes, other_bytes)
        self._last_net_recv: Optional[int] = None
        self._last_tick_time: Optional[float] = None
        self._rolling_baseline: float = 0.0
        
        # Timers
        self.monitor_timer = QTimer()
        self.monitor_timer.setInterval(self.CHECK_INTERVAL_MS)
        self.monitor_timer.timeout.connect(self._on_monitor_tick)
        
        self.health_check_timer = QTimer()
        self.health_check_timer.setInterval(self.CHECK_INTERVAL_MS)
        self.health_check_timer.timeout.connect(self._on_health_check)
    
    # ===== MÉTODOS PÚBLICOS =====
    
    def start_monitoring_for_exit(self, pid: int, process_name: str = ""):
        """Inicia monitoreo por cierre de aplicación (ON_EXIT)."""
        try:
            self.stop_monitoring()
            self._log(f"Iniciando monitoreo de cierre para proceso: {process_name} (ID: {pid})")

            if not psutil.pid_exists(pid):
                raise ValueError(f"El proceso con ID {pid} no existe o ya ha terminado.")

            self.monitored_pid = pid
            if not process_name:
                try:
                    process_name = psutil.Process(pid).name()
                except Exception:
                    process_name = f"PID {pid}"
            self.monitored_name = process_name
            self.monitoring_mode = MonitoringMode.ON_EXIT
            self.monitoring_start_time = time.time()
            self.consecutive_exit_checks = 0

            self.health_check_timer.start()
            self._log(f"Monitoreo de cierre activo para: {self.monitored_name}")

        except Exception as e:
            self._log_error(f"Error al iniciar monitoreo de cierre: {e}")
            raise
    
    def start_monitoring_for_network_idle(self, pid: int, process_name: str):
        """Inicia monitoreo para detectar fin de descarga (ON_NETWORK_IDLE)."""
        try:
            self.stop_monitoring()
            self._log(f"Iniciando monitoreo de fin de descarga para: {process_name} (ID: {pid})")

            if not psutil.pid_exists(pid):
                raise ValueError(f"El proceso con ID {pid} no existe.")

            self.monitored_pid = pid
            self.monitored_name = process_name
            self.monitoring_mode = MonitoringMode.ON_NETWORK_IDLE
            self.monitoring_start_time = time.time()
            self._last_tick_time = time.time()
            self._consecutive_dead_ticks = 0

            # Inicializar lecturas base de I/O de toda la familia
            self._last_proc_io.clear()
            for proc in self._get_process_family():
                try:
                    io = proc.io_counters()
                    self._last_proc_io[proc.pid] = (io.read_bytes, io.write_bytes, getattr(io, 'other_bytes', 0))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            # Inicializar red global
            try:
                self._last_net_recv = psutil.net_io_counters().bytes_recv
            except Exception:
                self._last_net_recv = None

            self.monitor_timer.start()
            self.health_check_timer.start(10000)
            self._log(f"Monitoreo de fin de descarga iniciado para: {process_name}")

        except Exception as e:
            self._log_error(f"Error al iniciar monitoreo de descarga: {e}")
            raise
    
    def stop_monitoring(self):
        """Detiene todo el monitoreo y resetea el estado."""
        self.consecutive_idle_seconds = 0.0
        self.consecutive_exit_checks = 0
        self._consecutive_dead_ticks = 0
        self._rolling_baseline = 0.0
        self.network_history.clear()
        self._last_proc_io.clear()
        self._last_net_recv = None
        self._last_tick_time = None
        
        self.monitor_timer.stop()
        self.health_check_timer.stop()
        
        self.monitored_pid = None
        self.monitored_name = None
        self.monitoring_mode = None
        self.monitoring_start_time = None
    
    # ===== INSPECCIÓN Y AGRUPACIÓN DE PROCESOS =====
    
    def _get_process_family(self) -> List[psutil.Process]:
        """
        Obtiene la lista de procesos activos que componen la familia de la aplicación:
        PID objetivo + procesos hijos recursivos + instancias con el mismo ejecutable.
        """
        processes = []
        seen_pids = set()
        target_name_lower = (self.monitored_name or "").lower()

        # 1. Proceso principal e hijos
        if self.monitored_pid and psutil.pid_exists(self.monitored_pid):
            try:
                main_proc = psutil.Process(self.monitored_pid)
                if main_proc.is_running() and main_proc.status() != psutil.STATUS_ZOMBIE:
                    processes.append(main_proc)
                    seen_pids.add(self.monitored_pid)
                    try:
                        for child in main_proc.children(recursive=True):
                            if child.pid not in seen_pids and child.is_running():
                                processes.append(child)
                                seen_pids.add(child.pid)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # 2. Otros procesos con el mismo nombre ejecutable (Chrome helpers, Steam workers, etc.)
        if target_name_lower:
            try:
                for p in psutil.process_iter(['pid', 'name']):
                    pid = p.info['pid']
                    if pid not in seen_pids and p.info['name'] and p.info['name'].lower() == target_name_lower:
                        try:
                            proc = psutil.Process(pid)
                            if proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE:
                                processes.append(proc)
                                seen_pids.add(pid)
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
            except Exception:
                pass

        return processes

    def _has_active_partial_download(self) -> bool:
        """
        Comprueba si existen archivos de descarga temporal activos (.crdownload, .part, etc.)
        modificados en los últimos 45 segundos. Actúa como salvaguarda ante micro-pausas de red.
        """
        try:
            now = time.time()
            target_name = (self.monitored_name or "").lower()

            # Navegadores y gestores
            browser_keys = ("chrome", "edge", "firefox", "brave", "opera", "browser", "torrent", "downloader", "idman")
            if any(k in target_name for k in browser_keys):
                downloads_dir = Path.home() / "Downloads"
                if downloads_dir.exists():
                    exts = ('.crdownload', '.part', '.opdownload', '.!ut', '.qb')
                    for entry in downloads_dir.iterdir():
                        try:
                            if entry.is_file() and entry.name.lower().endswith(exts):
                                if (now - entry.stat().st_mtime) < 45.0:
                                    return True
                        except (OSError, PermissionError):
                            continue

            # Steam
            if "steam" in target_name and self.monitored_pid and psutil.pid_exists(self.monitored_pid):
                try:
                    steam_proc = psutil.Process(self.monitored_pid)
                    steam_dir = Path(steam_proc.exe()).parent
                    downloading_dir = steam_dir / "steamapps" / "downloading"
                    if downloading_dir.exists():
                        for item in downloading_dir.rglob("*"):
                            try:
                                if item.is_file() and (now - item.stat().st_mtime) < 45.0:
                                    return True
                            except (OSError, PermissionError):
                                continue
                except Exception:
                    pass
        except Exception:
            pass

        return False

    # ===== CALLBACKS DE TIMERS =====
    
    def _on_monitor_tick(self):
        """Callback periódico de evaluación de fin de descarga."""
        if self.monitoring_mode != MonitoringMode.ON_NETWORK_IDLE:
            return

        try:
            family = self._get_process_family()
            if not family:
                self._consecutive_dead_ticks += 1
                if self._consecutive_dead_ticks >= 2:
                    self._log("Todos los procesos de la aplicación monitoreada han terminado.")
                    self._trigger_success()
                return
            else:
                self._consecutive_dead_ticks = 0

            # 1. Delta de I/O de la familia de procesos
            current_proc_io = {}
            delta_write_other = 0
            delta_disk_io = 0

            for proc in family:
                try:
                    io = proc.io_counters()
                    read_b = io.read_bytes
                    write_b = io.write_bytes
                    other_b = getattr(io, 'other_bytes', 0)
                    current_proc_io[proc.pid] = (read_b, write_b, other_b)

                    if proc.pid in self._last_proc_io:
                        last_r, last_w, last_o = self._last_proc_io[proc.pid]
                        dw = max(0, write_b - last_w)
                        do = max(0, other_b - last_o)
                        dr = max(0, read_b - last_r)
                        delta_write_other += (dw + do)
                        delta_disk_io += (dw + dr)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            self._last_proc_io = current_proc_io

            # 2. Delta de red global
            delta_net = 0
            try:
                now_net_recv = psutil.net_io_counters().bytes_recv
                if self._last_net_recv is not None:
                    delta_net = max(0, now_net_recv - self._last_net_recv)
                self._last_net_recv = now_net_recv
            except Exception:
                pass

            # 3. Intervalo temporal exacto
            now_time = time.time()
            interval_sec = max(0.5, now_time - (self._last_tick_time or (now_time - 2.0)))
            self._last_tick_time = now_time

            rate_write_other = delta_write_other / interval_sec
            rate_disk_io = delta_disk_io / interval_sec
            rate_net = delta_net / interval_sec

            # 4. Actividad efectiva combinada
            # Si el proceso escribe en disco a gran velocidad (descomprimiendo en Steam/Epic), cuenta como actividad
            if rate_disk_io > self.DISK_ACTIVE_THRESHOLD_BYTES:
                effective_rate = max(rate_write_other, rate_disk_io)
            else:
                # Fusión entre transferencia de la familia y recepción de red
                if rate_write_other > 512:
                    effective_rate = max(rate_write_other, min(rate_net, rate_write_other * 2))
                else:
                    effective_rate = min(rate_net, rate_disk_io)

            self.network_history.append(effective_rate)

            # 5. Actualizar baseline dinámico suavemente
            if effective_rate > self.IDLE_FLOOR_BYTES_PER_SEC:
                if self._rolling_baseline == 0:
                    self._rolling_baseline = effective_rate
                else:
                    self._rolling_baseline = (0.85 * self._rolling_baseline) + (0.15 * effective_rate)

            # 6. Umbral inteligente acotado
            adaptive_threshold = max(
                self.IDLE_FLOOR_BYTES_PER_SEC,
                min(self._rolling_baseline * 0.10, self.ACTIVE_CEILING_BYTES_PER_SEC)
            )

            # Candado de archivos temporales
            has_partial = self._has_active_partial_download()

            # 7. Evaluar inactividad
            is_sample_idle = (effective_rate < adaptive_threshold) and not has_partial

            if is_sample_idle:
                self.consecutive_idle_seconds += interval_sec
            else:
                # Si hubo actividad real, reiniciar contador
                if self.consecutive_idle_seconds > 0:
                    self._log(f"🔴 Actividad detectada: {_format_speed(effective_rate)} (umbral: {_format_speed(adaptive_threshold)}). Reiniciando verificación.")
                self.consecutive_idle_seconds = 0.0

            # 8. Notificar estado a la UI
            app_name = self.monitored_name or "App"
            if self.consecutive_idle_seconds > 0:
                elapsed_int = int(min(self.consecutive_idle_seconds, self.IDLE_CONFIRMATION_SECONDS))
                status_text = LocalizationManager.get("status_monitoring_verifying").format(
                    app_name, elapsed_int, self.IDLE_CONFIRMATION_SECONDS
                )
                mini_text = f"{elapsed_int}s/{self.IDLE_CONFIRMATION_SECONDS}s"
            else:
                speed_str = _format_speed(effective_rate)
                status_text = LocalizationManager.get("status_monitoring_active").format(
                    app_name, speed_str
                )
                mini_text = speed_str

            self.monitoring_status.emit(status_text, mini_text)

            # 9. Disparo tras confirmación sostenida
            if self.consecutive_idle_seconds >= self.IDLE_CONFIRMATION_SECONDS:
                self._log(f"✅ Descarga y escritura completadas ({self.consecutive_idle_seconds:.0f}s de inactividad sostenida).")
                self._trigger_success()

        except Exception as e:
            # Nunca disparar éxito ante errores transitorios
            self._log_error(f"Error en tick de monitoreo: {e}")

    def _on_health_check(self):
        """Verifica timeout de 24h y estado para ON_EXIT."""
        try:
            # 1. Timeout de seguridad
            if self.monitoring_start_time:
                elapsed_hours = (time.time() - self.monitoring_start_time) / 3600
                if elapsed_hours > self.MAX_MONITORING_DURATION_HOURS:
                    self._log(f"⏰ Timeout alcanzado ({self.MAX_MONITORING_DURATION_HOURS}h). Deteniendo.")
                    self.stop_monitoring()
                    return

            # 2. Modo ON_EXIT
            if self.monitoring_mode == MonitoringMode.ON_EXIT:
                family = self._get_process_family()
                is_alive = False
                for p in family:
                    try:
                        if p.is_running() and p.status() != psutil.STATUS_ZOMBIE:
                            is_alive = True
                            break
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

                if not is_alive:
                    self.consecutive_exit_checks += 1
                    self._log(f"Comprobación de cierre: proceso no detectado ({self.consecutive_exit_checks}/2)")
                    if self.consecutive_exit_checks >= 2:
                        self._log(f"✅ Proceso '{self.monitored_name}' cerrado.")
                        self._trigger_success()
                else:
                    self.consecutive_exit_checks = 0
                    app_name = self.monitored_name or "App"
                    status_text = LocalizationManager.get("status_monitoring").format(app_name)
                    self.monitoring_status.emit(status_text, "RUN")

        except Exception as e:
            self._log_error(f"Error en health check: {e}")

    # ===== MÉTODOS PRIVADOS =====
    
    def _trigger_success(self):
        """Dispara el evento de éxito y detiene el monitoreo."""
        self.stop_monitoring()
        self.monitoring_success.emit()
    
    def _log(self, message: str):
        """Registra un mensaje de log con timestamp."""
        timestamp = time.strftime('%H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        self.monitoring_log.emit(log_message)
        print(log_message)
    
    def _log_error(self, message: str):
        """Registra un mensaje de error con timestamp."""
        timestamp = time.strftime('%H:%M:%S')
        error_message = f"[ERROR {timestamp}] {message}"
        self.monitoring_error.emit(error_message)
        print(error_message)


# ===== FUNCIONES AUXILIARES =====

_PROCESS_LIST_TTL_SECONDS = 2.0
_process_list_cache = None
_process_list_cache_time = 0.0


def get_processes_with_windows(force_refresh: bool = False):
    """Obtiene una lista de procesos que tienen ventanas visibles (con caché TTL)."""
    global _process_list_cache, _process_list_cache_time

    now = time.time()
    if (not force_refresh and _process_list_cache is not None
            and (now - _process_list_cache_time) < _PROCESS_LIST_TTL_SECONDS):
        return _process_list_cache

    result = _enumerate_processes_with_windows()
    _process_list_cache = result
    _process_list_cache_time = now
    return result


def _enumerate_processes_with_windows():
    """Enumera las ventanas visibles del sistema de forma optimizada."""
    import win32gui
    import win32process

    processes = []
    seen_pids = {0, 4}  # Omitir System Idle y System
    
    def enum_windows_callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd).strip()
            if not window_text:
                return

            try:
                rect = win32gui.GetWindowRect(hwnd)
                if (rect[2] - rect[0] <= 0) or (rect[3] - rect[1] <= 0):
                    return
            except Exception:
                return

            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if pid not in seen_pids:
                try:
                    proc = psutil.Process(pid)
                    proc_name = proc.name()
                    processes.append({
                        'pid': pid,
                        'name': proc_name,
                        'window_title': window_text,
                        'display_name': f"{proc_name} ({window_text})"
                    })
                    seen_pids.add(pid)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
    
    win32gui.EnumWindows(enum_windows_callback, None)
    return sorted(processes, key=lambda x: x['display_name'].lower())
