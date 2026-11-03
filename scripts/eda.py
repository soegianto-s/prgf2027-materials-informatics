"""Eksplorasi ruang desain material (EDA): korelasi, VIF, PCA, t-SNE, klaster, rujukan, bias sumber.

Output: data/reports/laporan_eda.md + data/reports/figures/*.png
"""
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.manifold import TSNE
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler

from common import PROC, REPORTS

FIGDIR = REPORTS / "figures"
FIGDIR.mkdir(exist_ok=True, parents=True)

# ---- gaya visual (palet dataviz teruji, mode terang) ----
SURF, INK, SEC, MUT, GRID, BASE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "text.color": INK, "axes.labelcolor": INK, "axes.edgecolor": BASE,
    "xtick.color": MUT, "ytick.color": MUT, "grid.color": GRID,
    "font.size": 10, "axes.grid": True, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
})
CAT8 = ["#2a78d6", "#1baf7a", "#eda100", "#008300", "#4a3aa7", "#e34948", "#e87ba4", "#eb6834"]
DIV_CMAP = LinearSegmentedColormap.from_list("div", ["#2a78d6", "#f0efec", "#e34948"])

# urutan tetap kelompok (bukan berdasarkan frekuensi)
KELOMPOK_UTAMA = ["apatit_hidroksi", "apatit_fluor", "trikalsium_fosfat", "tetrakalsium_fosfat",
                  "dikalsium_fosfat", "oktakalsium_fosfat", "pirofosfat", "monokalsium_fosfat"]
SUMBER_URUT = ["MaterialsProject", "AFLOW", "COD", "PubChem", "OQMD"]


def warna_kelompok(df):
    cmap = dict(zip(KELOMPOK_UTAMA, CAT8[:len(KELOMPOK_UTAMA)]))
    def f(k):
        return cmap.get(k, "#898781")  # sisanya = "lainnya" (abu)
    return df["kelompok"].map(f)


