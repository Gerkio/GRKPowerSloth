"""
Gestor de notificaciones del sistema.
Equivalente a NotificationManager.cs
"""

from win10toast import ToastNotifier


class NotificationManager:
    """
    Gestor estático para mostrar notificaciones Toast nativas de Windows.
    """
    
    _toaster = ToastNotifier()
    
    @classmethod
    def show_notification(cls, title: str, message: str, duration: int = 5) -> None:
        """
        Muestra una notificación Toast simple.
        
        Args:
            title: Título de la notificación
            message: Mensaje de la notificación
            duration: Duración en segundos (por defecto 5)
        """
        try:
            cls._toaster.show_toast(
                title,
                message,
                duration=duration,
                threaded=True,  # No bloquear la UI
                icon_path=None
            )
        except Exception:
            # Si falla, ignorar silenciosamente
            # No queremos que la app se cierre por un error en notificaciones
            pass
