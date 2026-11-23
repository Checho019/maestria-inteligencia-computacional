"""Funciones objetivo de prueba (sección 7 de la guía y GEATbx).

Cada función recibe una matriz X de N filas por n variables y devuelve los N
valores de f. Al elegir una función, la interfaz carga su tipo, su dominio y su
óptimo desde este registro. Las tres primeras son las que pide la tarea, las demás
vienen del documento de funciones de prueba de GEATbx que entregó el docente.
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


def esfera(X):
    """De Jong 1, f(x) = sum_i x_i^2."""
    return np.sum(X**2, axis=1)


def rosenbrock(X):
    """De Jong 2, f(x) = sum_i [100 (x_{i+1} - x_i^2)^2 + (1 - x_i)^2]."""
    return np.sum(100 * (X[:, 1:] - X[:, :-1] ** 2) ** 2 + (1 - X[:, :-1]) ** 2, axis=1)


def ackley(X):
    """f(x) = -20 exp(-0.2 sqrt(mean(x^2))) - exp(mean(cos(2 pi x))) + 20 + e."""
    return (-20 * np.exp(-0.2 * np.sqrt(np.mean(X**2, axis=1)))
            - np.exp(np.mean(np.cos(2 * np.pi * X), axis=1)) + 20 + np.e)


def griewank(X):
    """f(x) = sum_i x_i^2 / 4000 - prod_i cos(x_i / sqrt(i)) + 1."""
    i = np.arange(1, X.shape[1] + 1)
    return np.sum(X**2, axis=1) / 4000 - np.prod(np.cos(X / np.sqrt(i)), axis=1) + 1


def schwefel(X):
    """f(x) = sum_i -x_i sin(sqrt(|x_i|))."""
    return np.sum(-X * np.sin(np.sqrt(np.abs(X))), axis=1)


def easom(X):
    """f(x, y) = -cos(x) cos(y) exp(-((x - pi)^2 + (y - pi)^2))."""
    x, y = X[:, 0], X[:, 1]
    return -np.cos(x) * np.cos(y) * np.exp(-((x - np.pi) ** 2 + (y - np.pi) ** 2))


def goldstein_price(X):
    """Función de Goldstein y Price en dos variables."""
    x, y = X[:, 0], X[:, 1]
    a = 1 + (x + y + 1) ** 2 * (19 - 14 * x + 3 * x**2 - 14 * y + 6 * x * y + 3 * y**2)
    b = 30 + (2 * x - 3 * y) ** 2 * (18 - 32 * x + 12 * x**2 + 48 * y - 36 * x * y + 27 * y**2)
    return a * b


@dataclass(frozen=True)
class FuncionObjetivo:
    nombre: str
    f: callable
    maximizar: bool
    dominio: tuple                  # (a, b), igual para todas las variables
    n_fijo: int | None              # None si el número de variables es libre
    f_optimo: float | None          # None si no se conoce (función personalizada)
    x_optimos: tuple                # puntos óptimos en 2 variables, para dibujarlos
    optimo_por_variable: bool = False   # el óptimo vale f_optimo por cada variable
    corte: float = 0.0              # valor de x3..xn en las curvas de nivel
    permite_log: bool = False       # f >= 0 con mínimo 0, admite eje logarítmico
    expresion: str = ""             # solo en la función personalizada

    @property
    def tipo(self):
        return "Maximizar" if self.maximizar else "Minimizar"

    def valor_optimo(self, n):
        """Valor óptimo con n variables, o None si no se conoce."""
        if self.f_optimo is None:
            return None
        return self.f_optimo * n if self.optimo_por_variable else self.f_optimo

    def x_optimo_texto(self, n):
        if not self.x_optimos:
            return "desconocido"
        if self.n_fijo is None:
            c = f"{self.x_optimos[0][0]:g}"
            return f"x = ({c}, ..., {c}) con {n} variables"
        return " o ".join(f"({x:g}, {y:g})" for x, y in self.x_optimos)


# Los óptimos de Himmelblau y Peaks se refinaron con Nelder-Mead de SciPy.
# El de Peaks, 8.10621358944234 en (-0.00931758, 1.58136796), coincide con el
# 8.1062 en (-0.0093, 1.5814) de la guía. Los dominios y óptimos de las demás
# son los de GEATbx (Pohlheim, 2006).
FUNCIONES = {
    "Rastrigin": FuncionObjetivo(
        "Rastrigin", rastrigin, False, (-5.12, 5.12), None, 0.0, ((0.0, 0.0),),
        permite_log=True),
    "Himmelblau": FuncionObjetivo(
        "Himmelblau", himmelblau, False, (-5.0, 5.0), 2, 0.0,
        ((3.0, 2.0), (-2.805118, 3.131312), (-3.779310, -3.283186), (3.584428, -1.848126)),
        permite_log=True),
    "Peaks": FuncionObjetivo(
        "Peaks", peaks, True, (-3.0, 3.0), 2, 8.10621358944234,
        ((-0.00931758, 1.58136796),)),
    "Esfera (De Jong 1)": FuncionObjetivo(
        "Esfera (De Jong 1)", esfera, False, (-5.12, 5.12), None, 0.0, ((0.0, 0.0),),
        permite_log=True),
    "Rosenbrock": FuncionObjetivo(
        "Rosenbrock", rosenbrock, False, (-2.048, 2.048), None, 0.0, ((1.0, 1.0),),
        corte=1.0, permite_log=True),
    "Ackley": FuncionObjetivo(
        "Ackley", ackley, False, (-32.768, 32.768), None, 0.0, ((0.0, 0.0),),
        permite_log=True),
    "Griewank": FuncionObjetivo(
        "Griewank", griewank, False, (-600.0, 600.0), None, 0.0, ((0.0, 0.0),),
        permite_log=True),
    "Schwefel": FuncionObjetivo(
        "Schwefel", schwefel, False, (-500.0, 500.0), None, -418.982887272433799,
        ((420.968746, 420.968746),), optimo_por_variable=True, corte=420.968746),
    "Easom": FuncionObjetivo(
        "Easom", easom, False, (-100.0, 100.0), 2, -1.0, ((np.pi, np.pi),)),
    "Goldstein-Price": FuncionObjetivo(
        "Goldstein-Price", goldstein_price, False, (-2.0, 2.0), 2, 3.0, ((0.0, -1.0),)),
}

PERSONALIZADA = "Personalizada"
