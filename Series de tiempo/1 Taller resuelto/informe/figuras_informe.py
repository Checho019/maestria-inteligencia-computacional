# -*- coding: utf-8 -*-
"""Genera las figuras, la tabla general y las cifras del informe a partir de experimentos.json."""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

AQUI = os.path.dirname(os.path.abspath(__file__))
E = json.load(open(os.path.join(AQUI, "experimentos.json"), encoding="utf-8"))
COLOR = {"SARIMAX": "tab:green", "NARX": "tab:purple", "NAR": "tab:red"}
plt.rcParams.update({"axes.grid": True, "grid.alpha": .3, "font.size": 9})
os.makedirs(os.path.join(AQUI, "figuras"), exist_ok=True)

h1 = lambda n, m: E[n]["tabla1"]["RMSE"][m]
hH = lambda n, m: E[n]["tablaH"]["RMSE"][m]
dm = lambda n: E[n]["dm"]["SARIMAX|NARX"]

# ---- Tabla general ----
FILAS = [("", "Base", "base"), ("1", "$(x_t-18)^2$ en SARIMAX", "g1_exog"), ("2", "$\\kappa=0$", "g2_lineal"),
         ("3", "$d_y=3$", "g3_dy3"), ("3", "$d_y=7$", "g3_dy7"), ("3", "$d_y=28$", "g3_dy28")]
for n in ("4", "64", "32-16", "12"):
    for l2, et in (("0", "0"), ("1e-3", "10^{-3}")):
        FILAS.append(("4", f"[{n.replace('-', ', ')}], $\\lambda={et}$", f"g4_n{n}_l2{l2}"))
FILAS = FILAS[:6] + [f for f in FILAS[6:] if "n12" not in f[2]] + [f for f in FILAS[6:] if "n12" in f[2]]
FILAS += [("5", "$\\sigma=1$", "g5_sigma1"), ("5", "$\\sigma=6$", "g5_sigma6"), ("6", "sin quitar tendencia", "g6_sin_quitar")]
FILAS += [("7", f"semilla {s}", f"g7_semilla{s}") for s in range(1, 6)]
p_txt = lambda p: "$<0.001$" if p < 0.001 else f"{p:.3f}"
lineas = []
previo = None
for g, et, n in FILAS:
    if previo is not None and g != previo:
        lineas.append("        \\midrule")
    previo = g
    d, p = dm(n)
    lineas.append(f"        {g} & {et} & {h1(n,'SARIMAX'):.3f} & {h1(n,'NARX'):.3f} & {h1(n,'NAR'):.3f} & "
                  f"{hH(n,'SARIMAX'):.3f} & {hH(n,'NARX'):.3f} & ${d:.2f}$ & {p_txt(p)} \\\\")
open(os.path.join(AQUI, "tabla_experimentos.tex"), "w", encoding="utf-8").write("\n".join(lineas) + "\n")

# ---- Cifras para el texto ----
sem = ["base"] + [f"g7_semilla{s}" for s in range(1, 6)]
dif = np.array([h1(n, "SARIMAX") - h1(n, "NARX") for n in sem])
c = {"difSemMedia": f"{dif.mean():.2f}", "difSemDesv": f"{dif.std(ddof=1):.2f}",
     "nSemSig": str(sum(dm(n)[1] < 0.05 and dm(n)[0] > 0 for n in sem)),
     "sigBase": f"{E['base']['sar']['params']['sigma2']:.1f}", "sigUno": f"{E['g5_sigma1']['sar']['params']['sigma2']:.1f}",
     "sigSeis": f"{E['g5_sigma6']['sar']['params']['sigma2']:.1f}", "sigCuad": f"{E['g1_exog']['sar']['params']['sigma2']:.1f}",
     "aicBase": f"{E['base']['sar']['aic']:.1f}", "aicCuad": f"{E['g1_exog']['sar']['aic']:.1f}",
     "kapCuad": f"{E['g1_exog']['sar']['params']['x2']:.3f}",
     "sesgoBase": f"{E['base']['sesgo']['NARX']:.2f}", "sesgoSin": f"{E['g6_sin_quitar']['sesgo']['NARX']:.2f}",
     "sesgoNarSin": f"{E['g6_sin_quitar']['sesgo']['NAR']:.2f}", "epSin": str(len(E['g6_sin_quitar']['hist_narx']['loss'])),
     "pBase": str(E['base']['p_narx'])}
