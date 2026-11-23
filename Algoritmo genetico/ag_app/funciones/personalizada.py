"""Función objetivo escrita por el usuario como una expresión de x1, ..., xn.

La expresión se revisa con el árbol sintáctico de Python antes de evaluarla. Solo
se admiten números, las variables x1 a xn (x e y como alias de x1 y x2), los
operadores aritméticos y las funciones de la tabla PERMITIDAS, así que no puede
ejecutar código arbitrario.
"""

import ast
from functools import lru_cache

import numpy as np

from .objetivo import PERSONALIZADA, FuncionObjetivo

PERMITIDAS = {
    "sin": np.sin, "cos": np.cos, "tan": np.tan, "exp": np.exp, "log": np.log,
    "log10": np.log10, "sqrt": np.sqrt, "abs": np.abs, "tanh": np.tanh,
    "arctan": np.arctan, "pi": np.pi, "e": np.e,
}
LARGO_MAXIMO = 500
NODOS = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Call, ast.Name, ast.Load,
         ast.Constant, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod,
         ast.USub, ast.UAdd)


def _variables(n):
    nombres = {f"x{i}" for i in range(1, n + 1)}
    return nombres | {"x", "y"} if n >= 2 else nombres | {"x"}


def revisar(expresion, n):
    """Devuelve el código compilado de la expresión o lanza ValueError con un
    mensaje para el usuario."""
    if not expresion.strip():
        raise ValueError("Escriba la expresión de la función, por ejemplo x1**2 + x2**2.")
    if len(expresion) > LARGO_MAXIMO:
        raise ValueError(f"La expresión supera los {LARGO_MAXIMO} caracteres.")
    try:
        arbol = ast.parse(expresion.replace("^", "**"), mode="eval")
    except (SyntaxError, RecursionError, MemoryError):
        raise ValueError(f"La expresión \"{expresion[:60]}\" no es válida.") from None
    validas = _variables(n)
    for nodo in ast.walk(arbol):
        if not isinstance(nodo, NODOS):
            raise ValueError(f"La expresión contiene un elemento no permitido ({type(nodo).__name__}).")
        if isinstance(nodo, ast.Name) and nodo.id not in validas and nodo.id not in PERMITIDAS:
            raise ValueError(f"\"{nodo.id}\" no es una variable (x1 a x{n}) ni una función permitida.")
        if isinstance(nodo, ast.Call):
            if not (isinstance(nodo.func, ast.Name) and callable(PERMITIDAS.get(nodo.func.id))):
                raise ValueError("Solo se permiten las funciones " + ", ".join(
                    k for k, v in PERMITIDAS.items() if callable(v)) + ".")
            # Un segundo argumento de NumPy sería el arreglo de salida y
            # sobrescribiría una variable
            if len(nodo.args) != 1 or nodo.keywords:
                raise ValueError(f"La función {nodo.func.id} recibe un solo argumento.")
        if isinstance(nodo, ast.Constant):
            if isinstance(nodo.value, bool) or not isinstance(nodo.value, (int, float)):
                raise ValueError("La expresión solo admite números.")
            # Con números reales una potencia enorme desborda al instante en vez de
            # calcular un entero gigante y congelar la aplicación
            nodo.value = float(nodo.value)
    try:
        return compile(arbol, "<expresion>", "eval")
    except (RecursionError, MemoryError):
        raise ValueError("La expresión es demasiado anidada.") from None


@lru_cache(maxsize=32)
def crear(expresion, a, b, maximizar, optimo, n):
    """Arma la FuncionObjetivo de una expresión. Comprueba en 2000 puntos del
    dominio que dé valores finitos."""
    codigo = revisar(expresion, n)

    def f(X):
        entorno = dict(PERMITIDAS)
        for i in range(X.shape[1]):
            entorno[f"x{i + 1}"] = X[:, i]
        entorno["x"] = X[:, 0]
        if X.shape[1] >= 2:
            entorno["y"] = X[:, 1]
        with np.errstate(all="ignore"):
            valores = eval(codigo, {"__builtins__": {}}, entorno)
        return np.broadcast_to(np.asarray(valores, dtype=float), (X.shape[0],)).copy()

    muestra = np.random.default_rng(0).uniform(a, b, size=(2000, n))
    try:
        valores = f(muestra)
    except OverflowError:
        raise ValueError("La expresión da un número demasiado grande.") from None
    except Exception as error:
        raise ValueError(f"La expresión no se pudo evaluar ({error}).") from None
    if not np.all(np.isfinite(valores)):
        raise ValueError("La expresión da valores no definidos o infinitos dentro del dominio "
                         "(por ejemplo, la raíz o el logaritmo de un número negativo).")
    centro = (a + b) / 2
    return FuncionObjetivo(PERSONALIZADA, f, maximizar, (a, b), None, optimo, (),
                           corte=centro, expresion=expresion)
