# -*- coding: utf-8 -*-
"""Genera las figuras del informe en figuras/ y sus cifras en cifras.tex a partir de resultados.json,
que escribe el último paso del cuaderno. Se ejecuta en esta carpeta, después del cuaderno."""
import json, os, math, itertools
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

AQUI = os.path.dirname(os.path.abspath(__file__))
PALETA = ["#00599f", "#d95f02", "#008c66", "#733388", "#cca61a", "#667380"]
plt.rcParams.update({"font.size": 9, "axes.titlesize": 9, "axes.labelsize": 9, "legend.fontsize": 8,
                     "xtick.labelsize": 8, "ytick.labelsize": 8, "axes.prop_cycle": plt.cycler(color=PALETA),
                     "figure.dpi": 300, "savefig.dpi": 300, "axes.grid": True, "grid.alpha": 0.3,
                     "font.family": "sans-serif", "legend.framealpha": 0.9})
CM = 1 / 2.54
COLOR_ETIQUETA = {"cerca": PALETA[0], "media": PALETA[4], "lejos": PALETA[3]}


def guardar(fig, carpeta, nombre):
    os.makedirs(carpeta, exist_ok=True)
    fig.savefig(os.path.join(carpeta, nombre), bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def macro(f, nombre, valor):
    f.write("\\newcommand{\\%s}{%s}\n" % (nombre, valor))


def miles(n):
    return "{:,}".format(int(n)).replace(",", "\\,")


def sci(v):
    m, e = ("%.1e" % v).split("e")
    return "$%s\\times10^{%d}$" % (m, int(e))


def limpiar(carpeta):
    os.makedirs(carpeta, exist_ok=True)
    for f in os.listdir(carpeta):
        os.remove(os.path.join(carpeta, f))


def trimf(x, a, b, c):
    x = np.asarray(x, dtype=float)
    izq = np.ones_like(x) if b == a else (x - a) / (b - a)
    der = np.ones_like(x) if c == b else (c - x) / (c - b)
    return np.clip(np.minimum(izq, der), 0, 1)


def trapmf(x, a, b, c, d):
    x = np.asarray(x, dtype=float)
    izq = np.ones_like(x) if b == a else (x - a) / (b - a)
    der = np.ones_like(x) if d == c else (d - x) / (d - c)
    return np.clip(np.minimum(np.minimum(izq, 1.0), der), 0, 1)


def gbellmf(x, a, b, c):
    return 1.0 / (1.0 + np.abs((np.asarray(x, dtype=float) - c) / a) ** (2 * b))


def sugeno1(x, P, L):
    W = np.stack([gbellmf(x, *p) for p in P], axis=1)
    f = L[:, 0][None, :] * x[:, None] + L[:, 1][None, :]
    return (W * f).sum(axis=1) / W.sum(axis=1)


def confusion(cm, clases, carpeta, nombre, tope, ancho=8.5):
    """El color codifica solo los errores, la diagonal va en gris claro con su número."""
    cm = np.array(cm); fuera = cm.astype(float); np.fill_diagonal(fuera, np.nan)
    fig, ax = plt.subplots(figsize=(ancho * CM, ancho * 0.92 * CM))
    ax.grid(False)
    diag = np.full(cm.shape, np.nan); np.fill_diagonal(diag, 1)
    ax.imshow(diag, cmap=ListedColormap(["#e6e6e6"]), vmin=0, vmax=1)
    im = ax.imshow(fuera, cmap="Oranges", vmin=0, vmax=tope)
    ax.set_xticks(range(len(clases))); ax.set_yticks(range(len(clases)))
    ax.set_xticklabels(clases, rotation=30, ha="right"); ax.set_yticklabels(clases)
    ax.set_xlabel("clase predicha"); ax.set_ylabel("clase real")
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, cm[i, j], ha="center", va="center", fontsize=8,
                    color="white" if (i != j and cm[i, j] > tope / 2) else "black")
    fig.colorbar(im, fraction=0.046, pad=0.03, label="errores", ticks=range(0, int(tope) + 1))
    guardar(fig, carpeta, nombre)


