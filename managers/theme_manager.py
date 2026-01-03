"""
Gestor de temas visuales - VERSIÓN MEJORADA
Diseño moderno con alto contraste y elementos visuales atractivos.
"""

from typing import Dict
import base64
from models.enums import Theme


class ColorPalette:
    """Paleta de colores para un tema"""
    
    def __init__(
        self,
        # Fondos
        background: str,
        surface: str,
        surface_hover: str,
        # Textos
        text_primary: str,
        text_secondary: str,
        text_disabled: str,
        # Acentos
        accent_primary: str,
        accent_hover: str,
        accent_pressed: str,
        # Estados
        success: str,
        warning: str,
        danger: str,
        # Bordes
        border: str,
        border_focus: str
    ):
        self.background = background
        self.surface = surface
        self.surface_hover = surface_hover
        self.text_primary = text_primary
        self.text_secondary = text_secondary
        self.text_disabled = text_disabled
        self.accent_primary = accent_primary
        self.accent_hover = accent_hover
        self.accent_pressed = accent_pressed
        self.success = success
        self.warning = warning
        self.danger = danger
        self.border = border
        self.border_focus = border_focus


class ThemeManager:
    """
    Gestor de temas con diseño moderno.
    """
    
    # ===== TEMA OSCURO - Diseño Premium =====
    DARK_THEME = ColorPalette(
        # Fondos - Escala de grises profundos
        background='#121212',  # Más profundo (Material Dark)
        surface='#1e1e1e',     # Elevación 1
        surface_hover='#2d2d2d',
        # Textos - Alto contraste
        text_primary='#ffffff',
        text_secondary='#e0e0e0',  # Más brillante para legibilidad
        text_disabled='#757575',
        # Azul vibrante como acento
        accent_primary='#0078D4',
        accent_hover='#1a8cff',
        accent_pressed='#005a9e',
        # Estados
        success='#10b981',
        warning='#f59e0b',
        danger='#ef4444',
        # Bordes
        border='#404040',
        border_focus='#0078D4'
    )
    
    # ===== TEMA CLARO - Limpio y Moderno =====
    LIGHT_THEME = ColorPalette(
        # Fondos - Blancos suaves
        background='#fafafa',  # Casi blanco
        surface='#ffffff',     # Blanco puro
        surface_hover='#f0f0f0',
        # Textos
        text_primary='#000000',  # Negro puro para máximo contraste
        text_secondary='#424242', # Gris muy oscuro
        text_disabled='#9e9e9e',
        # Azul como acento
        accent_primary='#0078D4',
        accent_hover='#1a8cff',
        accent_pressed='#005a9e',
        # Estados
        success='#059669',
        warning='#d97706',
        danger='#dc2626',
        # Bordes
        border='#d0d0d0',
        border_focus='#0078D4'
    )
    
    # ===== TEMA NORDIC - Azul Frío =====
    NORDIC_THEME = ColorPalette(
        background='#2E3440',
        surface='#3B4252',
        surface_hover='#434C5E',
        text_primary='#ECEFF4',
        text_secondary='#D8DEE9',
        text_disabled='#4C566A',
        accent_primary='#88C0D0',
        accent_hover='#81A1C1',
        accent_pressed='#5E81AC',
        success='#A3BE8C',
        warning='#EBCB8B',
        danger='#BF616A',
        border='#4C566A',
        border_focus='#88C0D0'
    )
    
    # ===== TEMA DRACULA - Vibrante =====
    DRACULA_THEME = ColorPalette(
        background='#282A36',
        surface='#44475A',
        surface_hover='#6272A4',
        text_primary='#F8F8F2',
        text_secondary='#BD93F9',
        text_disabled='#6272A4',
        accent_primary='#BD93F9',
        accent_hover='#FF79C6',
        accent_pressed='#8BE9FD',
        success='#50FA7B',
        warning='#F1FA8C',
        danger='#FF5555',
        border='#6272A4',
        border_focus='#FF79C6'
    )
    
    # ===== TEMA BLOOD MOON - Agresivo =====
    BLOOD_THEME = ColorPalette(
        background='#050505',
        surface='#1A1A1A',
        surface_hover='#2D2D2D',
        text_primary='#FFFFFF',
        text_secondary='#FF4D4D',
        text_disabled='#4D4D4D',
        accent_primary='#DC143C',
        accent_hover='#FF0000',
        accent_pressed='#800000',
        success='#008000',
        warning='#FFD700',
        danger='#FF0000',
        border='#800000',
        border_focus='#DC143C'
    )
    
    # ===== TEMA HIGH CONTRAST - Accesible =====
    # Diseñado para máxima legibilidad y compatibilidad con lectores de pantalla
    HIGH_CONTRAST_THEME = ColorPalette(
        # Fondos - Negro puro para máximo contraste
        background='#000000',
        surface='#000000',
        surface_hover='#1A1A1A',
        # Textos - Blanco puro y amarillo brillante
        text_primary='#FFFFFF',
        text_secondary='#FFFF00',  # Amarillo para información secundaria
        text_disabled='#808080',
        # Colores de alto contraste
        accent_primary='#00FFFF',   # Cyan brillante
        accent_hover='#FFFFFF',
        accent_pressed='#00CCCC',
        # Estados con colores muy distinguibles
        success='#00FF00',          # Verde brillante
        warning='#FFFF00',          # Amarillo brillante
        danger='#FF0000',           # Rojo brillante
        # Bordes visibles
        border='#FFFFFF',
        border_focus='#00FFFF'
    )
    
    @classmethod
    def get_palette(cls, theme: Theme) -> ColorPalette:
        """Obtiene la paleta de colores para un tema."""
        if theme == Theme.LIGHT:
            return cls.LIGHT_THEME
        elif theme == Theme.NORDIC:
            return cls.NORDIC_THEME
        elif theme == Theme.DRACULA:
            return cls.DRACULA_THEME
        elif theme == Theme.BLOOD:
            return cls.BLOOD_THEME
        elif theme == Theme.HIGH_CONTRAST:
            return cls.HIGH_CONTRAST_THEME
        else:
            return cls.DARK_THEME
    
    @staticmethod
    def _get_arrow_svg(color: str, is_up: bool) -> str:
        """Genera un data URI para un SVG de flecha con el color especificado."""
        path = "M7.41,15.41L12,10.83L16.59,15.41L18,14L12,8L6,14L7.41,15.41Z" if is_up else "M7.41,8.59L12,13.17L16.59,8.59L18,10L12,16L6,10L7.41,8.59Z"
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{color}"><path d="{path}"/></svg>'
        encoded = base64.b64encode(svg.encode('utf-8')).decode('ascii')
        return f"url(data:image/svg+xml;base64,{encoded})"

    @classmethod
    def apply_theme(cls, widget, palette: ColorPalette, scale_factor: float = 1.0) -> None:
        """
        Aplica un tema moderno completo al widget con escalado responsivo.
        
        Args:
            widget: Widget donde aplicar el tema
            palette: Paleta de colores a usar
            scale_factor: Factor de escala (0.85 para compacto, 1.0 normal, 1.1 grande)
        """
        # Calcular tamaños escalados
        font_base = int(10 * scale_factor)
        font_small = int(9 * scale_factor)
        font_large = int(11 * scale_factor)
        padding_base = int(10 * scale_factor)
        padding_small = int(6 * scale_factor)
        padding_large = int(15 * scale_factor)
        spacing = int(8 * scale_factor)
        border_radius = int(6 * scale_factor)
        border_radius_large = int(8 * scale_factor)
        indicator_size = int(18 * scale_factor)
        min_height = int(24 * scale_factor)
        btn_height = int(20 * scale_factor)
        
        # Generar flechas dinámicas con ALTO CONTRASTE y tamaño mayor
        # Si el fondo es oscuro, flechas blancas. Si es claro, flechas negras.
        # Comprobar si es un tema oscuro basado en la luminosidad o una lista de fondos oscuros
        dark_backgrounds = ["#121212", "#2E3440", "#282A36", "#050505", "#000000"]
        arrow_color = "#FFFFFF" if palette.background.upper() in [bg.upper() for bg in dark_backgrounds] else "#000000"
        
        # Para el tema de alto contraste, forzar blanco si el fondo es negro
        if palette.background == "#000000":
            arrow_color = "#FFFFFF"
            
        arrow_up = cls._get_arrow_svg(arrow_color, True)
        arrow_down = cls._get_arrow_svg(arrow_color, False)
        
        # Grosor de bordes para alto contraste
        border_width = "2px" if palette.background == "#000000" else "1px"
        border_width_focus = "3px" if palette.background == "#000000" else "2px"
        
        # Tamaño de botones escalado (más grande)
        spin_btn_width = int(24 * scale_factor)
        
        stylesheet = f"""
            /* ===== BASE ===== */
            QMainWindow, QWidget {{
                background-color: {palette.background};
                color: {palette.text_primary};
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: {font_base}pt;
            }}
            
            /* ===== LABELS ===== */
            QLabel {{
                color: {palette.text_primary};
                background-color: transparent;
                padding: 2px;
            }}
            
            /* ===== GROUP BOX - Estilo tarjeta ===== */
            QGroupBox {{
                background-color: {palette.surface};
                border: {border_width} solid {palette.border};
                border-radius: 8px;
                margin-top: 16px;
                padding: 15px 10px 10px 10px;
                font-weight: bold;
                color: {palette.text_primary};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                top: 4px;
                padding: 0 8px;
                background-color: {palette.surface};
                color: {palette.accent_primary};
                font-weight: bold;
            }}
            
            /* ===== RADIO BUTTONS - Visibles y modernos ===== */
            QRadioButton {{
                color: {palette.text_primary};
                background-color: transparent;
                spacing: 8px;
                padding: 6px 4px;
            }}
            
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid {palette.border};
                background-color: {palette.surface};
            }}
            
            QRadioButton::indicator:hover {{
                border-color: {palette.accent_primary};
                background-color: {palette.surface_hover};
            }}
            
            QRadioButton::indicator:checked {{
                border: 2px solid {palette.accent_primary};
                background-color: {palette.accent_primary};
            }}
            
            QRadioButton::indicator:checked::after {{
                width: 8px;
                height: 8px;
                border-radius: 4px;
                background-color: white;
            }}
            
            /* ===== CHECKBOXES - Modernos ===== */
            QCheckBox {{
                color: {palette.text_primary};
                background-color: transparent;
                spacing: 8px;
                padding: 6px 4px;
            }}
            
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {palette.border};
                background-color: {palette.surface};
            }}
            
            QCheckBox::indicator:hover {{
                border-color: {palette.accent_primary};
                background-color: {palette.surface_hover};
            }}
            
            QCheckBox::indicator:checked {{
                border: 2px solid {palette.accent_primary};
                background-color: {palette.accent_primary};
                image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMiIgaGVpZ2h0PSIxMiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjMiPjxwb2x5bGluZSBwb2ludHM9IjIwIDYgOSAxNyA0IDEyIj48L3BvbHlsaW5lPjwvc3ZnPg==);
            }}
            
            /* ===== BOTONES - Estilo moderno con gradiente ===== */
            QPushButton {{
                background-color: {palette.surface};
                color: {palette.text_primary};
                border: {border_width} solid {palette.border};
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 500;
                min-height: 20px;
            }}
            
            QPushButton:hover {{
                background-color: {palette.surface_hover};
                border-color: {palette.accent_primary};
            }}
            
            QPushButton:pressed {{
                background-color: {palette.accent_pressed};
                border-color: {palette.accent_pressed};
            }}
            
            QPushButton:disabled {{
                background-color: {palette.surface};
                color: {palette.text_disabled};
                border-color: {palette.border};
            }}
            
            /* Botón Start - Acento primario */
            QPushButton#btnStart {{
                background-color: {palette.accent_primary};
                color: #ffffff;
                border: none;
                font-weight: bold;
                font-size: 11pt;
            }}
            
            QPushButton#btnStart:hover {{
                background-color: {palette.accent_hover};
            }}
            
            QPushButton#btnStart:pressed {{
                background-color: {palette.accent_pressed};
            }}
            
            QPushButton#btnStart:disabled {{
                background-color: {palette.text_disabled};
                color: {palette.surface};
            }}
            
            /* ===== SPIN BOX - Moderno ===== */
            QSpinBox, QTimeEdit {{
                background-color: {palette.surface};
                color: {palette.text_primary};
                border: {border_width_focus} solid {palette.border};
                border-radius: 6px;
                padding: 6px 10px;
                min-height: 24px;
                selection-background-color: {palette.accent_primary};
            }}
            
            QSpinBox:hover, QTimeEdit:hover {{
                border-color: {palette.accent_primary};
            }}
            
            QSpinBox:focus, QTimeEdit:focus {{
                border-color: {palette.accent_primary};
                background-color: {palette.surface_hover};
            }}
            
            /* Error States */
            QSpinBox[error="true"] {{
                border-color: #ef4444 !important;
                background-color: {"#3a1a1a" if palette.background != "#FFFFFF" else "#ffe0e0"} !important;
            }}
            
            QSpinBox::up-button, QSpinBox::down-button,
            QTimeEdit::up-button, QTimeEdit::down-button {{
                background-color: {palette.surface_hover};
                border: none;
                width: {spin_btn_width}px;
                border-radius: 3px;
                margin: 1px;
            }}
            
            QSpinBox::up-button:hover, QSpinBox::down-button:hover,
            QTimeEdit::up-button:hover, QTimeEdit::down-button:hover {{
                background-color: {palette.accent_primary};
            }}
            
            QSpinBox::up-arrow, QTimeEdit::up-arrow {{
                image: {arrow_up};
                width: 14px;
                height: 14px;
            }}
            
            QSpinBox::down-arrow, QTimeEdit::down-arrow {{
                image: {arrow_down};
                width: 14px;
                height: 14px;
            }}
            
            /* ===== COMBOBOX - Estilizado ===== */
            QComboBox {{
                background-color: {palette.surface};
                color: {palette.text_primary};
                border: {border_width_focus} solid {palette.border};
                border-radius: 6px;
                padding: 6px 12px;
                min-height: 24px;
            }}
            
            QComboBox:hover {{
                border-color: {palette.accent_primary};
            }}
            
            QComboBox:focus {{
                border-color: {palette.accent_primary};
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 30px;
                background-color: transparent;
            }}
            
            QComboBox::down-arrow {{
                image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMiIgaGVpZ2h0PSIxMiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSIjYjBiMGIwIj48cGF0aCBkPSJNNyAxMGw1IDUgNS01eiIvPjwvc3ZnPg==);
                width: 12px;
                height: 12px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {palette.surface};
                color: {palette.text_primary};
                border: 1px solid {palette.border};
                border-radius: 6px;
                selection-background-color: {palette.accent_primary};
                selection-color: #ffffff;
                padding: 4px;
            }}
            
            /* ===== LINE EDIT ===== */
            QLineEdit {{
                background-color: {palette.surface};
                color: {palette.text_primary};
                border: {border_width_focus} solid {palette.border};
                border-radius: 6px;
                padding: 6px 12px;
                min-height: 24px;
                selection-background-color: {palette.accent_primary};
            }}
            
            QLineEdit:hover {{
                border-color: {palette.accent_primary};
            }}
            
            QLineEdit:focus {{
                border-color: {palette.accent_primary};
                background-color: {palette.surface_hover};
            }}
            
            QLineEdit::placeholder {{
                color: {palette.text_disabled};
            }}
            
            /* ===== PROGRESS BAR - Moderno ===== */
            QProgressBar {{
                background-color: {palette.surface};
                border: none;
                border-radius: 8px;
                text-align: center;
                color: {palette.text_primary};
                font-weight: bold;
                min-height: 24px;
            }}
            
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {palette.accent_primary},
                    stop:1 {palette.accent_hover});
                border-radius: 8px;
            }}
            
            /* ===== MENU BAR ===== */
            QMenuBar {{
                background-color: {palette.surface};
                color: {palette.text_primary};
                border-bottom: {border_width} solid {palette.border};
                padding: 4px 8px;
                spacing: 4px;
            }}
            
            QMenuBar::item {{
                background-color: transparent;
                padding: 6px 12px;
                border-radius: 4px;
            }}
            
            QMenuBar::item:selected {{
                background-color: {palette.accent_primary};
                color: #ffffff;
            }}
            
            /* ===== MENUS ===== */
            QMenu {{
                background-color: {palette.surface};
                color: {palette.text_primary};
                border: 1px solid {palette.border};
                border-radius: 8px;
                padding: 8px 4px;
            }}
            
            QMenu::item {{
                padding: 8px 32px 8px 16px;
                border-radius: 4px;
                margin: 2px 4px;
            }}
            
            QMenu::item:selected {{
                background-color: {palette.accent_primary};
                color: #ffffff;
            }}
            
            QMenu::separator {{
                height: 1px;
                background-color: {palette.border};
                margin: 6px 10px;
            }}
            
            QMenu::indicator {{
                width: 16px;
                height: 16px;
                margin-left: 8px;
            }}
            
            QMenu::indicator:checked {{
                background-color: {palette.accent_primary};
                border-radius: 3px;
            }}
            
            /* ===== SCROLLBARS ===== */
            QScrollBar:vertical {{
                background-color: {palette.background};
                width: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {palette.border};
                border-radius: 6px;
                min-height: 30px;
                margin: 2px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {palette.accent_primary};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            /* ===== TOOLTIPS ===== */
            QToolTip {{
                background-color: {palette.surface};
                color: {palette.text_primary};
                border: {border_width} solid {palette.accent_primary};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 9pt;
            }}
            
            /* ===== CONDITION CONTAINER (Monitor Mode) ===== */
            #conditionContainer {{
                background-color: {palette.surface};
                border: {border_width} solid {palette.border};
                border-radius: 8px;
            }}
            
            #conditionContainer QLabel {{
                color: {palette.accent_primary};
                font-weight: bold;
                font-size: 10pt;
                background: transparent;
            }}
            
            #conditionContainer QRadioButton {{
                color: {palette.text_primary};
                font-size: 9pt;
                background: transparent;
            }}
            
            #conditionContainer QRadioButton::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid {palette.border};
                background-color: {palette.surface};
            }}
            
            #conditionContainer QRadioButton::indicator:checked {{
                background-color: {palette.accent_primary};
                border-color: {palette.accent_primary};
            }}
            
            #conditionContainer QRadioButton::indicator:hover {{
                border-color: {palette.accent_hover};
            }}
        """
        
        widget.setStyleSheet(stylesheet)
