"""Capturas de la interfaz para el informe, tomadas sin abrir la ventana en pantalla.

Uso, desde la carpeta informe: python capturar_interfaz.py
"""

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_QPA_FONTDIR", r"C:\Windows\Fonts")
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "ag_app"))

from PySide6.QtCore import QEventLoop, QTimer  # noqa: E402
from PySide6.QtGui import QFont  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from interfaz.controlador import Controlador  # noqa: E402
from interfaz.ventana import VentanaPrincipal  # noqa: E402

app = QApplication(sys.argv)
app.setFont(QFont("Segoe UI", 9))
ventana = VentanaPrincipal()
controlador = Controlador(ventana)
ventana.resize(1320, 860)
ventana.show()


def ejecutar(**campos):
    for nombre, valor in campos.items():
        widget = getattr(ventana, nombre)
        if hasattr(widget, "setCurrentText"):
            widget.setCurrentText(valor)
        elif hasattr(widget, "setChecked"):
            widget.setChecked(valor)
        else:
            widget.setText(valor)
    ventana.iniciar.click()
    bucle, reloj = QEventLoop(), QTimer()
    reloj.timeout.connect(lambda: bucle.quit() if controlador.hilo is None else None)
    reloj.start(50)
    bucle.exec()
    app.processEvents()


carpeta = AQUI / "figuras"
carpeta.mkdir(exist_ok=True)
ejecutar(funcion="Himmelblau", seleccion="Ruleta", cruce="Un punto", mutacion="Bit-flip por bit",
         ejecuciones="10", pausa="0", escala_log=True)
ventana.grab().save(str(carpeta / "interfaz_himmelblau.png"))
print("Captura guardada en", carpeta)
