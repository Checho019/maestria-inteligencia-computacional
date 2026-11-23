"""Vista de la aplicación. Solo arma los controles y las gráficas, la lógica está
en el controlador (sección 9 de la guía)."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QAbstractItemView, QCheckBox, QComboBox, QFormLayout, QGridLayout, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMainWindow, QProgressBar,
    QPushButton, QScrollArea, QSplitter, QTableWidget, QVBoxLayout, QWidget,
)

from ag import cruce, mutacion, seleccion
from funciones.objetivo import FUNCIONES, PERSONALIZADA
from .graficas import GraficaConvergencia, GraficaNiveles

AYUDA = {
    "funcion": "Función objetivo. Rastrigin, Himmelblau y Peaks son las de la tarea, las siguientes vienen de GEATbx y Personalizada permite escribir una. Al elegirla se cargan su tipo, su dominio y su óptimo conocido.",
    "n": "Número de variables, libre en Rastrigin, Esfera, Rosenbrock, Ackley, Griewank, Schwefel y la personalizada (2 para ver las curvas de nivel, 10 en el experimento E1).",
    "expresion": "Expresión de x1, ..., xn (x e y valen por x1 y x2). Admite + − * / ** ^, números y sin, cos, tan, exp, log, log10, sqrt, abs, tanh, arctan, pi y e. Ejemplo: x1**2 + 10*sin(x2).",
    "tipo_personalizada": "Si la función personalizada se minimiza o se maximiza.",
    "a": "Límite inferior del dominio, igual para todas las variables.",
    "b": "Límite superior del dominio, igual para todas las variables.",
    "optimo_personalizada": "Valor óptimo si se conoce. Sin él no se calcula el error ni se puede usar la parada por error.",
    "modo_L": "Fijar L directamente o calcularlo a partir de la precisión ε con L = ⌈log2((b − a)/ε + 1)⌉.",
    "L": "Bits por variable. Con L pequeño el AG no puede acercarse al óptimo más que la resolución, con L grande el cromosoma crece y la búsqueda es más lenta.",
    "eps": "Precisión deseada ε. La resolución de la codificación es (b − a)/(2^L − 1).",
    "N": "Tamaño de la población. Más individuos dan más diversidad y exploración, pero más evaluaciones por generación.",
    "T": "Generaciones máximas. Es el criterio de parada que siempre está activo.",
    "pc": "Probabilidad de cruce Pc entre 0 y 1. Si no se cruza, los hijos son copias de los padres.",
    "elites": "Número de élites e. Los e mejores pasan intactos a la siguiente generación, así la mejor aptitud nunca empeora. Demasiados reducen la diversidad.",
    "semilla": "Semilla del generador aleatorio. Con la misma semilla y configuración se obtiene exactamente el mismo resultado.",
    "seleccion": "Ruleta (proporcional a la aptitud), torneo (gana el mejor de k) o ranking lineal (según el rango).",
    "k": "Tamaño del torneo k entre 2 y 10. Con k = 2 la presión selectiva es suave y con k = 7 es fuerte.",
    "s": "Presión selectiva s entre 1.0 y 2.0. Con s = 1 todos tienen la misma probabilidad y con s = 2 el peor tiene probabilidad cero.",
    "cruce": "Un punto (menos disruptivo, con sesgo posicional), dos puntos (trata el cromosoma como un anillo) o uniforme (el más disruptivo).",
    "p0": "Probabilidad de intercambio p0 del cruce uniforme, entre 0.1 y 0.9.",
    "mutacion": "Bit-flip (cada bit con probabilidad Pm), un bit (un solo bit con probabilidad Pmi) o inversión de segmento (invierte el orden de un tramo con probabilidad Pmi).",
    "pm_auto": "Usar el valor de referencia Pm = 1/ℓ, en promedio un bit mutado por cromosoma.",
    "pm": "Probabilidad de mutación por bit Pm entre 0 y 1. Si es muy alta el AG se vuelve búsqueda aleatoria.",
    "pmi": "Probabilidad de mutación por individuo Pmi entre 0 y 1. Más alta modifica más cromosomas por generación.",
    "parar_error": "Detener cuando |f(x*) − f óptimo| sea menor que la tolerancia ε.",
    "tolerancia": "Tolerancia del error respecto al óptimo conocido.",
    "parar_estancamiento": "Detener cuando la mejor aptitud no mejore en G generaciones seguidas.",
    "G": "Generaciones seguidas sin mejora antes de detener.",
    "ejecuciones": "Número de ejecuciones. Cada una usa la semilla siguiente (semilla, semilla + 1, ...).",
    "pausa": "Pausa entre generaciones para seguir la animación. No cuenta en el tiempo de ejecución.",
    "escala_log": "Curva de convergencia en escala logarítmica, útil cerca de un óptimo en 0. Solo para las funciones que no toman valores negativos y tienen mínimo 0.",
}


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Algoritmo genético binario")
        self.resize(1400, 860)

        self.panel = QWidget()
        izquierda = QVBoxLayout(self.panel)
        # Grupos que se bloquean mientras el AG se ejecuta
        self.grupos_configuracion = [
            self._grupo_problema(), self._grupo_codificacion(), self._grupo_parametros(),
            self._grupo_operadores(), self._grupo_parada()]
        for grupo in self.grupos_configuracion:
            izquierda.addWidget(grupo)
        izquierda.addWidget(self._grupo_ejecucion())
        izquierda.addStretch()
        desplazable = QScrollArea()
        desplazable.setWidget(self.panel)
        desplazable.setWidgetResizable(True)
        desplazable.setMinimumWidth(400)
        desplazable.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        derecha = QWidget()
        columna = QVBoxLayout(derecha)
        fila = QHBoxLayout()
        self.etiqueta_progreso = QLabel("Listo para ejecutar")
        self.progreso = QProgressBar()
        self.escala_log = QCheckBox("Eje y logarítmico")
        self.escala_log.setToolTip(AYUDA["escala_log"])
        fila.addWidget(self.etiqueta_progreso)
        fila.addWidget(self.progreso, 1)
        fila.addWidget(self.escala_log)
        columna.addLayout(fila)
        graficas = QHBoxLayout()
        self.niveles = GraficaNiveles()
        self.convergencia = GraficaConvergencia()
        graficas.addWidget(self.niveles)
        graficas.addWidget(self.convergencia)
        columna.addLayout(graficas, 3)
        columna.addWidget(self._grupo_resultados(), 2)

        divisor = QSplitter()
        divisor.addWidget(desplazable)
        divisor.addWidget(derecha)
        divisor.setSizes([410, 990])
        self.setCentralWidget(divisor)
        self.statusBar()

    def _campo(self, clave, texto):
        campo = QLineEdit(texto)
        campo.setToolTip(AYUDA[clave])
        campo.setMaximumWidth(110)
        return campo

    def _combo(self, clave, opciones):
        combo = QComboBox()
        combo.addItems(opciones)
        combo.setToolTip(AYUDA[clave])
        return combo

    def _grupo_problema(self):
        grupo, forma = QGroupBox("Problema"), QFormLayout()
        self.funcion = self._combo("funcion", list(FUNCIONES) + [PERSONALIZADA])
        self.funcion.insertSeparator(3)     # las tres de la tarea van primero
        self.funcion.insertSeparator(len(FUNCIONES) + 1)
        self.tipo = QLabel()
        self.n = self._campo("n", "2")
        self.dominio = QLabel()
        self.optimo = QLabel()
        self.optimo.setWordWrap(True)
        # Campos de la función personalizada
        self.expresion = QLineEdit("x1**2 + x2**2")
        self.expresion.setToolTip(AYUDA["expresion"])
        self.tipo_personalizada = self._combo("tipo_personalizada", ["Minimizar", "Maximizar"])
        self.a = self._campo("a", "-5")
        self.b = self._campo("b", "5")
        self.optimo_personalizada = self._campo("optimo_personalizada", "")
        self.optimo_personalizada.setPlaceholderText("desconocido")
        forma.addRow("Función", self.funcion)
        forma.addRow("f(x1, ..., xn) =", self.expresion)
        forma.addRow("Tipo", self.tipo)
        forma.addRow("Tipo de problema", self.tipo_personalizada)
        forma.addRow("Variables n", self.n)
        forma.addRow("Dominio", self.dominio)
        forma.addRow("Límite inferior a", self.a)
        forma.addRow("Límite superior b", self.b)
        forma.addRow("Óptimo", self.optimo)
        forma.addRow("Valor óptimo (opcional)", self.optimo_personalizada)
        self.forma_problema = forma
        grupo.setLayout(forma)
        return grupo

    def _grupo_codificacion(self):
        grupo, forma = QGroupBox("Codificación binaria"), QFormLayout()
        self.modo_L = self._combo("modo_L", ["Bits por variable", "Precisión ε"])
        self.L = self._campo("L", "16")
        self.eps = self._campo("eps", "0.0001")
        self.L_calculado = QLabel()
        self.longitud = QLabel()
        forma.addRow("Definir L por", self.modo_L)
        forma.addRow("Bits por variable L", self.L)
        forma.addRow("Precisión ε", self.eps)
        forma.addRow("L resultante", self.L_calculado)
        forma.addRow("Longitud ℓ = n·L", self.longitud)
        self.forma_codificacion = forma
        grupo.setLayout(forma)
        return grupo

    def _grupo_parametros(self):
        grupo, forma = QGroupBox("Parámetros generales"), QFormLayout()
        self.N = self._campo("N", "50")
        self.T = self._campo("T", "200")
        self.pc = self._campo("pc", "0.8")
        self.elites = self._campo("elites", "1")
        self.semilla = self._campo("semilla", "1")
        forma.addRow("Población N", self.N)
        forma.addRow("Generaciones T", self.T)
        forma.addRow("Probabilidad de cruce Pc", self.pc)
        forma.addRow("Élites e", self.elites)
        forma.addRow("Semilla", self.semilla)
        grupo.setLayout(forma)
        return grupo

    def _grupo_operadores(self):
        grupo, forma = QGroupBox("Operadores"), QFormLayout()
        self.seleccion = self._combo("seleccion", list(seleccion.METODOS))
        self.seleccion.setCurrentText("Torneo")
        self.k = self._campo("k", "3")
        self.s = self._campo("s", "1.5")
        self.cruce = self._combo("cruce", list(cruce.METODOS))
        self.cruce.setCurrentText("Dos puntos")
        self.p0 = self._campo("p0", "0.5")
        self.mutacion = self._combo("mutacion", list(mutacion.METODOS))
        self.pm_auto = QCheckBox("Pm = 1/ℓ")
        self.pm_auto.setChecked(True)
        self.pm_auto.setToolTip(AYUDA["pm_auto"])
        self.pm = self._campo("pm", "0.03125")
        self.pmi = self._campo("pmi", "0.2")
        forma.addRow("Selección", self.seleccion)
        forma.addRow("    Tamaño del torneo k", self.k)
        forma.addRow("    Presión selectiva s", self.s)
        forma.addRow("Cruce", self.cruce)
        forma.addRow("    Intercambio p0", self.p0)
        forma.addRow("Mutación", self.mutacion)
        forma.addRow("", self.pm_auto)
        forma.addRow("    Pm por bit", self.pm)
        forma.addRow("    Pmi por individuo", self.pmi)
        self.forma_operadores = forma
        grupo.setLayout(forma)
        return grupo

    def _grupo_parada(self):
        grupo, forma = QGroupBox("Criterios de parada"), QFormLayout()
        siempre = QLabel("Se alcanzan T generaciones (siempre activo)")
        siempre.setToolTip(AYUDA["T"])
        self.parar_error = QCheckBox("Error al óptimo menor que")
        self.parar_error.setChecked(True)
        self.parar_error.setToolTip(AYUDA["parar_error"])
        self.tolerancia = self._campo("tolerancia", "0.001")
        self.parar_estancamiento = QCheckBox("Sin mejora en G generaciones")
        self.parar_estancamiento.setToolTip(AYUDA["parar_estancamiento"])
        self.G = self._campo("G", "30")
        forma.addRow(siempre)
        forma.addRow(self.parar_error, self.tolerancia)
        forma.addRow(self.parar_estancamiento, self.G)
        grupo.setLayout(forma)
        return grupo

    def _grupo_ejecucion(self):
        grupo, forma = QGroupBox("Ejecución"), QFormLayout()
        self.ejecuciones = self._campo("ejecuciones", "1")
        self.pausa = self._campo("pausa", "20")
        self.iniciar = QPushButton("Iniciar")
        self.detener = QPushButton("Detener")
        self.detener.setEnabled(False)
        botones = QHBoxLayout()
        botones.addWidget(self.iniciar)
        botones.addWidget(self.detener)
        forma.addRow("Número de ejecuciones", self.ejecuciones)
        forma.addRow("Pausa por generación (ms)", self.pausa)
        forma.addRow(botones)
        grupo.setLayout(forma)
        return grupo

    def _grupo_resultados(self):
        grupo = QGroupBox("Resultados")
        rejilla = QGridLayout(grupo)
        mono = QFont("Consolas", 9)
        self.resultados = {}
        nombres = ["Mejor cromosoma", "x*", "f(x*)", "Error al óptimo",
                   "Generación del mejor", "Generaciones ejecutadas", "Tiempo",
                   "Motivo de parada"]
        for i, nombre in enumerate(nombres):
            etiqueta = QLabel("—")
            etiqueta.setTextInteractionFlags(Qt.TextSelectableByMouse)
            etiqueta.setWordWrap(True)
            if nombre in ("Mejor cromosoma", "x*"):
                etiqueta.setFont(mono)
            rejilla.addWidget(QLabel(f"<b>{nombre}</b>"), i, 0, Qt.AlignTop)
            rejilla.addWidget(etiqueta, i, 1)
            self.resultados[nombre] = etiqueta
        rejilla.setColumnStretch(1, 1)

        self.tabla = QTableWidget(0, 5)
        self.tabla.setHorizontalHeaderLabels(["Semilla", "f(x*)", "Error", "Gen. mejor", "Tiempo (ms)"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.resumen = QLabel("Con varias ejecuciones aquí aparecen la media y la desviación estándar del mejor valor final.")
        self.resumen.setWordWrap(True)
        self.exportar_csv = QPushButton("Exportar CSV")
        self.guardar_figuras = QPushButton("Guardar figuras")
        botones = QHBoxLayout()
        botones.addWidget(self.exportar_csv)
        botones.addWidget(self.guardar_figuras)
        botones.addStretch()
        lado = QVBoxLayout()
        lado.addWidget(self.tabla)
        lado.addWidget(self.resumen)
        lado.addLayout(botones)
        rejilla.addLayout(lado, 0, 2, len(nombres), 1)
        rejilla.setColumnStretch(2, 1)
        return grupo
