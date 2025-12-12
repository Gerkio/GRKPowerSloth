"""
Enumeraciones para GRK PowerSloth.
Equivalente a los enums definidos en AppSettings.cs y otros archivos C#
"""

from enum import Enum, auto


class Theme(Enum):
    """Temas visuales disponibles"""
    LIGHT = 0
    DARK = 1
    NORDIC = 2
    DRACULA = 3
    BLOOD = 4
    HIGH_CONTRAST = 5  # Modo accesible


class Language(Enum):
    """Idiomas soportados"""
    ENGLISH = 0
    SPANISH = 1
    PORTUGUESE = 2
    FRENCH = 3


class ScheduleMode(Enum):
    """Modos de programación de la acción"""
    COUNTDOWN = 0           # Cuenta regresiva
    SPECIFIC_TIME = 1       # Hora específica
    MONITOR_ACTIVITY = 2    # Monitoreo de actividad


class PowerAction(Enum):
    """Acciones del sistema disponibles"""
    SHUTDOWN = 0        # Apagar
    RESTART = 1         # Reiniciar
    SLEEP = 2           # Suspender
    RESTART_UEFI = 3    # Reiniciar a BIOS/UEFI
    HIBERNATE = 4       # Hibernar


class MonitoringMode(Enum):
    """Modos de monitoreo de procesos"""
    ON_EXIT = auto()            # Cuando el proceso se cierra
    ON_NETWORK_IDLE = auto()    # Cuando cesa la actividad de red
