"""Controlador. Conecta la vista con el motor: mantiene el panel al día, lanza el
AG en un hilo y pasa cada generación a las gráficas (sección 9 de la guía)."""

import time
from pathlib import Path

from PySide6.QtCore import QObject, QTimer
from PySide6.QtWidgets import QFileDialog, QMessageBox

from ag import Configuracion, Estado
from funciones.objetivo import FUNCIONES, PERSONALIZADA
from . import formulario, resultados
from .hilo import HiloAG


def _estado_final(res):
    """Estado con la historia completa de un resultado, para redibujar la convergencia."""
    return Estado(res.generaciones, None, None, res.mejor, res.media, res.peor, res.mejor_x, res.mejor_f)


class Controlador(QObject):
    def __init__(self, ventana):
        super().__init__()
        self.v = ventana
        self.hilo = None
        self.resultados = []
        self.cfg = None
        self._vista_niveles = None
        self._ultima_convergencia = 0.0
        self.temporizador = QTimer(self)        # refresco de las gráficas en marcha
        self.temporizador.setInterval(50)
        self.temporizador.timeout.connect(self._refrescar)
        self.espera_vista = QTimer(self)        # redibujo del fondo tras la última tecla
        self.espera_vista.setSingleShot(True)
        self.espera_vista.setInterval(300)
        self.espera_vista.timeout.connect(self._redibujar_niveles)

        v = ventana
        v.funcion.currentTextChanged.connect(self._cambiar_funcion)
        for campo in (v.n, v.L, v.eps, v.expresion, v.a, v.b, v.optimo_personalizada):
            campo.textChanged.connect(self._actualizar_panel)
        for combo in (v.tipo_personalizada, v.modo_L):
            combo.currentTextChanged.connect(self._actualizar_panel)
        v.pm_auto.toggled.connect(self._actualizar_panel)
        for combo in (v.seleccion, v.cruce, v.mutacion):
            combo.currentTextChanged.connect(self._mostrar_parametros)
        v.escala_log.toggled.connect(self._preparar_convergencia)
        v.parar_error.toggled.connect(v.tolerancia.setEnabled)
        v.parar_estancamiento.toggled.connect(v.G.setEnabled)
        v.G.setEnabled(False)
        v.iniciar.clicked.connect(self.iniciar)
        v.pausar.toggled.connect(self.pausar)
        v.detener.clicked.connect(self.detener)
        v.exportar_csv.clicked.connect(self.exportar_csv)
        v.guardar_figuras.clicked.connect(self.guardar_figuras)
        v.al_cerrar = self.cerrar

        self._cambiar_funcion(v.funcion.currentText())
        self._mostrar_parametros()

    # ----- Panel de parámetros -----

    def _cambiar_funcion(self, nombre):
        v, forma = self.v, self.v.forma_problema
        propia = nombre == PERSONALIZADA
        for widget in (v.expresion, v.tipo_personalizada, v.a, v.b, v.optimo_personalizada):
            forma.setRowVisible(widget, propia)
        for widget in (v.tipo, v.dominio):
            forma.setRowVisible(widget, not propia)
        if propia:
            v.n.setEnabled(True)
        else:
            obj = FUNCIONES[nombre]
            a, b = obj.dominio
            v.tipo.setText(obj.tipo)
            v.dominio.setText(f"[{a:g}, {b:g}] en cada variable")
            v.n.setEnabled(obj.n_fijo is None)
            if obj.n_fijo is not None:
                v.n.setText(str(obj.n_fijo))
        if self.cfg is not None and self.cfg.funcion != nombre:
            self._limpiar_resultados()
        self._actualizar_panel()

    def _actualizar_panel(self, *_):
        """Óptimo, L, longitud y Pm según la función y los campos de codificación."""
        v = self.v
        obj, mensaje = formulario.objetivo_elegido(v)
        n = formulario.n_elegido(v)
        por_bits = v.modo_L.currentText() == "Bits por variable"
        v.forma_codificacion.setRowVisible(v.L, por_bits)
        v.forma_codificacion.setRowVisible(v.eps, not por_bits)
        v.forma_codificacion.setRowVisible(v.L_calculado, not por_bits)
        v.pm.setEnabled(not v.pm_auto.isChecked())
        if obj is None:
            v.optimo.setText(f"<span style='color:#c0392b'>{mensaje}</span>")
            v.L_calculado.setText("—")
            v.longitud.setText("—")
            return
        valor = obj.valor_optimo(n or 2)
        if valor is None:
            v.optimo.setText("desconocido")
        elif obj.x_optimos:
            v.optimo.setText(f"f = {valor:g} en {obj.x_optimo_texto(n or 2)}")
        else:
            v.optimo.setText(f"f = {valor:g} (ubicación desconocida)")
        # Sin óptimo conocido no hay error que medir
        v.parar_error.setEnabled(valor is not None)
        if valor is None:
            v.parar_error.setChecked(False)
        v.escala_log.setEnabled(obj.permite_log)
        if not obj.permite_log:
            v.escala_log.setChecked(False)
        L = formulario.bits_elegidos(v, obj)
        if n and L and L > 0:
            a, b = obj.dominio
            v.L_calculado.setText(f"{L} bits, resolución {(b - a) / (2**L - 1):.2e}")
            v.longitud.setText(f"{n * L} bits")
            if v.pm_auto.isChecked():
                v.pm.setText(f"{1 / (n * L):.5g}")
        else:
            v.L_calculado.setText("—")
            v.longitud.setText("—")
        self.espera_vista.start()

    def _mostrar_parametros(self, *_):
        """Cada operador muestra solo sus parámetros."""
        v, forma = self.v, self.v.forma_operadores
        bit_flip = v.mutacion.currentText() == "Bit-flip por bit"
        forma.setRowVisible(v.k, v.seleccion.currentText() == "Torneo")
        forma.setRowVisible(v.s, v.seleccion.currentText() == "Ranking lineal")
        forma.setRowVisible(v.p0, v.cruce.currentText() == "Uniforme")
        forma.setRowVisible(v.pm_auto, bit_flip)
        forma.setRowVisible(v.pm, bit_flip)
        forma.setRowVisible(v.pmi, not bit_flip)

    @staticmethod
    def _vista(obj, n):
        """Lo que define el fondo de las curvas de nivel."""
        n = n if n and 2 <= n <= 50 else 2
        return (obj.nombre, obj.expresion, obj.dominio, obj.maximizar, obj.f_optimo, n)

    def _redibujar_niveles(self):
        """Redibuja el fondo si cambiaron la función, su definición o n."""
        if self.hilo is not None and self.hilo.isRunning():
            return
        obj, _ = formulario.objetivo_elegido(self.v)
        if obj is None:
            return
        vista = self._vista(obj, formulario.n_elegido(self.v))
        if vista == self._vista_niveles:
            return
        if self._vista_niveles is not None and self.resultados:
            self._limpiar_resultados()          # ya no corresponden a lo que se ve
        self._vista_niveles = vista
        self.v.niveles.preparar(obj, vista[-1])
        self._preparar_convergencia()

    def _preparar_convergencia(self, *_):
        """Prepara la convergencia y, si hay una ejecución de esta función, la redibuja."""
        v = self.v
        vigente = self.cfg is not None and self.cfg.funcion == v.funcion.currentText()
        if vigente:
            obj, n, T, tolerancia = self.cfg.objetivo, self.cfg.n_variables, self.cfg.T, self.cfg.tolerancia
        else:
            obj, _ = formulario.objetivo_elegido(v)
            if obj is None:
                return
            n, T, tolerancia = formulario.n_elegido(v) or 2, Configuracion.T, Configuracion.tolerancia
        v.convergencia.preparar(obj, T, v.escala_log.isChecked() and obj.permite_log,
                                tolerancia, obj.valor_optimo(n))
        if vigente and self.resultados and self.hilo is None:
            v.convergencia.actualizar(_estado_final(self.resultados[-1]))

    def _limpiar_resultados(self):
        self.cfg, self.resultados = None, []
        resultados.limpiar(self.v)
        self.v.progreso.setValue(0)
        self.v.etiqueta_progreso.setText("Listo para ejecutar")

    # ----- Ejecución -----

    def iniciar(self):
        (cfg, ejecuciones, pausa), errores = formulario.leer(self.v)
        if errores:
            QMessageBox.warning(self.v, "Revise los parámetros", "\n".join(errores))
            return
        v = self.v
        self.cfg, self.resultados, self.ejecuciones = cfg, [], ejecuciones
        # El fondo queda fijado por esta ejecución, así el redibujo diferido no borra sus resultados
        self.espera_vista.stop()
        self._vista_niveles = self._vista(cfg.objetivo, cfg.n_variables)
        v.niveles.preparar(cfg.objetivo, cfg.n_variables)
        self._preparar_convergencia()
        resultados.limpiar(v)
        v.progreso.setRange(0, cfg.T)
        v.progreso.setValue(0)
        self._bloquear(True)
        self.hilo = HiloAG(cfg, ejecuciones, pausa)
        self.hilo.ejecucion_terminada.connect(self._ejecucion_terminada)
        self.hilo.fallo.connect(self._fallo)
        self.hilo.finished.connect(self._terminado)
        self.hilo.start()
        self.temporizador.start()
        v.statusBar().showMessage(f"Ejecutando {cfg.funcion} con {cfg.seleccion}, {cfg.cruce} y {cfg.mutacion}")

    def _bloquear(self, ejecutando):
        """En marcha solo quedan activos Pausar y Detener."""
        v = self.v
        for widget in v.grupos_configuracion + [v.ejecuciones, v.pausa, v.iniciar, v.escala_log,
                                                v.exportar_csv, v.guardar_figuras]:
            widget.setEnabled(not ejecutando)
        v.detener.setEnabled(ejecutando)
        v.pausar.setEnabled(ejecutando)
        if not ejecutando:
            v.pausar.setChecked(False)
            self._actualizar_panel()            # reaplica lo que depende de la función

    def pausar(self, en_pausa):
        self.v.pausar.setText("Reanudar" if en_pausa else "Pausar")
        if self.hilo is not None:
            self.hilo.pausar(en_pausa)
            self.v.statusBar().showMessage("En pausa" if en_pausa else "Ejecutando")

    def detener(self):
        if self.hilo is not None:
            self.hilo.pedir_detener()

    def cerrar(self):
        """Detiene una ejecución en curso al cerrar la ventana y espera al hilo."""
        if self.hilo is not None:
            self.hilo.pedir_detener()
            self.hilo.wait(5000)
        self.temporizador.stop()

    def _refrescar(self, forzar=False):
        if self.hilo is None:
            return
        ultimo = self.hilo.tomar_ultimo()
        if ultimo is None:
            return
        ejecucion, estado = ultimo
        v = self.v
        v.niveles.actualizar(estado)
        # La convergencia redibuja toda la figura, se limita a cinco veces por segundo
        ahora = time.perf_counter()
        if forzar or ahora - self._ultima_convergencia > 0.2:
            v.convergencia.actualizar(estado)
            self._ultima_convergencia = ahora
        v.progreso.setValue(estado.generacion)
        v.etiqueta_progreso.setText(
            f"Ejecución {ejecucion + 1} de {self.ejecuciones} (semilla {self.cfg.semilla + ejecucion}), "
            f"generación {estado.generacion} de {self.cfg.T}")

    def _ejecucion_terminada(self, r, res):
        self._refrescar(forzar=True)
        self.resultados.append(res)
        self.v.convergencia.actualizar(_estado_final(res))
        resultados.mostrar(self.v, self.cfg, r, res)

    def _terminado(self):
        self.temporizador.stop()
        self._refrescar()
        v = self.v
        self._bloquear(False)
        if all(r.motivo != resultados.DETENIDA for r in self.resultados):
            v.progreso.setValue(v.progreso.maximum())   # también si paró antes de T
        v.resumen.setText(resultados.resumen(self.resultados, self.cfg.tolerancia))
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
        try:
            historia = resultados.escribir_csv(Path(ruta), self.resultados, self.cfg.semilla)
        except OSError as error:
            QMessageBox.critical(self.v, "No se pudo guardar", str(error))
            return
        self.v.statusBar().showMessage(f"Guardados {Path(ruta).name} y {historia.name}", 5000)

    def guardar_figuras(self):
        carpeta = QFileDialog.getExistingDirectory(self.v, "Carpeta para las figuras")
        if not carpeta:
            return
        try:
            self.v.niveles.guardar(Path(carpeta) / "curvas_de_nivel.png")
            self.v.convergencia.figura.savefig(Path(carpeta) / "convergencia.png", dpi=200)
        except OSError as error:
            QMessageBox.critical(self.v, "No se pudo guardar", str(error))
            return
        self.v.statusBar().showMessage("Figuras guardadas", 5000)