for n, k in (("g4_n64_l20", "SesentaCero"), ("g4_n32-16_l20", "DosCapasCero"), ("g4_n4_l21e-3", "CuatroL"), ("base", "Base")):
    h = E[n]["hist_narx"]
    c[f"ep{k}"] = str(len(h["loss"])); c[f"tr{k}"] = f"{min(h['loss']):.3f}"; c[f"va{k}"] = f"{min(h['val']):.3f}"
    c[f"par{k}"] = str(E[n]["p_narx"])
with open(os.path.join(AQUI, "cifras.tex"), "w", encoding="utf-8") as f:
    for k, v in c.items():
        f.write(f"\\newcommand{{\\{k}}}{{{v}}}\n")

# ---- Figura 1. Retardos y ruido ----
fig, ax = plt.subplots(1, 2, figsize=(9.2, 2.8))
dys = [3, 7, 14, 28]; nd = ["g3_dy3", "g3_dy7", "base", "g3_dy28"]
for m in ("NARX", "NAR"):
    ax[0].plot(dys, [h1(n, m) for n in nd], "o-", c=COLOR[m], label=f"{m}, a un paso")
ax[0].plot(dys, [hH(n, "NARX") for n in nd], "o--", c=COLOR["NARX"], alpha=.6, label="NARX, a 14 pasos")
ax[0].axhline(h1("base", "SARIMAX"), c=COLOR["SARIMAX"], lw=1.2, label="SARIMAX, a un paso")
ax[0].set_xscale("log", base=2); ax[0].set_xticks(dys); ax[0].set_xticklabels(dys)
ax[0].set_xlabel("$d_y$ (retardos de la salida)"); ax[0].set_ylabel("RMSE en prueba"); ax[0].legend(fontsize=7)
ax[0].axvline(7, c="0.6", ls=":", lw=1)
sig = [1, 3, 6]; ns = ["g5_sigma1", "base", "g5_sigma6"]
for m in ("SARIMAX", "NARX"):
    ax[1].plot(sig, [h1(n, m) for n in ns], "o-", c=COLOR[m], label=m)
ax[1].set_xticks(sig); ax[1].set_xlabel("$\\sigma$ del ruido"); ax[1].set_ylabel("RMSE a un paso en prueba"); ax[1].legend(fontsize=7)
plt.tight_layout(); plt.savefig(os.path.join(AQUI, "figuras", "fig01_retardos_ruido.png"), dpi=200); plt.close()

# ---- Figura 2. Curvas de aprendizaje ----
cur = [("g4_n4_l21e-3", "[4], $\\lambda=10^{-3}$"), ("base", "[12], $\\lambda=10^{-4}$"),
       ("g4_n64_l20", "[64], $\\lambda=0$"), ("g4_n32-16_l20", "[32, 16], $\\lambda=0$")]
fig, ax = plt.subplots(1, 4, figsize=(9.6, 2.3), sharey=True)
for a, (n, t) in zip(ax, cur):
    h = E[n]["hist_narx"]
    a.plot(h["loss"], c="tab:blue", lw=1, label="entrenamiento"); a.plot(h["val"], c="tab:orange", lw=1, label="validación")
    a.set_yscale("log"); a.set_title(t, fontsize=8); a.set_xlabel("época")
ax[0].set_ylabel("pérdida (MSE)"); ax[0].legend(fontsize=7)
plt.tight_layout(); plt.savefig(os.path.join(AQUI, "figuras", "fig02_curvas_aprendizaje.png"), dpi=200); plt.close()
print("listo")
