"""Comprueba el motor contra los ejemplos de la guía, sin abrir la interfaz.

Uso, desde la carpeta ag_app: python -m pruebas.probar_motor
"""

import numpy as np

from ag import Configuracion, ejecutar
from ag import cruce, mutacion, seleccion
from ag.codificacion import bits_por_precision, decodificar
from funciones.objetivo import FUNCIONES


class RngFijo:
    """Generador que devuelve valores dados, para reproducir los ejemplos."""

    def __init__(self, random=None, integers=None):
        self._random, self._integers = random, integers

    def random(self, forma):
        return np.asarray(self._random, dtype=float).reshape(forma)

    def integers(self, bajo, alto, size):
        return np.asarray(self._integers).reshape(size)


def bits(texto):
    return np.array([[int(c) for c in texto]], dtype=np.uint8)


def texto(H):
    return "".join(map(str, H[0]))


# Sección 2.4, decodificación y elección de L
x = decodificar(bits("10110100"), [-5.12], [5.12], 8)[0, 0]
assert abs(x - 2.108) < 1e-3, x
assert bits_por_precision(-5.12, 5.12, 0.01) == 11

# Sección 3.1, ruleta del ejemplo de Michalewicz con r = 0.55
F = np.array([1.3480, 0.5169, 1.2159, 0.7371])
p = F / F.sum()
assert np.allclose(np.cumsum(p), [0.3531, 0.4885, 0.8069, 1.0], atol=1e-4)
assert seleccion._muestrear(RngFijo(random=[0.55]), p, 1)[0] == 2

# Sección 3.3, ranking lineal con s = 2: el peor tiene probabilidad 0 y el mejor 2/N
rng = np.random.default_rng(0)
elegidos = seleccion.ranking_lineal(rng, np.array([1.0, 2.0, 3.0, 4.0]), 40000, s=2.0)
frecuencia = np.bincount(elegidos, minlength=4) / 40000
assert frecuencia[0] == 0 and abs(frecuencia[3] - 0.5) < 0.01, frecuencia

# Sección 3.2, el torneo con k = N siempre elige al mejor
assert np.all(seleccion.torneo(rng, np.array([3.0, 9.0, 1.0]), 50, k=3) == 1)

# Sección 4, cruces con p1 = 10110110 y p2 = 01001101
p1, p2 = bits("10110110"), bits("01001101")
h1, h2 = cruce.un_punto(RngFijo(integers=[3]), p1, p2)
assert (texto(h1), texto(h2)) == ("10101101", "01010110")
cortes = np.zeros((1, 7))
cortes[0, [1, 5]] = -1          # argsort pone primero los cortes 2 y 6
h1, h2 = cruce.dos_puntos(RngFijo(random=cortes), p1, p2)
assert (texto(h1), texto(h2)) == ("10001110", "01110101")
mascara = np.where(bits("11001010")[0] == 1, 0.0, 0.9)  # menor que p0 donde vale 1
h1, h2 = cruce.uniforme(RngFijo(random=mascara), p1, p2)
assert (texto(h1), texto(h2)) == ("10000111", "01111100")

# Sección 5, mutaciones sobre h = 10110110
h = bits("10110110")
assert texto(mutacion.bit_flip(RngFijo(random=[1, 0, 1, 1, 1, 1, 1, 1]), h, 0.5)) == "11110110"
assert texto(mutacion.un_bit(RngFijo(random=[0.0], integers=[7]), h, 0.2)) == "10110111"
extremos = np.zeros(8)
extremos[[2, 5]] = -1           # segmento de la tercera a la sexta posición


class RngInversion:
    """Primero decide que el individuo muta y después da los dos extremos."""

    def __init__(self):
        self.valores = [np.array([0.0]), extremos]

    def random(self, forma):
        return self.valores.pop(0).reshape(forma)


assert texto(mutacion.inversion_segmento(RngInversion(), h, 0.2)) == "10101110"

# Sección 7, cada función vale su óptimo en su óptimo
for nombre, obj in FUNCIONES.items():
    for punto in obj.x_optimos:
        valor = obj.f(np.array([punto]))[0]
        assert abs(valor - obj.f_optimo) < 1e-5, (nombre, punto, valor)

# Reproducibilidad, la misma semilla da exactamente el mismo resultado
cfg = Configuracion(funcion="Himmelblau", parar_por_error=False)
r1, r2 = ejecutar(cfg), ejecutar(cfg)
assert r1.mejor == r2.mejor and np.array_equal(r1.mejor_cromosoma, r2.mejor_cromosoma)

# Con elitismo la curva del mejor nunca empeora
for nombre in FUNCIONES:
    for sel in seleccion.METODOS:
        for cr in cruce.METODOS:
            for mu in mutacion.METODOS:
                res = ejecutar(Configuracion(funcion=nombre, seleccion=sel, cruce=cr,
                                             mutacion=mu, T=40, parar_por_error=False))
                curva = np.array(res.mejor) * (1 if FUNCIONES[nombre].maximizar else -1)
                assert np.all(np.diff(curva) >= 0), (nombre, sel, cr, mu)

print("Todas las comprobaciones pasaron.")
for nombre in FUNCIONES:
    res = ejecutar(Configuracion(funcion=nombre))
    print(f"{nombre:10s} f(x*) = {res.mejor_f:.6f}  error = {res.error:.2e}  "
          f"generaciones = {res.generaciones}  {res.motivo}  {res.tiempo * 1000:.0f} ms")
