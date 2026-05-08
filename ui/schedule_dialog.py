# -*- coding: utf-8 -*-
"""
Diálogo para gestionar eventos programados (calendario de apagados/reinicios).
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox, QTimeEdit, QDateEdit,
    QCheckBox, QSpinBox, QGroupBox, QHeaderView, QMessageBox, QWidget
)
from PyQt6.QtCore import Qt, QTime, QDate
from PyQt6.QtGui import QFont

from typing import List, Optional
from models.scheduled_event import ScheduledEvent, RecurrenceType
from managers.localization_manager import LocalizationManager


class ScheduleEventEditDialog(QDialog):
    """Diálogo para crear/editar un evento programado"""
    
    def __init__(self, parent, event: Optional[ScheduledEvent] = None):
        super().__init__(parent)
        self._event = event or ScheduledEvent()
        self._is_new = event is None
        self._setup_ui()
        self._load_event_data()
    
    def _setup_ui(self):
        self.setWindowTitle("🗓️ " + ("Nuevo Evento" if self._is_new else "Editar Evento"))
        self.setMinimumWidth(450)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Nombre del evento
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Nombre:"))
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Ej: Apagar cada noche")
        name_layout.addWidget(self.txt_name)
        layout.addLayout(name_layout)
        
        # Acción
        action_layout = QHBoxLayout()
        action_layout.addWidget(QLabel("Acción:"))
        self.cmb_action = QComboBox()
        self.cmb_action.addItems(["Apagar", "Reiniciar", "Suspender", "Reiniciar a UEFI", "Hibernar"])
        action_layout.addWidget(self.cmb_action)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        # Hora
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Hora:"))
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        time_layout.addWidget(self.time_edit)
        time_layout.addStretch()
        layout.addLayout(time_layout)
        
        # Recurrencia
        recurrence_group = QGroupBox("Recurrencia")
        recurrence_layout = QVBoxLayout(recurrence_group)
        
        self.cmb_recurrence = QComboBox()
        self.cmb_recurrence.addItems(["Una sola vez", "Todos los días", "Días específicos", "Mensual"])
        self.cmb_recurrence.currentIndexChanged.connect(self._on_recurrence_changed)
        recurrence_layout.addWidget(self.cmb_recurrence)
        
        # Panel de fecha específica (para "Una sola vez")
        self.date_widget = QWidget()
        date_layout = QHBoxLayout(self.date_widget)
        date_layout.setContentsMargins(0, 10, 0, 0)
        date_layout.addWidget(QLabel("Fecha:"))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        date_layout.addWidget(self.date_edit)
        date_layout.addStretch()
        recurrence_layout.addWidget(self.date_widget)
        
        # Panel de días de la semana (para "Días específicos")
        self.days_widget = QWidget()
        days_layout = QHBoxLayout(self.days_widget)
        days_layout.setContentsMargins(0, 10, 0, 0)
        self.day_checks = []
        day_names = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        for i, name in enumerate(day_names):
            chk = QCheckBox(name)
            self.day_checks.append(chk)
            days_layout.addWidget(chk)
        recurrence_layout.addWidget(self.days_widget)
        
        # Panel de día del mes (para "Mensual")
        self.monthly_widget = QWidget()
        monthly_layout = QHBoxLayout(self.monthly_widget)
        monthly_layout.setContentsMargins(0, 10, 0, 0)
        monthly_layout.addWidget(QLabel("Día del mes:"))
        self.spin_day = QSpinBox()
        self.spin_day.setRange(1, 31)
        monthly_layout.addWidget(self.spin_day)
        monthly_layout.addStretch()
        recurrence_layout.addWidget(self.monthly_widget)
        
        layout.addWidget(recurrence_group)
        
        # Forzar cierre
        self.chk_force = QCheckBox("Forzar cierre de aplicaciones")
        layout.addWidget(self.chk_force)
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton(LocalizationManager.get("dialog_btn_cancel"))
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_save = QPushButton(LocalizationManager.get("dialog_btn_save"))
        btn_save.setDefault(True)
        btn_save.clicked.connect(self._on_save)
        btn_layout.addWidget(btn_save)
        
        layout.addLayout(btn_layout)
        
        # Inicializar visibilidad
        self._on_recurrence_changed(0)
    
    def _on_recurrence_changed(self, index: int):
        """Actualiza la visibilidad de los paneles según la recurrencia"""
        self.date_widget.setVisible(index == 0)      # Una sola vez
        self.days_widget.setVisible(index == 2)      # Días específicos
        self.monthly_widget.setVisible(index == 3)   # Mensual
        self.adjustSize()
    
    def _load_event_data(self):
        """Carga los datos del evento en los controles"""
        self.txt_name.setText(self._event.name)
        self.cmb_action.setCurrentIndex(self._event.action_type)
        
        hour, minute = map(int, self._event.event_time.split(":"))
        self.time_edit.setTime(QTime(hour, minute))
        
        recurrence_index = {
            RecurrenceType.ONCE: 0,
            RecurrenceType.DAILY: 1,
            RecurrenceType.WEEKLY: 2,
            RecurrenceType.MONTHLY: 3
        }.get(self._event.recurrence, 0)
        self.cmb_recurrence.setCurrentIndex(recurrence_index)
        
        if self._event.specific_date:
            date = QDate.fromString(self._event.specific_date, "yyyy-MM-dd")
            if date.isValid():
                self.date_edit.setDate(date)
        
        for day in self._event.days_of_week:
            if 0 <= day < len(self.day_checks):
                self.day_checks[day].setChecked(True)
        
        self.spin_day.setValue(self._event.day_of_month)
        self.chk_force.setChecked(self._event.force_close)
    
    def _on_save(self):
        """Guarda el evento"""
        name = self.txt_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Por favor, ingrese un nombre para el evento.")
            return
        
        self._event.name = name
        self._event.action_type = self.cmb_action.currentIndex()
        self._event.event_time = self.time_edit.time().toString("HH:mm")
        
        recurrence_map = [RecurrenceType.ONCE, RecurrenceType.DAILY, RecurrenceType.WEEKLY, RecurrenceType.MONTHLY]
        self._event.recurrence = recurrence_map[self.cmb_recurrence.currentIndex()]
        
        self._event.specific_date = self.date_edit.date().toString("yyyy-MM-dd")
        self._event.days_of_week = [i for i, chk in enumerate(self.day_checks) if chk.isChecked()]
        self._event.day_of_month = self.spin_day.value()
        self._event.force_close = self.chk_force.isChecked()
        
        self.accept()
    
    def get_event(self) -> ScheduledEvent:
        """Retorna el evento editado"""
        return self._event


class ScheduleDialog(QDialog):
    """
    Diálogo principal para gestionar eventos programados.
    """
    
    def __init__(self, parent, events: List[ScheduledEvent], on_save_callback=None):
        super().__init__(parent)
        self._events = events.copy()
        self._on_save = on_save_callback
        self._setup_ui()
        self._populate_table()
    
    def _setup_ui(self):
        self.setWindowTitle(LocalizationManager.get("schedule_dialog_title"))
        self.setMinimumSize(750, 500)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title_label = QLabel("Eventos Programados")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # Descripción
        desc_label = QLabel("Configure apagados y reinicios automáticos recurrentes.")
        desc_label.setObjectName("dialogDescription")
        layout.addWidget(desc_label)
        
        # Barra de herramientas
        toolbar = QHBoxLayout()
        
        btn_add = QPushButton("➕ Nuevo Evento")
        btn_add.clicked.connect(self._on_add_event)
        toolbar.addWidget(btn_add)
        
        self.btn_edit = QPushButton("✏️ Editar")
        self.btn_edit.clicked.connect(self._on_edit_event)
        self.btn_edit.setEnabled(False)
        toolbar.addWidget(self.btn_edit)
        
        self.btn_delete = QPushButton("🗑️ Eliminar")
        self.btn_delete.clicked.connect(self._on_delete_event)
        self.btn_delete.setEnabled(False)
        toolbar.addWidget(self.btn_delete)
        
        toolbar.addStretch()
        
        self.btn_toggle = QPushButton("⏸️ Deshabilitar")
        self.btn_toggle.clicked.connect(self._on_toggle_event)
        self.btn_toggle.setEnabled(False)
        toolbar.addWidget(self.btn_toggle)
        
        layout.addLayout(toolbar)
        
        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Activo", "Nombre", "Acción", "Hora", "Recurrencia", "Próxima Ejecución"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 60)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.selectionModel().selectionChanged.connect(self._on_selection_changed)
        self.table.doubleClicked.connect(self._on_edit_event)
        layout.addWidget(self.table)
        
        # Botones inferiores
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton(LocalizationManager.get("dialog_btn_cancel"))
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_save = QPushButton(LocalizationManager.get("schedule_dialog_save_changes"))
        btn_save.setDefault(True)
        btn_save.clicked.connect(self._on_save_all)
        btn_layout.addWidget(btn_save)
        
        layout.addLayout(btn_layout)
    
    def _populate_table(self):
        """Llena la tabla con los eventos"""
        self.table.setRowCount(len(self._events))
        
        for row, event in enumerate(self._events):
            # Activo
            active_item = QTableWidgetItem("✅" if event.enabled else "❌")
            active_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, active_item)
            
            # Nombre
            self.table.setItem(row, 1, QTableWidgetItem(event.name))
            
            # Acción
            self.table.setItem(row, 2, QTableWidgetItem(event.get_action_name()))
            
            # Hora
            self.table.setItem(row, 3, QTableWidgetItem(event.event_time))
            
            # Recurrencia
            self.table.setItem(row, 4, QTableWidgetItem(event.get_recurrence_description()))
            
            # Próxima ejecución
            next_run = event.get_next_run()
            next_text = next_run.strftime("%Y-%m-%d %H:%M") if next_run else "-"
            self.table.setItem(row, 5, QTableWidgetItem(next_text))
    
    def _on_selection_changed(self):
        """Actualiza el estado de los botones según la selección"""
        has_selection = len(self.table.selectedItems()) > 0
        self.btn_edit.setEnabled(has_selection)
        self.btn_delete.setEnabled(has_selection)
        self.btn_toggle.setEnabled(has_selection)
        
        if has_selection:
            row = self.table.currentRow()
            if 0 <= row < len(self._events):
                event = self._events[row]
                self.btn_toggle.setText("⏸️ Deshabilitar" if event.enabled else "▶️ Habilitar")
    
    def _on_add_event(self):
        """Añade un nuevo evento"""
        dialog = ScheduleEventEditDialog(self)
        if dialog.exec():
            self._events.append(dialog.get_event())
            self._populate_table()
    
    def _on_edit_event(self):
        """Edita el evento seleccionado"""
        row = self.table.currentRow()
        if 0 <= row < len(self._events):
            dialog = ScheduleEventEditDialog(self, self._events[row])
            if dialog.exec():
                self._events[row] = dialog.get_event()
                self._populate_table()
    
    def _on_delete_event(self):
        """Elimina el evento seleccionado"""
        row = self.table.currentRow()
        if 0 <= row < len(self._events):
            event = self._events[row]
            reply = QMessageBox.question(
                self,
                "Confirmar eliminación",
                f"¿Está seguro de que desea eliminar el evento '{event.name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                del self._events[row]
                self._populate_table()
    
    def _on_toggle_event(self):
        """Habilita/deshabilita el evento seleccionado"""
        row = self.table.currentRow()
        if 0 <= row < len(self._events):
            self._events[row].enabled = not self._events[row].enabled
            self._populate_table()
            self.table.selectRow(row)
    
    def _on_save_all(self):
        """Guarda todos los cambios"""
        if self._on_save:
            self._on_save(self._events)
        self.accept()
    
    def get_events(self) -> List[ScheduledEvent]:
        """Retorna la lista de eventos"""
        return self._events
