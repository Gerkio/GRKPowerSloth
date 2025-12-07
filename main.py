"""
GRK PowerSloth - Python Version
Punto de entrada de la aplicación.

Equivalente a Program.cs

Uso: python main.py
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from ui.main_window import MainWindow
from presenters.main_presenter import MainPresenter


def main():
    """Función principal de la aplicación"""
    
    # Habilitar DPI awareness para pantallas de alta resolución
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Crear aplicación Qt
    app = QApplication(sys.argv)
    app.setApplicationName("GRK PowerSloth")
    app.setApplicationVersion("6.0")
    app.setOrganizationName("Gerkio")
    
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