# ============================ taller robot ============================
r = json.load(open(os.path.join(AQUI, "resultados.json"), encoding="utf-8"))
C = os.path.join(AQUI, "figuras"); limpiar(C)
SEN = ["frontal", "izquierdo", "derecho", "trasero"]
NOM = ["giro fuerte a la derecha", "giro suave a la derecha", "avanzar", "giro suave a la izquierda"]
NOMC = ["giro fuerte der.", "giro suave der.", "avanzar", "giro suave izq."]
CLASES = ["Sharp-Right-Turn", "Slight-Right-Turn", "Move-Forward", "Slight-Left-Turn"]
d4 = pd.read_csv(os.path.join(AQUI, "datos", "sensor_readings_4.csv"), header=None, names=SEN + ["accion"])
y = d4["accion"].map({c: k for k, c in enumerate(CLASES)}).to_numpy(); X = d4[SEN].to_numpy()
itr = np.array(r["itr"]); ite = np.array(r["ite"]); Xtr, ytr = X[itr], y[itr]
U = r["umbral"]; MF = r["MF"]
CORTES = {"frontal": [U["frontal"]], "izquierdo": [U["izq_bajo"], U["izq_alto"]], "derecho": [U["derecho"]], "trasero": [U["trasero"]]}

fig, ejes = plt.subplots(1, 4, figsize=(16 * CM, 4.4 * CM), gridspec_kw=dict(wspace=0.35))
for ax, k in zip(ejes, range(4)):
    ax.hist(Xtr[:, k], bins=np.linspace(0.3, 5.05, 96), color="0.45")
    ax.set_yscale("log"); ax.set(xlabel=SEN[k], ylabel="registros" if k == 0 else None); ax.set_xticks([1, 2, 3, 4, 5])
guardar(fig, C, "fig01_histogramas.png")

fig, ejes = plt.subplots(2, 2, figsize=(15 * CM, 9.8 * CM), gridspec_kw=dict(wspace=0.22, hspace=0.42))
lim = {"frontal": (0.4, 2.6), "izquierdo": (0.3, 2.0), "derecho": (0.8, 3.2), "trasero": (0.3, 3.2)}
for ax, k in zip(ejes.ravel(), range(4)):
    bins = np.linspace(*lim[SEN[k]], 70)
    for c in range(4):
        ax.hist(Xtr[ytr == c, k], bins=bins, histtype="stepfilled", alpha=0.45, color=PALETA[c], label=NOMC[c])
        ax.hist(Xtr[ytr == c, k], bins=bins, histtype="step", color=PALETA[c], lw=0.9)
    ax.set(xlabel=SEN[k], ylabel="registros" if k % 2 == 0 else None)
    for u in CORTES[SEN[k]]:
        ax.axvline(u, color="black", lw=0.9, ls="--")
fig.legend(*ejes[0, 0].get_legend_handles_labels(), loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.09), frameon=False)
guardar(fig, C, "fig02_histogramas_clase.png")

fig, (a1, a2) = plt.subplots(1, 2, figsize=(15 * CM, 6.2 * CM), gridspec_kw=dict(wspace=0.25))
for c in range(4):
    a1.scatter(Xtr[ytr == c, 0], Xtr[ytr == c, 1], s=2.5, color=PALETA[c], label=NOMC[c], rasterized=True)
    a2.scatter(Xtr[ytr == c, 2], Xtr[ytr == c, 3], s=2.5, color=PALETA[c], rasterized=True)
a1.axvline(U["frontal"], color="black", lw=0.8, ls="--"); a1.axhline(U["izq_bajo"], color="black", lw=0.8, ls="--"); a1.axhline(U["izq_alto"], color="black", lw=0.8, ls="--")
a2.axvline(U["derecho"], color="black", lw=0.8, ls="--"); a2.axhline(U["trasero"], color="black", lw=0.8, ls="--")
a1.set(xlabel="frontal", ylabel="izquierdo", xlim=(0.4, 2.6), ylim=(0.3, 2.0))
a2.set(xlabel="derecho", ylabel="trasero", xlim=(0.8, 3.2), ylim=(0.3, 3.2))
fig.legend(*a1.get_legend_handles_labels(), loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.16), frameon=False, markerscale=4)
guardar(fig, C, "fig03_nubes.png")

