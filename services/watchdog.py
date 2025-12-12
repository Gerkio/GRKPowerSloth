# -*- coding: utf-8 -*-
"""Watchdog process for GRK PowerSloth.

Este módulo lanza la aplicación principal (main.py) como un sub‑proceso y la
monitoriza. Si el sub‑proceso termina con un código de salida distinto de 0
(por ejemplo, porque un antivirus lo mata), el watchdog lo reinicia
automáticamente después de un breve retraso.

Para usarlo, ejecuta:
    python main.py --watchdog
"""

import os
import sys
import time
import subprocess
from typing import List

def _script_path() -> str:
    """Ruta absoluta al script principal (main.py)."""
    # Este archivo está en services/, subimos un nivel y apuntamos a main.py
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_dir, "main.py")

def _launch_app(extra_args: List[str] | None = None) -> subprocess.Popen:
    """Lanza la aplicación principal y devuelve el objeto Popen.

    ``extra_args`` permite pasar argumentos adicionales al script (por
    ejemplo, ``--some-flag``)."""
    if extra_args is None:
        extra_args = []
    python_exe = sys.executable
    script = _script_path()
    cmd = [python_exe, script] + extra_args
    # ``creationflags`` con ``DETACHED_PROCESS`` evita que el sub‑proceso se
    # cierre cuando la consola principal termina (solo Windows).
    creationflags = 0x00000008  # DETACHED_PROCESS
    return subprocess.Popen(cmd, creationflags=creationflags)

def monitor(restart_delay: float = 1.0, poll_interval: float = 2.0) -> None:
    """Monitoriza el proceso de la aplicación y lo reinicia si falla.

    - ``restart_delay``: segundos a esperar antes de volver a lanzar.
    - ``poll_interval``: frecuencia de comprobación del estado del proceso.
    """
    # Opcional: pasar argumentos que no incluyan ``--watchdog`` para evitar
    # bucles infinitos.
    extra = [arg for arg in sys.argv[1:] if arg != "--watchdog"]
    child = _launch_app(extra)
    while True:
        retcode = child.poll()
        if retcode is not None:
            # El proceso ha terminado.
            if retcode == 0:
                # Salida normal → no reiniciar.
                print("[Watchdog] Aplicación finalizó correctamente (código 0).")
                break
            else:
                print(f"[Watchdog] Aplicación terminó con código {retcode}. Reiniciando…")
                time.sleep(restart_delay)
                child = _launch_app(extra)
        time.sleep(poll_interval)

if __name__ == "__main__":
    monitor()
