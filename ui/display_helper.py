"""
Utilidades de visualización para UI responsiva.
Detecta la resolución de pantalla y calcula factores de escala.
"""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSize
from typing import Tuple


class DisplayHelper:
    """
    Clase de utilidad para calcular factores de escala basados en la resolución del monitor.
    Permite crear una UI responsiva que se adapta a pantallas pequeñas.
    """
    
    # Resoluciones de referencia
    REFERENCE_HEIGHT = 1080  # Full HD como base
    COMPACT_THRESHOLD = 900   # Por debajo de esto, usar modo compacto
    
    # Factores de escala
    SCALE_COMPACT = 0.85      # 85% para pantallas pequeñas
    SCALE_NORMAL = 1.0        # 100% para HD y superiores
    SCALE_LARGE = 1.1         # 110% para pantallas 4K
    
    _cached_scale_factor: float = None
    _cached_screen_size: Tuple[int, int] = None
    
    @classmethod
    def get_screen_size(cls) -> Tuple[int, int]:
        """Obtiene el tamaño de la pantalla principal disponible."""
        if cls._cached_screen_size:
            return cls._cached_screen_size
        
        app = QApplication.instance()
        if app:
            screen = app.primaryScreen()
            if screen:
                geometry = screen.availableGeometry()
                cls._cached_screen_size = (geometry.width(), geometry.height())
                return cls._cached_screen_size
        
        # Fallback a Full HD
        return (1920, 1080)
    
    @classmethod
    def get_scale_factor(cls) -> float:
        """
        Calcula el factor de escala basado en la altura de la pantalla.
        
        Returns:
            float: Factor de escala (0.85, 1.0, o 1.1)
        """
        if cls._cached_scale_factor is not None:
            return cls._cached_scale_factor
        
        width, height = cls.get_screen_size()
        
        if height < cls.COMPACT_THRESHOLD:
            # Pantallas pequeñas (laptops 768p, 900p)
            cls._cached_scale_factor = cls.SCALE_COMPACT
        elif height >= 1440:
            # Pantallas 2K/4K
            cls._cached_scale_factor = cls.SCALE_LARGE
        else:
            # HD y Full HD
            cls._cached_scale_factor = cls.SCALE_NORMAL
        
        return cls._cached_scale_factor
    
    @classmethod
    def scale_value(cls, value: int) -> int:
        """Escala un valor entero según el factor de escala."""
        return int(value * cls.get_scale_factor())
    
    @classmethod
    def get_window_size(cls, base_width: int = 520, base_height: int = 620) -> QSize:
        """
        Calcula el tamaño de ventana escalado.
        
        Args:
            base_width: Ancho base de la ventana
            base_height: Altura base de la ventana
        
        Returns:
            QSize con dimensiones escaladas
        """
        scale = cls.get_scale_factor()
        return QSize(
            int(base_width * scale),
            int(base_height * scale)
        )
    
    @classmethod
    def get_font_size(cls, base_size: int = 10) -> int:
        """Calcula el tamaño de fuente escalado."""
        return max(8, int(base_size * cls.get_scale_factor()))
    
    @classmethod
    def get_spacing(cls, base_spacing: int = 10) -> int:
        """Calcula el espaciado escalado."""
        return max(4, int(base_spacing * cls.get_scale_factor()))
    
    @classmethod
    def get_padding(cls, base_padding: int = 10) -> int:
        """Calcula el padding escalado."""
        return max(4, int(base_padding * cls.get_scale_factor()))
    
    @classmethod
    def is_compact_mode(cls) -> bool:
        """Retorna True si se debe usar modo compacto."""
        return cls.get_scale_factor() < 1.0
    
    @classmethod
    def reset_cache(cls):
        """Resetea el cache (útil para testing o cambio de monitor)."""
        cls._cached_scale_factor = None
        cls._cached_screen_size = None
