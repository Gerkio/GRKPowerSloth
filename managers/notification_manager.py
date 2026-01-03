"""
Gestor de notificaciones del sistema.
Equivalente a NotificationManager.cs (Legacy)

NOTA: Actualmente las notificaciones principales se manejan a través de 
MainWindow.show_notification usando QSystemTrayIcon (Nativo PyQt6).
Esta clase se mantiene por compatibilidad pero sin dependencias externas.
"""

class NotificationManager:
    """
    Gestor para mostrar notificaciones.
    Se ha eliminado win10toast por inestabilidad.
    """
    
    @classmethod
    def show_notification(cls, title: str, message: str, duration: int = 5) -> None:
        """
        No hace nada directamente para evitar dependencias externas.
        Las notificaciones deben canalizarse a través de la UI (MainWindow).
        """
        print(f"[NOTIFICATION] {title}: {message}")
