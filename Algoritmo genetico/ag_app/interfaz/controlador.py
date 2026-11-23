"""Controlador. Valida las entradas, lanza el motor en un hilo aparte y pasa cada
generación a las gráficas (sección 9 de la guía)."""

import csv
import math
import threading
import time
from dataclasses import replace
from pathlib import Path

import numpy as np
from PySide6.QtCore import QObject, QThread, QTimer, Signal
from PySide6.QtWidgets import QFileDialog, QMessageBox, QTableWidgetItem

from ag import Configuracion, Estado, ejecutar, validar
from ag.codificacion import bits_por_precision, cadena
from funciones import personalizada
from funciones.objetivo import FUNCIONES, PERSONALIZADA


class HiloAG(QThread):
    """Ejecuta el AG fuera del hilo de la interfaz para que la ventana no se congele."""

    ejecucion_terminada = Signal(int, object)
    fallo = Signal(str)

    def __init__(self, cfg, ejecuciones, pausa_ms):
        super().__init__()
        self.cfg, self.ejecuciones, self.pausa = cfg, ejecuciones, pausa_ms / 1000
        self._detener = False
        self._candado = threading.Lock()
        self._ultimo = None
        self._ejecucion = 0

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
            self._ultimo = (self._ejecucion, copia)
        if self.pausa:
            time.sleep(self.pausa)

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


