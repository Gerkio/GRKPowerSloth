"""
Gestor de Actualizaciones Automáticas (OTA) via GitHub Releases.
"""

import os
import sys
import shutil
import logging
import requests
import subprocess
from pathlib import Path
from typing import Optional, Tuple, Callable
from PyQt6.QtCore import QObject, pyqtSignal, QThread

# Constantes del Repositorio
GITHUB_USER = "Gerkio"
GITHUB_REPO = "GRKPowerSloth"
CURRENT_VERSION = "6.1.0"  # Sincronizar con localization o main

class DownloadWorker(QThread):
    """Worker thread para descargar la actualización sin congelar la UI"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)  # success, file_path_or_error

    def __init__(self, download_url: str, target_path: Path):
        super().__init__()
        self.download_url = download_url
        self.target_path = target_path

    def run(self):
        try:
            response = requests.get(self.download_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(self.target_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = int((downloaded / total_size) * 100)
                            self.progress.emit(percent)
                            
            self.finished.emit(True, str(self.target_path))
            
        except Exception as e:
            self.finished.emit(False, str(e))

class UpdateManager(QObject):
    """
    Gestiona la comprobación y aplicación de actualizaciones.
    """
    update_available = pyqtSignal(str, str, str)  # version, url, changelog
    check_failed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.api_url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"
        self._download_worker: Optional[DownloadWorker] = None

    def check_for_updates(self, manual_check=False):
        """
        Consulta la API de GitHub para ver si hay una nueva versión.
        """
        try:
            logging.info("Buscando actualizaciones en GitHub...")
            response = requests.get(self.api_url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                latest_tag = data.get("tag_name", "v0.0.0").lstrip('v')
                
                # Comparar versiones semánticamente (ej: "6.0.2" -> (6, 0, 2))
                def parse_v(v_str):
                    return tuple(map(int, (v_str.split('.'))))

                try:
                    latest_tuple = parse_v(latest_tag)
                    current_tuple = parse_v(CURRENT_VERSION)
                    
                    if latest_tuple > current_tuple:
                        # Encontrar el asset .exe
                        download_url = None
                        for asset in data.get("assets", []):
                            if asset["name"].endswith(".exe"):
                                download_url = asset["browser_download_url"]
                                break
                        
                        if download_url:
                            changelog = data.get("body", "Mejoras de rendimiento y corrección de errores.")
                            self.update_available.emit(latest_tag, download_url, changelog)
                            return
                except Exception as ex:
                    logging.error(f"Error parsing versions: {ex}")
                    
                    
            if manual_check:
                self.check_failed.emit("Ya tienes la última versión.")
                
        except Exception as e:
            logging.error(f"Error checking updates: {e}")
            if manual_check:
                self.check_failed.emit(f"Error de conexión: {str(e)}")

    def download_update(self, url: str, on_progress, on_finished):
        """
        Inicia la descarga del nuevo ejecutable.
        El archivo se guardará como 'GRK_PowerSloth.new'
        """
        current_exe = Path(sys.executable)
        target_path = current_exe.with_name("GRK_PowerSloth.new")
        
        self._download_worker = DownloadWorker(url, target_path)
        self._download_worker.progress.connect(on_progress)
        self._download_worker.finished.connect(lambda success, path: on_finished(success, path))
        self._download_worker.start()

    def apply_update(self):
        """
        Realiza el baile del renombrado (Hot-Swap) y reinicia.
        """
        exe_path = Path(sys.executable)
        dir_path = exe_path.parent
        new_file = dir_path / "GRK_PowerSloth.new"
        old_file = dir_path / "GRK_PowerSloth.old"
        
        if not new_file.exists():
            return False
            
        # Script bat temporal para realizar el swap y reiniciar fuera del proceso
        # Esto es necesario porque Windows bloquea el archivo mientras corre
        bat_script = f"""
@echo off
timeout /t 1 /nobreak > NUL
del "{old_file}" 2>NUL
move "{exe_path}" "{old_file}"
move "{new_file}" "{exe_path}"
start "" "{exe_path}"
del "%~f0"
"""
        bat_path = dir_path / "update_runner.bat"
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(bat_script)
            
        # Ejecutar bat y salir
        subprocess.Popen(str(bat_path), shell=True)
        sys.exit(0)

    @staticmethod
    def cleanup_old_updates():
        """Borra archivos .old de actualizaciones previas"""
        try:
            exe_path = Path(sys.executable)
            old_file = exe_path.with_name("GRK_PowerSloth.old")
            new_file_trash = exe_path.with_name("GRK_PowerSloth.new")
            
            if old_file.exists():
                old_file.unlink()
            if new_file_trash.exists():
                new_file_trash.unlink()
        except:
            pass
