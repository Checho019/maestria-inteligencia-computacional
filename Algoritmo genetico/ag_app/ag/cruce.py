"""Operadores de cruce sobre bits (sección 4 de la guía).

Cada operador recibe dos matrices de padres P1 y P2 (una pareja por fila) y
devuelve los dos hijos de cada pareja. Los cortes se hacen sobre el cromosoma
completo de l = n*L bits, sin mirar dónde termina cada variable. La decisión de
cruzar o copiar con probabilidad Pc la toma el motor.
"""

import numpy as np


def un_punto(rng, P1, P2):
    """Corte c entre 1 y l - 1. El hijo 1 toma los bits de P1 hasta c y los de P2
    después, y el hijo 2 al revés."""
    m, l = P1.shape
    c = rng.integers(1, l, size=m)
    de_p1 = np.arange(l) < c[:, None]
    return np.where(de_p1, P1, P2), np.where(de_p1, P2, P1)


def dos_puntos(rng, P1, P2):
    """Dos cortes c1 < c2 entre 1 y l - 1. Los hijos intercambian el segmento central."""
    m, l = P1.shape
    cortes = np.sort(rng.random((m, l - 1)).argsort(axis=1)[:, :2] + 1, axis=1)
    posicion = np.arange(l)
    central = (posicion >= cortes[:, :1]) & (posicion < cortes[:, 1:])
    return np.where(central, P2, P1), np.where(central, P1, P2)


def uniforme(rng, P1, P2, p0=0.5):
    """Máscara de l bits, cada uno 1 con probabilidad p0. Donde vale 1 el hijo 1
    copia a P1 y el hijo 2 a P2, y donde vale 0 al revés (Syswerda, 1989)."""
    mascara = rng.random(P1.shape) < p0
    return np.where(mascara, P1, P2), np.where(mascara, P2, P1)


METODOS = {
    "Un punto": un_punto,
    "Dos puntos": dos_puntos,
    "Uniforme": uniforme,
}
