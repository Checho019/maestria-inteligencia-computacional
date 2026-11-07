# -*- coding: utf-8 -*-
"""Genera las figuras del informe a partir de los CSV de resultados/."""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.graphics.tsaplots import plot_acf

AQUI = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(AQUI, "..", "resultados")
FIG = os.path.join(AQUI, "figuras")
os.makedirs(FIG, exist_ok=True)
plt.rcParams.update({"font.size": 9, "axes.grid": True, "grid.alpha": .3})

cl = pd.read_csv(os.path.join(RES, "sensibilidad_Clásico.csv"))
ne = pd.read_csv(os.path.join(RES, "sensibilidad_Neuronal_por_semillas.csv"))

ord_txt = {"(1, 0, 0)": "(1,0,0)", "(1, 0, 1)": "(1,0,1)", "(2, 0, 1)": "(2,0,1)"}
est_txt = {"(0, 0, 0, 0)": "sin", "(1, 0, 0, 7)": "(1,0,0)$_7$", "(1, 0, 1, 7)": "(1,0,1)$_7$"}
pc = cl.assign(o=cl["order"].map(ord_txt), s=cl["seasonal_order"].map(est_txt)).pivot(index="o", columns="s", values="RMSE medio")
pc = pc[["sin", "(1,0,0)$_7$", "(1,0,1)$_7$"]]
pn = ne.pivot(index="dy", columns="neuronas", values="RMSE medio (semillas)")

fig, ax = plt.subplots(1, 2, figsize=(9.2, 3.0))
for a, p, tit, xl, yl, vmax in ((ax[0], pc, "SARIMAX", "parte estacional", "orden $(p,d,q)$", 60),
                                (ax[1], pn, "NARX (media de tres semillas)", "neuronas", "$d_y$", None)):
    im = a.imshow(p.values, cmap="viridis_r", vmax=vmax)
    a.grid(False)
    a.set_xticks(range(p.shape[1])); a.set_xticklabels(p.columns)
    a.set_yticks(range(p.shape[0])); a.set_yticklabels(p.index)
    a.set_xlabel(xl); a.set_ylabel(yl); a.set_title(tit, fontsize=9)
    for i in range(p.shape[0]):
        for j in range(p.shape[1]):
            v = p.values[i, j]
            a.text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=8,
                   color="white" if (vmax is None and v > p.values.mean()) or (vmax and v > 52) else "black")
    fig.colorbar(im, ax=a, fraction=0.046, pad=0.04, label="RMSE medio")
plt.tight_layout()
plt.savefig(os.path.join(FIG, "fig01_sensibilidad.png"), dpi=200)
plt.close()

NOMBRES = {"Ingenuo estacional": "Ingenuo estacional", "Clásico": "SARIMAX", "Neuronal": "NARX"}
pr = pd.read_csv(os.path.join(RES, "pronosticos_prueba.csv"))
pr["error"] = pr["real"] - pr["pronostico"]

plt.figure(figsize=(9, 3.1))
for m, nombre in NOMBRES.items():
    d = pr[pr["modelo"] == m]
    rmse = np.sqrt((d["error"]**2).groupby(d["h"]).mean())
    plt.plot(rmse.index, rmse.values, marker="o", ms=3.5, label=nombre)
    print(f"{nombre}: RMSE {np.sqrt((d['error']**2).mean()):.2f}")
plt.xlabel("horizonte $h$"); plt.ylabel("RMSE")
plt.legend(ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.0), frameon=False)
plt.tight_layout()
plt.savefig(os.path.join(FIG, "fig02_rmse_horizonte.png"), dpi=200)
plt.close()

for m, archivo in (("Clásico", "fig03a_residuos_sarimax.png"), ("Neuronal", "fig03b_residuos_narx.png")):
    nombre = NOMBRES[m]
    e = pr[pr["modelo"] == m].sort_values(["origen", "h"])["error"].values
    fig, ax = plt.subplots(1, 4, figsize=(12, 2.6))
    ax[0].plot(e, lw=.7); ax[0].set_title(f"Residuos de {nombre}")
    ax[1].hist(e, bins=30); ax[1].set_title("Histograma")
    stats.probplot(e, dist="norm", plot=ax[2])
    ax[2].set_title("Q-Q normal"); ax[2].set_xlabel("cuantiles teóricos"); ax[2].set_ylabel("valores ordenados")
    plot_acf(e, lags=40, ax=ax[3]); ax[3].set_title("Autocorrelación")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG, archivo), dpi=200)
    plt.close()
print("listo")
