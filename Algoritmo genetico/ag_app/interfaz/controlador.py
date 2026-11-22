"""Controlador. Valida las entradas, lanza el motor en un hilo aparte y pasa cada
generación a las gráficas (sección 9 de la guía)."""

import csv
import threading
import time
from dataclasses import replace
from pathlib import Path

import numpy as np
from PySide6.QtCore import QObject, QThread, QTimer, Signal
from PySide6.QtWidgets import QFileDialog, QMessageBox, QTableWidgetItem

from ag import Configuracion, Estado, ejecutar, validar
from ag.codificacion import bits_por_precision, cadena
from funciones.objetivo import FUNCIONES


class HiloAG(QThread):
    """Ejecuta las corridas fuera del hilo de la interfaz para que no se congele."""

    corrida_terminada = Signal(int, object)
    fallo = Signal(str)

    def __init__(self, cfg, corridas, pausa_ms):
        super().__init__()
        self.cfg, self.corridas, self.pausa = cfg, corridas, pausa_ms / 1000
        self._detener = False
        self._candado = threading.Lock()
        self._ultimo = None
        self._corrida = 0

    def pedir_detener(self):
        self._detener = True

    def tomar_ultimo(self):
        with self._candado:
            ultimo, self._ultimo = self._ultimo, None
        return ultimo

    def _al_generar(self, estado):
        copia = Estado(estado.generacion, estado.X, estado.f, list(estado.mejor),
                       list(estado.media), list(estado.peor), estado.mejor_x, estado.mejor_f)
        with self._candado:
            self._ultimo = (self._corrida, copia)
        if self.pausa:
            time.sleep(self.pausa)

    def run(self):
        try:
            for r in range(self.corridas):
                if self._detener:
                    break
                self._corrida = r
                cfg = replace(self.cfg, semilla=self.cfg.semilla + r)
                resultado = ejecutar(cfg, self._al_generar, lambda: self._detener)
                self.corrida_terminada.emit(r, resultado)
        except Exception as error:
            self.fallo.emit(str(error))


