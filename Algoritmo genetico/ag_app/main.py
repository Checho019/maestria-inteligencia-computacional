"""Arranque de la interfaz del algoritmo genético binario.

Uso: python main.py
"""

import sys
import traceback

from PySide6.QtWidgets import QApplication, QMessageBox

from interfaz.controlador import Controlador
from interfaz.ventana import VentanaPrincipal


def mostrar_error(tipo, valor, rastro):
    """Muestra cualquier error inesperado en un mensaje, sin cerrar la aplicación."""
    traceback.print_exception(tipo, valor, rastro)
    QMessageBox.critical(None, "Error inesperado", f"{tipo.__name__}: {valor}")


def main():
    app = QApplication(sys.argv)
    sys.excepthook = mostrar_error
    ventana = VentanaPrincipal()
    controlador = Controlador(ventana)
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
