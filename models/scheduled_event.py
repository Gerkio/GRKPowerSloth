# -*- coding: utf-8 -*-
"""
Modelo para eventos programados (calendario de apagados/reinicios).
"""

from dataclasses import dataclass, field
from datetime import datetime, time
from typing import List, Optional
from enum import Enum
import uuid


class DayOfWeek(Enum):
    """Días de la semana"""
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class RecurrenceType(Enum):
    """Tipo de recurrencia del evento"""
    ONCE = "once"           # Una sola vez
    DAILY = "daily"         # Todos los días
    WEEKLY = "weekly"       # Días específicos de la semana
    MONTHLY = "monthly"     # Día específico del mes


@dataclass
class ScheduledEvent:
    """
    Representa un evento programado de apagado/reinicio.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Nombre descriptivo del evento
    name: str = "Evento programado"
    
    # Tipo de acción (0=shutdown, 1=restart, 2=sleep, 3=restart_uefi, 4=hibernate)
    action_type: int = 0
    
    # Hora del evento (HH:MM)
    event_time: str = "02:00"
    
    # Tipo de recurrencia
    recurrence: RecurrenceType = RecurrenceType.ONCE
    
    # Para ONCE: fecha específica (YYYY-MM-DD)
    specific_date: Optional[str] = None
    
    # Para WEEKLY: días de la semana habilitados
    days_of_week: List[int] = field(default_factory=list)  # 0=Lunes, 6=Domingo
    
    # Para MONTHLY: día del mes (1-31)
    day_of_month: int = 1
    
    # ¿Evento activo?
    enabled: bool = True
    
    # ¿Forzar cierre de aplicaciones?
    force_close: bool = False
    
    # Fecha de creación
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Última ejecución
    last_run: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convierte el evento a diccionario para serialización"""
        return {
            "id": self.id,
            "name": self.name,
            "action_type": self.action_type,
            "event_time": self.event_time,
            "recurrence": self.recurrence.value,
            "specific_date": self.specific_date,
            "days_of_week": self.days_of_week,
            "day_of_month": self.day_of_month,
            "enabled": self.enabled,
            "force_close": self.force_close,
            "created_at": self.created_at,
            "last_run": self.last_run
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ScheduledEvent":
        """Crea un evento desde un diccionario"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", "Evento programado"),
            action_type=data.get("action_type", 0),
            event_time=data.get("event_time", "02:00"),
            recurrence=RecurrenceType(data.get("recurrence", "once")),
            specific_date=data.get("specific_date"),
            days_of_week=data.get("days_of_week", []),
            day_of_month=data.get("day_of_month", 1),
            enabled=data.get("enabled", True),
            force_close=data.get("force_close", False),
            created_at=data.get("created_at", datetime.now().isoformat()),
            last_run=data.get("last_run")
        )
    
    def get_next_run(self) -> Optional[datetime]:
        """Calcula la próxima ejecución del evento"""
        if not self.enabled:
            return None
        
        now = datetime.now()
        event_hour, event_minute = map(int, self.event_time.split(":"))
        
        if self.recurrence == RecurrenceType.ONCE:
            if not self.specific_date:
                return None
            target = datetime.strptime(self.specific_date, "%Y-%m-%d")
            target = target.replace(hour=event_hour, minute=event_minute)
            return target if target > now else None
        
        elif self.recurrence == RecurrenceType.DAILY:
            target = now.replace(hour=event_hour, minute=event_minute, second=0, microsecond=0)
            if target <= now:
                target = target.replace(day=target.day + 1)
            return target
        
        elif self.recurrence == RecurrenceType.WEEKLY:
            if not self.days_of_week:
                return None
            
            # Buscar el próximo día habilitado
            for days_ahead in range(8):  # Máximo 7 días
                check_date = now + timedelta(days=days_ahead)
                if check_date.weekday() in self.days_of_week:
                    target = check_date.replace(hour=event_hour, minute=event_minute, second=0, microsecond=0)
                    if target > now:
                        return target
            return None
        
        elif self.recurrence == RecurrenceType.MONTHLY:
            target = now.replace(day=self.day_of_month, hour=event_hour, minute=event_minute, second=0, microsecond=0)
            if target <= now:
                # Próximo mes
                if now.month == 12:
                    target = target.replace(year=now.year + 1, month=1)
                else:
                    target = target.replace(month=now.month + 1)
            return target
        
        return None
    
    def get_action_name(self) -> str:
        """Obtiene el nombre de la acción"""
        actions = ["Apagar", "Reiniciar", "Suspender", "Reiniciar a UEFI", "Hibernar"]
        return actions[self.action_type] if 0 <= self.action_type < len(actions) else "Desconocido"
    
    def get_recurrence_description(self) -> str:
        """Obtiene una descripción legible de la recurrencia"""
        if self.recurrence == RecurrenceType.ONCE:
            return f"Una vez ({self.specific_date or 'sin fecha'})"
        elif self.recurrence == RecurrenceType.DAILY:
            return "Todos los días"
        elif self.recurrence == RecurrenceType.WEEKLY:
            day_names = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
            days = [day_names[d] for d in sorted(self.days_of_week)]
            return f"Semanal: {', '.join(days)}"
        elif self.recurrence == RecurrenceType.MONTHLY:
            return f"Mensual: día {self.day_of_month}"
        return "Desconocido"


# Importar timedelta para get_next_run
from datetime import timedelta
