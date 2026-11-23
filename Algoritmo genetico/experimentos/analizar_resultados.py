"""Métricas de la sección 10.3 y figuras del informe a partir de los CSV de
ejecutar_experimentos.py.

Uso, desde la carpeta experimentos: python analizar_resultados.py
"""

from dataclasses import replace
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from scipy import stats

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from ejecutar_experimentos import EXPERIMENTOS, TOLERANCIA  # noqa: E402
from ag import ejecutar  # noqa: E402
from ag.codificacion import decodificar  # noqa: E402

AQUI = Path(__file__).resolve().parent
RESULTADOS = AQUI / "resultados"
FIGURAS = AQUI.parent / "informe" / "figuras"
OPTIMO = {"E1": 0.0, "E2": 0.0, "E3": 8.10621358944234}
TITULO = {"E1": "E1, selección en Rastrigin (n = 10)", "E2": "E2, cruce en Himmelblau",
          "E3": "E3, mutación en Peaks"}
COLORES = ["#D85A30", "#378ADD", "#1D9E75"]


def metricas(ejecuciones):
    """Mejor, media y DE del valor final, error medio, tasa de éxito, generaciones
    hasta 1e-3, generación de la última mejora y diversidad final."""
    filas = []
    for (exp, variante), g in ejecuciones.groupby(["experimento", "variante"], sort=False):
        maximizar = exp == "E3"
        exitosas = g["generacion_tolerancia"].dropna()
        filas.append({
            "experimento": exp, "variante": variante,
            "mejor": g["f_mejor"].max() if maximizar else g["f_mejor"].min(),
            "media": g["f_mejor"].mean(), "de": g["f_mejor"].std(ddof=1),
            "error_medio": g["error"].mean(), "exito_pct": 100 * g["exito"].mean(),
            "gen_hasta_eps": exitosas.mean() if len(exitosas) else np.nan,
            "gen_ultima_mejora": g["generacion_mejor"].mean(),
            "diversidad_final": g["diversidad_final"].mean(),
            "optimos_himmelblau": (" ".join(f"{k}:{v}" for k, v in
                                            sorted(g["optimo_himmelblau"].value_counts().items()))
                                   if exp == "E2" else ""),
        })
    return pd.DataFrame(filas)


def cromosomas_exitosos(cfg, radio=0.05):
    """Cromosomas de 2 variables con error menor que la tolerancia, buscados en una
    caja de +-radio alrededor de cada óptimo sobre la rejilla de la codificación."""
    obj, L = cfg.objetivo, cfg.L
    a, b = obj.dominio
    paso = (b - a) / (2**L - 1)
    exitosos = []
    for xo, yo in obj.x_optimos:
        Dx = np.arange(max(0, round((xo - radio - a) / paso)), min(2**L, round((xo + radio - a) / paso)))
        Dy = np.arange(max(0, round((yo - radio - a) / paso)), min(2**L, round((yo + radio - a) / paso)))
        DX, DY = np.meshgrid(Dx, Dy)
        X = np.column_stack([a + paso * DX.ravel(), a + paso * DY.ravel()])
        ok = np.abs(obj.f(X) - obj.f_optimo) < TOLERANCIA
        exitosos.append(np.column_stack([DX.ravel()[ok], DY.ravel()[ok]]))
    D = np.vstack(exitosos).astype(np.int64)
    pesos = 1 << np.arange(L - 1, -1, -1)
    bits = np.hstack([(D[:, [0]] & pesos) > 0, (D[:, [1]] & pesos) > 0]).astype(np.uint8)
    return bits, D


