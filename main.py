# -*- coding: utf-8 -*-
"""
GRK PowerSloth - Python Version
Punto de entrada de la aplicación.

Equivalente a Program.cs

Uso: python main.py

NOTA: Esta aplicación REQUIERE privilegios de administrador.
      Si no se ejecuta como admin, se relanzará automáticamente con UAC.
"""

import sys
import ctypes
from pathlib import Path


# ===== VERIFICACIÓN DE PRIVILEGIOS (ANTES DE IMPORTAR PyQt6) =====

def is_admin() -> bool:
    """Detecta si la aplicación se ejecuta con privilegios de administrador."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def run_as_admin():
    """
    Relanza el script con privilegios de administrador usando UAC.
    Usa la ruta del Python del entorno virtual para asegurar que las dependencias estén disponibles.
    """
    # Ruta del script actual
    script_path = Path(__file__).resolve()
    
    # Ruta del Python del entorno virtual
    venv_python = script_path.parent / ".venv" / "Scripts" / "python.exe"
    
    # Verificar que el venv existe
    if venv_python.exists():
        python_exe = str(venv_python)
    else:
        python_exe = sys.executable
    
    # Parámetros: ruta del script entre comillas (por si hay espacios)
    params = f'"{script_path}"'
    
    # Agregar argumentos adicionales si los hay
    if len(sys.argv) > 1:
        extra_args = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])
        params = f'{params} {extra_args}'
    
    # Ejecutar con elevación UAC
    # ShellExecuteW devuelve un valor > 32 si tiene éxito
    result = ctypes.windll.shell32.ShellExecuteW(
        None,           # hwnd
        "runas",        # operación (solicitar elevación)
        python_exe,     # ejecutable
        params,         # parámetros
        None,           # directorio de trabajo
        1               # nShowCmd (SW_SHOWNORMAL)
    )
    
    return result > 32  # True si se lanzó exitosamente


# ===== VERIFICACIÓN OBLIGATORIA AL INICIO =====

if not is_admin():
    # No somos admin, intentar relanzar con elevación
    if run_as_admin():
        # Se lanzó la versión elevada, salir de esta instancia
        sys.exit(0)
    else:
        # El usuario canceló UAC o hubo un error
        # Mostrar mensaje y salir
        ctypes.windll.user32.MessageBoxW(
            0,
            "Esta aplicación requiere privilegios de administrador para funcionar.\n\n"
            "Por favor, ejecute la aplicación como administrador.",
            "GRK PowerSloth - Permisos requeridos",
            0x10  # MB_ICONERROR
        )
        sys.exit(1)


# ===== AHORA QUE SOMOS ADMIN, IMPORTAR PyQt6 Y EJECUTAR =====

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt, QLockFile, QDir


def global_exception_handler(exctype, value, traceback):
    """
    Robustez: Captura errores no controlados para que la app no desaparezca sin dejar rastro.
    """
    # Permitir Ctrl+C en consola
    if exctype == KeyboardInterrupt:
        sys.__excepthook__(exctype, value, traceback)
        return
        
    error_msg = f"Ha ocurrido un error inesperado:\n\n{value}\n\nLa aplicación debe cerrarse."
    
    # Intentar mostrar diálogo visual
    try:
        if QApplication.instance():
            QMessageBox.critical(None, "Error Crítico", error_msg)
        else:
            # Fallback nativo
            ctypes.windll.user32.MessageBoxW(0, error_msg, "GRK PowerSloth Error", 0x10)
    except:
        pass
        
    # Llamar al hook original (imprime en stderr)
    sys.__excepthook__(exctype, value, traceback)
    sys.exit(1)

# Asignar el manejador global
sys.excepthook = global_exception_handler


def main():
    """Función principal de la aplicación (solo se ejecuta con permisos de admin)"""
    
    # Habilitar DPI awareness para pantallas de alta resolución
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Crear aplicación Qt
    app = QApplication(sys.argv)
    app.setApplicationName("GRK PowerSloth")
    app.setApplicationVersion("6.0.1")  # Definitive Version
    app.setOrganizationName("Gerkio")

    # ===== SINGLETON CHECK (Instancia Única) =====
    # Evitar múltiples instancias consumiendo recursos
    lock_file = QLockFile(QDir.temp().absoluteFilePath("grk_powersloth_instance.lock"))
    # Intentar adquirir el bloqueo con un timeout de 100ms
    # QLockFile es inteligente: si el proceso dueño murió, roba el lock.
    if not lock_file.tryLock(100):
        # Ya existe una instancia
        QMessageBox.warning(None, "GRK PowerSloth", "⚠️ La aplicación ya se está ejecutando.\nRevise la bandeja del sistema (ícono junto al reloj).")
        sys.exit(0)
        
    # Mantener referencia global para que no se recolecte y libere el lock
    app._lock_file = lock_file

    # ===== OCULTAR CONSOLA (Limpieza Visual) =====
    # Si se ejecuta como script (.py) fuera de un EXE windowed, ocultar la ventana negra.
    try:
        if not getattr(sys, 'frozen', False):  # Solo si NO es un EXE congelado (PyInstaller maneja el EXE)
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32
            hwnd = kernel32.GetConsoleWindow()
            if hwnd != 0:
                user32.ShowWindow(hwnd, 0)  # 0 = SW_HIDE
    except:
        pass
    
    # Importar módulos de la aplicación
    from ui.main_window import MainWindow
    from presenters.main_presenter import MainPresenter
    
    # Patrón MVP:
    # 1. Crear la Vista
    view = MainWindow()
    
    # 2. Crear el Presentador y pasarle la Vista
    presenter = MainPresenter(view)
    
    # 3. Mostrar la Vista
    view.show()
    
    # 4. Ejecutar el loop de eventos
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
