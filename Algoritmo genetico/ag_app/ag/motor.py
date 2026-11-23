"""Ciclo generacional del AG (secciones 2.3 y 6 de la guía).

El motor no depende de la interfaz. Se ejecuta igual desde un script, y la
interfaz solo le pasa un aviso por generación y una función para detenerlo.
"""

import math
import time
from functools import partial
from dataclasses import dataclass, field

import numpy as np

from . import cruce, mutacion, seleccion
from .codificacion import decodificar, poblacion_inicial
from .configuracion import validar


@dataclass
class Estado:
    """Lo que la interfaz necesita para dibujar una generación."""
    generacion: int
    X: np.ndarray               # población decodificada
    f: np.ndarray               # f de cada individuo, en la escala original
    mejor: list                 # historia por generación
    media: list
    peor: list
    mejor_x: np.ndarray         # mejor individuo encontrado hasta ahora
    mejor_f: float
    P: np.ndarray | None = None  # población en bits


@dataclass
class Resultado:
    mejor_cromosoma: np.ndarray
    mejor_x: np.ndarray
    mejor_f: float
    error: float                # |f(x*) - f_optimo|
    generacion_mejor: int       # generación en que apareció x*
    generaciones: int           # generaciones ejecutadas
    tiempo: float               # segundos del motor, sin contar el dibujo
    motivo: str
    generacion_tolerancia: int | None   # primera generación con error < tolerancia
    mejor: list = field(default_factory=list)
    media: list = field(default_factory=list)
    peor: list = field(default_factory=list)


def ejecutar(cfg, al_generar=None, detener=None):
    """Ejecuta el AG con la configuración cfg y devuelve un Resultado.

    al_generar(estado) se llama después de evaluar cada generación, incluida la
    inicial. detener() se consulta en cada generación y, si devuelve True, la
    ejecución termina con el mejor individuo hallado hasta ese momento.
    """
    errores = validar(cfg)
    if errores:
        raise ValueError("\n".join(errores))

    rng = np.random.default_rng(cfg.semilla)
    objetivo = cfg.objetivo
    f_optimo = cfg.f_optimo             # None si no se conoce, el error queda en NaN
    a, b = objetivo.dominio
    inferior, superior = np.full(cfg.n_variables, a), np.full(cfg.n_variables, b)
    signo = 1.0 if objetivo.maximizar else -1.0
    operadores = _operadores(cfg)

    inicio = time.perf_counter()
    tiempo_dibujo = 0.0
    mejor, media, peor = [], [], []
    mejor_f = mejor_x = mejor_cromosoma = None      # mejor hallado hasta ahora
    generacion_mejor = 0
    P = poblacion_inicial(rng, cfg.N, cfg.longitud)
    generacion = 0
    while True:
        X = decodificar(P, inferior, superior, cfg.L)
        f = objetivo.f(X)
        aptitud, finitos = _aptitud(signo * f)

        # Registro en la escala original de f, solo con valores finitos
        i_mejor = aptitud.argmax()
        mejor.append(f[i_mejor])
        media.append(f[finitos].mean() if finitos.any() else np.nan)
        peor.append(f[np.where(finitos, aptitud, np.inf).argmin()] if finitos.any() else np.nan)
        if mejor_f is None or signo * f[i_mejor] > signo * mejor_f:
            mejor_f, mejor_x = f[i_mejor], X[i_mejor].copy()
            mejor_cromosoma, generacion_mejor = P[i_mejor].copy(), generacion
        error = abs(mejor_f - f_optimo) if f_optimo is not None else math.nan

        if al_generar is not None:
            t = time.perf_counter()
            al_generar(Estado(generacion, X, f, mejor, media, peor, mejor_x, mejor_f, P))
            tiempo_dibujo += time.perf_counter() - t

        motivo = _motivo_parada(cfg, generacion, generacion_mejor, error, detener)
        if motivo:
            break
        P = _nueva_generacion(rng, P, aptitud, cfg, operadores)
        generacion += 1

    return Resultado(
        mejor_cromosoma=mejor_cromosoma,
        mejor_x=mejor_x,
        mejor_f=float(mejor_f),
        error=float(error),
        generacion_mejor=generacion_mejor,
        generaciones=generacion,
        tiempo=time.perf_counter() - inicio - tiempo_dibujo,
        motivo=motivo,
        generacion_tolerancia=_generacion_tolerancia(mejor, f_optimo, objetivo.maximizar, cfg.tolerancia),
        mejor=list(map(float, mejor)),
        media=list(map(float, media)),
        peor=list(map(float, peor)),
    )


