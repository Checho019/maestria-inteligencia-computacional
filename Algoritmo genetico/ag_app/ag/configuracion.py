"""Configuración de una ejecución del AG y su validación.

Los valores por defecto son los de la tabla 6.2 de la guía, así que el AG se puede
ejecutar sin cambiar nada.
"""

import math
from dataclasses import dataclass

import numpy as np

from funciones import personalizada
from funciones.objetivo import FUNCIONES, PERSONALIZADA
from . import cruce, mutacion, seleccion


@dataclass
class Configuracion:
    funcion: str = "Rastrigin"
    n: int = 2                      # variables, se ignora en las funciones de n fijo
    L: int = 16                     # bits por variable
    N: int = 50                     # tamaño de la población
    T: int = 200                    # generaciones máximas
    pc: float = 0.8                 # probabilidad de cruce
    elites: int = 1
    semilla: int = 1
    seleccion: str = "Torneo"
    k: int = 3                      # tamaño del torneo
    s: float = 1.5                  # presión selectiva del ranking lineal
    cruce: str = "Dos puntos"
    p0: float = 0.5                 # probabilidad de intercambio del cruce uniforme
    mutacion: str = "Bit-flip por bit"
    pm: float | None = None         # por bit, None equivale a 1/l
    pmi: float = 0.2                # por individuo, un bit e inversión
    parar_por_error: bool = True
    tolerancia: float = 1e-3
    parar_por_estancamiento: bool = False
    G: int = 30                     # generaciones sin mejora
    # Solo para la función personalizada
    expresion: str = "x1**2 + x2**2"
    a: float = -5.0
    b: float = 5.0
    maximizar: bool = False
    optimo: float | None = None     # valor óptimo si se conoce

    @property
    def objetivo(self):
        """FuncionObjetivo elegida. La personalizada lanza ValueError si la
        expresión no es válida."""
        if self.funcion == PERSONALIZADA:
            return personalizada.crear(self.expresion, float(self.a), float(self.b),
                                       bool(self.maximizar), self.optimo, int(self.n))
        return FUNCIONES[self.funcion]

    @property
    def f_optimo(self):
        """Valor óptimo con las variables de esta configuración, o None."""
        return self.objetivo.valor_optimo(self.n_variables)

    @property
    def n_variables(self):
        return self.objetivo.n_fijo or self.n

    @property
    def longitud(self):
        return self.n_variables * self.L

    @property
    def pm_efectiva(self):
        return 1 / self.longitud if self.pm is None else self.pm


def verbo(nombre):
    """'deben' para los sujetos en plural ("Los bits...", "Las generaciones...")."""
    return "deben" if nombre.startswith(("Los ", "Las ")) else "debe"


def validar(cfg):
    """Devuelve la lista de errores de la configuración, vacía si es válida."""
    errores = []

    def rango(nombre, valor, minimo, maximo):
        if not (minimo <= valor <= maximo):
            errores.append(f"{nombre} {verbo(nombre)} estar entre {minimo} y {maximo} (se recibió {valor}).")

    # Enteros también al usar el motor sin la interfaz
    for nombre, valor in (("El número de variables n", cfg.n), ("Los bits por variable L", cfg.L),
                          ("El tamaño de población N", cfg.N), ("Las generaciones T", cfg.T),
                          ("El número de élites e", cfg.elites), ("La semilla", cfg.semilla),
                          ("El tamaño del torneo k", cfg.k), ("Las generaciones sin mejora G", cfg.G)):
        if isinstance(valor, bool) or not isinstance(valor, (int, np.integer)):
            errores.append(f"{nombre} {verbo(nombre)} ser un número entero (se recibió {valor}).")
    if errores:
        return errores

    if cfg.funcion not in FUNCIONES and cfg.funcion != PERSONALIZADA:
        errores.append(f"La función {cfg.funcion} no existe.")
        return errores
    if cfg.funcion == PERSONALIZADA:
        if not (math.isfinite(cfg.a) and math.isfinite(cfg.b) and cfg.a < cfg.b):
            errores.append("El dominio debe cumplir a < b con números finitos.")
            return errores
        if cfg.optimo is not None and not math.isfinite(cfg.optimo):
            errores.append("El óptimo conocido debe ser un número finito o quedar vacío.")
        if not 2 <= cfg.n <= 50:
            errores.append(f"El número de variables n debe estar entre 2 y 50 (se recibió {cfg.n}).")
            return errores
        try:
            cfg.objetivo
        except ValueError as error:
            errores.append(str(error))
            return errores
        if cfg.parar_por_error and cfg.optimo is None:
            errores.append("Sin óptimo conocido no se puede usar el criterio de error al óptimo.")
    elif cfg.objetivo.n_fijo is None:
        rango("El número de variables n", cfg.n, 2, 50)
    rango("Los bits por variable L", cfg.L, 2, 32)
    rango("El tamaño de población N", cfg.N, 2, 1000)
    rango("Las generaciones T", cfg.T, 1, 100000)
    rango("La probabilidad de cruce Pc", cfg.pc, 0.0, 1.0)
    rango("El número de élites e", cfg.elites, 0, cfg.N - 1)
    if cfg.semilla < 0:
        errores.append("La semilla debe ser un entero mayor o igual que 0.")

    if cfg.seleccion not in seleccion.METODOS:
        errores.append(f"El método de selección {cfg.seleccion} no existe.")
    elif cfg.seleccion == "Torneo":
        rango("El tamaño del torneo k", cfg.k, 2, min(10, cfg.N))
    elif cfg.seleccion == "Ranking lineal":
        rango("La presión selectiva s", cfg.s, 1.0, 2.0)

    if cfg.cruce not in cruce.METODOS:
        errores.append(f"El método de cruce {cfg.cruce} no existe.")
    elif cfg.cruce == "Uniforme":
        rango("La probabilidad de intercambio p0", cfg.p0, 0.1, 0.9)

    if cfg.mutacion not in mutacion.METODOS:
        errores.append(f"El método de mutación {cfg.mutacion} no existe.")
    elif cfg.mutacion == "Bit-flip por bit":
        if cfg.pm is not None:
            rango("La probabilidad de mutación por bit Pm", cfg.pm, 0.0, 1.0)
    else:
        rango("La probabilidad de mutación por individuo Pmi", cfg.pmi, 0.0, 1.0)

    if cfg.parar_por_error and not (math.isfinite(cfg.tolerancia) and cfg.tolerancia > 0):
        errores.append("La tolerancia del error debe ser un número mayor que 0.")
    if cfg.parar_por_estancamiento:
        rango("Las generaciones sin mejora G", cfg.G, 1, 100000)
    return errores
