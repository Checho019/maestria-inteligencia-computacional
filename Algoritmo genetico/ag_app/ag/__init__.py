"""Motor del algoritmo genético binario, independiente de la interfaz."""

from .configuracion import Configuracion, validar
from .motor import Estado, Resultado, ejecutar

__all__ = ["Configuracion", "validar", "Estado", "Resultado", "ejecutar"]