fig, ejes = plt.subplots(2, 2, figsize=(15 * CM, 8.4 * CM), gridspec_kw=dict(wspace=0.22, hspace=0.45))
for ax, s in zip(ejes.ravel(), SEN):
    xg = np.linspace(*lim[s], 600)
    k = SEN.index(s)
    ax2 = ax.twinx(); ax2.grid(False)
    ax2.hist(Xtr[:, k], bins=np.linspace(*lim[s], 70), color="0.85"); ax2.set_yticks([])
    ax.set_zorder(ax2.get_zorder() + 1); ax.patch.set_visible(False)
    for e, (t, p) in MF[s].items():
        ax.plot(xg, trapmf(xg, *p), lw=2, color=COLOR_ETIQUETA[e], label=e)
    ax.set(xlabel=s, ylabel="grado" if k % 2 == 0 else None, ylim=(-0.02, 1.05))
handles = [plt.Line2D([], [], color=COLOR_ETIQUETA[e], lw=2, label=e) for e in ("cerca", "media", "lejos")]
fig.legend(handles=handles, loc="lower center", ncol=3, bbox_to_anchor=(0.5, 0.97), frameon=False)
guardar(fig, C, "fig04_pertenencia.png")

R2 = np.array(r["reglas"]["2 sensores"]["R"]); c2 = np.array(r["reglas"]["2 sensores"]["c"])
def fuerzas2(f_, i_):
    Gf = np.stack([trapmf(f_, *p) for _, p in MF["frontal"].values()], -1); Gi = np.stack([trapmf(i_, *p) for _, p in MF["izquierdo"].values()], -1)
    return np.stack([Gf[..., a] * Gi[..., b] for a, b in R2], -1)
fg, ig = np.meshgrid(np.linspace(0.4, 2.0, 500), np.linspace(0.3, 1.6, 420))
pred = c2[fuerzas2(fg, ig).argmax(-1)]
fig, ax = plt.subplots(figsize=(11 * CM, 7.2 * CM))
ax.grid(False)
ax.imshow(pred, origin="lower", extent=(0.4, 2.0, 0.3, 1.6), aspect="auto", cmap=ListedColormap(PALETA[:4]), alpha=0.22, vmin=-0.5, vmax=3.5)
dl = r["delta"]
ax.axvspan(U["frontal"] - dl, U["frontal"] + dl, color="0.35", alpha=0.18, lw=0)
for uu in (U["izq_bajo"], U["izq_alto"]):
    ax.axhspan(uu - dl, uu + dl, xmin=(U["frontal"] - 0.4) / 1.6, color="0.35", alpha=0.18, lw=0)
Xte, yte = X[ite], y[ite]
for c in range(4):
    ax.scatter(Xte[yte == c, 0], Xte[yte == c, 1], s=2, color=PALETA[c], label=NOMC[c], rasterized=True)
ax.set(xlabel="frontal", ylabel="izquierdo", xlim=(0.4, 2.0), ylim=(0.3, 1.6))
ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=7, markerscale=4, frameon=False)
guardar(fig, C, "fig05_mapa.png")

uni = r["uniforme"]
fig, ax = plt.subplots(figsize=(11 * CM, 6.6 * CM))
estilos = {("mínimo y máximo", "registro de mayor grado"): (PALETA[0], "o-"), ("mínimo y máximo", "suma de fuerzas"): (PALETA[0], "s--"),
           ("cuantiles", "registro de mayor grado"): (PALETA[1], "o-"), ("cuantiles", "suma de fuerzas"): (PALETA[1], "s--")}
