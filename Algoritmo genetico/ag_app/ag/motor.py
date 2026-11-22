"""Ciclo generacional del AG (secciones 2.3 y 6 de la guía).

El motor no depende de la interfaz. Se ejecuta igual desde un script, y la
interfaz solo le pasa un aviso por generación y una función para detenerlo.
"""

import math
import time
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
    n, L, N = cfg.n_variables, cfg.L, cfg.N
    a, b = objetivo.dominio
    inferior, superior = np.full(n, a), np.full(n, b)
    signo = 1.0 if objetivo.maximizar else -1.0

    seleccionar = seleccion.METODOS[cfg.seleccion]
    param_sel = {"Torneo": {"k": cfg.k}, "Ranking lineal": {"s": cfg.s}}.get(cfg.seleccion, {})
    cruzar = cruce.METODOS[cfg.cruce]
    param_cruce = {"p0": cfg.p0} if cfg.cruce == "Uniforme" else {}
    mutar = mutacion.METODOS[cfg.mutacion]
    param_mut = {"pm": cfg.pm_efectiva} if cfg.mutacion == "Bit-flip por bit" else {"pmi": cfg.pmi}

    hijos_por_generacion = N - cfg.elites
    parejas = math.ceil(hijos_por_generacion / 2)

    inicio = time.perf_counter()
    tiempo_dibujo = 0.0
    mejor, media, peor = [], [], []

    P = poblacion_inicial(rng, N, cfg.longitud)
    generacion = 0
    motivo = f"Se alcanzaron las {cfg.T} generaciones"
    while True:
        X = decodificar(P, inferior, superior, L)
        f = objetivo.f(X)
        aptitud = signo * f

        # Registro de la generación, en la escala original de f
        i_mejor = aptitud.argmax()
        mejor.append(f[i_mejor])
        media.append(f.mean())
        peor.append(f[aptitud.argmin()])
        if generacion == 0 or signo * f[i_mejor] > signo * mejor_f:
            mejor_f, mejor_x = f[i_mejor], X[i_mejor].copy()
            mejor_cromosoma, generacion_mejor = P[i_mejor].copy(), generacion
        error = abs(mejor_f - objetivo.f_optimo)

        if al_generar is not None:
            t = time.perf_counter()
            al_generar(Estado(generacion, X, f, mejor, media, peor, mejor_x, mejor_f))
            tiempo_dibujo += time.perf_counter() - t

        # Criterios de parada, gana el primero que se cumpla
        if detener is not None and detener():
            motivo = "Detenido por el usuario"
            break
        if cfg.parar_por_error and error < cfg.tolerancia:
            motivo = f"Error menor que {cfg.tolerancia:g}"
            break
        if cfg.parar_por_estancamiento and generacion - generacion_mejor >= cfg.G:
            motivo = f"Sin mejora en {cfg.G} generaciones"
            break
        if generacion >= cfg.T:
            break

        # Elitismo, los e mejores pasan intactos
        elite = P[np.argsort(-aptitud, kind="stable")[:cfg.elites]]

        # Selección de 2 padres por pareja
        padres = seleccionar(rng, aptitud, 2 * parejas, **param_sel)
        P1, P2 = P[padres[0::2]], P[padres[1::2]]

        # Cruce con probabilidad Pc, si no los hijos son copias de los padres
        H1, H2 = cruzar(rng, P1, P2, **param_cruce)
        cruzan = (rng.random(parejas) < cfg.pc)[:, None]
        H = np.empty((2 * parejas, cfg.longitud), dtype=P.dtype)
        H[0::2] = np.where(cruzan, H1, P1)
        H[1::2] = np.where(cruzan, H2, P2)

        # Mutación de los hijos y reemplazo generacional
        H = mutar(rng, H[:hijos_por_generacion], **param_mut)
        P = np.vstack([elite, H])
        generacion += 1

    acumular = np.maximum.accumulate if objetivo.maximizar else np.minimum.accumulate
    errores_mejor = np.abs(acumular(np.array(mejor)) - objetivo.f_optimo)
    bajo_tolerancia = np.flatnonzero(errores_mejor < cfg.tolerancia)
    return Resultado(
        mejor_cromosoma=mejor_cromosoma,
        mejor_x=mejor_x,
        mejor_f=float(mejor_f),
        error=float(error),
        generacion_mejor=generacion_mejor,
        generaciones=generacion,
        tiempo=time.perf_counter() - inicio - tiempo_dibujo,
        motivo=motivo,
        generacion_tolerancia=int(bajo_tolerancia[0]) if bajo_tolerancia.size else None,
        mejor=list(map(float, mejor)),
        media=list(map(float, media)),
        peor=list(map(float, peor)),
    )
