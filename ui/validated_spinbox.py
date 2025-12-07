"""
Widget SpinBox personalizado con validación visual no intrusiva.
Permite escribir valores fuera de rango y muestra feedback visual.
"""

from PyQt6.QtWidgets import QSpinBox, QToolTip
from PyQt6.QtCore import QTimer, QPoint
from PyQt6.QtGui import QValidator


class ValidatedSpinBox(QSpinBox):
    """
    SpinBox personalizado que permite entrada libre y valida visualmente.
    
    Características:
    - Permite escribir valores fuera de rango temporalmente
    - Muestra borde rojo cuando el valor es inválido
    - Muestra tooltip temporal con límite permitido
    - Corrige el valor al perder el foco
    """
    
    STYLE_NORMAL = ""
    STYLE_ERROR = "border: 2px solid #ef4444 !important; background-color: #3a1a1a !important;"
    STYLE_ERROR_LIGHT = "border: 2px solid #ef4444 !important; background-color: #ffe0e0 !important;"
    
    def __init__(self, parent=None, is_dark_theme: bool = True):
        super().__init__(parent)
        self._is_dark_theme = is_dark_theme
        self._is_error_state = False
        self._tooltip_timer = QTimer(self)
        self._tooltip_timer.setSingleShot(True)
        self._tooltip_timer.timeout.connect(self._hide_error_tooltip)
        
        # Conectar señal de cambio de texto
        self.lineEdit().textEdited.connect(self._on_text_edited)
    
    def set_theme(self, is_dark: bool):
        """Actualiza el tema para los estilos de error."""
        self._is_dark_theme = is_dark
        if self._is_error_state:
            self._apply_error_style()
    
    def _on_text_edited(self, text: str):
        """Handler cuando el usuario edita el texto manualmente."""
        try:
            value = int(text) if text else 0
            
            if value > self.maximum():
                self._show_error(f"Máximo: {self.maximum()}")
            elif value < self.minimum():
                self._show_error(f"Mínimo: {self.minimum()}")
            else:
                self._clear_error()
        except ValueError:
            # No es un número válido, ignorar
            pass
    
    def _show_error(self, message: str):
        """Muestra el estado de error con borde rojo y tooltip."""
        if not self._is_error_state:
            self._is_error_state = True
            self._apply_error_style()
        
        # Mostrar tooltip temporal
        global_pos = self.mapToGlobal(QPoint(0, self.height() + 5))
        QToolTip.showText(global_pos, message, self, self.rect(), 2000)
        
        # Timer para ocultar el tooltip
        self._tooltip_timer.start(2500)
    
    def _apply_error_style(self):
        """Aplica el estilo visual de error."""
        style = self.STYLE_ERROR if self._is_dark_theme else self.STYLE_ERROR_LIGHT
        self.setStyleSheet(style)
    
    def _clear_error(self):
        """Limpia el estado de error."""
        if self._is_error_state:
            self._is_error_state = False
            self.setStyleSheet(self.STYLE_NORMAL)
            self._tooltip_timer.stop()
    
    def _hide_error_tooltip(self):
        """Oculta el tooltip de error."""
        QToolTip.hideText()
    
    def focusOutEvent(self, event):
        """Override: corregir valor al perder el foco."""
        # Leer el texto actual
        text = self.lineEdit().text()
        try:
            value = int(text) if text else 0
            
            # Corregir si está fuera de rango
            if value > self.maximum():
                self.setValue(self.maximum())
            elif value < self.minimum():
                self.setValue(self.minimum())
            else:
                self.setValue(value)
            
            self._clear_error()
        except ValueError:
            # Si no es número válido, restaurar al mínimo
            self.setValue(self.minimum())
            self._clear_error()
        
        super().focusOutEvent(event)
    
    def validate(self, text: str, pos: int):
        """
        Override: Validación permisiva para permitir escribir valores fuera de rango.
        Solo acepta dígitos pero no limita el rango mientras se escribe.
        """
        if not text:
            return (QValidator.State.Intermediate, text, pos)
        
        # Solo permitir dígitos
        if text.isdigit():
            return (QValidator.State.Acceptable, text, pos)
        
        return (QValidator.State.Invalid, text, pos)
