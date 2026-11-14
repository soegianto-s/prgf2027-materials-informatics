"""Regenerasi Fig 1 (PCA) & Fig 3 (t-SNE) dari dataset konsolidasi PENUH.

Alasan: versi lama eda.py men-sampling 1500 entri untuk t-SNE (legend 34/125/1183/158
tidak cocok dengan Tabel 1) dan PCA tanpa keterangan n. Skrip ini menggambar ulang
kedua figur pada seluruh entri (tanpa sampling), mencetak semua angka untuk caption
manuskrip (jumlah per sumber, per keluarga, varians PCA, fraksi tetangga sesumber),
dan menimpa file PNG dengan nama yang sama (dpi 150).
"""
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import PROC, REPORTS

FIGDIR = REPORTS / "figures"
FIGDIR.mkdir(exist_ok=True, parents=True)

SURF, INK, SEC, MUT, GRID, BASE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "text.color": INK, "axes.labelcolor": INK, "axes.edgecolor": BASE,
    "xtick.color": MUT, "ytick.color": MUT, "grid.color": GRID,
    "font.size": 10, "axes.grid": True, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
})
CAT8 = ["#2a78d6", "#1baf7a", "#eda100", "#008300", "#4a3aa7", "#e34948", "#e87ba4", "#eb6834"]
KELOMPOK_UTAMA = ["apatit_hidroksi", "apatit_fluor", "trikalsium_fosfat", "tetrakalsium_fosfat",
                  "dikalsium_fosfat", "oktakalsium_fosfat", "pirofosfat", "monokalsium_fosfat"]
KELOMPOK_EN = {"apatit_hidroksi": "Hydroxyapatite family", "apatit_fluor": "Fluorapatite",
               "trikalsium_fosfat": "TCP", "tetrakalsium_fosfat": "TTCP",
               "dikalsium_fosfat": "DCP", "oktakalsium_fosfat": "OCP",
               "pirofosfat": "Pyrophosphate", "monokalsium_fosfat": "MCP"}
SUMBER_URUT = ["MaterialsProject", "AFLOW", "COD", "PubChem", "OQMD"]

df = pd.read_csv(PROC / "dataset_deskriptor.csv")
print("baris dataset_deskriptor.csv:", len(df))
print("per sumber (Tabel 1 pembanding):")
print(df["sumber"].value_counts().reindex(SUMBER_URUT).to_string())

feat = ["densitas_final_gcm3", "volume_A3", "EN_avg", "berat_molekul", "ca_p_ratio"]
dfp = df.dropna(subset=feat).copy()
print("n PCA/t-SNE (dropna 5 fitur):", len(dfp))
print("per sumber pada dfp:")
print(dfp["sumber"].value_counts().reindex(SUMBER_URUT).to_string())
print("per keluarga pada dfp:")
print(dfp["kelompok"].value_counts().to_string())

Xp = StandardScaler().fit_transform(dfp[feat])
pca = PCA(n_components=2, random_state=0).fit(Xp)
dfp["PC1"], dfp["PC2"] = pca.transform(Xp).T
ev = pca.explained_variance_ratio_
print(f"varians PCA: PC1 {ev[0]*100:.1f}% + PC2 {ev[1]*100:.1f}% = {ev.sum()*100:.1f}%")

fig, ax = plt.subplots(figsize=(7.5, 6))
for k in KELOMPOK_UTAMA + ["lain"]:
    m = dfp["kelompok"] == k if k != "lain" else ~dfp["kelompok"].isin(KELOMPOK_UTAMA)
    d = dfp[m]
    if len(d):
        c = dict(zip(KELOMPOK_UTAMA, CAT8[:len(KELOMPOK_UTAMA)])).get(k, "#898781")
        lab = KELOMPOK_EN.get(k, k) if k != "lain" else "other"
        ax.scatter(d["PC1"], d["PC2"], s=10, alpha=0.65, c=c, label=f"{lab} ({len(d)})")
ax.set_xlabel(f"PC1 ({ev[0] * 100:.1f}%)")
ax.set_ylabel(f"PC2 ({ev[1] * 100:.1f}%)")
ax.set_title(f"Design space: PCA (5 non-collinear descriptors, n = {len(dfp):,})")
ax.legend(fontsize=7, frameon=False, ncol=2)
fig.tight_layout()
fig.savefig(FIGDIR / "fig_pca_kelompok.png", dpi=150)
plt.close(fig)
print("fig_pca_kelompok.png disimpan")

# t-SNE SEMUA entri (tanpa sampling)
Xs = StandardScaler().fit_transform(dfp[feat])
ts = TSNE(n_components=2, perplexity=30, random_state=0, init="pca").fit_transform(Xs)
dfp["t1"], dfp["t2"] = ts[:, 0], ts[:, 1]
fig, ax = plt.subplots(figsize=(7.5, 6))
for i, s in enumerate(SUMBER_URUT):
    d = dfp[dfp["sumber"] == s]
    if len(d):
        ax.scatter(d["t1"], d["t2"], s=12, alpha=0.7, c=CAT8[i % 8], label=f"{s} ({len(d)})")
ax.set_xlabel("t-SNE 1"); ax.set_ylabel("t-SNE 2")
ax.set_title(f"Source-bias check: t-SNE colored by database (n = {len(dfp):,})")
ax.legend(fontsize=8, frameon=False)
fig.tight_layout()
fig.savefig(FIGDIR / "fig_tsne_sumber.png", dpi=150)
plt.close(fig)
print("fig_tsne_sumber.png disimpan")

nn = NearestNeighbors(n_neighbors=6).fit(Xs)
_, idx = nn.kneighbors(Xs)
tetangga = dfp["sumber"].values[idx][:, 1:]  # buang diri sendiri
frac = (tetangga == dfp["sumber"].values[:, None]).mean()
print(f"fraksi tetangga terdekat sesumber (k=5, n={len(dfp)}): {frac*100:.1f}%")
