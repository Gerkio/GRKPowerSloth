"""
Presentador principal (lógica de negocio).
Equivalente a MainFormPresenter.cs

Este es el cerebro de la aplicación en el patrón MVP.
Coordina entre la Vista (MainWindow) y los Servicios.
"""

import ctypes
import subprocess
from datetime import datetime, timedelta
from typing import Optional
from PyQt6.QtCore import QObject, QTimer, Qt
from PyQt6.QtWidgets import QApplication

from models.enums import ScheduleMode, PowerAction, Theme, Language
from services.process_monitor import ProcessMonitorService, get_processes_with_windows
from services.settings_manager import SettingsManager, AppSettings
from services.system_integration import SystemIntegration
from managers.localization_manager import LocalizationManager
from managers.theme_manager import ThemeManager
from managers.notification_manager import NotificationManager


class MainPresenter(QObject):
    """
    Presentador principal que contiene toda la lógica de la aplicación.
    
    Patrón MVP: el presentador coordina entre la vista y los servicios.
    NO conoce los detalles de implementación de la UI.
    """
    
    # ===== CONSTANTES =====
    WARNING_SECONDS = 10 * 60   # 10 minutos - cambiar color a amarillo
    DANGER_SECONDS = 2 * 60     # 2 minutos - cambiar color a rojo
    TIMER_INTERVAL_MS = 1000    # 1 segundo
    
    # Windows API para prevenir suspensión
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001
    ES_DISPLAY_REQUIRED = 0x00000002
    
    def __init__(self, view):
        """
        Inicializa el presentador con una vista.
        
        Args:
            view: Instancia de MainWindow (IMainFormView)
        """
        super().__init__()
        
        self.view = view
        self.settings = SettingsManager.load()
        self.process_monitor = ProcessMonitorService()
        
        # Estado del countdown
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self._on_countdown_tick)
        
        self.total_seconds = 0
        self.remaining_seconds = 0
        self.is_running = False
        
        # Conectar eventos de la vista
        self._connect_view_signals()
        
        # Conectar eventos del monitor de procesos
        self.process_monitor.monitoring_success.connect(self._on_monitoring_success)
        self.process_monitor.monitoring_log.connect(lambda msg: print(msg))
        self.process_monitor.monitoring_error.connect(lambda err: print(f"ERROR: {err}"))
    
    def _connect_view_signals(self):
        """Conecta todos los signals de la vista a los handlers del presentador"""
        # Ciclo de vida
        self.view.form_loaded.connect(self._on_form_loaded)
        self.view.form_closing.connect(self._on_form_closing)
        self.view.window_state_changed.connect(self._on_window_state_changed)
        
        # Acciones principales
        self.view.start_clicked.connect(self._on_start_clicked)
        self.view.stop_clicked.connect(self._on_stop_clicked)
        
        # Cambios de configuración
        self.view.mode_changed.connect(self._on_mode_changed)
        self.view.action_changed.connect(lambda _: self._update_and_save_settings())
        self.view.force_close_changed.connect(lambda _: self._update_and_save_settings())
        self.view.prevent_sleep_changed.connect(lambda _: self._update_and_save_settings())
        self.view.specific_time_changed.connect(lambda _: self._on_time_changed())
        
        self.view.start_with_windows_changed.connect(self._on_start_with_windows_changed)
        self.view.always_on_top_changed.connect(self._on_always_on_top_changed)
        self.view.theme_changed.connect(self._on_theme_changed)
        self.view.language_changed.connect(self._on_language_changed)
        
        # Monitor de procesos
        self.view.refresh_processes_clicked.connect(self._populate_process_list)
        self.view.monitor_mode_changed.connect(lambda _: self._update_and_save_settings())
        
        # System tray
        self.view.tray_icon_double_clicked.connect(self._on_tray_restore)
        self.view.show_from_tray_clicked.connect(self._on_tray_restore)
        self.view.exit_from_tray_clicked.connect(lambda: QApplication.quit())
    
    # ===== HANDLERS DEL CICLO DE VIDA =====
    
    def _on_form_loaded(self):
        """Handler cuando el formulario se carga"""
        # Aplicar configuración guardada
        LocalizationManager.set_language(Language(self.settings.current_language))
        self._apply_theme_and_language()
        
        # Restaurar valores de UI
        self.view.set_countdown_time(
            self.settings.last_hours,
            self.settings.last_minutes,
            self.settings.last_seconds
        )
        self.view.set_specific_time(self.settings.last_specific_time)
        self.view.set_action(PowerAction(self.settings.last_action_index))
        self.view.set_force_close(self.settings.is_force_close_enabled)
        self.view.set_prevent_sleep(self.settings.prevent_sleep)
        self.view.set_start_with_windows(SystemIntegration.is_startup_enabled())
        self.view.set_always_on_top(self.settings.always_on_top)
        self.view.set_mode(ScheduleMode(self.settings.last_mode))
        self.view.set_monitor_by_exit(self.settings.monitor_by_exit)
        
        # Si está en modo monitor, cargar lista de procesos
        if ScheduleMode(self.settings.last_mode) == ScheduleMode.MONITOR_ACTIVITY:
            self._populate_process_list()
        
        self._update_ui_state(False)
        self._update_end_time_preview()
    
    def _on_form_closing(self):
        """Handler cuando se cierra el formulario"""
        if not self.is_running:
            self._update_and_save_settings()
        
        self._deactivate_keep_awake()
        self.process_monitor.stop_monitoring()
        self.countdown_timer.stop()
    
    def _on_window_state_changed(self, state):
        """Handler cuando cambia el estado de la ventana"""
        if state == Qt.WindowState.WindowMinimized:
            self.view.hide_window()
            self.view.show_tray_icon()
            NotificationManager.show_notification(
                "GRK PowerSloth",
                LocalizationManager.get("status_minimized")
            )
        elif state in (Qt.WindowState.WindowNoState, Qt.WindowState.WindowMaximized):
            self.view.hide_tray_icon()
    
    def _on_tray_restore(self):
        """Handler para restaurar desde la bandeja"""
        self.view.show_window()
        self.view.bring_to_front()
        self.view.hide_tray_icon()
    
    # ===== HANDLERS DE ACCIONES PRINCIPALES =====
    
    def _on_start_clicked(self):
        """Handler cuando se hace clic en Start"""
        mode = self.view.get_selected_mode()
        
        if mode in (ScheduleMode.COUNTDOWN, ScheduleMode.SPECIFIC_TIME):
            self._start_countdown_mode()
        elif mode == ScheduleMode.MONITOR_ACTIVITY:
            self._start_monitoring_mode()
    
    def _start_countdown_mode(self):
        """Inicia el modo de cuenta regresiva"""
        mode = self.view.get_selected_mode()
        
        if mode == ScheduleMode.COUNTDOWN:
            self.remaining_seconds = self.view.get_countdown_total_seconds()
        else:  # SPECIFIC_TIME
            now = datetime.now()
            target_time = self.view.get_specific_time()
            
            target_datetime = now.replace(
                hour=target_time.hour(),
                minute=target_time.minute(),
                second=target_time.second(),
                microsecond=0
            )
            
            # Si la hora ya pasó, agregar un día
            if target_datetime <= now:
                target_datetime += timedelta(days=1)
            
            self.remaining_seconds = int((target_datetime - now).total_seconds())
        
        if self.remaining_seconds <= 0:
            return
        
        self.total_seconds = self.remaining_seconds
        self.countdown_timer.start(self.TIMER_INTERVAL_MS)
        self._update_ui_state(True)
        self._activate_keep_awake()
        
        NotificationManager.show_notification(
            LocalizationManager.get("notification_timer_started"),
            LocalizationManager.get("notification_timer_started_body")
        )
    
    def _start_monitoring_mode(self):
        """Inicia el modo de monitoreo de procesos"""
        selected_process = self.view.get_selected_process()
        if not selected_process:
            self.view.show_error_message("Error", "Selecciona un proceso primero.")
            return
        
        try:
            if self.view.get_is_monitor_by_exit():
                self.process_monitor.start_monitoring_for_exit(selected_process['pid'])
            else:
                self.process_monitor.start_monitoring_for_network_idle(
                    selected_process['pid'],
                    selected_process['name']
                )
            
            self._update_ui_state(True)
            status_text = LocalizationManager.get("status_monitoring").format(
                selected_process['display_name']
            )
            self.view.update_status(status_text)
            
            NotificationManager.show_notification(
                LocalizationManager.get("notification_timer_started"),
                status_text
            )
        
        except ValueError:
            self.view.show_error_message(
                "Error",
                LocalizationManager.get("error_process_not_found")
            )
            self._update_ui_state(False)
        except PermissionError:
            self.view.show_error_message(
                "Error",
                LocalizationManager.get("error_admin_required_for_monitor")
            )
            self._update_ui_state(False)
        except Exception as e:
            self.view.show_error_message("Error", str(e))
            self._update_ui_state(False)
    
    def _on_stop_clicked(self):
        """Handler cuando se hace clic en Stop"""
        self.countdown_timer.stop()
        self.process_monitor.stop_monitoring()
        self._deactivate_keep_awake()
        self._update_ui_state(False)
        self.view.update_status(LocalizationManager.get("status_stopped"))
    
    # ===== HANDLERS DEL TIMER =====
    
    def _on_countdown_tick(self):
        """Handler del tick del timer de countdown"""
        if self.remaining_seconds > 0:
            # Notificación cuando queda 1 minuto
            if self.remaining_seconds == 60:
                NotificationManager.show_notification(
                    LocalizationManager.get("notification_minute_warning"),
                    LocalizationManager.get("notification_minute_warning_body")
                )
            
            self.remaining_seconds -= 1
            self._update_status_label()
            self._update_progress_bar_color()
            self._update_window_title()
        else:
            # Tiempo agotado
            self.countdown_timer.stop()
            self._deactivate_keep_awake()
            self._execute_final_action()
    
    def _on_monitoring_success(self):
        """Handler cuando el monitoreo detecta la condición"""
        self._execute_final_action()
    
    # ===== MÉTODOS DE ACTUALIZACIÓN DE UI =====
    
    def _populate_process_list(self):
        """Pobla la lista de procesos con ventanas"""
        try:
            processes = get_processes_with_windows()
            self.view.set_process_list(processes)
        except Exception as e:
            self.view.show_error_message(
                "Process List Error",
                f"Failed to load process list: {e}"
            )
    
    def _update_status_label(self):
        """Actualiza la etiqueta de estado con el tiempo restante"""
        action = self.view.get_selected_action()
        action_text = LocalizationManager.get(f"action_{action.name.lower()}")
        
        hours = self.remaining_seconds // 3600
        minutes = (self.remaining_seconds % 3600) // 60
        seconds = self.remaining_seconds % 60
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        status = LocalizationManager.get("status_countdown").format(action_text, time_str)
        # Reemplazar {0} y {1} con los valores
        status = status.replace("{0}", action_text).replace("{1}", time_str)
        self.view.update_status(status)
        
        if self.total_seconds > 0:
            progress = self.total_seconds - self.remaining_seconds
            self.view.update_progress_bar(progress, self.total_seconds)
    
    def _update_window_title(self):
        """Actualiza el título de la ventana con el tiempo restante"""
        hours = self.remaining_seconds // 3600
        minutes = (self.remaining_seconds % 3600) // 60
        seconds = self.remaining_seconds % 60
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        self.view.update_window_title(f"[{time_str}] GRK PowerSloth")
    
    def _update_progress_bar_color(self):
        """Actualiza el color de la barra de progreso según el tiempo restante"""
        palette = ThemeManager.get_palette(Theme(self.settings.current_theme))
        
        if self.remaining_seconds < self.DANGER_SECONDS:
            color = palette.danger
        elif self.remaining_seconds < self.WARNING_SECONDS:
            color = palette.warning
        else:
            color = palette.accent_primary
        
        self.view.set_progress_bar_color(color)
    
    def _update_end_time_preview(self):
        """Actualiza la vista previa de la hora de finalización"""
        mode = self.view.get_selected_mode()
        
        if mode not in (ScheduleMode.COUNTDOWN, ScheduleMode.SPECIFIC_TIME):
            self.view.set_end_time("", False)
            return
        
        now = datetime.now()
        
        if mode == ScheduleMode.COUNTDOWN:
            total_seconds = self.view.get_countdown_total_seconds()
            if total_seconds > 0:
                end_time = now + timedelta(seconds=total_seconds)
                # Formato 12 horas con AM/PM
                time_fmt = end_time.strftime("%I:%M %p")
                text = LocalizationManager.get("status_will_run_at").format(time_fmt)
                # Reemplazar {0}
                text = text.replace("{0}", time_fmt)
                self.view.set_end_time(text, True)
            else:
                self.view.set_end_time("", False)
        else:  # SPECIFIC_TIME
            target_time = self.view.get_specific_time()
            # Formato 12 horas con AM/PM
            self.view.set_end_time(f"→ {target_time.toString('hh:mm:ss AP')}", True)
    
    def _update_ui_state(self, is_running: bool):
        """Actualiza el estado de la UI (habilitado/deshabilitado)"""
        self.is_running = is_running
        self.view.set_ui_state(is_running)
        
        if not is_running:
            self.view.update_status(LocalizationManager.get("status_default"))
            self.view.update_window_title(LocalizationManager.get("main_title"))
            
            palette = ThemeManager.get_palette(Theme(self.settings.current_theme))
            self.view.set_progress_bar_color(palette.accent_primary)
            self.view.update_progress_bar(0, 1)
            
            self._update_and_save_settings()
    
    # ===== EJECUCIÓN DE ACCIONES =====
    
    def _execute_final_action(self):
        """Ejecuta la acción final (shutdown, restart, etc.)"""
        self.view.update_window_title(LocalizationManager.get("main_title"))
        self.view.bring_to_front()
        
        action = self.view.get_selected_action()
        action_text = LocalizationManager.get(f"action_{action.name.lower()}")
        
        # Mostrar diálogo de advertencia
        if self.view.show_warning_dialog(action_text):
            self.view.update_status("Ejecutando...")
            
            try:
                force_flag = " /f" if self.view.get_is_force_close_enabled() else ""
                
                if action == PowerAction.SHUTDOWN:
                    subprocess.run(f"shutdown /s{force_flag} /t 0", shell=True)
                elif action == PowerAction.RESTART:
                    subprocess.run(f"shutdown /r{force_flag} /t 0", shell=True)
                elif action == PowerAction.RESTART_UEFI:
                    subprocess.run(f"shutdown /r /fw{force_flag} /t 0", shell=True)
                elif action == PowerAction.HIBERNATE:
                    subprocess.run("shutdown /h", shell=True)
                elif action == PowerAction.SLEEP:
                    subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
                
                QApplication.quit()
            
            except Exception as e:
                self.view.show_error_message("Error", str(e))
                self._update_ui_state(False)
        else:
            # Usuario canceló
            self._on_stop_clicked()
    
    # ===== KEEP AWAKE (PREVENIR SUSPENSIÓN) =====
    
    def _activate_keep_awake(self):
        """Previene la suspensión del sistema si está habilitado"""
        if self.view.get_is_prevent_sleep_enabled():
            ctypes.windll.kernel32.SetThreadExecutionState(
                self.ES_CONTINUOUS | self.ES_SYSTEM_REQUIRED | self.ES_DISPLAY_REQUIRED
            )
    
    def _deactivate_keep_awake(self):
        """Permite la suspensión del sistema"""
        ctypes.windll.kernel32.SetThreadExecutionState(self.ES_CONTINUOUS)
    
    # ===== HANDLERS DE CONFIGURACIÓN =====
    
    def _on_time_changed(self):
        """Handler cuando cambia la hora específica o el countdown"""
        self._update_end_time_preview()
        self._update_and_save_settings()
    
    def _on_mode_changed(self, mode):
        """Handler cuando cambia el modo de operación"""
        if mode == ScheduleMode.MONITOR_ACTIVITY:
            self._populate_process_list()
        self._update_end_time_preview()
        self._update_and_save_settings()
    
    def _on_start_with_windows_changed(self, enabled: bool):
        """Handler cuando cambia la opción de inicio con Windows"""
        try:
            SystemIntegration.set_startup(enabled)
            self.settings.start_with_windows = enabled
            SettingsManager.save(self.settings)
        except Exception as e:
            self.view.show_error_message("Error de Permisos", str(e))
            self.view.set_start_with_windows(not enabled)  # Revertir UI
    
    def _on_always_on_top_changed(self, enabled: bool):
        """Handler cuando cambia la opción de siempre visible"""
        self.settings.always_on_top = enabled
        SettingsManager.save(self.settings)
    
    def _on_theme_changed(self, theme: Theme):
        """Handler cuando cambia el tema"""
        self.settings.current_theme = theme.value
        self._apply_theme_and_language()
        SettingsManager.save(self.settings)
    
    def _on_language_changed(self, language: Language):
        """Handler cuando cambia el idioma"""
        self.settings.current_language = language.value
        LocalizationManager.set_language(language)
        self._apply_theme_and_language()
        SettingsManager.save(self.settings)
    
    def _apply_theme_and_language(self):
        """Aplica el tema y el idioma actual"""
        palette = ThemeManager.get_palette(Theme(self.settings.current_theme))
        self.view.apply_theme(palette)
        
        # Actualizar acciones disponibles con traducciones
        actions = [
            LocalizationManager.get("action_shutdown"),
            LocalizationManager.get("action_restart"),
            LocalizationManager.get("action_sleep"),
            LocalizationManager.get("action_restart_uefi"),
            LocalizationManager.get("action_hibernate")
        ]
        current_action = self.view.get_selected_action()
        self.view.set_available_actions(actions)
        self.view.set_action(current_action)
        
        self.view.reapply_localization()
        self.view.update_window_title(LocalizationManager.get("main_title"))
    
    def _update_and_save_settings(self):
        """Actualiza y guarda la configuración"""
        if self.is_running:
            return
        
        hours, minutes, seconds = self.view.get_countdown_time()
        self.settings.last_hours = hours
        self.settings.last_minutes = minutes
        self.settings.last_seconds = seconds
        
        specific_time = self.view.get_specific_time()
        self.settings.last_specific_time = specific_time.toString("HH:mm:ss")
        
        self.settings.last_action_index = self.view.get_selected_action().value
        self.settings.is_force_close_enabled = self.view.get_is_force_close_enabled()
        self.settings.prevent_sleep = self.view.get_is_prevent_sleep_enabled()
        self.settings.last_mode = self.view.get_selected_mode().value
        self.settings.monitor_by_exit = self.view.get_is_monitor_by_exit()
        
        selected_process = self.view.get_selected_process()
        if selected_process:
            self.settings.last_monitored_process_name = selected_process['name']
        
        SettingsManager.save(self.settings)
