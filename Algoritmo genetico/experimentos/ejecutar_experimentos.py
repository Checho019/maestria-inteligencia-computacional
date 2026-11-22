"""Experimentos E1, E2 y E3 de la sección 10 de la guía.

Configuración base N = 50, T = 200, L = 16, Pc = 0.8, Pm = 1/l, e = 1, torneo con
k = 3, cruce de dos puntos y mutación bit-flip. Cada experimento cambia un solo
factor y repite cada variante con las semillas 1 a 10. Se ejecutan las 200
generaciones sin parada anticipada para promediar las curvas completas, y la
generación en que el error baja de 1e-3 se lee de la historia de cada ejecución.

Uso, desde la carpeta experimentos: python ejecutar_experimentos.py
"""

import csv
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "ag_app"))

from ag import Configuracion, ejecutar  # noqa: E402
from funciones.objetivo import FUNCIONES  # noqa: E402

SEMILLAS = range(1, 11)
TOLERANCIA = 1e-3
BASE = Configuracion(N=50, T=200, L=16, pc=0.8, pm=None, elites=1, seleccion="Torneo", k=3,
                     cruce="Dos puntos", mutacion="Bit-flip por bit", pmi=0.2,
                     tolerancia=TOLERANCIA, parar_por_error=False, parar_por_estancamiento=False)

EXPERIMENTOS = {
    "E1": ("seleccion", ["Ruleta", "Torneo", "Ranking lineal"], replace(BASE, funcion="Rastrigin", n=10)),
    "E2": ("cruce", ["Un punto", "Dos puntos", "Uniforme"], replace(BASE, funcion="Himmelblau")),
    "E3": ("mutacion", ["Bit-flip por bit", "Un bit", "Inversión de segmento"], replace(BASE, funcion="Peaks")),
}


def diversidad(P):
    """Diversidad genotípica, media de 4 p (1 - p) sobre los l loci, con p la
    fracción de unos. Vale 1 si cada bit está repartido por mitades y 0 si todos
    los cromosomas son iguales."""
    p = P.mean(axis=0)
    return float(np.mean(4 * p * (1 - p)))


def optimo_alcanzado(x):
    """Índice del óptimo de Himmelblau más cercano a x (1 a 4, en el orden de la guía)."""
    optimos = np.array(FUNCIONES["Himmelblau"].x_optimos)
    return int(np.argmin(np.linalg.norm(optimos - x, axis=1))) + 1


def main():
    resultados = AQUI / "resultados"
    resultados.mkdir(exist_ok=True)
    filas, curvas = [], []
    for nombre, (factor, variantes, base) in EXPERIMENTOS.items():
        for variante in variantes:
            for semilla in SEMILLAS:
                cfg = replace(base, semilla=semilla, **{factor: variante})
                historia = []
                res = ejecutar(cfg, al_generar=lambda e: historia.append(diversidad(e.P)))
                filas.append({
                    "experimento": nombre, "funcion": cfg.funcion, "factor": factor,
                    "variante": variante, "semilla": semilla, "f_mejor": res.mejor_f,
                    "error": res.error, "exito": int(res.error < TOLERANCIA),
                    "generacion_tolerancia": res.generacion_tolerancia,
                    "generacion_mejor": res.generacion_mejor,
                    "diversidad_final": historia[-1],
                    "optimo_himmelblau": optimo_alcanzado(res.mejor_x) if cfg.funcion == "Himmelblau" else "",
                    "tiempo_s": res.tiempo,
                    "x_mejor": " ".join(f"{x:.6f}" for x in res.mejor_x),
                })
                for g in range(len(res.mejor)):
                    curvas.append([nombre, variante, semilla, g, res.mejor[g], res.media[g],
                                   res.peor[g], historia[g]])
            hechas = [f for f in filas if f["experimento"] == nombre and f["variante"] == variante]
            print(f"{nombre} {variante:22s} f final {np.mean([f['f_mejor'] for f in hechas]):.4f} "
                  f"éxito {sum(f['exito'] for f in hechas)}/10")

    with open(resultados / "ejecuciones.csv", "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)
    with open(resultados / "curvas.csv", "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["experimento", "variante", "semilla", "generacion", "mejor", "media",
                           "peor", "diversidad"])
        escritor.writerows(curvas)
    print(f"Guardados {len(filas)} ejecuciones y {len(curvas)} filas de curvas en {resultados}")


if __name__ == "__main__":
    main()