def estancamientos(ejecuciones):
    """Para cada ejecución de E2 y E3 que terminó sin éxito comprueba si el mejor
    cromosoma es un óptimo local frente a cambiar un solo bit. Mide la distancia de
    Hamming al cromosoma con éxito más cercano en bits, y al más cercano en el
    dominio junto con los pasos de la rejilla que lo separan."""
    filas = []
    sin_exito = ejecuciones[(ejecuciones["experimento"] != "E1") & (ejecuciones["exito"] == 0)]
    for _, fila in sin_exito.iterrows():
        factor, _, base = EXPERIMENTOS[fila["experimento"]]
        cfg = replace(base, semilla=int(fila["semilla"]), **{factor: fila["variante"]})
        res = ejecutar(cfg)
        obj, a, b = cfg.objetivo, *cfg.objetivo.dominio
        signo = 1 if obj.maximizar else -1
        vecinos = np.tile(res.mejor_cromosoma, (cfg.longitud, 1))
        vecinos[np.arange(cfg.longitud), np.arange(cfg.longitud)] ^= 1
        f_vecinos = obj.f(decodificar(vecinos, [a, a], [b, b], cfg.L))
        exitosos, D_exitosos = cromosomas_exitosos(cfg)
        diferencias = (exitosos != res.mejor_cromosoma).sum(axis=1)
        pesos = 2 ** np.arange(cfg.L - 1, -1, -1)
        D_mejor = res.mejor_cromosoma.reshape(2, cfg.L) @ pesos
        pasos = np.linalg.norm(D_exitosos - D_mejor, axis=1)
        cercano = pasos.argmin()
        filas.append({"experimento": fila["experimento"], "variante": fila["variante"],
                      "semilla": fila["semilla"], "error": res.error,
                      "optimo_local_un_bit": bool(np.all(signo * f_vecinos <= signo * res.mejor_f)),
                      "hamming_al_exito": int(diferencias.min()),
                      "pasos_al_exito_cercano": float(pasos[cercano]),
                      "hamming_exito_cercano": int(diferencias[cercano])})
    return pd.DataFrame(filas)


def tabla_latex(tabla):
    """Filas de la tabla de métricas para el informe."""
    nombres = {}

    def cientifico(x, decimales):
        """Notación científica para los valores menores que 0.001."""
        if x == 0 or abs(x) >= 0.001:
            return f"{x:.{decimales}f}"
        mantisa, exponente = f"{x:.1e}".split("e")
        return f"${mantisa}\\times10^{{{int(exponente)}}}$"

    filas = []
    for exp, g in tabla.groupby("experimento", sort=False):
        for i, (_, r) in enumerate(g.iterrows()):
            decimales = 2 if exp == "E1" else 4
            gen = "--" if np.isnan(r["gen_hasta_eps"]) else f"{r['gen_hasta_eps']:.1f}"
            optimos = ""
            if exp == "E2":
                cuenta = dict(par.split(":") for par in r["optimos_himmelblau"].split())
                optimos = "/".join(str(cuenta.get(f"{k}.0", cuenta.get(str(k), 0))) for k in range(1, 5))
            filas.append(
                f"{exp if i == 0 else ''} & {nombres.get(r['variante'], r['variante'])} & "
                f"{cientifico(r['mejor'], decimales)} & {r['media']:.{decimales}f} $\\pm$ {r['de']:.{decimales}f} & "
                f"{cientifico(r['error_medio'], decimales)} & {r['exito_pct']:.0f} & {gen} & "
                f"{r['diversidad_final']:.2f} & {optimos} \\\\")
        filas.append("\\midrule")
    # El \bottomrule va en el archivo porque tras un \input dentro de tabular falla
    return "\n".join(filas[:-1]) + "\n\\bottomrule\n"