for u in uni:
    if u["sensores"] != 2:
        continue
    cvn = u["cv"]; ns_ = sorted(int(k) for k in cvn)
    col, est = estilos[(u["escala"], u["metodo"])]
    ax.plot(ns_, [100 * cvn[str(n)] for n in ns_], est, color=col, ms=4, mfc="white" if "--" in est else col,
            label=f"{u['escala']}, {u['metodo']}")
ax.axhline(100 * r["cv_modelos"]["2 sensores"], color="black", lw=1.4, label="cortes del análisis, 6 reglas")
ax.set(xlabel="etiquetas uniformes por sensor", ylabel="exactitud de validación (%)", ylim=(35, 102)); ax.set_xticks(range(2, 11))
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2, fontsize=8, frameon=False)
guardar(fig, C, "fig06_uniforme.png")

des = np.array(r["desplazamientos"])
fig, ax = plt.subplots(figsize=(11 * CM, 5.8 * CM))
for k, (clave, et) in enumerate((("frontal", "umbral del frontal"), ("izq_bajo", "umbral bajo del izquierdo"), ("izq_alto", "umbral alto del izquierdo"))):
    ax.plot(des, 100 * np.array(r["sens"][clave]), "o-", ms=3, color=PALETA[[3, 4, 5][k]], label=et)
ax.set(xlabel="desplazamiento del umbral", ylabel="exactitud en prueba (%)"); ax.legend(loc="lower center", fontsize=7)
ax.set_xticks([-0.10, -0.05, 0, 0.05, 0.10])
guardar(fig, C, "fig07_sensibilidad.png")

GIRO = np.array([-2.0, -1.0, 0.0, 1.0])
def sugeno0(f_, i_):
    w = fuerzas2(f_, i_)
    return (w * GIRO[c2]).sum(-1) / w.sum(-1)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(15 * CM, 5.4 * CM), sharey=True, gridspec_kw=dict(wspace=0.08))
xi = np.linspace(0.3, 1.3, 600)
for k, fr in enumerate((0.88, 0.90, 1.2)):
    a1.plot(xi, sugeno0(np.full_like(xi, fr), xi), color=PALETA[[3, 4, 5][k]], lw=1.6, label=f"frontal = {fr:g}")
a1.set(xlabel="izquierdo", yticks=[-2, -1, 0, 1]); a1.legend(loc="upper left", fontsize=7)
xfr = np.linspace(0.6, 1.3, 600)
for k, iz in enumerate((0.47, 0.6, 1.2)):
    a2.plot(xfr, sugeno0(xfr, np.full_like(xfr, iz)), color=PALETA[[3, 4, 5][k]], lw=1.6, label=f"izquierdo = {iz:g}")
a2.set(xlabel="frontal"); a2.legend(loc="lower right", fontsize=7)
a1.set_yticklabels(["giro fuerte der.", "giro suave der.", "avanzar", "giro suave izq."])
a1.set_ylabel(None)
guardar(fig, C, "fig08_sugeno.png")

