# -*- coding: utf-8 -*-
"""
Diálogo para mostrar el historial de eventos ejecutados.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from typing import List
from models.history_entry import HistoryEntry
from managers.localization_manager import LocalizationManager


class HistoryDialog(QDialog):
    """
    Diálogo que muestra el historial de apagados/reinicios.
    """
    
    def __init__(self, parent, history_entries: List[HistoryEntry], on_clear_callback=None):
        super().__init__(parent)
        self._entries = history_entries
        self._on_clear = on_clear_callback
        self._setup_ui()
        self._populate_table()
    
    def _setup_ui(self):
        """Configura la interfaz del diálogo"""
        self.setWindowTitle(LocalizationManager.get("history_dialog_title"))
        self.setMinimumSize(700, 450)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title_label = QLabel(LocalizationManager.get("history_title"))
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # Descripción
        desc_label = QLabel(LocalizationManager.get("history_description"))
        desc_label.setObjectName("dialogDescription")
        layout.addWidget(desc_label)
        
        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            LocalizationManager.get("history_col_datetime"),
            LocalizationManager.get("history_col_action"),
            LocalizationManager.get("history_col_mode"),
            LocalizationManager.get("history_col_process"),
            LocalizationManager.get("history_col_status")
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 150)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)
        
        # Contador
        self.count_label = QLabel()
        layout.addWidget(self.count_label)
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        if self._on_clear:
            btn_clear = QPushButton(LocalizationManager.get("history_btn_clear"))
            btn_clear.clicked.connect(self._on_clear_clicked)
            btn_layout.addWidget(btn_clear)

        btn_close = QPushButton(LocalizationManager.get("dialog_btn_close"))
        btn_close.setDefault(True)
        btn_close.clicked.connect(self.close)
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
    
    def _populate_table(self):
        """Llena la tabla con las entradas del historial"""
        self.table.setRowCount(len(self._entries))
        
        for row, entry in enumerate(self._entries):
            # Fecha/Hora
            self.table.setItem(row, 0, QTableWidgetItem(entry.get_formatted_timestamp()))
            
            # Acción
            action_item = QTableWidgetItem(entry.get_action_name())
            self.table.setItem(row, 1, action_item)
            
            # Modo
            self.table.setItem(row, 2, QTableWidgetItem(entry.get_trigger_name()))
            
            # Proceso
            process_text = entry.monitored_process or "-"
            self.table.setItem(row, 3, QTableWidgetItem(process_text))
            
            # Estado
            if entry.completed:
                status_item = QTableWidgetItem(LocalizationManager.get("history_status_completed"))
            else:
                err_text = entry.error_message or LocalizationManager.get("update_dlg_error_title")
                status_item = QTableWidgetItem(LocalizationManager.get("history_status_error").format(err_text))
            self.table.setItem(row, 4, status_item)
        
        self.count_label.setText(LocalizationManager.get("history_total_count").format(len(self._entries)))
    
    def _on_clear_clicked(self):
        """Handler para limpiar el historial"""
        reply = QMessageBox.question(
            self,
            LocalizationManager.get("history_confirm_clear_title"),
            LocalizationManager.get("history_confirm_clear_msg"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self._on_clear:
                self._on_clear()
            self._entries = []
            self._populate_table()
            QMessageBox.information(
                self,
                LocalizationManager.get("history_title"),
                LocalizationManager.get("history_cleared_msg")
            )
