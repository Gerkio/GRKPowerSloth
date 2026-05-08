# -*- coding: utf-8 -*-
"""
Servicio para gestionar eventos programados (calendario) y el historial.
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from models.scheduled_event import ScheduledEvent, RecurrenceType
from models.history_entry import HistoryEntry


class ScheduleManager(QObject):
    """
    Gestor de eventos programados.
    Monitoriza los eventos y emite señales cuando es hora de ejecutar una acción.
    """
    
    # Señales
    event_triggered = pyqtSignal(object)  # ScheduledEvent
    events_changed = pyqtSignal()  # Lista de eventos modificada
    
    # Rutas de archivos
    _SETTINGS_DIR = Path.home() / ".grk_powersloth"
    _SCHEDULE_FILE = _SETTINGS_DIR / "scheduled_events.json"
    _HISTORY_FILE = _SETTINGS_DIR / "history.json"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._events: List[ScheduledEvent] = []
        self._history: List[HistoryEntry] = []
        
        # Timer para verificar eventos cada minuto. La ventana de disparo
        # es [0..60s) hacia el futuro, así que un polling de 60s no pierde eventos
        # y reduce a la mitad el riesgo de doble disparo respecto a 30s.
        self._check_timer = QTimer(self)
        self._check_timer.timeout.connect(self._check_scheduled_events)
        self._check_timer.setInterval(60000)
        
        # Cargar datos
        self._ensure_settings_dir()
        self._load_events()
        self._load_history()
    
    def _ensure_settings_dir(self):
        """Asegura que el directorio de configuración exista"""
        self._SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # ===== EVENTOS PROGRAMADOS =====
    
    def start_monitoring(self):
        """Inicia el monitoreo de eventos programados"""
        self._check_timer.start()
        # Verificar inmediatamente
        self._check_scheduled_events()
    
    def stop_monitoring(self):
        """Detiene el monitoreo de eventos programados"""
        self._check_timer.stop()
    
    def _check_scheduled_events(self):
        """Verifica si hay eventos que deben ejecutarse ahora"""
        now = datetime.now()
        triggered: List[ScheduledEvent] = []

        for event in self._events:
            if not event.enabled:
                continue

            next_run = event.get_next_run()
            if next_run is None:
                continue

            # Ventana de disparo: próximos 60s. Evita el doble disparo que tenía
            # el código anterior (-30..+30 con polling de 30s).
            time_diff = (next_run - now).total_seconds()
            if 0 <= time_diff <= 60:
                # Anti-rebote por last_run, robusto frente a cambios de hora del sistema
                # (abs() en vez de resta sin signo para no permitir disparos cuando
                # last_run quede en el "futuro" tras un cambio de reloj/DST).
                if event.last_run:
                    try:
                        last_run_dt = datetime.fromisoformat(event.last_run)
                        if abs((now - last_run_dt).total_seconds()) < 120:
                            continue
                    except ValueError:
                        pass

                event.last_run = now.isoformat()
                triggered.append(event)

        # Persistir una sola vez al final (antes los emit podían disparar
        # _execute_final_action y reiniciar el sistema antes de cerrar el JSON).
        if triggered:
            self._save_events()
            for event in triggered:
                self.event_triggered.emit(event)
    
    def get_events(self) -> List[ScheduledEvent]:
        """Obtiene todos los eventos programados"""
        return self._events.copy()
    
    def add_event(self, event: ScheduledEvent):
        """Agrega un nuevo evento programado"""
        self._events.append(event)
        self._save_events()
        self.events_changed.emit()
    
    def update_event(self, event: ScheduledEvent):
        """Actualiza un evento existente"""
        for i, e in enumerate(self._events):
            if e.id == event.id:
                self._events[i] = event
                self._save_events()
                self.events_changed.emit()
                return
    
    def remove_event(self, event_id: str):
        """Elimina un evento por su ID"""
        self._events = [e for e in self._events if e.id != event_id]
        self._save_events()
        self.events_changed.emit()
    
    def toggle_event(self, event_id: str, enabled: bool):
        """Habilita/deshabilita un evento"""
        for event in self._events:
            if event.id == event_id:
                event.enabled = enabled
                self._save_events()
                self.events_changed.emit()
                return
    
    def _load_events(self):
        """Carga los eventos desde el archivo JSON"""
        if not self._SCHEDULE_FILE.exists():
            self._events = []
            return
        
        try:
            with open(self._SCHEDULE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._events = [ScheduledEvent.from_dict(e) for e in data]
        except Exception as e:
            print(f"Error loading scheduled events: {e}")
            self._events = []
    
    def _save_events(self):
        """Guarda los eventos en el archivo JSON con escritura atómica (escribe
        a un .tmp y hace rename) para que un crash entre escrituras no deje
        el JSON corrupto."""
        try:
            tmp = self._SCHEDULE_FILE.with_suffix(self._SCHEDULE_FILE.suffix + '.tmp')
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump([e.to_dict() for e in self._events], f, indent=2, ensure_ascii=False)
            os.replace(tmp, self._SCHEDULE_FILE)
        except Exception as e:
            print(f"Error saving scheduled events: {e}")
    
    # ===== HISTORIAL =====
    
    def get_history(self, limit: int = 100) -> List[HistoryEntry]:
        """Obtiene el historial de eventos (más recientes primero)"""
        sorted_history = sorted(self._history, key=lambda x: x.timestamp, reverse=True)
        return sorted_history[:limit]
    
    def add_history_entry(self, entry: HistoryEntry):
        """Agrega una entrada al historial"""
        self._history.append(entry)
        self._save_history()
    
    def log_action(
        self,
        action_type: int,
        trigger_mode: str,
        reason: str = "",
        monitored_process: Optional[str] = None,
        scheduled_event_id: Optional[str] = None,
        completed: bool = True,
        error_message: Optional[str] = None
    ):
        """Registra una acción en el historial (método de conveniencia)"""
        entry = HistoryEntry(
            action_type=action_type,
            trigger_mode=trigger_mode,
            reason=reason,
            monitored_process=monitored_process,
            scheduled_event_id=scheduled_event_id,
            completed=completed,
            error_message=error_message
        )
        self.add_history_entry(entry)
    
    def clear_history(self):
        """Limpia todo el historial"""
        self._history = []
        self._save_history()
    
    def _load_history(self):
        """Carga el historial desde el archivo JSON"""
        if not self._HISTORY_FILE.exists():
            self._history = []
            return
        
        try:
            with open(self._HISTORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._history = [HistoryEntry.from_dict(e) for e in data]
        except Exception as e:
            print(f"Error loading history: {e}")
            self._history = []
    
    def _save_history(self):
        """Guarda el historial en el archivo JSON (escritura atómica)."""
        try:
            # Mantener solo las últimas 500 entradas
            if len(self._history) > 500:
                self._history = sorted(self._history, key=lambda x: x.timestamp, reverse=True)[:500]

            tmp = self._HISTORY_FILE.with_suffix(self._HISTORY_FILE.suffix + '.tmp')
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump([e.to_dict() for e in self._history], f, indent=2, ensure_ascii=False)
            os.replace(tmp, self._HISTORY_FILE)
        except Exception as e:
            print(f"Error saving history: {e}")
