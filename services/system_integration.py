import sys
import winreg
import ctypes
import subprocess
from pathlib import Path
from models.enums import PowerAction


class SystemIntegration:
    """
    Gestor estático para la integración con Windows.
    Maneja el inicio automático con el sistema y la ejecución de acciones de energía.
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
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                cls._RUN_KEY_PATH,
                0,
                winreg.KEY_SET_VALUE
            ) as key:
                if enabled:
                    cmd_str = cls._get_startup_command()
                    winreg.SetValueEx(
                        key,
                        cls._APP_NAME,
                        0,
                        winreg.REG_SZ,
                        cmd_str
                    )
                else:
                    try:
                        winreg.DeleteValue(key, cls._APP_NAME)
                    except FileNotFoundError:
                        pass  # La entrada no existía
        except Exception as e:
            raise RuntimeError(f"Error modifying the registry: {e}")
    
    @classmethod
    def is_startup_enabled(cls) -> bool:
        """
        Verifica si la aplicación está configurada para iniciar con Windows.
        Considera "no habilitado" si la entrada existe pero el ejecutable
        registrado ya no existe en disco.

        Returns:
            True si está habilitado y la ruta apunta a un ejecutable existente.
        """
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                cls._RUN_KEY_PATH,
                0,
                winreg.KEY_READ
            ) as key:
                try:
                    value, _ = winreg.QueryValueEx(key, cls._APP_NAME)
                except FileNotFoundError:
                    return False

                # Puede ser f'"{exe}"' o f'"{python}" "{script}"'
                clean_val = value.strip()
                if clean_val.startswith('"'):
                    first_path = clean_val[1:].split('"', 1)[0]
                else:
                    first_path = clean_val.split(' ', 1)[0]

                if not first_path:
                    return False
                return Path(first_path).exists()
        except Exception:
            return False
    
    @classmethod
    def _get_startup_command(cls) -> str:
        """
        Obtiene el comando completo de inicio automático para registrar en Windows Run.
        """
        if getattr(sys, 'frozen', False):
            # En EXE congelado, invocar el ejecutable
            return f'"{sys.executable}"'
        else:
            # En script de Python, invocar python + script principal
            script_path = Path(sys.argv[0]).resolve()
            return f'"{sys.executable}" "{script_path}"'
    
    @classmethod
    def execute_power_action(cls, action: PowerAction, force_close: bool = False) -> None:
        """
        Ejecuta la acción del sistema (shutdown, restart, sleep, uefi, hibernate).
        Desacopla la lógica de ejecución del Presenter para facilitar la extensibilidad.
        """
        force_args = ["/f"] if force_close else []

        if action == PowerAction.SHUTDOWN:
            subprocess.run(["shutdown", "/s", *force_args, "/t", "0"], shell=False)
        elif action == PowerAction.RESTART:
            subprocess.run(["shutdown", "/r", *force_args, "/t", "0"], shell=False)
        elif action == PowerAction.RESTART_UEFI:
            subprocess.run(["shutdown", "/r", "/fw", *force_args, "/t", "0"], shell=False)
        elif action == PowerAction.HIBERNATE:
            subprocess.run(["shutdown", "/h"], shell=False)
        elif action == PowerAction.SLEEP:
            ctypes.windll.powrprof.SetSuspendState(0, 1, 0)
        else:
            raise ValueError(f"Acción no soportada: {action}")
