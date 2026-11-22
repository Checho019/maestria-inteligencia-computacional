"""Codificación binaria de las variables (sección 2.4 de la guía).

Cada variable x_j en [a_j, b_j] ocupa L bits, con el bit más significativo a la
izquierda. El cromosoma concatena los n segmentos y mide l = n*L bits. La
población es una matriz de N filas por l columnas con valores 0 y 1.
"""

import math

import numpy as np


def bits_por_precision(a, b, epsilon):
    """Bits necesarios para resolver [a, b] con precisión epsilon.

    L = ceil(log2((b - a) / epsilon + 1)). Con [-5.12, 5.12] y 0.01 da 11.
    """
    return math.ceil(math.log2((b - a) / epsilon + 1))


def resolucion(a, b, L):
    """Distancia entre dos valores representables consecutivos, (b - a) / (2^L - 1)."""
    return (b - a) / (2**L - 1)


def poblacion_inicial(rng, N, longitud):
    """N cromosomas de `longitud` bits, cada bit 1 con probabilidad 0.5."""
    return rng.integers(0, 2, size=(N, longitud), dtype=np.uint8)


def decodificar(poblacion, inferior, superior, L):
    """Convierte cada cromosoma en sus n variables reales.

    D_j = sum_k s_k 2^k (k contado desde la derecha) y
    x_j = a_j + (b_j - a_j) D_j / (2^L - 1).
    Como D_j nunca sale de [0, 2^L - 1], x_j siempre queda dentro de sus límites.
    """
    inferior = np.asarray(inferior, dtype=float)
    superior = np.asarray(superior, dtype=float)
    N = poblacion.shape[0]
    n = inferior.size
    pesos = 2.0 ** np.arange(L - 1, -1, -1)
    D = poblacion.reshape(N, n, L) @ pesos
    return inferior + (superior - inferior) * D / (2**L - 1)


def cadena(cromosoma, L=None):
    """Cromosoma como texto de bits, con un espacio entre variables si se da L."""
    bits = "".join(str(int(b)) for b in cromosoma)
    if not L:
        return bits
    return " ".join(bits[i:i + L] for i in range(0, len(bits), L))
