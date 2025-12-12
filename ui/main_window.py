"""
Ventana principal de la aplicación.
Equivalente a MainForm.cs + MainForm.Designer.cs

Esta es la vista principal del patrón MVP.
Contiene todos los controles de UI y expone eventos (signals) al Presenter.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QRadioButton, QCheckBox, QGroupBox,
    QComboBox, QSpinBox, QTimeEdit, QProgressBar, QLineEdit,
    QMenuBar, QMenu, QSystemTrayIcon, QMessageBox, QButtonGroup,
    QStyle
)
from PyQt6.QtCore import pyqtSignal, Qt, QTime, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon, QAction, QFont, QActionGroup

from models.enums import ScheduleMode, PowerAction, Theme, Language
from managers.localization_manager import LocalizationManager
from managers.theme_manager import ThemeManager, ColorPalette
from ui.display_helper import DisplayHelper
from ui.validated_spinbox import ValidatedSpinBox


class MainWindow(QMainWindow):
    """
    Vista principal de la aplicación (patrón MVP).
    
    Responsabilidades:
    - Renderizar la interfaz de usuario
    - Capturar eventos del usuario y emitir signals
    - Proporcionar métodos para que el presenter actualice la UI
    
    NO contiene lógica de negocio.
    """
    
    # ===== SIGNALS (Eventos para el Presenter) =====
    
    # Ciclo de vida
    form_loaded = pyqtSignal()
    form_closing = pyqtSignal()
    window_state_changed = pyqtSignal(object)  # WindowState
    
    # Acciones principales
    start_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    
    # Cambios de configuración
    mode_changed = pyqtSignal(object)         # ScheduleMode
    action_changed = pyqtSignal(object)       # PowerAction
    force_close_changed = pyqtSignal(bool)
    prevent_sleep_changed = pyqtSignal(bool)
    start_with_windows_changed = pyqtSignal(bool)
    always_on_top_changed = pyqtSignal(bool)
    watchdog_enabled_changed = pyqtSignal(bool)  # Watchdog toggle
    theme_changed = pyqtSignal(object)        # Theme
    language_changed = pyqtSignal(object)     # Language
    specific_time_changed = pyqtSignal(object) # QTime
    
    # Monitor de procesos
    refresh_processes_clicked = pyqtSignal()
    monitor_mode_changed = pyqtSignal(bool)   # True = exit, False = network
    
    # System tray
    tray_icon_double_clicked = pyqtSignal()
    show_from_tray_clicked = pyqtSignal()
    
    # Updates
    check_updates_clicked = pyqtSignal()
    show_from_tray_clicked = pyqtSignal()
    exit_from_tray_clicked = pyqtSignal()
    
    # Nuevas funcionalidades
    schedule_clicked = pyqtSignal()           # Calendario de eventos
    history_clicked = pyqtSignal()            # Ver historial
    compact_mode_changed = pyqtSignal(bool)   # Modo compacto
    
    def __init__(self):
        super().__init__()
        self._loaded = False
        self._setup_ui()
        self._setup_menu()
        self._setup_tray_icon()
        self._connect_signals()
        self._update_panel_visibility()
    
    # ===== SETUP DE LA UI =====
    
    def _setup_ui(self):
        """Configura todos los widgets de la interfaz"""
        self.setWindowTitle(LocalizationManager.get("main_title"))
        
        # Usar DisplayHelper para tamaño responsivo
        self._scale_factor = DisplayHelper.get_scale_factor()
        
        # Ancho fijo, altura dinámica
        self.setFixedWidth(DisplayHelper.scale_value(480))
        # La altura se ajustará automáticamente al contenido
        
        # Intentar cargar icono desde el proyecto original
        self._set_window_icon()
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self._main_layout = QVBoxLayout(central_widget)
        self._main_layout.setSpacing(DisplayHelper.get_spacing(10))
        self._main_layout.setContentsMargins(
            DisplayHelper.get_padding(14),
            DisplayHelper.get_padding(14),
            DisplayHelper.get_padding(14),
            DisplayHelper.get_padding(14)
        )
        
        # Referencia para usar en el resto del setup
        main_layout = self._main_layout
        
        # ========== GRUPO: CONDICIÓN DE DISPARO (Layout Horizontal) ==========
        self.group_trigger = QGroupBox(LocalizationManager.get("trigger_condition_label"))
        trigger_layout = QHBoxLayout()  # Horizontal para ahorrar espacio
        trigger_layout.setSpacing(DisplayHelper.get_spacing(15))
        
        # Radio buttons para modos
        self.radio_countdown = QRadioButton(LocalizationManager.get("mode_countdown"))
        self.radio_specific_time = QRadioButton(LocalizationManager.get("mode_specific_time"))
        self.radio_monitor = QRadioButton(LocalizationManager.get("mode_monitor_activity"))
        self.radio_countdown.setChecked(True)
        
        # Agrupar radio buttons
        self.mode_group = QButtonGroup()
        self.mode_group.addButton(self.radio_countdown, 0)
        self.mode_group.addButton(self.radio_specific_time, 1)
        self.mode_group.addButton(self.radio_monitor, 2)
        
        trigger_layout.addWidget(self.radio_countdown)
        trigger_layout.addWidget(self.radio_specific_time)
        trigger_layout.addWidget(self.radio_monitor)
        trigger_layout.addStretch()  # Empujar a la izquierda
        self.group_trigger.setLayout(trigger_layout)
        main_layout.addWidget(self.group_trigger)
        
        # ========== PANEL: COUNTDOWN ==========
        self.panel_countdown = QWidget()
        countdown_layout = QGridLayout(self.panel_countdown)
        countdown_layout.setSpacing(10)
        
        # Labels
        lbl_hours = QLabel(LocalizationManager.get("hours"))
        lbl_minutes = QLabel(LocalizationManager.get("minutes"))
        lbl_seconds = QLabel(LocalizationManager.get("seconds"))
        
        # SpinBoxes con validación visual
        spinbox_width = DisplayHelper.scale_value(80)
        
        self.spin_hours = ValidatedSpinBox()
        self.spin_hours.setRange(0, 23)  # Límite lógico de horas
        self.spin_hours.setValue(0)
        self.spin_hours.setMinimumWidth(spinbox_width)
        
        self.spin_minutes = ValidatedSpinBox()
        self.spin_minutes.setRange(0, 59)
        self.spin_minutes.setValue(30)
        self.spin_minutes.setMinimumWidth(spinbox_width)
        
        self.spin_seconds = ValidatedSpinBox()
        self.spin_seconds.setRange(0, 59)
        self.spin_seconds.setValue(0)
        self.spin_seconds.setMinimumWidth(spinbox_width)
        
        # Layout de countdown
        countdown_layout.addWidget(lbl_hours, 0, 0)
        countdown_layout.addWidget(self.spin_hours, 0, 1)
        countdown_layout.addWidget(lbl_minutes, 0, 2)
        countdown_layout.addWidget(self.spin_minutes, 0, 3)
        countdown_layout.addWidget(lbl_seconds, 0, 4)
        countdown_layout.addWidget(self.spin_seconds, 0, 5)
        countdown_layout.setColumnStretch(6, 1)
        
        main_layout.addWidget(self.panel_countdown)
        
        # ========== PANEL: HORA ESPECÍFICA ==========
        self.panel_specific_time = QWidget()
        specific_time_layout = QHBoxLayout(self.panel_specific_time)
        specific_time_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_time = QLabel("⏰")
        lbl_time.setFont(QFont("Segoe UI", 16))
        
        self.time_picker = QTimeEdit()
        self.time_picker.setDisplayFormat("hh:mm:ss AP")  # Formato 12 horas con AM/PM
        self.time_picker.setTime(QTime(12, 0, 0))
        self.time_picker.setMinimumWidth(DisplayHelper.scale_value(170))
        
        specific_time_layout.addWidget(lbl_time)
        specific_time_layout.addWidget(self.time_picker)
        specific_time_layout.addStretch()
        
        main_layout.addWidget(self.panel_specific_time)
        
        # ========== PANEL: MONITOR DE PROCESOS ==========
        self.panel_monitor = QWidget()
        monitor_layout = QVBoxLayout(self.panel_monitor)
        monitor_layout.setContentsMargins(0, 0, 0, 0)
        monitor_layout.setSpacing(12)
        
        # Selector de proceso (Movido arriba, filtro eliminado)
        
        # Selector de proceso
        process_layout = QHBoxLayout()
        lbl_process = QLabel(LocalizationManager.get("process_label"))
        self.cmb_processes = QComboBox()
        self.cmb_processes.setMinimumWidth(250)
        self.cmb_processes.setFixedHeight(32)
        
        # Botón de actualización con icono del sistema
        self.btn_refresh_processes = QPushButton()
        refresh_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)
        self.btn_refresh_processes.setIcon(refresh_icon)
        self.btn_refresh_processes.setFixedSize(
            DisplayHelper.scale_value(40),
            DisplayHelper.scale_value(32)
        )
        self.btn_refresh_processes.setToolTip(LocalizationManager.get("tooltip_refresh"))
        
        process_layout.addWidget(lbl_process)
        process_layout.addWidget(self.cmb_processes, 1)
        process_layout.addWidget(self.btn_refresh_processes)
        monitor_layout.addLayout(process_layout)
        
        # ===== CONDICIÓN DE MONITOREO (Layout Horizontal Compacto) =====
        condition_container = QWidget()
        condition_container.setObjectName("conditionContainer")
        condition_container.setFixedHeight(DisplayHelper.scale_value(65))  # Altura reducida
        
        condition_layout = QVBoxLayout(condition_container)
        condition_layout.setContentsMargins(12, 8, 12, 8)
        condition_layout.setSpacing(4)
        
        # Título
        lbl_condition = QLabel(LocalizationManager.get("monitoring_condition"))
        lbl_condition.setFixedHeight(20)
        
        # Layout horizontal para los radio buttons
        radio_layout = QHBoxLayout()
        radio_layout.setSpacing(DisplayHelper.get_spacing(20))
        
        # Radio buttons
        self.radio_on_exit = QRadioButton(LocalizationManager.get("condition_on_exit"))
        self.radio_on_exit.setChecked(True)
        
        self.radio_on_network_idle = QRadioButton(LocalizationManager.get("condition_on_idle"))
        
        # Grupo de radio buttons
        self.monitor_mode_group = QButtonGroup()
        self.monitor_mode_group.addButton(self.radio_on_exit, 0)
        self.monitor_mode_group.addButton(self.radio_on_network_idle, 1)
        
        # Agregar a layout horizontal
        radio_layout.addWidget(self.radio_on_exit)
        radio_layout.addWidget(self.radio_on_network_idle)
        radio_layout.addStretch()
        
        # Agregar widgets al layout principal del container
        condition_layout.addWidget(lbl_condition)
        condition_layout.addLayout(radio_layout)
        
        # Guardar referencia para aplicar tema dinámicamente
        self.condition_container = condition_container
        self.lbl_condition = lbl_condition
        
        monitor_layout.addWidget(condition_container)
        
        main_layout.addWidget(self.panel_monitor)
        
        # ========== ACCIÓN ==========
        action_layout = QHBoxLayout()
        lbl_action = QLabel(LocalizationManager.get("action"))
        lbl_action.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        
        self.cmb_action = QComboBox()
        self.cmb_action.addItems([
            LocalizationManager.get("action_shutdown"),
            LocalizationManager.get("action_restart"),
            LocalizationManager.get("action_sleep"),
            LocalizationManager.get("action_restart_uefi"),
            LocalizationManager.get("action_hibernate")
        ])
        self.cmb_action.setMinimumWidth(200)
        
        action_layout.addWidget(lbl_action)
        action_layout.addWidget(self.cmb_action)
        action_layout.addStretch()
        main_layout.addLayout(action_layout)
        
        # ========== OPCIONES ==========
        options_layout = QHBoxLayout()
        
        self.chk_force_close = QCheckBox(LocalizationManager.get("force_close_apps"))
        self.chk_force_close.setToolTip(LocalizationManager.get("tooltip_force_close"))
        
        self.chk_prevent_sleep = QCheckBox(LocalizationManager.get("prevent_sleep_screen_off"))
        self.chk_prevent_sleep.setChecked(True)
        self.chk_prevent_sleep.setToolTip(LocalizationManager.get("tooltip_prevent_sleep"))
        
        options_layout.addWidget(self.chk_force_close)
        options_layout.addWidget(self.chk_prevent_sleep)
        options_layout.addStretch()
        main_layout.addLayout(options_layout)
        
        # ========== BARRA DE PROGRESO ==========
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMinimumHeight(25)
        main_layout.addWidget(self.progress_bar)
        
        # ========== ETIQUETAS DE ESTADO ==========
        self.lbl_status = QLabel(LocalizationManager.get("status_default"))
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setFont(QFont("Segoe UI", 10))
        main_layout.addWidget(self.lbl_status)
        
        self.lbl_end_time = QLabel("")
        self.lbl_end_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_end_time.setFont(QFont("Segoe UI", 9))
        main_layout.addWidget(self.lbl_end_time)
        
        # NO usar addStretch() - dejamos que la ventana se ajuste al contenido
        
        # ========== BOTONES DE ACCIÓN ==========
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        self.btn_start = QPushButton(f"▶ {LocalizationManager.get('start')}")
        self.btn_start.setObjectName("btnStart")
        self.btn_start.setFixedHeight(45)
        self.btn_start.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        
        self.btn_stop = QPushButton(f"⏹ {LocalizationManager.get('stop')}")
        self.btn_stop.setFixedHeight(45)
        self.btn_stop.setEnabled(False)
        self.btn_stop.setFont(QFont("Segoe UI", 11))
        
        buttons_layout.addWidget(self.btn_start, 1)
        buttons_layout.addWidget(self.btn_stop, 1)
        main_layout.addLayout(buttons_layout)
    
    def _setup_menu(self):
        """Configura la barra de menú"""
        menubar = self.menuBar()
        
        # ========== MENÚ FILE ==========
        menu_file = menubar.addMenu(LocalizationManager.get("menu_file"))
        
        self.action_start = QAction(LocalizationManager.get("menu_start"), self)
        self.action_stop = QAction(LocalizationManager.get("menu_stop"), self)
        self.action_stop.setEnabled(False)
        self.action_exit = QAction(LocalizationManager.get("menu_exit"), self)
        
        menu_file.addAction(self.action_start)
        menu_file.addAction(self.action_stop)
        menu_file.addSeparator()
        
        # Nuevas opciones
        self.action_schedule = QAction("🗓️ Calendario de Eventos...", self)
        self.action_history = QAction("📋 Ver Historial...", self)
        self.action_compact_mode = QAction("🔲 Modo Compacto", self)
        self.action_compact_mode.setCheckable(True)
        
        menu_file.addAction(self.action_schedule)
        menu_file.addAction(self.action_history)
        menu_file.addSeparator()
        menu_file.addAction(self.action_compact_mode)
        menu_file.addSeparator()
        menu_file.addAction(self.action_exit)
        
        # ========== MENÚ SETTINGS ==========
        menu_settings = menubar.addMenu(LocalizationManager.get("menu_settings"))
        
        self.action_start_with_windows = QAction(LocalizationManager.get("menu_start_with_windows"), self)
        self.action_start_with_windows.setCheckable(True)
        
        self.action_always_on_top = QAction(LocalizationManager.get("menu_always_on_top"), self)
        self.action_always_on_top.setCheckable(True)
        
        self.action_enable_watchdog = QAction(LocalizationManager.get("menu_watchdog"), self)
        self.action_enable_watchdog.setCheckable(True)
        self.action_enable_watchdog.setToolTip(LocalizationManager.get("tooltip_watchdog"))
        
        menu_settings.addAction(self.action_start_with_windows)
        menu_settings.addAction(self.action_always_on_top)
        menu_settings.addAction(self.action_enable_watchdog)
        menu_settings.addSeparator()
        
        # Submenú Theme
        menu_theme = menu_settings.addMenu(LocalizationManager.get("menu_theme"))
        
        theme_group = QActionGroup(self)
        
        self.action_theme_light = QAction(LocalizationManager.get("menu_light"), self)
        self.action_theme_light.setCheckable(True)
        theme_group.addAction(self.action_theme_light)
        
        self.action_theme_dark = QAction(LocalizationManager.get("menu_dark"), self)
        self.action_theme_dark.setCheckable(True)
        self.action_theme_dark.setChecked(True)  # Default
        theme_group.addAction(self.action_theme_dark)
        
        self.action_theme_nordic = QAction("Nordic Night", self)
        self.action_theme_nordic.setCheckable(True)
        theme_group.addAction(self.action_theme_nordic)
        
        self.action_theme_dracula = QAction("Dracula", self)
        self.action_theme_dracula.setCheckable(True)
        theme_group.addAction(self.action_theme_dracula)
        
        self.action_theme_blood = QAction("Blood Moon", self)
        self.action_theme_blood.setCheckable(True)
        theme_group.addAction(self.action_theme_blood)
        
        self.action_theme_high_contrast = QAction("♿ Alto Contraste", self)
        self.action_theme_high_contrast.setCheckable(True)
        theme_group.addAction(self.action_theme_high_contrast)
        
        menu_theme.addAction(self.action_theme_light)
        menu_theme.addAction(self.action_theme_dark)
        menu_theme.addAction(self.action_theme_nordic)
        menu_theme.addAction(self.action_theme_dracula)
        menu_theme.addAction(self.action_theme_blood)
        menu_theme.addAction(self.action_theme_high_contrast)
        
        # Submenú Language
        menu_language = menu_settings.addMenu(LocalizationManager.get("menu_language"))
        
        lang_group = QActionGroup(self)
        
        self.action_lang_english = QAction(LocalizationManager.get("menu_english"), self)
        self.action_lang_english.setCheckable(True)
        lang_group.addAction(self.action_lang_english)
        
        self.action_lang_spanish = QAction(LocalizationManager.get("menu_spanish"), self)
        self.action_lang_spanish.setCheckable(True)
        self.action_lang_spanish.setChecked(True)  # Default
        lang_group.addAction(self.action_lang_spanish)
        
        self.action_lang_portuguese = QAction("Português (Brasil)", self)
        self.action_lang_portuguese.setCheckable(True)
        lang_group.addAction(self.action_lang_portuguese)
        
        self.action_lang_french = QAction("Français", self)
        self.action_lang_french.setCheckable(True)
        lang_group.addAction(self.action_lang_french)
        
        menu_language.addAction(self.action_lang_english)
        menu_language.addAction(self.action_lang_spanish)
        menu_language.addAction(self.action_lang_portuguese)
        menu_language.addAction(self.action_lang_french)
        
        # ========== MENÚ HELP ==========
        menu_help = menubar.addMenu(LocalizationManager.get("menu_help"))
        
        self.action_check_updates = QAction("Buscar Actualizaciones...", self)
        self.action_about = QAction(LocalizationManager.get("menu_about"), self)
        
        menu_help.addAction(self.action_check_updates)
        menu_help.addSeparator()
        menu_help.addAction(self.action_about)
    
    def _setup_tray_icon(self):
        """Configura el icono de la bandeja del sistema"""
        from pathlib import Path
        
        self.tray_icon = QSystemTrayIcon(self)
        
        # Cargar el icono de la aplicación
        icon_path = Path(__file__).parent.parent / "app_icon.ico"
        if icon_path.exists():
            self.tray_icon.setIcon(QIcon(str(icon_path)))
        
        # Menú contextual del tray
        tray_menu = QMenu()
        
        action_show = QAction(LocalizationManager.get("tray_show"), self)
        action_show.triggered.connect(self.show_from_tray_clicked.emit)
        
        action_exit = QAction(LocalizationManager.get("tray_exit"), self)
        action_exit.triggered.connect(self.exit_from_tray_clicked.emit)
        
        tray_menu.addAction(action_show)
        tray_menu.addSeparator()
        tray_menu.addAction(action_exit)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
    
    def _connect_signals(self):
        """Conecta los eventos internos de la UI a los signals"""
        # Botones principales
        self.btn_start.clicked.connect(self.start_clicked.emit)
        self.btn_stop.clicked.connect(self.stop_clicked.emit)
        
        # Menú File
        self.action_start.triggered.connect(self.start_clicked.emit)
        self.action_stop.triggered.connect(self.stop_clicked.emit)
        self.action_exit.triggered.connect(self.close)
        
        # Radio buttons de modo
        self.radio_countdown.toggled.connect(lambda checked: 
            self._on_mode_toggled(ScheduleMode.COUNTDOWN) if checked else None)
        self.radio_specific_time.toggled.connect(lambda checked: 
            self._on_mode_toggled(ScheduleMode.SPECIFIC_TIME) if checked else None)
        self.radio_monitor.toggled.connect(lambda checked: 
            self._on_mode_toggled(ScheduleMode.MONITOR_ACTIVITY) if checked else None)
        
        # Cambios de tiempo (para actualizar preview)
        self.spin_hours.valueChanged.connect(lambda _: self.specific_time_changed.emit(None))
        self.spin_minutes.valueChanged.connect(lambda _: self.specific_time_changed.emit(None))
        self.spin_seconds.valueChanged.connect(lambda _: self.specific_time_changed.emit(None))
        
        # Acción y opciones
        self.time_picker.timeChanged.connect(self.specific_time_changed.emit)
        self.cmb_action.currentIndexChanged.connect(self._on_action_changed)
        self.chk_force_close.toggled.connect(self.force_close_changed.emit)
        self.chk_prevent_sleep.toggled.connect(self.prevent_sleep_changed.emit)
        
        # Monitor de procesos
        # self.txt_process_filter eliminado
        self.btn_refresh_processes.clicked.connect(self.refresh_processes_clicked.emit)
        self.radio_on_exit.toggled.connect(lambda checked: 
            self.monitor_mode_changed.emit(True) if checked else None)
        self.radio_on_network_idle.toggled.connect(lambda checked: 
            self.monitor_mode_changed.emit(False) if checked else None)
        
        # Menú Settings
        self.action_start_with_windows.toggled.connect(self.start_with_windows_changed.emit)
        self.action_always_on_top.toggled.connect(self._on_always_on_top_toggled)
        self.action_enable_watchdog.toggled.connect(self.watchdog_enabled_changed.emit)
        
        self.action_theme_light.triggered.connect(lambda: self._on_theme_selected(Theme.LIGHT))
        self.action_theme_dark.triggered.connect(lambda: self._on_theme_selected(Theme.DARK))
        self.action_theme_nordic.triggered.connect(lambda: self._on_theme_selected(Theme.NORDIC))
        self.action_theme_dracula.triggered.connect(lambda: self._on_theme_selected(Theme.DRACULA))
        self.action_theme_blood.triggered.connect(lambda: self._on_theme_selected(Theme.BLOOD))
        self.action_theme_high_contrast.triggered.connect(lambda: self._on_theme_selected(Theme.HIGH_CONTRAST))
        
        # Menú File (Nuevas opciones)
        self.action_schedule.triggered.connect(self.schedule_clicked.emit)
        self.action_history.triggered.connect(self.history_clicked.emit)
        self.action_compact_mode.toggled.connect(self.compact_mode_changed.emit)
        
        self.action_lang_english.triggered.connect(lambda: self._on_language_selected(Language.ENGLISH))
        self.action_lang_spanish.triggered.connect(lambda: self._on_language_selected(Language.SPANISH))
        self.action_lang_portuguese.triggered.connect(lambda: self._on_language_selected(Language.PORTUGUESE))
        self.action_lang_french.triggered.connect(lambda: self._on_language_selected(Language.FRENCH))
        
        # About & Updates
        self.action_check_updates.triggered.connect(self.check_updates_clicked.emit)
        self.action_about.triggered.connect(self._show_about_dialog)
    
    # ===== HANDLERS INTERNOS =====
    
    def _on_action_changed(self, idx: int):
        """Handler cuando cambia la acción seleccionada"""
        if idx >= 0 and idx < len(PowerAction):
            self.action_changed.emit(PowerAction(idx))
        self._update_panel_visibility()
    
    def _on_mode_toggled(self, mode: ScheduleMode):
        """Handler cuando cambia el modo de operación"""
        self._update_panel_visibility()
        self.mode_changed.emit(mode)
    
    def _update_panel_visibility(self):
        """Actualiza qué paneles son visibles según el modo seleccionado"""
        self.panel_countdown.setVisible(self.radio_countdown.isChecked())
        self.panel_specific_time.setVisible(self.radio_specific_time.isChecked())
        self.panel_monitor.setVisible(self.radio_monitor.isChecked())
        
        is_timer_mode = self.radio_countdown.isChecked() or self.radio_specific_time.isChecked()
        self.progress_bar.setVisible(is_timer_mode)
        self.lbl_end_time.setVisible(is_timer_mode)
        
        # Force close solo visible para shutdown/restart/hibernate
        is_shutdown_type = self.cmb_action.currentIndex() in (0, 1, 3, 4)
        self.chk_force_close.setVisible(is_shutdown_type)
        
        # Ajustar tamaño de ventana al contenido visible (elimina el aire)
        self.adjustSize()
    
    def _on_always_on_top_toggled(self, checked: bool):
        """Handler para always on top"""
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, checked)
        self.show()  # Necesario para aplicar el flag
        self.always_on_top_changed.emit(checked)
    
    def _on_theme_selected(self, theme: Theme):
        """Handler cuando se selecciona un tema"""
        self.action_theme_light.setChecked(theme == Theme.LIGHT)
        self.action_theme_dark.setChecked(theme == Theme.DARK)
        self.action_theme_nordic.setChecked(theme == Theme.NORDIC)
        self.action_theme_dracula.setChecked(theme == Theme.DRACULA)
        self.action_theme_blood.setChecked(theme == Theme.BLOOD)
        self.theme_changed.emit(theme)
    
    def _on_language_selected(self, language: Language):
        """Handler cuando se selecciona un idioma"""
        self.action_lang_english.setChecked(language == Language.ENGLISH)
        self.action_lang_spanish.setChecked(language == Language.SPANISH)
        self.action_lang_portuguese.setChecked(language == Language.PORTUGUESE)
        self.action_lang_french.setChecked(language == Language.FRENCH)
        self.language_changed.emit(language)
    
    def _on_tray_activated(self, reason):
        """Handler cuando se activa el icono de bandeja"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.tray_icon_double_clicked.emit()
    
    def _show_about_dialog(self):
        """Muestra el diálogo About"""
        from ui.about_dialog import AboutDialog
        dialog = AboutDialog(self)
        dialog.exec()
    
    def _set_window_icon(self):
        """Establece el icono de la ventana y lo guarda para uso global"""
        from pathlib import Path
        
        # Ruta al icono (en la carpeta raíz del proyecto Python)
        icon_path = Path(__file__).parent.parent / "app_icon.ico"
        
        if icon_path.exists():
            self.app_icon = QIcon(str(icon_path))
            self.setWindowIcon(self.app_icon)
            # También establecer en el tray icon
            if hasattr(self, 'tray_icon'):
                self.tray_icon.setIcon(self.app_icon)
        else:
            # Fallback: icono vacío
            self.app_icon = QIcon()
    
    def get_app_icon(self) -> QIcon:
        """Retorna el icono de la aplicación para uso externo (ej: AboutDialog)"""
        if hasattr(self, 'app_icon'):
            return self.app_icon
        return QIcon()
    
    # ===== EVENTOS DEL CICLO DE VIDA =====
    
    def showEvent(self, event):
        """Override: cuando se muestra la ventana"""
        super().showEvent(event)
        if not self._loaded:
            self._loaded = True
            
            # Animación de entrada suave (Premium Feel)
            self.setWindowOpacity(0.0)
            self._fade_anim = QPropertyAnimation(self, b"windowOpacity")
            self._fade_anim.setDuration(450)
            self._fade_anim.setStartValue(0.0)
            self._fade_anim.setEndValue(1.0)
            self._fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._fade_anim.start()
            
            self.form_loaded.emit()
    
    def closeEvent(self, event):
        """Override: cuando se cierra la ventana"""
        self.form_closing.emit()
        super().closeEvent(event)
    
    def changeEvent(self, event):
        """Override: cuando cambia el estado de la ventana"""
        if event.type() == event.Type.WindowStateChange:
            self.window_state_changed.emit(self.windowState())
        super().changeEvent(event)
    
    # ===== GETTERS (Para que el Presenter lea el estado de la UI) =====
    
    def get_selected_mode(self) -> ScheduleMode:
        """Obtiene el modo seleccionado"""
        if self.radio_countdown.isChecked():
            return ScheduleMode.COUNTDOWN
        elif self.radio_specific_time.isChecked():
            return ScheduleMode.SPECIFIC_TIME
        return ScheduleMode.MONITOR_ACTIVITY
    
    def get_countdown_time(self) -> tuple:
        """Obtiene el tiempo de countdown (hours, minutes, seconds)"""
        return (self.spin_hours.value(), self.spin_minutes.value(), self.spin_seconds.value())
    
    def get_countdown_total_seconds(self) -> int:
        """Obtiene el total de segundos del countdown"""
        h, m, s = self.get_countdown_time()
        return h * 3600 + m * 60 + s
    
    def get_specific_time(self) -> QTime:
        """Obtiene la hora específica seleccionada"""
        return self.time_picker.time()
    
    def get_selected_process(self) -> dict:
        """Obtiene el proceso seleccionado (como diccionario con pid, name, display_name)"""
        return self.cmb_processes.currentData()
    
    def get_is_monitor_by_exit(self) -> bool:
        """True si monitorea por cierre, False si por inactividad de red"""
        return self.radio_on_exit.isChecked()
    
    def get_selected_action(self) -> PowerAction:
        """Obtiene la acción seleccionada"""
        return PowerAction(self.cmb_action.currentIndex())
    
    def get_is_force_close_enabled(self) -> bool:
        """Obtiene si force close está habilitado"""
        return self.chk_force_close.isChecked()
    
    def get_is_prevent_sleep_enabled(self) -> bool:
        """Obtiene si prevent sleep está habilitado"""
        return self.chk_prevent_sleep.isChecked()
    
    # ===== SETTERS (Para que el Presenter actualice la UI) =====
    
    def set_countdown_time(self, hours: int, minutes: int, seconds: int):
        """Establece el tiempo de countdown"""
        self.spin_hours.setValue(hours)
        self.spin_minutes.setValue(minutes)
        self.spin_seconds.setValue(seconds)
    
    def set_specific_time(self, time_str: str):
        """Establece la hora específica (formato HH:MM:SS)"""
        try:
            parts = time_str.split(":")
            self.time_picker.setTime(QTime(int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0))
        except:
            self.time_picker.setTime(QTime(12, 0, 0))
    
    def set_process_list(self, processes: list):
        """Establece la lista de procesos (lista de dicts)"""
        self.cmb_processes.clear()
        for proc in processes:
            self.cmb_processes.addItem(proc['display_name'], proc)
    
    def set_action(self, action: PowerAction):
        """Establece la acción seleccionada"""
        self.cmb_action.setCurrentIndex(action.value if isinstance(action, PowerAction) else action)
        self._update_panel_visibility()
    
    def set_available_actions(self, actions: list):
        """Establece las acciones disponibles (lista de strings)"""
        current = self.cmb_action.currentIndex()
        self.cmb_action.clear()
        self.cmb_action.addItems(actions)
        if current < len(actions):
            self.cmb_action.setCurrentIndex(current)
    
    def set_force_close(self, value: bool):
        """Establece el estado de force close"""
        self.chk_force_close.setChecked(value)
    
    def set_prevent_sleep(self, value: bool):
        """Establece el estado de prevent sleep"""
        self.chk_prevent_sleep.setChecked(value)
    
    def set_start_with_windows(self, value: bool):
        """Establece el estado de start with windows"""
        self.action_start_with_windows.setChecked(value)
    
    def set_always_on_top(self, value: bool):
        """Establece el estado de always on top"""
        self.action_always_on_top.setChecked(value)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, value)
        if self.isVisible():
            self.show()
    
    def set_mode(self, mode: ScheduleMode):
        """Establece el modo de operación"""
        if mode == ScheduleMode.COUNTDOWN:
            self.radio_countdown.setChecked(True)
        elif mode == ScheduleMode.SPECIFIC_TIME:
            self.radio_specific_time.setChecked(True)
        else:
            self.radio_monitor.setChecked(True)
        self._update_panel_visibility()
    
    def set_monitor_by_exit(self, value: bool):
        """Establece el modo de monitoreo"""
        self.radio_on_exit.setChecked(value)
        self.radio_on_network_idle.setChecked(not value)
    
    def update_status(self, message: str):
        """Actualiza el texto de estado"""
        self.lbl_status.setText(message)
    
    def update_progress_bar(self, value: int, maximum: int):
        """Actualiza la barra de progreso"""
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(value)
    
    def set_progress_bar_color(self, color: str):
        """Establece el color de la barra de progreso"""
        self.progress_bar.setStyleSheet(f"""
            QProgressBar::chunk {{
                background-color: {color};
            }}
        """)
    
    def update_window_title(self, title: str):
        """Actualiza el título de la ventana"""
        self.setWindowTitle(title)
    
    def set_ui_state(self, is_running: bool):
        """Habilita/deshabilita controles según si está corriendo"""
        enabled = not is_running
        
        # Modos
        self.radio_countdown.setEnabled(enabled)
        self.radio_specific_time.setEnabled(enabled)
        self.radio_monitor.setEnabled(enabled)
        
        # Countdown
        self.spin_hours.setEnabled(enabled)
        self.spin_minutes.setEnabled(enabled)
        self.spin_seconds.setEnabled(enabled)
        
        # Specific time
        self.time_picker.setEnabled(enabled)
        
        # Monitor
        self.cmb_processes.setEnabled(enabled)
        self.btn_refresh_processes.setEnabled(enabled)
        self.radio_on_exit.setEnabled(enabled)
        self.radio_on_network_idle.setEnabled(enabled)
        # self.txt_process_filter eliminado
        
        # Action y opciones
        self.cmb_action.setEnabled(enabled)
        self.chk_force_close.setEnabled(enabled)
        self.chk_prevent_sleep.setEnabled(enabled)
        
        # Botones
        self.btn_start.setEnabled(enabled)
        self.btn_stop.setEnabled(is_running)
        
        # Menú
        self.action_start.setEnabled(enabled)
        self.action_stop.setEnabled(is_running)
    
    def set_end_time(self, text: str, visible: bool):
        """Establece el texto de hora de finalización"""
        self.lbl_end_time.setText(text)
        self.lbl_end_time.setVisible(visible)
    
    def show_error_message(self, title: str, message: str):
        """Muestra un mensaje de error"""
        QMessageBox.critical(self, title, message)
    
    def show_warning_dialog(self, action_name: str) -> bool:
        """Muestra el diálogo de advertencia. Retorna True si se acepta."""
        from ui.warning_dialog import WarningDialog
        dialog = WarningDialog(action_name, self)
        return dialog.exec() == 1  # QDialog.Accepted
    
    def apply_theme(self, palette: ColorPalette):
        """Aplica un tema a la ventana con escalado responsivo"""
        scale = getattr(self, '_scale_factor', 1.0)
        ThemeManager.apply_theme(self, palette, scale)
        
        # Actualizar tema en los ValidatedSpinBox
        # Consideramos oscuro cualquier tema que no sea el Light
        is_dark = palette.background != '#f5f5f5' 
        for spinbox in [self.spin_hours, self.spin_minutes, self.spin_seconds]:
            if hasattr(spinbox, 'set_theme'):
                spinbox.set_theme(is_dark)
    
    def reapply_localization(self):
        """Reaplicar traducciones a todos los controles"""
        # Labels y grupos
        self.group_trigger.setTitle(LocalizationManager.get("trigger_condition_label"))
        self.radio_countdown.setText(LocalizationManager.get("mode_countdown"))
        self.radio_specific_time.setText(LocalizationManager.get("mode_specific_time"))
        self.radio_monitor.setText(LocalizationManager.get("mode_monitor_activity"))
        
        # Opciones
        self.chk_force_close.setText(LocalizationManager.get("force_close_apps"))
        self.chk_prevent_sleep.setText(LocalizationManager.get("prevent_sleep_screen_off"))
        
        # Botones
        self.btn_start.setText(f"▶ {LocalizationManager.get('start')}")
        self.btn_stop.setText(f"⏹ {LocalizationManager.get('stop')}")
        
        # Menús (Acciones)
        self.action_start.setText(LocalizationManager.get("menu_start"))
        self.action_stop.setText(LocalizationManager.get("menu_stop"))
        self.action_exit.setText(LocalizationManager.get("menu_exit"))
        self.action_start_with_windows.setText(LocalizationManager.get("menu_start_with_windows"))
        self.action_always_on_top.setText(LocalizationManager.get("menu_always_on_top"))
        self.action_enable_watchdog.setText(LocalizationManager.get("menu_watchdog"))
        self.action_enable_watchdog.setToolTip(LocalizationManager.get("tooltip_watchdog"))
        self.action_theme_light.setText(LocalizationManager.get("menu_light"))

        self.action_theme_dark.setText(LocalizationManager.get("menu_dark"))
        self.action_lang_english.setText(LocalizationManager.get("menu_english"))
        self.action_lang_spanish.setText(LocalizationManager.get("menu_spanish"))
        self.action_about.setText(LocalizationManager.get("menu_about"))
        
        # Condiciones de monitor
        self.radio_on_exit.setText(LocalizationManager.get("condition_on_exit"))
        self.radio_on_network_idle.setText(LocalizationManager.get("condition_on_idle"))
        
        # Status
        self.lbl_status.setText(LocalizationManager.get("status_default"))
    
    # ===== SYSTEM TRAY =====
    
    def show_window(self):
        """Muestra la ventana"""
        self.show()
        self.activateWindow()
    
    def hide_window(self):
        """Oculta la ventana"""
        self.hide()
    
    def show_notification(self, title: str, message: str, duration_sec: int = 5):
        """Muestra una notificación nativa usando el Tray Icon (PyQt6 Native)"""
        if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
            self.tray_icon.showMessage(
                title, 
                message, 
                QSystemTrayIcon.MessageIcon.Information, 
                duration_sec * 1000
            )
        else:
            # Si no hay tray visible, no podemos mostrar notificación nativa fácilmente sin bloquear.
            # Alternativa: QToolTip o status bar. Por ahora solo Status.
            self.update_status(message)
    
    def show_tray_icon(self):
        """Muestra el icono de bandeja"""
        self.tray_icon.setVisible(True)
    
    def hide_tray_icon(self):
        """Oculta el icono de bandeja"""
        self.tray_icon.setVisible(False)
    
    def bring_to_front(self):
        """Trae la ventana al frente"""
        self.activateWindow()
        self.setWindowState(Qt.WindowState.WindowActive)

    # ===== MODO COMPACTO Y ANIMACIONES =====
    
    def set_compact_mode(self, enabled: bool):
        """Activa o desactiva el modo compacto (minimalista)"""
        # Actualizar check del menú
        self.action_compact_mode.setChecked(enabled)
        
        # Animar transición (Fade Out -> Cambios -> Fade In)
        self._animate_transition(lambda: self._apply_compact_mode(enabled))
    
    def _apply_compact_mode(self, enabled: bool):
        """Aplica los cambios de visibilidad para el modo compacto"""
        # Elementos a ocultar/mostrar
        elements_to_toggle = [
            self.group_trigger,
            self.chk_force_close,
            self.chk_prevent_sleep
        ]
        
        for widget in elements_to_toggle:
            widget.setVisible(not enabled)
            
        # Si estamos en modo compacto, el GroupBox de acción puede simplificarse
        if enabled:
            # En modo compacto, solo mostramos el timer/progreso y botones start/stop
            self.resize(300, 200)  # Tamaño mínimo
        else:
            self.resize(400, 550)  # Tamaño normal (aprox)
            
        # Forzar reajuste de layout
        self.adjustSize()
    
    def _animate_transition(self, change_callback):
        """Ejecuta una animación de fade-out, llama al callback, y fade-in"""
        # Fade Out
        self._fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self._fade_anim.setDuration(200)
        self._fade_anim.setStartValue(1.0)
        self._fade_anim.setEndValue(0.0)
        self._fade_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        def on_fade_out_finished():
            change_callback()
            # Fade In
            self._fade_anim.setDirection(QPropertyAnimation.Direction.Backward)
            self._fade_anim.start()
            
            # Desconectar para que no se repita
            try:
                self._fade_anim.finished.disconnect(on_fade_out_finished)
            except:
                pass
        
        self._fade_anim.finished.connect(on_fade_out_finished)
        self._fade_anim.start()