def _operadores(cfg):
    """Los tres operadores elegidos con sus parámetros ya fijados."""
    param_sel = {"Torneo": {"k": cfg.k}, "Ranking lineal": {"s": cfg.s}}.get(cfg.seleccion, {})
    param_cruce = {"p0": cfg.p0} if cfg.cruce == "Uniforme" else {}
    param_mut = {"pm": cfg.pm_efectiva} if cfg.mutacion == "Bit-flip por bit" else {"pmi": cfg.pmi}
    return (partial(seleccion.METODOS[cfg.seleccion], **param_sel),
            partial(cruce.METODOS[cfg.cruce], **param_cruce),
            partial(mutacion.METODOS[cfg.mutacion], **param_mut))


def _aptitud(aptitud):
    """Un valor inf o NaN (posible en una función personalizada) pasa a ser el peor
    individuo para que no gane la selección."""
    finitos = np.isfinite(aptitud)
    if not finitos.all():
        peor_finito = aptitud[finitos].min() if finitos.any() else 0.0
        aptitud = np.where(finitos, aptitud, peor_finito - 1.0)
    return aptitud, finitos


def _motivo_parada(cfg, generacion, generacion_mejor, error, detener):
    """Texto del criterio que detiene la ejecución, o None. Gana el primero."""
    if detener is not None and detener():
        return "Detenido por el usuario"
    if cfg.parar_por_error and error < cfg.tolerancia:
        return f"Error menor que {cfg.tolerancia:g}"
    if cfg.parar_por_estancamiento and generacion - generacion_mejor >= cfg.G:
        return f"Sin mejora en {cfg.G} generaciones"
    if generacion >= cfg.T:
        return f"Se alcanzaron las {cfg.T} generaciones"
    return None


def _nueva_generacion(rng, P, aptitud, cfg, operadores):
    """Elitismo, selección de 2 padres por pareja, cruce con probabilidad Pc,
    mutación y reemplazo generacional."""
    seleccionar, cruzar, mutar = operadores
    hijos = cfg.N - cfg.elites
    parejas = math.ceil(hijos / 2)
    elite = P[np.argsort(-aptitud, kind="stable")[:cfg.elites]]
    padres = seleccionar(rng, aptitud, 2 * parejas)
    P1, P2 = P[padres[0::2]], P[padres[1::2]]
    H1, H2 = cruzar(rng, P1, P2)
    cruzan = (rng.random(parejas) < cfg.pc)[:, None]    # si no cruzan, copian a los padres
    H = np.empty((2 * parejas, cfg.longitud), dtype=P.dtype)
    H[0::2] = np.where(cruzan, H1, P1)
    H[1::2] = np.where(cruzan, H2, P2)
    return np.vstack([elite, mutar(rng, H[:hijos])])


def _generacion_tolerancia(mejor, f_optimo, maximizar, tolerancia):
    """Primera generación en que el mejor hallado queda a menos de la tolerancia."""
    if f_optimo is None:
        return None
    acumular = np.maximum.accumulate if maximizar else np.minimum.accumulate
    bajo = np.flatnonzero(np.abs(acumular(np.array(mejor)) - f_optimo) < tolerancia)
    return int(bajo[0]) if bajo.size else None
