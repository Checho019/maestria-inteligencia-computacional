"""Funciones objetivo de prueba (sección 7 de la guía).

Cada función recibe una matriz X de N filas por n variables y devuelve los N
valores de f. Al elegir una función, la interfaz carga su tipo, su dominio y su
óptimo desde este registro.
"""

from dataclasses import dataclass

import numpy as np


def rastrigin(X):
    """f(x) = 10 n + sum_i [x_i^2 - 10 cos(2 pi x_i)]."""
    n = X.shape[1]
    return 10 * n + np.sum(X**2 - 10 * np.cos(2 * np.pi * X), axis=1)


def himmelblau(X):
    """f(x, y) = (x^2 + y - 11)^2 + (x + y^2 - 7)^2."""
    x, y = X[:, 0], X[:, 1]
    return (x**2 + y - 11) ** 2 + (x + y**2 - 7) ** 2


def peaks(X):
    """La función peaks de MATLAB."""
    x, y = X[:, 0], X[:, 1]
    return (3 * (1 - x) ** 2 * np.exp(-x**2 - (y + 1) ** 2)
            - 10 * (x / 5 - x**3 - y**5) * np.exp(-x**2 - y**2)
            - np.exp(-(x + 1) ** 2 - y**2) / 3)


@dataclass(frozen=True)
class FuncionObjetivo:
    nombre: str
    f: callable
    maximizar: bool
    dominio: tuple          # (a, b), igual para todas las variables
    n_fijo: int | None      # None si el número de variables es libre
    f_optimo: float
    x_optimos: tuple        # puntos óptimos en 2 variables, para dibujarlos

    @property
    def tipo(self):
        return "Maximizar" if self.maximizar else "Minimizar"

    def x_optimo_texto(self, n):
        if self.nombre == "Rastrigin":
            return f"x = (0, ..., 0) con {n} variables"
        return " o ".join(f"({x:g}, {y:g})" for x, y in self.x_optimos)


# Los óptimos de Himmelblau y Peaks se refinaron con Nelder-Mead de SciPy.
# El de Peaks, 8.10621358944234 en (-0.00931758, 1.58136796), coincide con el
# 8.1062 en (-0.0093, 1.5814) de la guía.
FUNCIONES = {
    "Rastrigin": FuncionObjetivo(
        "Rastrigin", rastrigin, False, (-5.12, 5.12), None, 0.0, ((0.0, 0.0),)),
    "Himmelblau": FuncionObjetivo(
        "Himmelblau", himmelblau, False, (-5.0, 5.0), 2, 0.0,
        ((3.0, 2.0), (-2.805118, 3.131312), (-3.779310, -3.283186), (3.584428, -1.848126))),
    "Peaks": FuncionObjetivo(
        "Peaks", peaks, True, (-3.0, 3.0), 2, 8.10621358944234,
        ((-0.00931758, 1.58136796),)),
}
