"""
Gestor de configuración persistente.
Equivalente a AppSettings.cs
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, asdict
from PyQt6.QtCore import QTime
from models.enums import Theme, Language, ScheduleMode, PowerAction


@dataclass
class AppSettings:
    """
    Configuración de la aplicación que se persiste en JSON.
    """
    # Configuración de countdown
    last_hours: int = 0
    last_minutes: int = 30
    last_seconds: int = 0
    
    # Configuración de hora específica (guardado como string HH:MM:SS)
    last_specific_time: str = "12:00:00"
    
    # Acción seleccionada
    last_action_index: int = 0
    
    # Tema e idioma
    current_theme: int = Theme.DARK.value
    current_language: int = Language.SPANISH.value
    
    # Modo de operación
    last_mode: int = ScheduleMode.COUNTDOWN.value
    
    # Flags
    is_force_close_enabled: bool = False
    prevent_sleep: bool = True
    start_with_windows: bool = False
    always_on_top: bool = False
    monitor_by_exit: bool = True
    
    # Último proceso monitoreado
    last_monitored_process_name: Optional[str] = None
    
    def to_dict(self):
        """Convierte la configuración a diccionario"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        """Crea una instancia desde un diccionario"""
        return cls(**data)


class SettingsManager:
    """
    Gestor estático para cargar y guardar la configuración.
    """
    
    _SETTINGS_DIR = Path.home() / ".grk_powersloth"
    _SETTINGS_FILE = _SETTINGS_DIR / "settings.json"
    
    @classmethod
    def _ensure_settings_dir(cls) -> None:
        """Asegura que el directorio de configuración exista"""
        cls._SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def load(cls) -> AppSettings:
        """
        Carga la configuración desde el archivo JSON.
        
        Returns:
            Configuración cargada, o valores por defecto si no existe
        """
        cls._ensure_settings_dir()
        
        if not cls._SETTINGS_FILE.exists():
            return AppSettings()
        
        try:
            with open(cls._SETTINGS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return AppSettings.from_dict(data)
        except Exception as e:
            print(f"Error loading settings: {e}")
            print("Using default settings.")
            return AppSettings()
    
    @classmethod
    def save(cls, settings: AppSettings) -> None:
        """
        Guarda la configuración en el archivo JSON.
        
        Args:
            settings: Configuración a guardar
        """
        cls._ensure_settings_dir()
        
        try:
            # Sincronizar con el estado real de inicio con Windows
            from services.system_integration import SystemIntegration
            settings.start_with_windows = SystemIntegration.is_startup_enabled()
            
            with open(cls._SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    @classmethod
    def get_settings_path(cls) -> Path:
        """Obtiene la ruta del archivo de configuración"""
        return cls._SETTINGS_FILE
