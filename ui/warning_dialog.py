"""
Diálogo de advertencia final.
Equivalente a WarningForm.cs
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from managers.localization_manager import LocalizationManager


class WarningDialog(QDialog):
    """
    Diálogo de cuenta regresiva final antes de ejecutar la acción.
    Da al usuario 30 segundos para cancelar.
    """
    
    def __init__(self, action_name: str, parent=None):
        super().__init__(parent)
        self.action_name = action_name
        self.seconds_left = 30
        self.setup_ui()
        
        # Timer de cuenta regresiva
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self._on_countdown_tick)
        self.countdown_timer.start(1000)  # 1 segundo
    
    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        self.setWindowTitle(LocalizationManager.get("warning_title"))
        self.setFixedSize(400, 180)
        self.setModal(True)
        
        # Sin botón de cerrar (X)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowTitleHint
        )
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        
        # ===== MENSAJE DE ADVERTENCIA =====
        self.lbl_message = QLabel()
        self.lbl_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_message.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.lbl_message.setWordWrap(True)
        self._update_message()
        
        # ===== BOTÓN CANCELAR =====
        btn_cancel = QPushButton(LocalizationManager.get("warning_cancel"))
        btn_cancel.setFixedSize(150, 40)
        btn_cancel.setFont(QFont("Segoe UI", 10))
        btn_cancel.clicked.connect(self._on_cancel_clicked)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addStretch()
        
        # ===== ENSAMBLAR =====
        main_layout.addStretch()
        main_layout.addWidget(self.lbl_message)
        main_layout.addStretch()
        main_layout.addLayout(btn_layout)
        
        self.setLayout(main_layout)
    
    def _update_message(self):
        """Actualiza el mensaje con el tiempo restante"""
        message = LocalizationManager.get("warning_text").format(
            self.action_name.upper(),
            self.seconds_left
        )
        self.lbl_message.setText(message)
    
    def _on_countdown_tick(self):
        """Callback del timer de cuenta regresiva"""
        self.seconds_left -= 1
        
        if self.seconds_left <= 0:
            # Tiempo agotado - aceptar y ejecutar acción
            self.countdown_timer.stop()
            self.accept()  # QDialog.Accepted (código 1)
        else:
            # Actualizar mensaje
            self._update_message()
    
    def _on_cancel_clicked(self):
        """Callback cuando se cancela"""
        self.countdown_timer.stop()
        self.reject()  # QDialog.Rejected (código 0)
    
    def closeEvent(self, event):
        """Override: limpiar el timer al cerrar"""
        self.countdown_timer.stop()
        super().closeEvent(event)