with open(os.path.join(AQUI, "cifras.tex"), "w", encoding="utf-8") as f:
    macro(f, "nReg", miles(r["n"])); macro(f, "nTr", miles(r["n_tr"])); macro(f, "nTe", miles(r["n_te"]))
    for k in range(4):
        e = "ABCD"[k]
        macro(f, "cuenta" + e, miles(r["conteo"][k])); macro(f, "pct" + e, "%.1f" % (100 * r["conteo"][k] / r["n"]))
        macro(f, "cuentaTe" + e, miles(r["conteo_te"][k]))
    for s, e in zip(SEN, "ABCD"):
        macro(f, "sat" + e, r["saturadas"][s]); macro(f, "satTr" + e, r["saturadas_tr"][s])
    cm_ = r["cambio_med"]; macro(f, "cambioMin", "%.3f" % min(cm_)); macro(f, "cambioMax", "%.3f" % max(cm_))
    macro(f, "cambioAccion", "%.1f" % (100 * r["cambio_accion"]))
    macro(f, "filasRangos", "\n".join(
        "        %s & %s \\\\" % (NOM[c], " & ".join("%.3f & %.3f" % (r["rangos"][s][c][0], r["rangos"][s][c][2]) for s in SEN[:2]))
        for c in range(4)))
    macro(f, "filasRangosDT", "\n".join(
        "        %s & %s & %.2f & %.2f \\\\" % (NOM[c], " & ".join("%.2f & %.2f & %.2f" % tuple(r["rangos"][s][c]) for s in SEN[2:]),
                                             100 * r["arriba"]["derecho"][c], 100 * r["arriba"]["trasero"][c])
        for c in range(4)))
    macro(f, "uFrontal", "%.4f" % U["frontal"]); macro(f, "uIzqBajo", "%.4f" % U["izq_bajo"]); macro(f, "uIzqAlto", "%.4f" % U["izq_alto"])
    macro(f, "uDerecho", "%.4f" % U["derecho"]); macro(f, "uTrasero", "%.4f" % U["trasero"]); macro(f, "semiancho", "%.2f" % r["delta"])
    ar = r["arriba"]; macro(f, "trasIzq", "%.0f" % (100 * ar["trasero"][3])); macro(f, "trasOtrasMax", "%.0f" % (100 * max(ar["trasero"][:3])))
    macro(f, "derSuave", "%.0f" % (100 * ar["derecho"][1])); macro(f, "derOtrasMax", "%.0f" % (100 * max(ar["derecho"][c] for c in (0, 2, 3))))
    def params(s, e):
        t, p = MF[s][e]
        return ", ".join("%.0f" % v if v in (-1, 6) else "%.4f" % v for v in p)
    macro(f, "filasMF", "\n".join("        %s & %s & %s \\\\" % (s, e, params(s, e)) for s in SEN for e in MF[s]))
    et = {s: list(MF[s]) for s in SEN}
    R2d = r["reglas"]["2 sensores"]
    orden2 = np.argsort(-np.array(R2d["soporte"]))
    macro(f, "filasReglasDos", "\n".join("        %d & %s & %s & %s & %.1f & %.3f & %s \\\\" % (
        j + 1, et["frontal"][R2d["R"][k][0]], et["izquierdo"][R2d["R"][k][1]], NOM[R2d["c"][k]], R2d["soporte"][k], R2d["certeza"][k], miles(R2d["gana"][k]))
        for j, k in enumerate(orden2)))
    R4d = r["reglas"]["4 sensores"]
    orden4 = np.argsort(-np.array(R4d["soporte"]))
    macro(f, "filasReglasCuatro", "\n".join("        %d & %s & %s & %s & %s & %s & %.2f & %.3f & %s \\\\" % (
        j + 1, *[et[s][R4d["R"][k][m]] for m, s in enumerate(SEN)], NOMC[R4d["c"][k]], R4d["soporte"][k], R4d["certeza"][k], R4d["gana"][k])
        for j, k in enumerate(orden4)))
    dis = r["distintas"]
    numeros = {1: "una", 2: "dos", 3: "tres", 4: "cuatro"}
    macro(f, "nDistintas", numeros.get(len(dis), str(len(dis))))
    macro(f, "distSoporteMax", "%.1f" % max(R4d["soporte"][k] for k in dis)); macro(f, "distGanaTot", sum(R4d["gana"][k] for k in dis))
    macro(f, "distReglas", " y ".join("«%s entonces %s»" % (" y ".join("%s %s" % (s, et[s][R4d["R"][k][m]]) for m, s in enumerate(SEN)), NOM[R4d["c"][k]]) for k in dis))
    macro(f, "reglasSinGanar", int(np.sum(np.array(R4d["gana"]) == 0)))
    cert2 = np.array(R2d["certeza"]); macro(f, "certMinDos", "%.3f" % cert2.min()); macro(f, "certMaxDos", "%.3f" % cert2.max())
    cert4 = np.array(R4d["certeza"]); macro(f, "certMinCuatro", "%.3f" % cert4[np.array(R4d["soporte"]) >= 1].min())
    res = r["resultados"]
    for nombre, e in (("4 sensores", "Cuatro"), ("2 sensores", "Dos")):
        macro(f, "acc" + e, "%.1f" % (100 * res[nombre]["exactitud"])); macro(f, "bal" + e, "%.1f" % (100 * res[nombre]["balanceada"]))
        macro(f, "arbol" + e, "%.1f" % (100 * res[nombre]["arbol"])); macro(f, "hojas" + e, res[nombre]["hojas"])
        macro(f, "reglas" + e, res[nombre]["reglas"]); macro(f, "cv" + e, "%.1f" % (100 * r["cv_modelos"][nombre]))
    macro(f, "aciertosNitida", miles(r["aciertos_nitida"])); macro(f, "accSoloDT", "%.1f" % (100 * r["acc_solo_dt"]))
    macro(f, "mayoritaria", "%.1f" % (100 * r["mayoritaria"]))
    CORTA = {"mínimo y máximo": "mín. y máx.", "cuantiles": "cuantiles", "registro de mayor grado": "mayor grado", "suma de fuerzas": "suma de fuerzas"}
    def fila_uni(u):
        return "        %d & %s & %s & %d & %d & %d & %.1f & %.1f & %.1f \\\\" % (
            u["sensores"], CORTA[u["escala"]], CORTA[u["metodo"]], u["n"], u["rejilla"], u["reglas"], 100 * u["cv"][str(u["n"])], 100 * u["exactitud"], 100 * u["balanceada"])
    cmz = r["celda_mezcla"]; macro(f, "mezclaAvanzar", miles(cmz[2])); macro(f, "mezclaSuave", miles(cmz[1]))
    macro(f, "filasUniforme", "\n".join(fila_uni(u) for u in uni))
    def buscar(k, esc, met):
        return next(u for u in uni if u["sensores"] == k and u["escala"] == esc and u["metodo"] == met)
    b = buscar(2, "mínimo y máximo", "registro de mayor grado")
    macro(f, "uniCursoAcc", "%.1f" % (100 * b["exactitud"])); macro(f, "uniCursoN", b["n"]); macro(f, "uniCursoAvanzar", b["avanzar"])
    macro(f, "uniCursoBal", "%.1f" % (100 * b["balanceada"]))
    b = buscar(2, "mínimo y máximo", "suma de fuerzas"); macro(f, "uniSumaAcc", "%.1f" % (100 * b["exactitud"])); macro(f, "uniSumaN", b["n"])
    b = buscar(2, "cuantiles", "registro de mayor grado"); macro(f, "uniCuantAcc", "%.1f" % (100 * b["exactitud"])); macro(f, "uniCuantN", b["n"]); macro(f, "uniCuantReglas", b["reglas"])
    b = buscar(2, "cuantiles", "suma de fuerzas"); macro(f, "uniCuantSumaAcc", "%.1f" % (100 * b["exactitud"]))
    b = buscar(4, "cuantiles", "suma de fuerzas"); macro(f, "uniCuatroMejor", "%.1f" % (100 * b["exactitud"]))
    macro(f, "uniTresMinMax", "%.1f" % (100 * buscar(4, "mínimo y máximo", "registro de mayor grado")["exactitud"]))
    macro(f, "uniTresCuant", "%.1f" % (100 * buscar(4, "cuantiles", "registro de mayor grado")["exactitud"]))
    mejor = max(uni, key=lambda u: u["exactitud"]); macro(f, "uniMejor", "%.1f" % (100 * mejor["exactitud"]))
    macro(f, "nAvanzarTe", miles(r["conteo_te"][2]))
    macro(f, "escIzqA", "%.3f" % r["escala_izq"][0]); macro(f, "escIzqB", "%.3f" % r["escala_izq"][1])
    n_nec = int(round(1 / (2 * r["escala_izq"][0]) + 1)); macro(f, "nNecesario", n_nec); macro(f, "reglasNecesarias", n_nec ** 2)
    sens = {k: np.array(v) for k, v in r["sens"].items()}; lst = list(np.round(des, 2)); i01 = lst.index(0.01); im01 = lst.index(-0.01)
    macro(f, "sensFmas", "%.1f" % (100 * sens["frontal"][i01])); macro(f, "sensFmenos", "%.1f" % (100 * sens["frontal"][im01]))
    macro(f, "sensBmas", "%.1f" % (100 * sens["izq_bajo"][i01])); macro(f, "sensBmenos", "%.1f" % (100 * sens["izq_bajo"][im01]))
    macro(f, "sensAmin", "%.1f" % (100 * sens["izq_alto"].min()))
    macro(f, "cercaAbajo", r["cerca_abajo"]); macro(f, "cercaArriba", r["cerca_arriba"])
    macro(f, "filasAncho", "\n".join("        %.3f & %.1f & %.1f & %.3f \\\\" % (dl_, 100 * a, 100 * fr, ce) for dl_, a, fr, ce in r["ancho"]))
    macro(f, "dentroBanda", "%.1f" % (100 * r["en_franja"])); macro(f, "compite", "%.1f" % (100 * r["compite"])); macro(f, "misma", "%.1f" % (100 * r["misma"]))
    macro(f, "nCompite", r["n_compite"])
    macro(f, "filasRuido", "\n".join("        %.3f & %.1f & %.1f & %.1f & %.1f & %.1f \\\\" % (q[0], 100 * q[1], 100 * q[2], 100 * q[3], 100 * q[4], 100 * q[5]) for q in r["ruido"]))
    rr = {round(q[0], 3): q for q in r["ruido"]}
    macro(f, "ruidoUno", "%.1f" % (100 * rr[0.01][1])); macro(f, "ruidoUnoMin", "%.1f" % (100 * rr[0.01][2])); macro(f, "ruidoUnoMax", "%.1f" % (100 * rr[0.01][3]))
    macro(f, "avCelda", r["av_celda"]); macro(f, "hojasSoloDT", r["hojas_solo_dt"]); macro(f, "accSoloDTt", "%.1f" % (100 * r["acc_solo_dt_t"]))
    macro(f, "mayT", "%.1f" % (100 * r["may_t"])); macro(f, "erroresSugeno", r["errores_sugeno"]); macro(f, "erroresFranja", r["errores_franja_f"])
    macro(f, "erroresSuave", r["errores_a_suave"]); macro(f, "accSugenoB", "%.1f" % (100 * r["acc_sugeno_b"]))
    macro(f, "distSoportes", " y ".join("%.2f" % R4d["soporte"][k] for k in dis))
    # registros que quedan fuera de los ejes en las figuras
    fuera2 = sum(int(np.sum((Xtr[:, k] < lim[SEN[k]][0]) | (Xtr[:, k] > lim[SEN[k]][1]))) for k in range(4))
    fuera3a = int(np.sum((Xtr[:, 0] < 0.4) | (Xtr[:, 0] > 2.6) | (Xtr[:, 1] < 0.3) | (Xtr[:, 1] > 2.0)))
    fuera3b = int(np.sum((Xtr[:, 2] < 0.8) | (Xtr[:, 2] > 3.2) | (Xtr[:, 3] < 0.3) | (Xtr[:, 3] > 3.2)))
    fuera5 = int(np.sum((X[ite, 0] < 0.4) | (X[ite, 0] > 2.0) | (X[ite, 1] < 0.3) | (X[ite, 1] > 1.6)))
    macro(f, "fueraHist", fuera2); macro(f, "fueraNubeA", fuera3a); macro(f, "fueraNubeB", fuera3b); macro(f, "fueraMapa", fuera5)
    macro(f, "accSugeno", "%.1f" % (100 * r["acc_sugeno"])); macro(f, "nIntermedio", r["n_intermedio"])
    t = r["temporal"]; macro(f, "tempCuatro", "%.1f" % (100 * t["4 sensores"][0])); macro(f, "tempDos", "%.1f" % (100 * t["2 sensores"][0]))
    ut = r["umbral_t"]; macro(f, "utDerecho", "%.4f" % ut["derecho"]); macro(f, "utTrasero", "%.4f" % ut["trasero"])
print("figuras y cifras listas")

