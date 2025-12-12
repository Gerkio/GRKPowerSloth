# -*- coding: utf-8 -*-
"""
Modelo para el historial de eventos ejecutados.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class HistoryEntry:
    """
    Representa una entrada en el historial de apagados/reinicios.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Fecha y hora del evento
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Tipo de acción ejecutada (0=shutdown, 1=restart, 2=sleep, 3=restart_uefi, 4=hibernate)
    action_type: int = 0
    
    # Modo que disparó la acción (countdown, specific_time, monitor, scheduled)
    trigger_mode: str = "countdown"
    
    # Motivo o descripción
    reason: str = ""
    
    # Proceso monitorizado (si aplica)
    monitored_process: Optional[str] = None
    
    # ID del evento programado (si fue disparado por el calendario)
    scheduled_event_id: Optional[str] = None
    
    # ¿Se completó exitosamente?
    completed: bool = True
    
    # Mensaje de error (si hubo)
    error_message: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convierte la entrada a diccionario para serialización"""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "action_type": self.action_type,
            "trigger_mode": self.trigger_mode,
            "reason": self.reason,
            "monitored_process": self.monitored_process,
            "scheduled_event_id": self.scheduled_event_id,
            "completed": self.completed,
            "error_message": self.error_message
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "HistoryEntry":
        """Crea una entrada desde un diccionario"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            action_type=data.get("action_type", 0),
            trigger_mode=data.get("trigger_mode", "countdown"),
            reason=data.get("reason", ""),
            monitored_process=data.get("monitored_process"),
            scheduled_event_id=data.get("scheduled_event_id"),
            completed=data.get("completed", True),
            error_message=data.get("error_message")
        )
    
    def get_action_name(self) -> str:
        """Obtiene el nombre de la acción"""
        actions = ["Apagar", "Reiniciar", "Suspender", "Reiniciar a UEFI", "Hibernar"]
        return actions[self.action_type] if 0 <= self.action_type < len(actions) else "Desconocido"
    
    def get_trigger_name(self) -> str:
        """Obtiene el nombre del modo de disparo"""
        triggers = {
            "countdown": "Cuenta regresiva",
            "specific_time": "Hora específica",
            "monitor": "Monitor de proceso",
            "scheduled": "Evento programado"
        }
        return triggers.get(self.trigger_mode, self.trigger_mode)
    
    def get_formatted_timestamp(self) -> str:
        """Obtiene la fecha/hora formateada"""
        try:
            dt = datetime.fromisoformat(self.timestamp)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return self.timestamp
