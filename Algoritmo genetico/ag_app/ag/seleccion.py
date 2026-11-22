"""Operadores de selección (sección 3 de la guía).

Todos reciben la aptitud F de la población (mayor es mejor, F = f al maximizar y
F = -f al minimizar) y devuelven los índices de los m padres elegidos. Los padres
se copian después como cadenas de bits completas.
"""

import numpy as np

EPSILON_RULETA = 1e-6


def _muestrear(rng, p, m):
    """Elige m índices con probabilidades p.

    Calcula la suma acumulada, genera r ~ U(0, 1) y toma el primer índice cuya
    suma acumulada sea mayor o igual que r.
    """
    acumulada = np.cumsum(p)
    acumulada[-1] = 1.0
    r = rng.random(m)
    return np.searchsorted(acumulada, r, side="left")


def ruleta(rng, aptitud, m):
    """Selección proporcional, p_i = F_i / sum(F_j).

    Antes se desplaza la aptitud para que sea positiva, F_i - F_min + epsilon,
    que equivale a f_i - f_min + epsilon al maximizar y a f_max - f_i + epsilon
    al minimizar (sección 2.5).
    """
    F = aptitud - aptitud.min() + EPSILON_RULETA
    return _muestrear(rng, F / F.sum(), m)


def torneo(rng, aptitud, m, k=3):
    """Toma k individuos distintos al azar y gana el de mayor aptitud.

    Se repite una vez por cada padre. Con k = 2 la presión es suave y con k = 7
    es fuerte. No necesita aptitudes positivas.
    """
    N = aptitud.size
    participantes = rng.random((m, N)).argsort(axis=1)[:, :k]
    ganador = aptitud[participantes].argmax(axis=1)
    return participantes[np.arange(m), ganador]


def ranking_lineal(rng, aptitud, m, s=1.5):
    """Probabilidad según el rango y no según el valor de la aptitud.

    Rango r_i de 1 (peor) a N (mejor) y
    p_i = (1/N) [(2 - s) + 2 (s - 1) (r_i - 1) / (N - 1)], con 1 <= s <= 2.
    Con s = 1 todos tienen la misma probabilidad y con s = 2 el peor tiene cero.
    """
    N = aptitud.size
    rango = np.empty(N)
    rango[np.argsort(aptitud, kind="stable")] = np.arange(1, N + 1)
    p = ((2 - s) + 2 * (s - 1) * (rango - 1) / (N - 1)) / N
    return _muestrear(rng, p, m)


METODOS = {
    "Ruleta": ruleta,
    "Torneo": torneo,
    "Ranking lineal": ranking_lineal,
}