def main():
    df = pd.read_csv(PROC / "dataset_deskriptor.csv")
    temuan = []

    # ===== 1. korelasi (subset pemodelan MP+AFLOW) =====
    sub = df[df["sumber"].isin(["MaterialsProject", "AFLOW"])].copy()
    cols = ["Eform_eV_atom", "densitas_final_gcm3", "bandgap_eV", "volume_A3",
            "EN_avg", "EN_diff", "VEC", "berat_molekul", "ca_p_ratio"]
    corr = sub[cols].corr()
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(corr.values, cmap=DIV_CMAP, vmin=-1, vmax=1)
    ax.set_xticks(range(len(cols))); ax.set_xticklabels(cols, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(cols))); ax.set_yticklabels(cols, fontsize=8)
    for i in range(len(cols)):
        for j in range(len(cols)):
            v = corr.values[i, j]
            if i != j:
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=7, color=INK)
    fig.colorbar(im, ax=ax, shrink=0.8)
    ax.set_title("Korelasi Pearson antar deskriptor (subset MP+AFLOW)", fontsize=10)
    fig.tight_layout()
    fig.savefig(FIGDIR / "fig_korelasi.png", dpi=150)
    plt.close(fig)

    # pasangan redundan r>0.85
    pasangan = []
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            r = corr.values[i, j]
            if abs(r) > 0.85:
                pasangan.append(f"- {cols[i]} vs {cols[j]}: r = {r:.3f} -> redundan (pilih satu wakil)")
    temuan.append("## Korelasi & Multikolinearitas")
    temuan.append("\n".join(pasangan) if pasangan else "- Tidak ada pasangan dengan |r| > 0.85")

    # ===== 2. VIF =====
    vif_cols = ["Eform_eV_atom", "densitas_final_gcm3", "volume_A3",
                "EN_avg", "EN_diff", "VEC", "berat_molekul", "ca_p_ratio"]
    vif_df = sub[vif_cols].dropna()
    Xv = vif_df.values
    vifs = {}
    for k, c in enumerate(vif_cols):
        y = Xv[:, k]
        Xo = np.delete(Xv, k, axis=1)
        lr = LinearRegression().fit(Xo, y)
        r2 = lr.score(Xo, y)
        vifs[c] = 1 / (1 - r2) if r2 < 0.999 else np.inf
    temuan.append("## VIF (subset pemodelan, n=%d)" % len(vif_df))
    temuan.append("\n".join(f"- {c}: {v:.1f}" for c, v in vifs.items()))

    # ===== 3. PCA (seluruh dataset, deskriptor komposisi+sel) =====
    feat = ["densitas_final_gcm3", "volume_A3", "EN_avg", "EN_diff", "VEC", "berat_molekul", "ca_p_ratio"]
    dfp = df.dropna(subset=feat).copy()
    Xp = StandardScaler().fit_transform(dfp[feat])
    pca = PCA(n_components=2, random_state=0).fit(Xp)
    dfp["PC1"], dfp["PC2"] = pca.transform(Xp).T
    ev = pca.explained_variance_ratio_
    fig, ax = plt.subplots(figsize=(7.5, 6))
    for k in KELOMPOK_UTAMA + ["lain"]:
        m = dfp["kelompok"] == k if k != "lain" else ~dfp["kelompok"].isin(KELOMPOK_UTAMA)
        d = dfp[m]
        if len(d):
            c = dict(zip(KELOMPOK_UTAMA, CAT8[:len(KELOMPOK_UTAMA)])).get(k, "#898781")
            lab = k if k != "lain" else "lainnya"
            ax.scatter(d["PC1"], d["PC2"], s=10, alpha=0.65, c=c, label=f"{lab} ({len(d)})")
    ax.set_xlabel(f"PC1 ({ev[0] * 100:.1f}%)")
    ax.set_ylabel(f"PC2 ({ev[1] * 100:.1f}%)")
    ax.set_title("Ruang desain material: PCA (7 deskriptor)")
    ax.legend(fontsize=7, frameon=False, ncol=2)
    fig.tight_layout()
    fig.savefig(FIGDIR / "fig_pca_kelompok.png", dpi=150)
    plt.close(fig)
    temuan.append(f"## PCA: PC1 {ev[0] * 100:.1f}% + PC2 {ev[1] * 100:.1f}% = {ev.sum() * 100:.1f}% varians")

    # ===== 4. t-SNE diwarnai sumber (cek bias sumber) =====
    samp = dfp.sample(min(1500, len(dfp)), random_state=0)
    Xs = StandardScaler().fit_transform(samp[feat])
    ts = TSNE(n_components=2, perplexity=30, random_state=0, init="pca").fit_transform(Xs)
    samp["t1"], samp["t2"] = ts[:, 0], ts[:, 1]
    fig, ax = plt.subplots(figsize=(7.5, 6))
    for i, s in enumerate(SUMBER_URUT):
        d = samp[samp["sumber"] == s]
        if len(d):
            ax.scatter(d["t1"], d["t2"], s=12, alpha=0.7, c=CAT8[i % 8], label=f"{s} ({len(d)})")
    ax.set_xlabel("t-SNE 1"); ax.set_ylabel("t-SNE 2")
    ax.set_title("Cek bias sumber: t-SNE diwarnai basis data")
    ax.legend(fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(FIGDIR / "fig_tsne_sumber.png", dpi=150)
    plt.close(fig)
    # kuantifikasi: fraksi tetangga terdekat sesumber (k=5) -> makin tinggi makin terpisah
    from sklearn.neighbors import NearestNeighbors
    nn = NearestNeighbors(n_neighbors=6).fit(Xs)
    _, idx = nn.kneighbors(Xs)
    src = samp["sumber"].values
    sama = np.mean([np.mean(src[idx[i, 1:]] == src[i]) for i in range(len(samp))])
    temuan.append(f"## Bias sumber: fraksi tetangga-terdekat (k=5) sesumber = {sama:.2f} (mendekati 1 = klaster terbentuk oleh sumber, bukan sifat)")

    # ===== 5. K-Means + uji stabilitas =====
    ks = range(3, 9)
    sils = {}
    labels = {}
    for k in ks:
        km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(Xp)
        labels[k] = km.labels_
        sils[k] = silhouette_score(Xp, km.labels_, sample_size=2000, random_state=0)
    kbest = max(sils, key=sils.get)
    temuan.append("## Klaster K-Means (silhouette): " + ", ".join(f"k={k}:{sils[k]:.3f}" for k in ks))
    ari = adjusted_rand_score(labels[kbest], KMeans(n_clusters=kbest, n_init=10, random_state=1).fit_predict(Xp))
    dfp["klaster"] = labels[kbest]
    temuan.append(f"- k terbaik = {kbest}; stabilitas ARI antar-seed = {ari:.3f}")
    prof = dfp.groupby("klaster")[feat + ["kelompok"]].agg(
        lambda s: s.mode().iloc[0] if s.dtype == object else s.mean())
    temuan.append("## Profil Klaster (rerata deskriptor, kelompok dominan)")
    temuan.append(prof.round(2).to_markdown())
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(list(ks), [sils[k] for k in ks], marker="o", lw=1.5, c="#2a78d6", markersize=6)
    ax.set_xlabel("jumlah klaster k"); ax.set_ylabel("silhouette")
    ax.set_title("Pemilihan jumlah klaster")
    fig.tight_layout()
    fig.savefig(FIGDIR / "fig_silhouette.png", dpi=150)
    plt.close(fig)

    # ===== 6. perbandingan kelompok =====
    grp = dfp.groupby("kelompok")["densitas_final_gcm3"].agg(["count", "mean", "std"]).round(3)
    grp = grp.reindex(KELOMPOK_UTAMA + sorted(set(dfp["kelompok"]) - set(KELOMPOK_UTAMA)))
    temuan.append("## Densitas per Kelompok Material (g/cm3)")
    temuan.append(grp.to_markdown())
    fig, ax = plt.subplots(figsize=(8, 5))
    boxes = [dfp[dfp["kelompok"] == k]["densitas_final_gcm3"].dropna() for k in KELOMPOK_UTAMA]
    bp = ax.boxplot(boxes, labels=KELOMPOK_UTAMA, patch_artist=True, widths=0.6)
    for patch, c in zip(bp["boxes"], CAT8[:len(KELOMPOK_UTAMA)]):
        patch.set_facecolor(c); patch.set_alpha(0.75)
    for med in bp["medians"]:
        med.set_color(INK)
    ax.set_ylabel("densitas (g/cm3)")
    ax.set_title("Sebaran densitas per kelompok material")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(FIGDIR / "fig_densitas_kelompok.png", dpi=150)
    plt.close(fig)

    # ===== 7. material rujukan vs literatur =====
    temuan.append("## Material Rujukan vs Literatur")
    hap = dfp[(dfp["kelompok"] == "apatit_hidroksi") & (dfp["sumber"] == "COD")]
    tcp = dfp[(dfp["kelompok"] == "trikalsium_fosfat") & (dfp["sumber"] == "COD")]
    temuan.append(f"- HAp (COD, n={len(hap)}): densitas {hap['densitas_final_gcm3'].mean():.2f} g/cm3 "
                  f"(literatur 3.16); volume sel {hap['volume_A3'].mean():.0f} A3")
    temuan.append(f"- TCP (COD, n={len(tcp)}): densitas {tcp['densitas_final_gcm3'].mean():.2f} g/cm3 "
                  f"(literatur b-TCP 3.07); volume sel {tcp['volume_A3'].mean():.0f} A3")
    # MP & AFLOW rujukan
    for src in ["MaterialsProject", "AFLOW"]:
        d = dfp[(dfp["kelompok"].isin(["apatit_hidroksi", "trikalsium_fosfat"])) & (dfp["sumber"] == src)]
        if len(d):
            temuan.append(f"- {src}: " + "; ".join(
                f"{r['formula']} rho={r['densitas_final_gcm3']:.2f}, Eform={r['Eform_eV_atom']:.2f}"
                for _, r in d.iterrows()))

    # ===== 8. perbandingan antar sumber utk komposisi sama =====
    kunci = ["Ca", "P", "O", "H", "F"]
    dfp["komposisi_key"] = dfp[kunci].round(1).astype(str).agg("-".join, axis=1)
    multi = dfp.groupby("komposisi_key")["sumber"].nunique()
    kompos_bersama = multi[multi >= 2].index
    catatan = []
    for ck in kompos_bersama[:30]:
        d = dfp[dfp["komposisi_key"] == ck]
        dens = d.groupby("sumber")["densitas_final_gcm3"].mean().dropna()
        if len(dens) >= 2 and dens.max() > 0:
            selisih = (dens.max() - dens.min()) / dens.mean()
            if selisih > 0.15:
                catatan.append(f"- {ck} ({d['formula'].iloc[0]}): selisih densitas antar sumber {selisih * 100:.0f}% "
                               f"-> periksa metode perhitungan")
    temuan.append("## Perbandingan Antar Basis Data (bias sumber)")
    temuan.append("\n".join(catatan[:15]) if catatan else "- Tidak ada selisih densitas > 15% antar sumber")

    # ===== hipotesis untuk pemodelan =====
    temuan.append("## Hipotesis untuk Pemodelan")
    temuan.append("- H1: Eform berkorelasi dengan EN_diff dan ca_p_ratio (stabilitas ditentukan komposisi).")
    temuan.append("- H2: Densitas dapat diprediksi dari berat molekul, volume sel, dan EN_avg.")
    temuan.append("- H3: Kelompok apatit_hidroksi memiliki densitas paling dekat ke tulang kortikal.")

    laporan = f"""# Laporan Eksplorasi Ruang Desain Material
**Tanggal:** {time.strftime('%Y-%m-%d %H:%M:%S')} | **Tahapan:** Bagian 4-5 panduan utama

{chr(10).join(temuan)}

## Gambar
- korelasi: `reports/figures/fig_korelasi.png`
- PCA: `reports/figures/fig_pca_kelompok.png`
- t-SNE sumber: `reports/figures/fig_tsne_sumber.png`
- silhouette: `reports/figures/fig_silhouette.png`
- densitas kelompok: `reports/figures/fig_densitas_kelompok.png`
"""
    (REPORTS / "laporan_eda.md").write_text(laporan, encoding="utf-8")
    print(laporan.encode("ascii", "replace").decode("ascii"))


if __name__ == "__main__":
    main()
