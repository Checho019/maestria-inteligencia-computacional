"""Operadores de mutación sobre bits (sección 5 de la guía).

Cada operador recibe la matriz de hijos H (un cromosoma por fila) y devuelve una
copia mutada.
"""

import numpy as np


def bit_flip(rng, H, pm):
    """Recorre cada bit y lo invierte con probabilidad Pm. La referencia es
    Pm = 1/l, en promedio un bit mutado por cromosoma."""
    return H ^ (rng.random(H.shape) < pm).astype(H.dtype)


def un_bit(rng, H, pmi=0.2):
    """Con probabilidad Pmi por individuo invierte un solo bit elegido al azar.
    Nunca muta más de un bit."""
    H = H.copy()
    m, l = H.shape
    elegidos = np.flatnonzero(rng.random(m) < pmi)
    posicion = rng.integers(0, l, size=elegidos.size)
    H[elegidos, posicion] ^= 1
    return H


def inversion_segmento(rng, H, pmi=0.2):
    """Con probabilidad Pmi por individuo elige dos posiciones i < j e invierte el
    orden de los bits entre ellas, inclusive. Conserva la cantidad de unos."""
    H = H.copy()
    m, l = H.shape
    elegidos = np.flatnonzero(rng.random(m) < pmi)
    if elegidos.size == 0:
        return H
    extremos = np.sort(rng.random((elegidos.size, l)).argsort(axis=1)[:, :2], axis=1)
    i, j = extremos[:, :1], extremos[:, 1:]
    posicion = np.arange(l)
    dentro = (posicion >= i) & (posicion <= j)
    origen = np.where(dentro, i + j - posicion, posicion)
    H[elegidos] = np.take_along_axis(H[elegidos], origen, axis=1)
    return H


METODOS = {
    "Bit-flip por bit": bit_flip,
    "Un bit": un_bit,
    "Inversión de segmento": inversion_segmento,
}
