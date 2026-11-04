"""Interpretabilitas (XAI): SHAP TreeExplainer pada model RF Eform & densitas + dependence plots."""
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance

from common import PROC, REPORTS

FIGDIR = REPORTS / "figures"
SURF, INK, SEC, MUT, GRID, BASE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "text.color": INK, "axes.labelcolor": INK, "axes.edgecolor": BASE,
    "xtick.color": MUT, "ytick.color": MUT, "grid.color": GRID,
    "font.size": 10, "axes.grid": True, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
})

# KOREKSI (2026-11-04 ronde 3): hanya 4 DOF komposisi independen (sistem 5 unsur)
FEATURES = ["ca_p_ratio", "frac_P", "frac_H", "frac_F"]


def muat_subset():
    df = pd.read_csv(PROC / "dataset_deskriptor.csv")
    sub = df[df["sumber"].isin(["MaterialsProject", "AFLOW", "OQMD"])].copy()
    tot = sub[["Ca", "P", "O", "H", "F"]].fillna(0).sum(axis=1)
    for el in ["Ca", "P", "O", "H", "F"]:
        sub[f"frac_{el}"] = sub[el].fillna(0) / tot
    return sub


FITUR_EN = {"ca_p_ratio": "Ca/P", "frac_P": "P fraction", "frac_H": "H fraction", "frac_F": "F fraction"}


def shap_untuk(sub, target, nama_file):
    fitur = [f for f in FEATURES if f != target]  # jangan pakai target sebagai fitur
    d = sub.dropna(subset=fitur + [target])
    X, y = d[fitur], d[target].values
    rf = RandomForestRegressor(n_estimators=400, random_state=0, n_jobs=-1).fit(X, y)
    explainer = shap.TreeExplainer(rf)
    sv = explainer.shap_values(X)
    # panel tunggal (sebelumnya subplots(1,2) menyisakan panel kiri kosong — reviewer ronde 5)
    Xd = X.rename(columns=FITUR_EN)
    shap.summary_plot(sv, Xd, plot_type="bar", show=False, max_display=10)
    plt.gcf().savefig(FIGDIR / f"fig_shap_bar_{nama_file}.png", dpi=150, bbox_inches="tight")
    plt.close("all")
    shap.summary_plot(sv, Xd, show=False, max_display=10)
    plt.gcf().savefig(FIGDIR / f"fig_shap_beeswarm_{nama_file}.png", dpi=150, bbox_inches="tight")
    plt.close("all")
    # dependence plot utk fitur teratas
    imp = np.abs(sv).mean(0)
    top2 = [fitur[i] for i in np.argsort(imp)[-2:][::-1]]
    for f in top2:
        shap.dependence_plot(FITUR_EN.get(f, f), sv, Xd, show=False)
        plt.gcf().savefig(FIGDIR / f"fig_shap_dep_{nama_file}_{f}.png", dpi=150, bbox_inches="tight")
        plt.close("all")
    perm = permutation_importance(rf, X, y, n_repeats=10, random_state=0)
    return d, rf, imp, top2, perm, fitur


def main():
    sub = muat_subset()
    laporan = [f"# Laporan Interpretasi Model (XAI)\n**Tanggal:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
               f"**Tahapan:** Bagian 9 panduan utama\n"]
    for target in ["Eform_eV_atom", "densitas_final_gcm3"]:
        nama = "eform" if "Eform" in target else "densitas"
        # Eform: subset pelatihan MP+OQMD (skala konsisten; AFLOW dikecualikan); densitas: semua sumber
        subs = sub[sub["sumber"].isin(["MaterialsProject", "OQMD"])] if nama == "eform" else sub
        d, rf, imp, top2, perm, fitur = shap_untuk(subs, target, nama)
        laporan.append(f"## SHAP: {target} (RandomForest, n={len(d)})")
        laporan.append(f"- Dua fitur paling berpengaruh (|SHAP| rata-rata): {top2[0]}, {top2[1]}")
        pi = pd.Series(perm.importances_mean, index=fitur).sort_values(ascending=False)
        laporan.append(f"- Permutation importance (cek silang): {pi.index[0]}, {pi.index[1]}, {pi.index[2]}")
        # arah pengaruh ca_p_ratio dan densitas via korelasi SHAP
        if "ca_p_ratio" in d.columns:
            idx = fitur.index("ca_p_ratio")
            sv = shap.TreeExplainer(rf).shap_values(d[fitur])
            corr = np.corrcoef(d["ca_p_ratio"], sv[:, idx])[0, 1]
            laporan.append(f"- Korelasi SHAP ca_p_ratio vs nilai ca_p_ratio: {corr:.2f} "
                           f"({'nilai Ca/P lebih tinggi -> prediksi lebih tinggi' if corr > 0 else 'nilai Ca/P lebih tinggi -> prediksi lebih rendah'})")
    laporan.append("## Gambar SHAP: reports/figures/fig_shap_*.png")
    (REPORTS / "laporan_xai.md").write_text("\n".join(laporan), encoding="utf-8")
    print("\n".join(laporan).encode("ascii", "replace").decode("ascii"))


if __name__ == "__main__":
    main()
