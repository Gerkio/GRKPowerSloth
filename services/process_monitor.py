"""
Servicio para monitorizar procesos.
Equivalente a ProcessMonitorService.cs

Este es el componente más complejo del sistema, responsable de:
1. Monitorear cierre de procesos
2. Detectar inactividad de red (algoritmo sofisticado)
3. Health checks periódicos
4. Manejo robusto de errores con reintentos
"""

import psutil
import time
from collections import deque
from typing import Optional
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from models.enums import MonitoringMode


class ProcessMonitorService(QObject):
    """
    Servicio mejorado para monitorizar procesos, con detección robusta
    tanto por finalización como por inactividad de red.
    
    Características:
    - Monitoreo por cierre de proceso (ON_EXIT)
    - Monitoreo por inactividad de red (ON_NETWORK_IDLE)
    - Baseline dinámico de actividad de red
    - Ventana deslizante para filtrar picos transitorios
    - Threshold adaptativo
    - Health checks periódicos
    - Timeout de seguridad (24h máximo)
    - Reintentos con backoff exponencial
    """
    
    # Signals (eventos thread-safe de PyQt6)
    monitoring_success = pyqtSignal()
    monitoring_error = pyqtSignal(str)
    monitoring_log = pyqtSignal(str)
    
    # ===== CONFIGURACIÓN =====
    
    # Para detección de inactividad de red
    HISTORY_WINDOW_SIZE = 10              # Últimas 10 mediciones
    IDLE_THRESHOLD_SECONDS = 15           # 15 segundos de inactividad sostenida
    NETWORK_USAGE_THRESHOLD_BYTES = 1024  # 1 KB/s mínimo
    BASELINE_SAMPLES_NEEDED = 15          # 30 segundos de muestreo para baseline
    REQUIRED_IDLE_CHECKS = 7              # 7 de 10 mediciones deben estar inactivas
    
    # Control de monitoreo
    MAX_RETRIES = 3
    MAX_MONITORING_DURATION_HOURS = 24
    
    def __init__(self):
        super().__init__()
        
        # ===== ESTADO DEL MONITOREO =====
        self.monitored_process: Optional[psutil.Process] = None
        self.monitoring_mode: Optional[MonitoringMode] = None
        
        # ===== PARA MONITOREO DE RED =====
        self.network_history = deque(maxlen=self.HISTORY_WINDOW_SIZE)
        self.baseline_network_usage = 0.0
        self.baseline_calculated = False
        self.baseline_sample_count = 0
        self.consecutive_idle_checks = 0
        self.last_io_counters = None
        
        # ===== TIMERS =====
        # Timer principal de monitoreo (para red)
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._on_monitor_tick)
        
        # Timer de health check (para ambos modos)
        self.health_check_timer = QTimer()
        self.health_check_timer.timeout.connect(self._on_health_check)
        
        # ===== CONTROL =====
        self.retry_count = 0
        self.monitoring_start_time: Optional[float] = None
    
    # ===== MÉTODOS PÚBLICOS =====
    
    def start_monitoring_for_exit(self, pid: int):
        """
        Inicia la monitorización para detectar cuándo un proceso se cierra.
        
        Modo: ON_EXIT
        - Verifica periódicamente si el proceso sigue existiendo
        - Health check cada 5 segundos
        - Timeout de 24 horas
        
        Args:
            pid: ID del proceso a monitorizar
            
        Raises:
            ValueError: Si el proceso no existe
        """
        try:
            self.stop_monitoring()
            self._log(f"Iniciando monitoreo de cierre para proceso ID: {pid}")
            
            # Validar que el proceso existe
            if not psutil.pid_exists(pid):
                raise ValueError(f"El proceso con ID {pid} no existe o ya ha terminado.")
            
            self.monitored_process = psutil.Process(pid)
            self.monitoring_mode = MonitoringMode.ON_EXIT
            self.monitoring_start_time = time.time()
            
            # Health check cada 5 segundos
            self.health_check_timer.start(5000)
            
            self._log(f"Monitoreo iniciado correctamente para: {self.monitored_process.name()}")
            
        except Exception as e:
            # Reintentos con backoff exponencial
            if self.retry_count < self.MAX_RETRIES:
                self.retry_count += 1
                self._log(f"Error al iniciar monitoreo (intento {self.retry_count}/{self.MAX_RETRIES}): {e}")
                time.sleep(self.retry_count)  # Esperar 1s, 2s, 3s...
                self.start_monitoring_for_exit(pid)
            else:
                self._log_error(f"Error fatal después de {self.MAX_RETRIES} intentos: {e}")
                raise
    
    def start_monitoring_for_network_idle(self, pid: int, process_name: str):
        """
        Inicia la monitorización para detectar inactividad de red.
        
        Modo: ON_NETWORK_IDLE
        
        Algoritmo:
        1. Calcular baseline dinámico (primeros 30 segundos)
        2. Medir I/O bytes cada 2 segundos
        3. Mantener ventana deslizante de 10 mediciones
        4. Threshold adaptativo: max(baseline * 5%, 1KB/s)
        5. Requerir 7 de 10 mediciones bajo threshold
        6. Detectar 15 segundos sostenidos de inactividad
        
        Args:
            pid: ID del proceso a monitorizar
            process_name: Nombre del proceso (para logging)
            
        Raises:
            ValueError: Si el proceso no existe
            PermissionError: Si no hay permisos suficientes
        """
        try:
            self.stop_monitoring()
            self._log(f"Iniciando monitoreo de red para proceso: {process_name} (ID: {pid})")
            
            if not psutil.pid_exists(pid):
                raise ValueError(f"El proceso con ID {pid} no existe.")
            
            self.monitored_process = psutil.Process(pid)
            self.monitoring_mode = MonitoringMode.ON_NETWORK_IDLE
            self.monitoring_start_time = time.time()
            
            # Intentar obtener IO counters (requiere permisos)
            try:
                self.last_io_counters = self.monitored_process.io_counters()
                self._log(f"IO counters inicializados: read={self.last_io_counters.read_bytes}, write={self.last_io_counters.write_bytes}")
            except psutil.AccessDenied:
                self._log_error("Se requieren permisos de administrador para monitorear la actividad de red.")
                raise PermissionError("Se requieren permisos de administrador para esta función.")
            
            # Timer de monitoreo cada 2 segundos (intervalo rápido inicial)
            self.monitor_timer.start(2000)
            
            # Health check cada 10 segundos
            self.health_check_timer.start(10000)
            
            self._log("Monitoreo de red iniciado correctamente")
            
        except Exception as e:
            if self.retry_count < self.MAX_RETRIES:
                self.retry_count += 1
                self._log(f"Error al iniciar monitoreo de red (intento {self.retry_count}/{self.MAX_RETRIES}): {e}")
                time.sleep(self.retry_count)
                self.start_monitoring_for_network_idle(pid, process_name)
            else:
                self._log_error(f"Error fatal: {e}")
                raise
    
    def stop_monitoring(self):
        """
        Detiene el monitoreo y limpia todo el estado.
        Safe to call multiple times.
        """
        # Resetear estado de red
        self.consecutive_idle_checks = 0
        self.baseline_calculated = False
        self.baseline_sample_count = 0
        self.baseline_network_usage = 0.0
        self.network_history.clear()
        self.retry_count = 0
        self.last_io_counters = None
        
        # Detener timers
        self.monitor_timer.stop()
        self.health_check_timer.stop()
        
        # Limpiar referencias
        self.monitored_process = None
        self.monitoring_mode = None
        self.monitoring_start_time = None
    
    # ===== CALLBACKS DE TIMERS =====
    
    def _on_monitor_tick(self):
        """
        Callback del timer de monitoreo (solo para modo ON_NETWORK_IDLE).
        Se ejecuta cada 2-5 segundos dependiendo de la actividad.
        """
        if self.monitoring_mode != MonitoringMode.ON_NETWORK_IDLE:
            return
        
        try:
            # Verificar si el proceso sigue existiendo
            if not self.monitored_process or not self.monitored_process.is_running():
                self._log("Proceso terminado (detectado en monitor tick)")
                self._trigger_success()
                return
            
            # Obtener IO counters actuales
            current_io = self.monitored_process.io_counters()
            
            if self.last_io_counters is None:
                self.last_io_counters = current_io
                return
            
            # Calcular bytes transferidos desde la última medición
            # Sumamos read_bytes + write_bytes para tener I/O total
            bytes_delta = (
                (current_io.read_bytes - self.last_io_counters.read_bytes) +
                (current_io.write_bytes - self.last_io_counters.write_bytes)
            )
            
            # Convertir a bytes/segundo
            # El timer puede variar entre 2s y 5s, usar el intervalo actual
            interval_seconds = self.monitor_timer.interval() / 1000.0
            network_usage = bytes_delta / interval_seconds
            
            self.last_io_counters = current_io
            
            # ===== FASE 1: CALCULAR BASELINE DINÁMICO =====
            if not self.baseline_calculated:
                self.baseline_sample_count += 1
                self.baseline_network_usage += network_usage
                
                if self.baseline_sample_count >= self.BASELINE_SAMPLES_NEEDED:
                    self.baseline_network_usage /= self.BASELINE_SAMPLES_NEEDED
                    self.baseline_calculated = True
                    self._log(f"📊 Baseline calculado: {self.baseline_network_usage:.2f} bytes/sec")
                else:
                    self._log(f"📈 Calculando baseline... ({self.baseline_sample_count}/{self.BASELINE_SAMPLES_NEEDED}) - Actual: {network_usage:.2f} bytes/sec")
                return  # No evaluar inactividad durante el período de baseline
            
            # ===== FASE 2: VENTANA DESLIZANTE =====
            self.network_history.append(network_usage)
            
            # ===== FASE 3: THRESHOLD ADAPTATIVO =====
            # Usar 5% del baseline o mínimo 1KB/s (lo que sea mayor)
            adaptive_threshold = max(
                self.baseline_network_usage * 0.05,
                self.NETWORK_USAGE_THRESHOLD_BYTES
            )
            
            # ===== FASE 4: CONTAR MEDICIONES INACTIVAS =====
            idle_count = sum(1 for usage in self.network_history if usage < adaptive_threshold)
            
            # ===== FASE 5: EVALUAR INACTIVIDAD SOSTENIDA =====
            if idle_count >= self.REQUIRED_IDLE_CHECKS:
                # Mayoría de mediciones están inactivas
                self.consecutive_idle_checks += 1
                current_idle_seconds = self.consecutive_idle_checks * interval_seconds
                
                self._log(f"⏸️  Inactividad detectada: {idle_count}/{len(self.network_history)} mediciones bajo threshold ({adaptive_threshold:.0f} bytes/s) - Tiempo inactivo: {current_idle_seconds:.0f}s")
                
                if current_idle_seconds >= self.IDLE_THRESHOLD_SECONDS:
                    # ¡INACTIVIDAD CONFIRMADA!
                    avg_usage = sum(self.network_history) / len(self.network_history)
                    self._log(f"✅ INACTIVIDAD SOSTENIDA ({current_idle_seconds:.0f}s). Promedio: {avg_usage:.2f} bytes/sec")
                    self._trigger_success()
                else:
                    # Aumentar intervalo de monitoreo para ahorrar recursos
                    if self.monitor_timer.interval() < 5000:
                        self.monitor_timer.setInterval(5000)
                        self._log("⏱️  Intervalo aumentado a 5s (modo ahorro)")
            else:
                # Hay actividad significativa
                if self.consecutive_idle_checks > 0:
                    self._log(f"🔴 Actividad detectada: {network_usage:.2f} bytes/sec (threshold: {adaptive_threshold:.0f}). Reseteando contador.")
                self.consecutive_idle_checks = 0
                
                # Volver a intervalo rápido
                if self.monitor_timer.interval() > 2000:
                    self.monitor_timer.setInterval(2000)
                    self._log("⏱️  Intervalo reducido a 2s (modo activo)")
        
        except psutil.NoSuchProcess:
            self._log("Proceso terminado (NoSuchProcess exception)")
            self._trigger_success()
        except Exception as e:
            self._log_error(f"Error en monitoreo de red: {e}")
            # Si hay error crítico, considerar completado
            self._trigger_success()
    
    def _on_health_check(self):
        """
        Callback del timer de health check.
        Verifica timeout y existencia del proceso.
        """
        try:
            # ===== VERIFICAR TIMEOUT =====
            if self.monitoring_start_time:
                elapsed_hours = (time.time() - self.monitoring_start_time) / 3600
                if elapsed_hours > self.MAX_MONITORING_DURATION_HOURS:
                    self._log(f"⏰ Timeout alcanzado ({self.MAX_MONITORING_DURATION_HOURS}h). Cancelando monitoreo.")
                    self.stop_monitoring()
                    return
            
            # ===== VERIFICAR EXISTENCIA DEL PROCESO =====
            if self.monitored_process and not self.monitored_process.is_running():
                self._log("✅ Proceso terminado (detectado por health check)")
                self._trigger_success()
        
        except Exception as e:
            self._log_error(f"Error en health check: {e}")
    
    # ===== MÉTODOS PRIVADOS =====
    
    def _trigger_success(self):
        """Dispara el evento de éxito y detiene el monitoreo"""
        self.stop_monitoring()
        self.monitoring_success.emit()
    
    def _log(self, message: str):
        """Registra un mensaje de log con timestamp"""
        timestamp = time.strftime('%H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        self.monitoring_log.emit(log_message)
        print(log_message)  # También a consola para debugging
    
    def _log_error(self, message: str):
        """Registra un mensaje de error con timestamp"""
        timestamp = time.strftime('%H:%M:%S')
        error_message = f"[ERROR {timestamp}] {message}"
        self.monitoring_error.emit(error_message)
        print(error_message)


# ===== FUNCIONES AUXILIARES =====

def get_processes_with_windows():
    """
    Obtiene una lista de procesos que tienen ventanas visibles.
    
    Returns:
        List[dict]: Lista de diccionarios con:
            - pid: ID del proceso
            - name: Nombre del proceso
            - window_title: Título de laventana
            - display_name: Nombre para mostrar en UI
    """
    import win32gui
    import win32process
    
    processes = []
    seen_pids = set()
    
    def enum_windows_callback(hwnd, _):
        """Callback para enumerar ventanas"""
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            if window_text:  # Solo ventanas con título
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                if pid not in seen_pids:
                    try:
                        proc = psutil.Process(pid)
                        processes.append({
                            'pid': pid,
                            'name': proc.name(),
                            'window_title': window_text,
                            'display_name': f"{proc.name()} ({window_text})"
                        })
                        seen_pids.add(pid)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass  # Ignorar procesos inaccesibles
    
    # Enumerar todas las ventanas
    win32gui.EnumWindows(enum_windows_callback, None)
    
    # Ordenar por display_name
    return sorted(processes, key=lambda x: x['display_name'])
