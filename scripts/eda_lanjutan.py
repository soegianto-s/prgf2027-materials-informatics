"""EDA lanjutan: UMAP, HDBSCAN, klaster hierarkis + validasi literatur top kandidat."""
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import umap
from hdbscan import HDBSCAN
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler

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
CAT8 = ["#2a78d6", "#1baf7a", "#eda100", "#008300", "#4a3aa7", "#e34948", "#e87ba4", "#eb6834"]
KELOMPOK_UTAMA = ["apatit_hidroksi", "trikalsium_fosfat", "tetrakalsium_fosfat",
                  "dikalsium_fosfat", "oktakalsium_fosfat", "monokalsium_fosfat"]

# validasi literatur (nilai eksperimen acuan, ditandai referensi)
LITERATUR = {
    "Hidroksiapatit Ca5(PO4)3OH": {"densitas": 3.16, "Eform_eV_atom": -3.15,
                                   "a_A": 9.42, "c_A": 6.88, "E_GPa": "80-120 (padat)"},
    "Fluorapatit Ca5(PO4)3F": {"densitas": 3.19, "Eform_eV_atom": -3.39,
                               "a_A": 9.37, "c_A": 6.88, "E_GPa": "~110 (padat)"},
    "b-TCP Ca3(PO4)2": {"densitas": 3.07, "Eform_eV_atom": -3.29,
                        "a_A": 10.44, "c_A": 37.38, "E_GPa": "~33 (padat)"},
    "Karbonat apatit (B-type)": {"densitas": 3.0, "Eform_eV_atom": None,
                                 "a_A": 9.38, "c_A": 6.90, "E_GPa": "~80 (padat)"},
    "TTCP Ca4(PO4)2O": {"densitas": 3.05, "Eform_eV_atom": None,
                        "a_A": 15.19, "c_A": None, "E_GPa": "~80 (padat)"},
}


def main():
    df = pd.read_csv(PROC / "dataset_deskriptor.csv")
    feat = ["densitas_final_gcm3", "volume_A3", "EN_avg", "EN_diff", "VEC", "berat_molekul", "ca_p_ratio"]
    dfp = df.dropna(subset=feat).copy()
    X = StandardScaler().fit_transform(dfp[feat])

    # ---- UMAP ----
    um = umap.UMAP(n_components=2, random_state=0, n_neighbors=30, min_dist=0.1).fit_transform(X)
    dfp["u1"], dfp["u2"] = um[:, 0], um[:, 1]
    fig, ax = plt.subplots(figsize=(7.5, 6))
    cmap = dict(zip(KELOMPOK_UTAMA, CAT8[:len(KELOMPOK_UTAMA)]))
    for k in KELOMPOK_UTAMA:
        d = dfp[dfp["kelompok"] == k]
        if len(d):
            ax.scatter(d["u1"], d["u2"], s=8, alpha=0.6, c=cmap[k], label=f"{k} ({len(d)})")
    ax.set_xlabel("UMAP 1"); ax.set_ylabel("UMAP 2")
    ax.set_title("UMAP: ruang desain material (7 deskriptor)")
    ax.legend(fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(FIGDIR / "fig_umap_kelompok.png", dpi=150)
    plt.close(fig)

    # ---- HDBSCAN ----
    hdb = HDBSCAN(min_cluster_size=30, min_samples=10).fit(X)
    hdb_lbl = hdb.labels_
    n_kl = len(set(hdb_lbl) - {-1})
    # ---- hierarkis (ward) ----
    agg = AgglomerativeClustering(n_clusters=5).fit(X)
    agg_lbl = agg.labels_
    # bandingkan dengan K-Means k=5 (seed 0)
    from sklearn.cluster import KMeans
    km_lbl = KMeans(n_clusters=5, n_init=10, random_state=0).fit_predict(X)

    hasil = [
        f"# Laporan EDA Lanjutan\n**Tanggal:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
        f"## Perbandingan Metode Klaster (n={len(dfp)})",
        f"- HDBSCAN (min_cluster=30): {n_kl} klaster + {int((hdb_lbl == -1).sum())} titik noise",
        f"- Hierarkis ward k=5: ARI vs K-Means = {adjusted_rand_score(agg_lbl, km_lbl):.3f}",
        f"- Silhouette hierarkis: {silhouette_score(X, agg_lbl, sample_size=2000, random_state=0):.3f} (K-Means: 0.552)",
        f"- Kesimpulan stabilitas: struktur klaster K-Means vs hierarkis {'KONSISTEN' if adjusted_rand_score(agg_lbl, km_lbl) > 0.7 else 'PERLU PERIKSA'}",
    ]

    # ---- validasi literatur top kandidat ----
    kd = pd.read_csv(PROC / "kandidat_top15_dedup.csv")
    hasil.append("## Validasi Top Kandidat vs Literatur Eksperimen\n")
    PETA = {
        ("Ca5P3HO13", "Ca10H2O26P6"): "Hidroksiapatit Ca5(PO4)3OH",
        ("Ca5P3O12F", "Ca10F2O24P6"): "Fluorapatit Ca5(PO4)3F",
        ("Ca3P2O8", "Ca3O8P2"): "b-TCP Ca3(PO4)2",
        ("Ca4P2O9", "Ca16O36P8"): "TTCP Ca4(PO4)2O",
    }
    baris = []
    for _, r in kd.head(8).iterrows():
        f = str(r["formula"])
        if "CO27" in f or "P6C" in f:
            lit = LITERATUR["Karbonat apatit (B-type)"]
        else:
            kunci = next((k for k in PETA if f in k), None)
            lit = LITERATUR[PETA[kunci]] if kunci else None
        rho_lit = lit["densitas"] if lit else None
        rho_kita = r["densitas_final_gcm3"]
        selisih = (rho_kita - rho_lit) / rho_lit * 100 if (rho_lit and pd.notna(rho_kita)) else None
        baris.append({
            "formula": f, "kelompok": r["kelompok"],
            "rho_kita": round(rho_kita, 3) if pd.notna(rho_kita) else None,
            "rho_literatur": rho_lit,
            "selisih_%": round(selisih, 1) if selisih is not None else None,
            "Eform_kita": r["Eform_eV_atom"],
            "Eform_lit_eV_atom": lit["Eform_eV_atom"] if lit else None,
        })
    hasil.append(pd.DataFrame(baris).round(3).to_markdown(index=False))
    hasil.append("\n*Literatur: nilai densitas standar (kristalografi); Eform literatur dari entalpi pembentukan standar (per atom).*")
    (REPORTS / "laporan_eda_lanjutan.md").write_text("\n".join(hasil), encoding="utf-8")
    print("\n".join(hasil).encode("ascii", "replace").decode("ascii"))


if __name__ == "__main__":
    main()