class Controlador(QObject):
    def __init__(self, ventana):
        super().__init__()
        self.v = ventana
        self.hilo = None
        self.resultados = []
        self.cfg = None
        self._vista_niveles = None
        self.temporizador = QTimer(self)
        self.temporizador.setInterval(30)
        self.temporizador.timeout.connect(self._refrescar)
        # El fondo de las curvas de nivel se redibuja 300 ms después de la última
        # tecla, para que escribir en los campos no trabe la ventana
        self.espera_vista = QTimer(self)
        self.espera_vista.setSingleShot(True)
        self.espera_vista.setInterval(300)
        self.espera_vista.timeout.connect(self._redibujar_niveles)

        v = ventana
        v.funcion.currentTextChanged.connect(self._cambiar_funcion)
        for campo in (v.n, v.L, v.eps, v.expresion, v.a, v.b, v.optimo_personalizada):
            campo.textChanged.connect(self._actualizar_codificacion)
        v.tipo_personalizada.currentTextChanged.connect(self._actualizar_codificacion)
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
        v = self.v
        propia = nombre == PERSONALIZADA
        forma = v.forma_problema
        for widget in (v.expresion, v.tipo_personalizada, v.a, v.b, v.optimo_personalizada):
            forma.setRowVisible(widget, propia)
        for widget in (v.tipo, v.dominio):
            forma.setRowVisible(widget, not propia)
        if propia:
            v.n.setEnabled(True)
        else:
            obj = FUNCIONES[nombre]
            v.tipo.setText(obj.tipo)
            a, b = obj.dominio
            v.dominio.setText(f"[{a:g}, {b:g}] en cada variable")
            v.n.setEnabled(obj.n_fijo is None)
            if obj.n_fijo is not None:
                v.n.setText(str(obj.n_fijo))
        if self.cfg is not None and self.cfg.funcion != nombre:
            self._limpiar_resultados()
        self._actualizar_codificacion()

    def _numero_opcional(self, campo):
        texto = campo.text().strip().replace(",", ".")
        if not texto:
            return None
        valor = float(texto)
        if not math.isfinite(valor):
            raise ValueError
        return valor

    def _objetivo_actual(self):
        """Función elegida y un mensaje de error si la personalizada no es válida."""
        v = self.v
        nombre = v.funcion.currentText()
        if nombre != PERSONALIZADA:
            return FUNCIONES[nombre], ""
        try:
            a, b = float(v.a.text().replace(",", ".")), float(v.b.text().replace(",", "."))
            optimo = self._numero_opcional(v.optimo_personalizada)
            n = int(v.n.text())
            if not (math.isfinite(a) and math.isfinite(b) and a < b and 2 <= n <= 50):
                return None, "Revise el dominio (a < b) y el número de variables (2 a 50)."
            return personalizada.crear(v.expresion.text(), a, b,
                                       v.tipo_personalizada.currentText() == "Maximizar",
                                       optimo, n), ""
        except ValueError as error:
            return None, str(error) or "Revise los números del dominio y del óptimo."

    def _limpiar_resultados(self):
        """Borra los resultados de otra función para que no se lean con la nueva."""
        v = self.v
        self.cfg, self.resultados = None, []
        for etiqueta in v.resultados.values():
            etiqueta.setText("—")
        v.tabla.setRowCount(0)
        v.resumen.setText("")
        v.progreso.setValue(0)
        v.etiqueta_progreso.setText("Listo para ejecutar")

    def _preparar_convergencia(self, *_):
        """Prepara la curva de convergencia y, si ya hay una ejecución, la vuelve a dibujar."""
        v = self.v
        vigente = self.cfg is not None and self.cfg.funcion == v.funcion.currentText()
        if vigente:
            obj, n, T, tolerancia = self.cfg.objetivo, self.cfg.n_variables, self.cfg.T, self.cfg.tolerancia
        else:
            obj, _ = self._objetivo_actual()
            if obj is None:
                return
            n, T, tolerancia = self._n_actual() or 2, Configuracion.T, Configuracion.tolerancia
        logaritmica = v.escala_log.isChecked() and obj.permite_log
        v.convergencia.preparar(obj, T, logaritmica, tolerancia, obj.valor_optimo(n))
        if vigente and self.resultados and self.hilo is None:
            res = self.resultados[-1]
            v.convergencia.actualizar(Estado(res.generaciones, None, None, res.mejor,
                                             res.media, res.peor, res.mejor_x, res.mejor_f))

    def _n_actual(self):
        nombre = self.v.funcion.currentText()
        try:
            fijo = FUNCIONES[nombre].n_fijo if nombre in FUNCIONES else None
            return fijo or int(self.v.n.text())
        except ValueError:
            return None

    def _L_actual(self, obj):
        v = self.v
        try:
            if v.modo_L.currentText() == "Bits por variable":
                return int(v.L.text())
            a, b = obj.dominio
            return bits_por_precision(a, b, float(v.eps.text()))
        except (ValueError, ZeroDivisionError, OverflowError):
            return None

    def _actualizar_codificacion(self, *_):
        v = self.v
        obj, mensaje = self._objetivo_actual()
        n = self._n_actual()
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
        # Sin óptimo conocido no hay error que medir ni parada por error
        v.parar_error.setEnabled(valor is not None)
        if valor is None:
            v.parar_error.setChecked(False)
        v.escala_log.setEnabled(obj.permite_log)
        if not obj.permite_log:
            v.escala_log.setChecked(False)
        L = self._L_actual(obj)
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

    def _redibujar_niveles(self):
        """Redibuja el fondo de las curvas de nivel y la convergencia vacía si
        cambiaron la función, su definición o n."""
        if self.hilo is not None and self.hilo.isRunning():
            return
        obj, _ = self._objetivo_actual()
        n = self._n_actual()
        if obj is None:
            return
        n = n if n and 2 <= n <= 50 else 2
        vista = (obj.nombre, obj.expresion, obj.dominio, obj.maximizar, obj.f_optimo, n)
        if vista != self._vista_niveles:
            self._vista_niveles = vista
            self.v.niveles.preparar(obj, n)
            self._preparar_convergencia()

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
        """Arma la configuración desde los campos. Devuelve (cfg, ejecuciones, pausa)
        y la lista de errores con mensajes claros."""
        v, errores, ilegibles = self.v, [], []

        defecto = Configuracion()

        def numero(campo, nombre, tipo, clave=None):
            """Lee un campo. Si no es un número finito anota el error y devuelve el
            valor por defecto, para no generar errores de rango en cadena."""
            texto = campo.text().strip().replace(",", ".")
            try:
                valor = tipo(texto)
                if math.isfinite(valor):
                    return valor
            except ValueError:
                pass
            clase = "un número entero" if tipo is int else "un número finito"
            errores.append(f"{nombre} debe ser {clase} (se recibió \"{campo.text()}\").")
            ilegibles.append(nombre)
            return getattr(defecto, clave) if clave else tipo(1)

        cfg = Configuracion(
            funcion=v.funcion.currentText(),
            n=numero(v.n, "El número de variables n", int, "n"),
            N=numero(v.N, "El tamaño de población N", int, "N"),
            T=numero(v.T, "Las generaciones T", int, "T"),
            pc=numero(v.pc, "La probabilidad de cruce Pc", float, "pc"),
            elites=numero(v.elites, "El número de élites e", int, "elites"),
            semilla=numero(v.semilla, "La semilla", int, "semilla"),
            seleccion=v.seleccion.currentText(),
            k=numero(v.k, "El tamaño del torneo k", int, "k"),
            s=numero(v.s, "La presión selectiva s", float, "s"),
            cruce=v.cruce.currentText(),
            p0=numero(v.p0, "La probabilidad de intercambio p0", float, "p0"),
            mutacion=v.mutacion.currentText(),
            pm=None if v.pm_auto.isChecked() else numero(v.pm, "La probabilidad de mutación por bit Pm", float),
            pmi=numero(v.pmi, "La probabilidad de mutación por individuo Pmi", float, "pmi"),
            parar_por_error=v.parar_error.isChecked(),
            tolerancia=numero(v.tolerancia, "La tolerancia del error", float, "tolerancia"),
            parar_por_estancamiento=v.parar_estancamiento.isChecked(),
            G=numero(v.G, "Las generaciones sin mejora G", int, "G"),
        )
        if cfg.funcion == PERSONALIZADA:
            cfg.expresion = v.expresion.text()
            cfg.a = numero(v.a, "El límite inferior a", float, "a")
            cfg.b = numero(v.b, "El límite superior b", float, "b")
            cfg.maximizar = v.tipo_personalizada.currentText() == "Maximizar"
            cfg.optimo = (None if not v.optimo_personalizada.text().strip()
                          else numero(v.optimo_personalizada, "El valor óptimo", float))
        if v.modo_L.currentText() == "Bits por variable":
            cfg.L = numero(v.L, "Los bits por variable L", int, "L")
        else:
            eps = numero(v.eps, "La precisión ε", float)
            a, b = (cfg.a, cfg.b) if cfg.funcion == PERSONALIZADA else cfg.objetivo.dominio
            if eps <= 0:
                errores.append("La precisión ε debe ser mayor que 0.")
            elif "La precisión ε" not in ilegibles and a < b:
                cfg.L = bits_por_precision(a, b, eps)
        ejecuciones = numero(v.ejecuciones, "El número de ejecuciones", int)
        pausa = numero(v.pausa, "La pausa por generación", int)
        # Los rangos se revisan también cuando otro campo no se pudo leer, sin
        # repetir el mensaje de los campos ilegibles
        errores += [e for e in validar(cfg) if not any(e.startswith(n) for n in ilegibles)]
        if "El número de ejecuciones" not in ilegibles and not 1 <= ejecuciones <= 100:
            errores.append(f"El número de ejecuciones debe estar entre 1 y 100 (se recibió {ejecuciones}).")
        if "La pausa por generación" not in ilegibles and not 0 <= pausa <= 2000:
            errores.append(f"La pausa debe estar entre 0 y 2000 ms (se recibió {pausa}).")
        return (cfg, ejecuciones, pausa), errores

    # ----- Ejecución -----

    def iniciar(self):
        (cfg, ejecuciones, pausa), errores = self._leer()
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
        self.ejecuciones = ejecuciones
        self.hilo = HiloAG(cfg, ejecuciones, pausa)
        self.hilo.ejecucion_terminada.connect(self._ejecucion_terminada)
        self.hilo.fallo.connect(self._fallo)
        self.hilo.finished.connect(self._terminado)
        self.hilo.start()
        self.temporizador.start()
        v.statusBar().showMessage(f"Ejecutando {cfg.funcion} con {cfg.seleccion}, {cfg.cruce} y {cfg.mutacion}")

    def _bloquear(self, ejecutando):
        """Mientras el AG está en marcha solo queda activo el botón Detener."""
        v = self.v
        for widget in v.grupos_configuracion + [v.ejecuciones, v.pausa, v.iniciar, v.escala_log,
                                                v.exportar_csv, v.guardar_figuras]:
            widget.setEnabled(not ejecutando)
        v.detener.setEnabled(ejecutando)
        if not ejecutando:
            # Vuelve a aplicar lo que depende de la función (eje logarítmico, parada por error)
            self._actualizar_codificacion()

    def detener(self):
        if self.hilo is not None:
            self.hilo.pedir_detener()

    def _refrescar(self):
        if self.hilo is None:
            return
        ultimo = self.hilo.tomar_ultimo()
        if ultimo is None:
            return
        ejecucion, estado = ultimo
        v = self.v
        v.niveles.actualizar(estado)
        v.convergencia.actualizar(estado)
        v.progreso.setValue(estado.generacion)
        v.etiqueta_progreso.setText(
            f"Ejecución {ejecucion + 1} de {self.ejecuciones} (semilla {self.cfg.semilla + ejecucion}), "
            f"generación {estado.generacion} de {self.cfg.T}")

    def _ejecucion_terminada(self, r, res):
        self._refrescar()
        self.resultados.append(res)
        v, cfg = self.v, self.cfg
        v.resultados["Mejor cromosoma"].setText(cadena(res.mejor_cromosoma, cfg.L))
        v.resultados["x*"].setText("(" + ", ".join(f"{x:.6f}" for x in res.mejor_x) + ")")
        v.resultados["f(x*)"].setText(f"{res.mejor_f:.8f}")
        conocido = not math.isnan(res.error)
        v.resultados["Error al óptimo"].setText(f"{res.error:.3e}" if conocido else "— (óptimo desconocido)")
        v.resultados["Generación del mejor"].setText(str(res.generacion_mejor))
        v.resultados["Generaciones ejecutadas"].setText(str(res.generaciones))
        v.resultados["Tiempo"].setText(f"{res.tiempo * 1000:.1f} ms")
        v.resultados["Motivo de parada"].setText(res.motivo)
        fila = v.tabla.rowCount()
        v.tabla.insertRow(fila)
        valores = [cfg.semilla + r, f"{res.mejor_f:.6f}", f"{res.error:.2e}" if conocido else "—",
                   res.generacion_mejor, f"{res.tiempo * 1000:.1f}"]
        for columna, valor in enumerate(valores):
            v.tabla.setItem(fila, columna, QTableWidgetItem(str(valor)))
        v.tabla.scrollToBottom()

    def _terminado(self):
        self.temporizador.stop()
        self._refrescar()
        v = self.v
        self._bloquear(False)
        # La ejecución detenida a mitad de camino no entra en el resumen
        completas = [r for r in self.resultados if r.motivo != "Detenido por el usuario"]
        detenidas = len(self.resultados) - len(completas)
        nota = " La ejecución detenida no entra en el resumen." if detenidas else ""
        if completas:
            finales = np.array([r.mejor_f for r in completas])
            errores = np.array([r.error for r in completas])
            exito = np.mean(errores < self.cfg.tolerancia) * 100
            desviacion = finales.std(ddof=1) if finales.size > 1 else 0.0
            cuantas = "1 ejecución completa" if len(finales) == 1 else f"{len(finales)} ejecuciones completas"
            texto = (f"{cuantas}. Mejor valor final {finales.mean():.6f} ± "
                     f"{desviacion:.6f} (media ± DE)")
            if not np.isnan(errores).any():
                texto += (f", error medio {errores.mean():.2e}, éxito {exito:.0f} % "
                          f"con error menor que {self.cfg.tolerancia:g}")
            v.resumen.setText(texto + "." + nota)
        elif detenidas:
            v.resumen.setText("La ejecución se detuvo antes de terminar, no hay resumen.")
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
                escritor.writerow(["ejecucion", "semilla", "f_mejor", "error", "generacion_mejor",
                                   "generaciones", "tiempo_s", "motivo", "x_mejor"])
                for r, res in enumerate(self.resultados):
                    escritor.writerow([r + 1, self.cfg.semilla + r, res.mejor_f, res.error,
                                       res.generacion_mejor, res.generaciones, res.tiempo,
                                       res.motivo, " ".join(map(str, res.mejor_x))])
            historia = ruta.with_name(ruta.stem + "_historia.csv")
            with open(historia, "w", newline="", encoding="utf-8") as archivo:
                escritor = csv.writer(archivo)
                escritor.writerow(["ejecucion", "semilla", "generacion", "mejor", "media", "peor"])
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
