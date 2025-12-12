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
        self.setWindowTitle("📋 Historial de Eventos")
        self.setMinimumSize(700, 450)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title_label = QLabel("Historial de Apagados/Reinicios")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # Descripción
        desc_label = QLabel("Registro de todas las acciones ejecutadas por la aplicación.")
        desc_label.setStyleSheet("color: #888888;")
        layout.addWidget(desc_label)
        
        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Fecha/Hora", "Acción", "Modo", "Proceso", "Estado"
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
            btn_clear = QPushButton("🗑️ Limpiar Historial")
            btn_clear.clicked.connect(self._on_clear_clicked)
            btn_layout.addWidget(btn_clear)
        
        btn_close = QPushButton("Cerrar")
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
                status_item = QTableWidgetItem("✅ Completado")
            else:
                status_item = QTableWidgetItem(f"❌ {entry.error_message or 'Error'}")
            self.table.setItem(row, 4, status_item)
        
        self.count_label.setText(f"Total: {len(self._entries)} eventos registrados")
    
    def _on_clear_clicked(self):
        """Handler para limpiar el historial"""
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "¿Está seguro de que desea eliminar todo el historial?\n\nEsta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self._on_clear:
                self._on_clear()
            self._entries = []
            self._populate_table()
            QMessageBox.information(self, "Historial", "El historial ha sido eliminado.")
