"""
Modelo de datos para representar un proceso.
Equivalente a ProcessItem.cs
"""

from dataclasses import dataclass


@dataclass
class ProcessItem:
    """
    Clase de datos para representar un proceso de forma legible en la UI.
    """
    pid: int
    name: str
    display_name: str
    
    def __str__(self) -> str:
        return self.display_name
    
    def __repr__(self) -> str:
        return f"ProcessItem(pid={self.pid}, name='{self.name}')"