def macros(ejecuciones, curvas, atascos):
    """Cifras que el informe cita en la prosa."""
    m = {}

    def valor_p(p):
        if p < 0.001:
            return "$p<0.001$"
        return f"$p={p:.2f}$" if p >= 0.01 else f"$p={p:.3f}$"

    def grupo(exp, variante, columna="f_mejor"):
        filtro = (ejecuciones["experimento"] == exp) & (ejecuciones["variante"] == variante)
        return ejecuciones.loc[filtro, columna].to_numpy()

    # E1, pruebas sobre el valor final y la diversidad final (diez semillas por variante)
    finales = [grupo("E1", v) for v in ("Ruleta", "Torneo", "Ranking lineal")]
    m["EunoKruskalP"] = valor_p(stats.kruskal(*finales).pvalue)
    m["EunoMannRankingTorneoP"] = valor_p(stats.mannwhitneyu(finales[2], finales[1]).pvalue)
    m["EunoDivMannP"] = valor_p(stats.mannwhitneyu(grupo("E1", "Torneo", "diversidad_final"),
                                                   grupo("E1", "Ranking lineal", "diversidad_final")).pvalue)
    e1 = curvas[curvas["experimento"] == "E1"]
    g25 = e1[e1["generacion"] == 25]
    torneo25 = g25[g25["variante"] == "Torneo"]["mejor"].to_numpy()
    for variante, clave in (("Ruleta", "Ruleta"), ("Ranking lineal", "Ranking")):
        otro = g25[g25["variante"] == variante]["mejor"].to_numpy()
        m[f"EunoGenVeinticincoTorneo{clave}P"] = valor_p(stats.mannwhitneyu(torneo25, otro).pvalue)
    ultima = ejecuciones[ejecuciones["experimento"] == "E1"].groupby("variante")["generacion_mejor"].mean()
    m["EunoUltimaMejoraMin"] = f"{ultima.min():.0f}"

    # E2, a qué óptimo llegan las ejecuciones con y sin éxito, y medianas de generaciones
    e2 = ejecuciones[ejecuciones["experimento"] == "E2"]
    exito = e2[e2["exito"] == 1]
    m["EdosExitos"] = str(len(exito))
    m["EdosExitosOptimoUno"] = str(int((exito["optimo_himmelblau"] == 1).sum()))
    m["EdosExitosOptimoCuatro"] = str(int((exito["optimo_himmelblau"] == 4).sum()))
    m["EdosExitosOptimosDosTres"] = str(int(exito["optimo_himmelblau"].isin([2, 3]).sum()))
    cerca = e2[e2["optimo_himmelblau"].isin([2, 3])]
    m["EdosCercaDosTres"] = str(len(cerca))
    m["EdosCercaDosTresErrorMin"] = f"{cerca['error'].min():.1e}".replace("e-0", "\\times10^{-") + "}"
    m["EdosCercaDosTresErrorMax"] = f"{cerca['error'].max():.3f}"
    for variante, clave in (("Un punto", "UnPunto"), ("Dos puntos", "DosPuntos"), ("Uniforme", "Uniforme")):
        m[f"EdosMediana{clave}"] = f"{np.median(grupo('E2', variante, 'generacion_tolerancia')[~np.isnan(grupo('E2', variante, 'generacion_tolerancia'))]):.0f}"

    # E3, prueba exacta de Fisher sobre la tasa de éxito de bit-flip frente a un bit
    exitos_bf = int(grupo("E3", "Bit-flip por bit", "exito").sum())
    exitos_ub = int(grupo("E3", "Un bit", "exito").sum())
    m["EtresFisherP"] = valor_p(stats.fisher_exact([[exitos_bf, 10 - exitos_bf],
                                                    [exitos_ub, 10 - exitos_ub]]).pvalue)
    for exp, clave in (("E2", "Edos"), ("E3", "Etres")):
        a = atascos[atascos["experimento"] == exp]
        m[f"{clave}PasosMediana"] = f"{a['pasos_al_exito_cercano'].median():.0f}"
        m[f"{clave}HammingCercanoMin"] = str(a["hamming_exito_cercano"].min())
        m[f"{clave}HammingCercanoMax"] = str(a["hamming_exito_cercano"].max())

    claves = {"Ruleta": "Ruleta", "Torneo": "Torneo", "Ranking lineal": "Ranking"}
    for g, sufijo, decimales in ((25, "GenVeinticinco", 1), (200, "GenDoscientos", 2)):
        medias = e1[e1["generacion"] == g].groupby("variante")[["mejor", "diversidad"]].mean()
        for variante, clave in claves.items():
            m[f"EunoMejor{clave}{sufijo}"] = f"{medias.loc[variante, 'mejor']:.{decimales}f}"
            m[f"EunoDiv{clave}{sufijo}"] = f"{medias.loc[variante, 'diversidad']:.2f}"
    # Generación desde la cual una curva media queda por debajo de otra hasta el final
    media = e1.groupby(["variante", "generacion"])["mejor"].mean().unstack(0)
    for a, b, clave in (("Ranking lineal", "Torneo", "CruceRankingTorneo"),
                        ("Ranking lineal", "Ruleta", "CruceRankingRuleta"),
                        ("Ruleta", "Torneo", "CruceRuletaTorneo")):
        debajo = (media[a] < media[b]).to_numpy()
        arriba = np.flatnonzero(~debajo)
        m[f"Euno{clave}"] = str(arriba[-1] + 1 if arriba.size else 0)
    for exp, clave in (("E2", "Edos"), ("E3", "Etres")):
        a = atascos[atascos["experimento"] == exp]
        m[f"{clave}SinExito"] = str(len(a))
        m[f"{clave}OptimoLocal"] = str(int(a["optimo_local_un_bit"].sum()))
        m[f"{clave}HammingMin"] = str(a["hamming_al_exito"].min())
        m[f"{clave}HammingMax"] = str(a["hamming_al_exito"].max())
    un_bit = atascos[atascos["variante"] == "Un bit"]
    m["EtresUnBitOptimoLocal"] = str(int(un_bit["optimo_local_un_bit"].sum()))
    m["EtresUnBitSinExito"] = str(len(un_bit))
    inversion = atascos[atascos["variante"] == "Inversión de segmento"]
    m["EtresInversionOptimoLocal"] = str(int(inversion["optimo_local_un_bit"].sum()))
    m["EtresInversionSinExito"] = str(len(inversion))
    # Con Pm = 1/l y l = 32, probabilidad de que bit-flip cambie dos o más bits de un hijo
    l, pm = 32, 1 / 32
    m["ProbDosBits"] = f"{1 - (1 - pm) ** l - l * pm * (1 - pm) ** (l - 1):.2f}"
    # Probabilidad de que bit-flip cambie justo un conjunto dado de j bits y ningún otro,
    # y cuántas veces se espera en una ejecución de (N - e) hijos por 200 generaciones
    hijos = 49 * 200
    for j, clave in ((2, "Dos"), (5, "Cinco")):
        p = pm**j * (1 - pm) ** (l - j)
        mantisa, exponente = f"{p:.1e}".split("e")
        m[f"ProbConcretos{clave}"] = f"{mantisa}\\times10^{{{int(exponente)}}}"
        m[f"EsperadoConcretos{clave}"] = f"{hijos * p:.1g}" if hijos * p >= 0.01 else \
            f"{(hijos * p):.0e}".replace("e-0", "\\times10^{-") + "}"
    return "".join(f"\\newcommand{{\\{k}}}{{{v}}}\n" for k, v in m.items())


