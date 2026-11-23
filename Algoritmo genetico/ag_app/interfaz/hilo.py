"""Hilo que ejecuta el AG fuera de la interfaz para que la ventana no se congele."""

import threading
import time
from dataclasses import replace

from PySide6.QtCore import QThread, Signal

from ag import Estado, ejecutar


class HiloAG(QThread):
    """Ejecuta las ejecuciones pedidas con semillas consecutivas. La interfaz lee
    la última generación con `tomar_ultimo` y puede pausar o detener."""

    ejecucion_terminada = Signal(int, object)
    fallo = Signal(str)

    def __init__(self, cfg, ejecuciones, pausa_ms):
        super().__init__()
        self.cfg, self.ejecuciones, self.pausa = cfg, ejecuciones, pausa_ms / 1000
        self._detener = False
        self._continuar = threading.Event()     # sin marcar = en pausa
        self._continuar.set()
        self._candado = threading.Lock()
        self._ultimo = None
        self._ejecucion = 0

    def pedir_detener(self):
        self._detener = True
        self._continuar.set()                   # libera una pausa

    def pausar(self, en_pausa):
        if en_pausa:
            self._continuar.clear()
        else:
            self._continuar.set()

    def tomar_ultimo(self):
        with self._candado:
            ultimo, self._ultimo = self._ultimo, None
        return ultimo

    def _al_generar(self, estado):
        copia = Estado(estado.generacion, estado.X, estado.f, list(estado.mejor),
                       list(estado.media), list(estado.peor), estado.mejor_x, estado.mejor_f)
        with self._candado:
            self._ultimo = (self._ejecucion, copia)
        if self.pausa:
            time.sleep(self.pausa)
        self._continuar.wait()

    def run(self):
        try:
            for r in range(self.ejecuciones):
                if self._detener:
                    break
                self._ejecucion = r
                cfg = replace(self.cfg, semilla=self.cfg.semilla + r)
                resultado = ejecutar(cfg, self._al_generar, lambda: self._detener)
                self.ejecucion_terminada.emit(r, resultado)
        except Exception as error:
            self.fallo.emit(str(error))
