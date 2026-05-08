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

from managers.localization_manager import LocalizationManager


class UpdateDialog(QDialog):
    def __init__(self, parent, version_tag: str, changelog: str, download_url: str, update_manager):
        super().__init__(parent)
        self.download_url = download_url
        self.update_manager = update_manager

        self.setWindowTitle(LocalizationManager.get("update_dialog_title"))
        self.setFixedSize(400, 350)

        layout = QVBoxLayout(self)

        # Cabecera
        lbl_title = QLabel(LocalizationManager.get("update_new_version").format(version_tag))
        lbl_title.setObjectName("updateDialogTitle")
        layout.addWidget(lbl_title)

        # Changelog
        self.txt_changelog = QTextBrowser()
        header = LocalizationManager.get("update_changelog_header")
        self.txt_changelog.setHtml(f"<h3>{header}</h3>{changelog.replace(chr(10), '<br>')}")
        layout.addWidget(self.txt_changelog)

        # Progreso
        self.lbl_status = QLabel(LocalizationManager.get("update_question"))
        layout.addWidget(self.lbl_status)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Botones
        btn_layout = QHBoxLayout()
        self.btn_cancel = QPushButton(LocalizationManager.get("dialog_btn_cancel"))
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_update = QPushButton(LocalizationManager.get("update_btn_install"))
        self.btn_update.setObjectName("updateDialogPrimary")
        self.btn_update.clicked.connect(self.start_download)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_update)
        layout.addLayout(btn_layout)

        if parent and hasattr(parent, "app_icon"):
            self.setWindowIcon(parent.app_icon)

    def closeEvent(self, event):
        """Si el diálogo se cierra (X / reject) durante la descarga, pedir al
        worker que aborte para no dejarlo huérfano emitiendo señales sobre un
        objeto destruido."""
        try:
            self.update_manager.cancel_download()
        except Exception:
            pass
        super().closeEvent(event)

    def start_download(self):
        """Inicia el proceso de descarga"""
        self.btn_update.setEnabled(False)
        self.btn_cancel.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.lbl_status.setText(LocalizationManager.get("update_status_downloading"))

        self.update_manager.download_update(
            self.download_url,
            self.update_progress,
            self.download_finished
        )

    def update_progress(self, percent: int):
        self.progress_bar.setValue(percent)

    def download_finished(self, success, result):
        if result == "cancelled":
            return  # Cancelación silenciosa: el diálogo ya se está cerrando.
        if success:
            self.lbl_status.setText(LocalizationManager.get("update_status_completed"))
            self.progress_bar.setValue(100)

            reply = QMessageBox.question(
                self,
                LocalizationManager.get("update_dlg_restart_title"),
                LocalizationManager.get("update_dlg_restart_msg"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.update_manager.apply_update()
            else:
                self.accept()
        else:
            self.lbl_status.setText(LocalizationManager.get("update_status_error"))
            QMessageBox.critical(
                self,
                LocalizationManager.get("update_dlg_error_title"),
                LocalizationManager.get("update_dlg_error_msg").format(result)
            )
            self.btn_update.setEnabled(True)
            self.btn_cancel.setEnabled(True)
