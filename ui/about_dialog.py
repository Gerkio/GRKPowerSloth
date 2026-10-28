"""
Diálogo About (Acerca de).
Equivalente a AboutForm.cs
"""

from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont
from managers.localization_manager import LocalizationManager


class AboutDialog(QDialog):
    """
    Diálogo que muestra información de la aplicación.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        self.setWindowTitle(LocalizationManager.get("about_title"))
        self.setFixedSize(400, 250)
        self.setModal(True)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        
        # ===== ENCABEZADO CON ICONO Y TÍTULO =====
        header_layout = QHBoxLayout()
        
        # Icono de la aplicación (usando QIcon para ICO multitamaño)
        from PyQt6.QtGui import QIcon
        from PyQt6.QtCore import QSize
        
        lbl_icon = QLabel()
        app_icon = None
        if self.parent() and hasattr(self.parent(), "get_app_icon"):
            app_icon = self.parent().get_app_icon()
        if not app_icon or app_icon.isNull():
            from pathlib import Path
            icon_path = Path(__file__).parent.parent / "app_icon.ico"
            if icon_path.exists():
                app_icon = QIcon(str(icon_path))
        
        if app_icon and not app_icon.isNull():
            self.setWindowIcon(app_icon)
            icon_pixmap = app_icon.pixmap(QSize(64, 64))
            lbl_icon.setPixmap(icon_pixmap)
            lbl_icon.setFixedSize(72, 72)
            lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header_layout.addWidget(lbl_icon)
        
        # Título
        title_layout = QVBoxLayout()
        lbl_title = QLabel("GRK PowerSloth")
        lbl_title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        
        app_version = QApplication.applicationVersion()
        version_text = LocalizationManager.get("about_version")
        if app_version:
            import re
            version_text = re.sub(r'\d+\.\d+\.\d+', app_version, version_text)
            
        lbl_version = QLabel(version_text)
        lbl_version.setFont(QFont("Segoe UI", 9))
        
        title_layout.addWidget(lbl_title)
        title_layout.addWidget(lbl_version)
        title_layout.addStretch()
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # ===== INFORMACIÓN =====
        info_layout = QVBoxLayout()
        info_layout.setSpacing(10)
        
        lbl_dev = QLabel(LocalizationManager.get("about_dev"))
        lbl_dev.setFont(QFont("Segoe UI", 10))
        
        lbl_tech = QLabel(LocalizationManager.get("about_tech"))
        lbl_tech.setFont(QFont("Segoe UI", 10))
        
        lbl_date = QLabel(LocalizationManager.get("about_date"))
        lbl_date.setFont(QFont("Segoe UI", 10))
        
        info_layout.addWidget(lbl_dev)
        info_layout.addWidget(lbl_tech)
        info_layout.addWidget(lbl_date)
        
        # ===== BOTÓN OK =====
        btn_ok = QPushButton("OK")
        btn_ok.setFixedWidth(100)
        btn_ok.clicked.connect(self.accept)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_ok)
        
        # ===== ENSAMBLAR =====
        main_layout.addLayout(header_layout)
        main_layout.addLayout(info_layout)
        main_layout.addStretch()
        main_layout.addLayout(btn_layout)
        
        self.setLayout(main_layout)