class Controlador(QObject):
    def __init__(self, ventana):
        super().__init__()
        self.v = ventana
        self.hilo = None
        self.resultados = []
        self.cfg = None
        self.temporizador = QTimer(self)
        self.temporizador.setInterval(30)
        self.temporizador.timeout.connect(self._refrescar)

        v = ventana
        v.funcion.currentTextChanged.connect(self._cambiar_funcion)
        for campo in (v.n, v.L, v.eps):
            campo.textChanged.connect(self._actualizar_codificacion)
        v.modo_L.currentTextChanged.connect(self._actualizar_codificacion)
        v.pm_auto.toggled.connect(self._actualizar_codificacion)
        for combo in (v.seleccion, v.cruce, v.mutacion):
            combo.currentTextChanged.connect(self._mostrar_parametros)
        v.escala_log.toggled.connect(self._preparar_convergencia)
        v.parar_error.toggled.connect(v.tolerancia.setEnabled)
        v.parar_estancamiento.toggled.connect(v.G.setEnabled)
        v.G.setEnabled(False)
        v.iniciar.clicked.connect(self.iniciar)
        v.detener.clicked.connect(self.detener)
        v.exportar_csv.clicked.connect(self.exportar_csv)
        v.guardar_figuras.clicked.connect(self.guardar_figuras)

        self._cambiar_funcion(v.funcion.currentText())
        self._mostrar_parametros()

    # ----- Reacciones de la interfaz -----

    def _cambiar_funcion(self, nombre):
        v, obj = self.v, FUNCIONES[nombre]
        v.tipo.setText(obj.tipo)
        a, b = obj.dominio
        v.dominio.setText(f"[{a:g}, {b:g}] en cada variable")
        libre = obj.n_fijo is None
        v.n.setEnabled(libre)
        if not libre:
            v.n.setText(str(obj.n_fijo))
        v.escala_log.setEnabled(not obj.maximizar)
        if obj.maximizar:
            v.escala_log.setChecked(False)
        self._actualizar_codificacion()
        self._preparar_convergencia()

    def _preparar_convergencia(self, *_):
        """Prepara la curva de convergencia y, si ya hay una corrida, la vuelve a dibujar."""
        v = self.v
        vigente = self.cfg is not None and self.cfg.funcion == v.funcion.currentText()
        cfg = self.cfg if vigente else Configuracion(funcion=v.funcion.currentText())
        v.convergencia.preparar(cfg.objetivo, cfg.T, v.escala_log.isChecked(), cfg.tolerancia)
        if vigente and self.resultados and self.hilo is None:
            res = self.resultados[-1]
            v.convergencia.actualizar(Estado(res.generaciones, None, None, res.mejor,
                                             res.media, res.peor, res.mejor_x, res.mejor_f))

    def _n_actual(self):
        obj = FUNCIONES[self.v.funcion.currentText()]
        try:
            return obj.n_fijo or int(self.v.n.text())
        except ValueError:
            return None

    def _L_actual(self):
        v = self.v
        try:
            if v.modo_L.currentText() == "Bits por variable":
                return int(v.L.text())
            a, b = FUNCIONES[v.funcion.currentText()].dominio
            return bits_por_precision(a, b, float(v.eps.text()))
        except (ValueError, ZeroDivisionError):
            return None

    def _actualizar_codificacion(self, *_):
        v = self.v
        obj = FUNCIONES[v.funcion.currentText()]
        n, L = self._n_actual(), self._L_actual()
        por_bits = v.modo_L.currentText() == "Bits por variable"
        v.forma_codificacion.setRowVisible(v.L, por_bits)
        v.forma_codificacion.setRowVisible(v.eps, not por_bits)
        v.forma_codificacion.setRowVisible(v.L_calculado, not por_bits)
        v.optimo.setText(f"f = {obj.f_optimo:g} en {obj.x_optimo_texto(n or 2)}")
        if n and L and L > 0:
            a, b = obj.dominio
            v.L_calculado.setText(f"{L} bits, resolución {(b - a) / (2**L - 1):.2e}")
            v.longitud.setText(f"{n * L} bits")
            if v.pm_auto.isChecked():
                v.pm.setText(f"{1 / (n * L):.5g}")
        else:
            v.L_calculado.setText("—")
            v.longitud.setText("—")
        v.pm.setEnabled(not v.pm_auto.isChecked())
        if self.hilo is None or not self.hilo.isRunning():
            v.niveles.preparar(obj, n if n and n >= 2 else 2)

    def _mostrar_parametros(self, *_):
        v, forma = self.v, self.v.forma_operadores
        forma.setRowVisible(v.k, v.seleccion.currentText() == "Torneo")
        forma.setRowVisible(v.s, v.seleccion.currentText() == "Ranking lineal")
        forma.setRowVisible(v.p0, v.cruce.currentText() == "Uniforme")
        bit_flip = v.mutacion.currentText() == "Bit-flip por bit"
        forma.setRowVisible(v.pm_auto, bit_flip)
        forma.setRowVisible(v.pm, bit_flip)
        forma.setRowVisible(v.pmi, not bit_flip)

    # ----- Lectura y validación de las entradas -----

    def _leer(self):
        """Arma la configuración desde los campos. Devuelve (cfg, corridas, pausa)
        y la lista de errores con mensajes claros."""
        v, errores = self.v, []

        def numero(campo, nombre, tipo):
            texto = campo.text().strip().replace(",", ".")
            try:
                return tipo(texto)
            except ValueError:
                clase = "un número entero" if tipo is int else "un número"
                errores.append(f"{nombre} debe ser {clase} (se recibió \"{campo.text()}\").")
                return tipo(0)

        cfg = Configuracion(
            funcion=v.funcion.currentText(),
            n=numero(v.n, "El número de variables n", int),
            N=numero(v.N, "El tamaño de población N", int),
            T=numero(v.T, "Las generaciones T", int),
            pc=numero(v.pc, "La probabilidad de cruce Pc", float),
            elites=numero(v.elites, "El número de élites e", int),
            semilla=numero(v.semilla, "La semilla", int),
            seleccion=v.seleccion.currentText(),
            k=numero(v.k, "El tamaño del torneo k", int),
            s=numero(v.s, "La presión selectiva s", float),
            cruce=v.cruce.currentText(),
            p0=numero(v.p0, "La probabilidad de intercambio p0", float),
            mutacion=v.mutacion.currentText(),
            pm=None if v.pm_auto.isChecked() else numero(v.pm, "La probabilidad Pm", float),
            pmi=numero(v.pmi, "La probabilidad Pmi", float),
            parar_por_error=v.parar_error.isChecked(),
            tolerancia=numero(v.tolerancia, "La tolerancia del error", float),
            parar_por_estancamiento=v.parar_estancamiento.isChecked(),
            G=numero(v.G, "Las generaciones sin mejora G", int),
        )
        if v.modo_L.currentText() == "Bits por variable":
            cfg.L = numero(v.L, "Los bits por variable L", int)
        else:
            eps = numero(v.eps, "La precisión ε", float)
            if eps <= 0:
                errores.append("La precisión ε debe ser mayor que 0.")
            else:
                a, b = cfg.objetivo.dominio
                cfg.L = bits_por_precision(a, b, eps)
        corridas = numero(v.corridas, "El número de corridas", int)
        pausa = numero(v.pausa, "La pausa por generación", int)
        if not errores:
            errores += validar(cfg)
            if not 1 <= corridas <= 100:
                errores.append(f"El número de corridas debe estar entre 1 y 100 (se recibió {corridas}).")
            if not 0 <= pausa <= 2000:
                errores.append(f"La pausa debe estar entre 0 y 2000 ms (se recibió {pausa}).")
        return (cfg, corridas, pausa), errores

    # ----- Ejecución -----

    def iniciar(self):
        (cfg, corridas, pausa), errores = self._leer()
        if errores:
            QMessageBox.warning(self.v, "Revise los parámetros", "\n".join(errores))
            return
        v = self.v
        self.cfg, self.resultados = cfg, []
        v.niveles.preparar(cfg.objetivo, cfg.n_variables)
        self._preparar_convergencia()
        v.tabla.setRowCount(0)
        v.resumen.setText("")
        v.progreso.setRange(0, cfg.T)
        v.progreso.setValue(0)
        self._bloquear(True)
        self.corridas = corridas
        self.hilo = HiloAG(cfg, corridas, pausa)
        self.hilo.corrida_terminada.connect(self._corrida_terminada)
        self.hilo.fallo.connect(self._fallo)
        self.hilo.finished.connect(self._terminado)
        self.hilo.start()
        self.temporizador.start()
        v.statusBar().showMessage(f"Ejecutando {cfg.funcion} con {cfg.seleccion}, {cfg.cruce} y {cfg.mutacion}")

    def _bloquear(self, ejecutando):
        """Mientras corre el AG solo queda activo el botón Detener."""
        v = self.v
        for widget in v.grupos_configuracion + [v.corridas, v.pausa, v.iniciar, v.escala_log,
                                                v.exportar_csv, v.guardar_figuras]:
            widget.setEnabled(not ejecutando)
        v.detener.setEnabled(ejecutando)

    def detener(self):
        if self.hilo is not None:
            self.hilo.pedir_detener()

    def _refrescar(self):
        if self.hilo is None:
            return
        ultimo = self.hilo.tomar_ultimo()
        if ultimo is None:
            return
        corrida, estado = ultimo
        v = self.v
        v.niveles.actualizar(estado)
        v.convergencia.actualizar(estado)
        v.progreso.setValue(estado.generacion)
        v.etiqueta_progreso.setText(
            f"Corrida {corrida + 1} de {self.corridas} (semilla {self.cfg.semilla + corrida}), "
            f"generación {estado.generacion} de {self.cfg.T}")

    def _corrida_terminada(self, r, res):
        self._refrescar()
        self.resultados.append(res)
        v, cfg = self.v, self.cfg
        v.resultados["Mejor cromosoma"].setText(cadena(res.mejor_cromosoma, cfg.L))
        v.resultados["x*"].setText("(" + ", ".join(f"{x:.6f}" for x in res.mejor_x) + ")")
        v.resultados["f(x*)"].setText(f"{res.mejor_f:.8f}")
        v.resultados["Error al óptimo"].setText(f"{res.error:.3e}")
        v.resultados["Generación del mejor"].setText(str(res.generacion_mejor))
        v.resultados["Generaciones ejecutadas"].setText(str(res.generaciones))
        v.resultados["Tiempo"].setText(f"{res.tiempo * 1000:.1f} ms")
        v.resultados["Motivo de parada"].setText(res.motivo)
        fila = v.tabla.rowCount()
        v.tabla.insertRow(fila)
        valores = [cfg.semilla + r, f"{res.mejor_f:.6f}", f"{res.error:.2e}",
                   res.generacion_mejor, f"{res.tiempo * 1000:.1f}"]
        for columna, valor in enumerate(valores):
            v.tabla.setItem(fila, columna, QTableWidgetItem(str(valor)))
        v.tabla.scrollToBottom()

    def _terminado(self):
        self.temporizador.stop()
        self._refrescar()
        v = self.v
        self._bloquear(False)
        if self.resultados:
            finales = np.array([r.mejor_f for r in self.resultados])
            errores = np.array([r.error for r in self.resultados])
            exito = np.mean(errores < self.cfg.tolerancia) * 100
            desviacion = finales.std(ddof=1) if finales.size > 1 else 0.0
            v.resumen.setText(
                f"{len(finales)} corridas. Mejor valor final {finales.mean():.6f} ± {desviacion:.6f} "
                f"(media ± DE), error medio {errores.mean():.2e}, éxito {exito:.0f} % "
                f"con error menor que {self.cfg.tolerancia:g}.")
        v.statusBar().showMessage("Ejecución terminada", 5000)
        self.hilo = None

    def _fallo(self, mensaje):
        QMessageBox.critical(self.v, "Error en la ejecución", mensaje)

    # ----- Exportación -----

    def exportar_csv(self):
        if not self.resultados:
            QMessageBox.information(self.v, "Sin resultados", "Ejecute el AG antes de exportar.")
            return
        ruta, _ = QFileDialog.getSaveFileName(self.v, "Exportar resultados", "resultados_ag.csv", "CSV (*.csv)")
        if not ruta:
            return
        ruta = Path(ruta)
        try:
            with open(ruta, "w", newline="", encoding="utf-8") as archivo:
                escritor = csv.writer(archivo)
                escritor.writerow(["corrida", "semilla", "f_mejor", "error", "generacion_mejor",
                                   "generaciones", "tiempo_s", "motivo", "x_mejor"])
                for r, res in enumerate(self.resultados):
                    escritor.writerow([r + 1, self.cfg.semilla + r, res.mejor_f, res.error,
                                       res.generacion_mejor, res.generaciones, res.tiempo,
                                       res.motivo, " ".join(map(str, res.mejor_x))])
            historia = ruta.with_name(ruta.stem + "_historia.csv")
            with open(historia, "w", newline="", encoding="utf-8") as archivo:
                escritor = csv.writer(archivo)
                escritor.writerow(["corrida", "semilla", "generacion", "mejor", "media", "peor"])
                for r, res in enumerate(self.resultados):
                    for g, fila in enumerate(zip(res.mejor, res.media, res.peor)):
                        escritor.writerow([r + 1, self.cfg.semilla + r, g, *fila])
        except OSError as error:
            QMessageBox.critical(self.v, "No se pudo guardar", str(error))
            return
        self.v.statusBar().showMessage(f"Guardados {ruta.name} y {historia.name}", 5000)

    def guardar_figuras(self):
        carpeta = QFileDialog.getExistingDirectory(self.v, "Carpeta para las figuras")
        if not carpeta:
            return
        try:
            self.v.niveles.figura.savefig(Path(carpeta) / "curvas_de_nivel.png", dpi=200)
            self.v.convergencia.figura.savefig(Path(carpeta) / "convergencia.png", dpi=200)
        except OSError as error:
            QMessageBox.critical(self.v, "No se pudo guardar", str(error))
            return
        self.v.statusBar().showMessage("Figuras guardadas", 5000)
