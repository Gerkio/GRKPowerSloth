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

from managers.localization_manager import LocalizationManager

# Constantes del Repositorio
GITHUB_USER = "Gerkio"
GITHUB_REPO = "GRKPowerSloth"
CURRENT_VERSION = "6.1.1"  # Sincronizar con main.py app.setApplicationVersion()

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
            # timeout=(connect, read): un servidor que se queda mudo durante 5 min cancela.
            response = requests.get(self.download_url, stream=True, timeout=(10, 300))
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))

            # Validar espacio en disco antes de escribir (margen del 20%) si el servidor reporta tamaño.
            if total_size > 0:
                free = shutil.disk_usage(self.target_path.parent).free
                required = int(total_size * 1.2)
                if free < required:
                    self.finished.emit(False, f"Espacio insuficiente: {free:,} bytes libres, se requieren ~{required:,}.")
                    return

            downloaded = 0

            with open(self.target_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    # Si el diálogo padre pide cancelar, abortamos limpio.
                    if self.isInterruptionRequested():
                        f.close()
                        try:
                            self.target_path.unlink()
                        except OSError:
                            pass
                        self.finished.emit(False, "cancelled")
                        return
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
            # 10s es razonable para una API REST con latencia ocasional.
            response = requests.get(self.api_url, timeout=10)
            
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
                self.check_failed.emit(LocalizationManager.get("update_already_latest"))

        except Exception as e:
            logging.error(f"Error checking updates: {e}")
            if manual_check:
                self.check_failed.emit(LocalizationManager.get("update_check_error").format(str(e)))

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

    def cancel_download(self):
        """Solicita la cancelación del worker de descarga (si está corriendo)
        y espera a que termine. Pensado para llamarse cuando el diálogo padre
        se cierra y dejaría al worker huérfano."""
        worker = self._download_worker
        if worker is None:
            return
        if worker.isRunning():
            worker.requestInterruption()
            # Damos hasta 3s al worker para limpiar y emitir 'finished'.
            worker.wait(3000)
        self._download_worker = None

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

        # CMD interpreta % como prefijo de variable; doblar % en rutas que se incrustan en el bat.
        # NO escapar %~f0: es una variable real que apunta al propio bat.
        def _esc(p):
            return str(p).replace('%', '%%')

        esc_dir = _esc(dir_path)
        esc_exe = _esc(exe_path)
        esc_old = _esc(old_file)
        esc_new = _esc(new_file)

        # Script bat temporal para realizar el swap y reiniciar fuera del proceso
        # (Windows bloquea el .exe mientras corre). Si el primer move falla
        # abortamos; si falla el segundo intentamos revertir el primero para
        # no dejar al usuario sin ejecutable.
        bat_script = f"""
@echo off
cd /d "{esc_dir}"
timeout /t 1 /nobreak > NUL
del "{esc_old}" 2>NUL
move "{esc_exe}" "{esc_old}" || exit /b 1
move "{esc_new}" "{esc_exe}" || (move "{esc_old}" "{esc_exe}" >NUL 2>&1 & exit /b 1)
start "" "{esc_exe}"
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
        """Borra archivos residuales de actualizaciones previas (.old, .new, runner bat)"""
        try:
            exe_path = Path(sys.executable)
            for residual in ("GRK_PowerSloth.old", "GRK_PowerSloth.new", "update_runner.bat"):
                f = exe_path.with_name(residual)
                if f.exists():
                    f.unlink()
        except:
            pass
