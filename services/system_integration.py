"""
Gestor de integración con el sistema Windows.
Equivalente a SystemIntegrationManager.cs
"""

import sys
import winreg
from pathlib import Path


class SystemIntegration:
    """
    Gestor estático para la integración con Windows.
    Maneja el inicio automático con el sistema.
    """
    
    _APP_NAME = "GRKPowerSloth"
    _RUN_KEY_PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
    
    @classmethod
    def set_startup(cls, enabled: bool) -> None:
        """
        Configura si la aplicación se inicia con Windows.
        
        Args:
            enabled: True para habilitar, False para deshabilitar
            
        Raises:
            RuntimeError: Si hay un error al acceder al registro
        """
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                cls._RUN_KEY_PATH,
                0,
                winreg.KEY_SET_VALUE
            )
            
            if enabled:
                # Obtener ruta del ejecutable
                exe_path = cls._get_executable_path()
                winreg.SetValueEx(
                    key,
                    cls._APP_NAME,
                    0,
                    winreg.REG_SZ,
                    f'"{exe_path}"'
                )
            else:
                # Eliminar la entrada si existe
                try:
                    winreg.DeleteValue(key, cls._APP_NAME)
                except FileNotFoundError:
                    pass  # La entrada no existía
            
            winreg.CloseKey(key)
            
        except Exception as e:
            raise RuntimeError(f"Error modifying the registry: {e}")
    
    @classmethod
    def is_startup_enabled(cls) -> bool:
        """
        Verifica si la aplicación está configurada para iniciar con Windows.
        
        Returns:
            True si está habilitado, False en caso contrario
        """
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                cls._RUN_KEY_PATH,
                0,
                winreg.KEY_READ
            )
            
            try:
                winreg.QueryValueEx(key, cls._APP_NAME)
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False
                
        except Exception:
            return False
    
    @classmethod
    def _get_executable_path(cls) -> str:
        """
        Obtiene la ruta del ejecutable actual.
        
        Returns:
            Ruta completa al ejecutable
        """
        # Si está ejecutándose como script de Python
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            return sys.executable
        else:
            # Running as Python script
            # Retornar el script principal
            return str(Path(sys.argv[0]).resolve())