def figura_convergencia(curvas):
    """Error del mejor (promedio de las 10 ejecuciones) y diversidad por generación."""
    fig, ejes = plt.subplots(2, 3, figsize=(7.2, 2.9), sharex=True, layout="constrained")
    for j, exp in enumerate(["E1", "E2", "E3"]):
        datos = curvas[curvas["experimento"] == exp]
        for color, (variante, g) in zip(COLORES, datos.groupby("variante", sort=False)):
            tabla = g.pivot(index="generacion", columns="semilla", values="mejor")
            error = (tabla - OPTIMO[exp]).abs().mean(axis=1)
            ejes[0, j].plot(error.index, error.values, color=color, lw=1.3, label=variante)
            div = g.pivot(index="generacion", columns="semilla", values="diversidad").mean(axis=1)
            ejes[1, j].plot(div.index, div.values, color=color, lw=1.3)
        ejes[0, j].set_yscale("log")
        if exp != "E1":
            ejes[0, j].axhline(1e-3, color="0.4", ls="--", lw=0.8)
        ejes[0, j].set_title(TITULO[exp], fontsize=8)
        ejes[0, j].legend(fontsize=6, loc="upper right")
        ejes[1, j].set_xlabel("Generación", fontsize=8)
        ejes[1, j].set_ylim(0, 1)
        for eje in ejes[:, j]:
            eje.tick_params(labelsize=7)
            eje.grid(alpha=0.3)
    ejes[0, 0].set_ylabel("Error del mejor", fontsize=8)
    ejes[1, 0].set_ylabel("Diversidad", fontsize=8)
    fig.savefig(FIGURAS / "convergencia_experimentos.pdf")
    plt.close(fig)


def main():
    FIGURAS.mkdir(parents=True, exist_ok=True)
    ejecuciones = pd.read_csv(RESULTADOS / "ejecuciones.csv")
    curvas = pd.read_csv(RESULTADOS / "curvas.csv")
    tabla = metricas(ejecuciones)
    tabla.to_csv(RESULTADOS / "metricas.csv", index=False)
    with pd.option_context("display.width", 200, "display.max_columns", 20):
        print(tabla.round(4).to_string(index=False))
    for g in (10, 25, 50, 200):
        print(f"E1, generación {g}, mejor y diversidad medios por método")
        e1 = curvas[(curvas["experimento"] == "E1") & (curvas["generacion"] == g)]
        print(e1.groupby("variante", sort=False)[["mejor", "diversidad"]].mean().round(3).to_string())
    atascos = estancamientos(ejecuciones)
    atascos.to_csv(RESULTADOS / "estancamientos.csv", index=False)
    print(atascos.to_string(index=False))
    print(atascos.groupby(["experimento", "variante"], sort=False)
          .agg(sin_exito=("semilla", "size"), optimo_local=("optimo_local_un_bit", "sum"),
               hamming_medio=("hamming_al_exito", "mean")).to_string())
    informe = FIGURAS.parent
    (informe / "tabla_metricas.tex").write_text(tabla_latex(tabla), encoding="utf-8")
    (informe / "cifras.tex").write_text(macros(ejecuciones, curvas, atascos), encoding="utf-8")
    figura_convergencia(curvas)
    print(f"Tabla, cifras y figura guardadas en {informe}")


if __name__ == "__main__":
    main()
