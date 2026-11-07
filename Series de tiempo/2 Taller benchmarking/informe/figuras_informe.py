# -*- coding: utf-8 -*-
"""Genera la figura de sensibilidad del informe a partir de los CSV de resultados/."""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

AQUI = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(AQUI, "..", "resultados")
plt.rcParams.update({"font.size": 9})

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
os.makedirs(os.path.join(AQUI, "figuras"), exist_ok=True)
plt.savefig(os.path.join(AQUI, "figuras", "fig01_sensibilidad.png"), dpi=200)
print("listo")
