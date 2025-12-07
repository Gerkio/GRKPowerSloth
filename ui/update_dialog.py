"""
Diálogo de actualización OTA.
Muestra información de la nueva versión y el progreso de descarga.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, 
    QProgressBar, QTextBrowser, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

class UpdateDialog(QDialog):
    def __init__(self, parent, version_tag: str, changelog: str, download_url: str, update_manager):
        super().__init__(parent)
        self.download_url = download_url
        self.update_manager = update_manager
        
        self.setWindowTitle("Actualización Disponible")
        self.setFixedSize(400, 350)
        
        # UI Setup
        layout = QVBoxLayout(self)
        
        # Cabecera
        lbl_title = QLabel(f"¡Nueva versión {version_tag} disponible!")
        lbl_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #0078D4;")
        layout.addWidget(lbl_title)
        
        # Changelog
        self.txt_changelog = QTextBrowser()
        self.txt_changelog.setHtml(f"<h3>Novedades:</h3>{changelog.replace(chr(10), '<br>')}")
        self.txt_changelog.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc; padding: 5px;")
        layout.addWidget(self.txt_changelog)
        
        # Progreso
        self.lbl_status = QLabel("¿Deseas descargar e instalar ahora?")
        layout.addWidget(self.lbl_status)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Botones
        btn_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.clicked.connect(self.reject)
        
        self.btn_update = QPushButton("Actualizar Ahora")
        self.btn_update.setStyleSheet("background-color: #0078D4; color: white; font-weight: bold; padding: 6px;")
        self.btn_update.clicked.connect(self.start_download)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_update)
        layout.addLayout(btn_layout)
        
        # Estilo
        if parent and hasattr(parent, "app_icon"):
            self.setWindowIcon(parent.app_icon)

    def start_download(self):
        """Inicia el proceso de descarga"""
        self.btn_update.setEnabled(False)
        self.btn_cancel.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.lbl_status.setText("Descargando actualización...")
        
        self.update_manager.download_update(
            self.download_url,
            self.update_progress,
            self.download_finished
        )

    def update_progress(self, percent: int):
        self.progress_bar.setValue(percent)

    def download_finished(self, success, result):
        if success:
            self.lbl_status.setText("Descarga completada. Instalando...")
            self.progress_bar.setValue(100)
            
            reply = QMessageBox.question(
                self, 
                "Reiniciar", 
                "La actualización está lista. La aplicación necesita reiniciarse para aplicar los cambios.\n¿Reiniciar ahora?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.update_manager.apply_update()
            else:
                self.accept() # Cerrar diálogo, actualizará al próximo inicio (si implementado)
        else:
            self.lbl_status.setText("Error en la descarga.")
            QMessageBox.critical(self, "Error", f"No se pudo descargar la actualización:\n{result}")
            self.btn_update.setEnabled(True)
            self.btn_cancel.setEnabled(True)
