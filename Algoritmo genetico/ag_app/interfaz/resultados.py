"""Presentación y exportación de los resultados de las ejecuciones."""

import csv
import math

import numpy as np
from PySide6.QtWidgets import QTableWidgetItem

from ag.codificacion import cadena

DETENIDA = "Detenido por el usuario"


def mostrar(v, cfg, r, res):
    """Escribe una ejecución en el panel de resultados y en la tabla."""
    conocido = not math.isnan(res.error)
    v.resultados["Mejor cromosoma"].setText(cadena(res.mejor_cromosoma, cfg.L))
    v.resultados["x*"].setText("(" + ", ".join(f"{x:.6f}" for x in res.mejor_x) + ")")
    v.resultados["f(x*)"].setText(f"{res.mejor_f:.8f}")
    v.resultados["Error al óptimo"].setText(f"{res.error:.3e}" if conocido else "— (óptimo desconocido)")
    v.resultados["Generación del mejor"].setText(str(res.generacion_mejor))
    v.resultados["Generaciones ejecutadas"].setText(str(res.generaciones))
    v.resultados["Tiempo de ejecución"].setText(f"{res.tiempo * 1000:.1f} ms")
    v.resultados["Motivo de parada"].setText(res.motivo)
    fila = v.tabla.rowCount()
    v.tabla.insertRow(fila)
    valores = [cfg.semilla + r, f"{res.mejor_f:.6f}", f"{res.error:.2e}" if conocido else "—",
               res.generacion_mejor, f"{res.tiempo * 1000:.1f}"]
    for columna, valor in enumerate(valores):
        v.tabla.setItem(fila, columna, QTableWidgetItem(str(valor)))
    v.tabla.scrollToBottom()


def limpiar(v):
    for etiqueta in v.resultados.values():
        etiqueta.setText("—")
    v.tabla.setRowCount(0)
    v.resumen.setText("")


def resumen(resultados, tolerancia):
    """Media y desviación del mejor valor final de las ejecuciones completas. La
    ejecución detenida a mitad de camino no entra."""
    completas = [r for r in resultados if r.motivo != DETENIDA]
    nota = " La ejecución detenida no entra en el resumen." if len(completas) < len(resultados) else ""
    if not completas:
        return "La ejecución se detuvo antes de terminar, no hay resumen." if resultados else ""
    finales = np.array([r.mejor_f for r in completas])
    errores = np.array([r.error for r in completas])
    desviacion = finales.std(ddof=1) if finales.size > 1 else 0.0
    cuantas = "1 ejecución completa" if len(finales) == 1 else f"{len(finales)} ejecuciones completas"
    texto = f"{cuantas}. Mejor valor final {finales.mean():.6f} ± {desviacion:.6f} (media ± DE)"
    if not np.isnan(errores).any():
        exito = np.mean(errores < tolerancia) * 100
        texto += (f", error medio {errores.mean():.2e}, éxito {exito:.0f} % "
                  f"con error menor que {tolerancia:g}")
    return texto + "." + nota


def escribir_csv(ruta, resultados, semilla):
    """Guarda una fila por ejecución en `ruta` y la historia por generación en
    `<ruta>_historia.csv`. Devuelve la ruta de la historia."""
    with open(ruta, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["ejecucion", "semilla", "f_mejor", "error", "generacion_mejor",
                           "generaciones", "tiempo_s", "motivo", "x_mejor"])
        for r, res in enumerate(resultados):
            escritor.writerow([r + 1, semilla + r, res.mejor_f, res.error, res.generacion_mejor,
                               res.generaciones, res.tiempo, res.motivo, " ".join(map(str, res.mejor_x))])
    historia = ruta.with_name(ruta.stem + "_historia.csv")
    with open(historia, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["ejecucion", "semilla", "generacion", "mejor", "media", "peor"])
        for r, res in enumerate(resultados):
            for g, fila in enumerate(zip(res.mejor, res.media, res.peor)):
                escritor.writerow([r + 1, semilla + r, g, *fila])
    return historia
