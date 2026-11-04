"""Propagasi ketidakpastian MCDM (reviewer ronde 4): Monte Carlo bobot + noise prediksi ML.

Per run (1000/skenario, seed tetap):
  - bobot ~ Dirichlet(alpha = w_manual * 20)  -> menjelajah sekitar bobot manual
  - Eform  += N(0, 0.297) eV/atom  (MAE CV model komposisi murni)
  - densitas += N(0, 0.307) g/cm3   (MAE CV model densitas)
  -> TOPSIS + VIKOR (v=0.5), peringkat rata-rata keduanya.

Agregat per KOMPOSISI TEREDUKSI (polimorf & kelipatan formula satu grup):
  median rank, persentil 5-95, fraksi masuk top-5/top-10.
Keluaran: laporan_montecarlo.md + fig_rank_mc.png.
"""
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import PROC, REPORTS
from mcdm import KRITERIA, WEIGHTS, muatan_formula, topsis, vikor

FIGDIR = REPORTS / "figures"
SURF, INK, SEC, MUT, GRID, BASE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "text.color": INK, "axes.labelcolor": INK, "axes.edgecolor": BASE,
    "xtick.color": MUT, "ytick.color": MUT, "grid.color": GRID,
    "font.size": 10, "axes.grid": True, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
})

N_RUNS = 1000
SIGMA_EFORM = 0.297   # MAE CV model komposisi murni (eV/atom)
SIGMA_RHO = 0.307     # MAE CV model densitas (g/cm3)
KONSENTRASI = 20.0    # konsentrasi Dirichlet: makin besar makin sempit sekitar bobot manual


def main():
    rng = np.random.default_rng(0)
    k = pd.read_csv(PROC / "kandidat_scaffold.csv")
    for c in ["Eform_eV_atom", "densitas_final_gcm3", "ca_p_ratio"]:
        k[c] = pd.to_numeric(k[c], errors="coerce")

    # filter identik mcdm.py
    q = k["formula"].map(muatan_formula)
    tak_dikenal = q.isna()
    tak_netral = q.notna() & (q.abs() > 1e-6)
    tanpa_o = ~k["ada_O"].fillna(False).astype(bool)
    k = k[~(tak_dikenal | tak_netral | tanpa_o)].copy().reset_index(drop=True)

    k["C_stabilitas"] = -k["Eform_eV_atom"]
    rho = k["densitas_final_gcm3"]
    k["C_densitas"] = np.where(rho.between(1.0, 3.2), 0.0,
                               -np.minimum((rho - 3.2).abs(), (rho - 1.0).abs()))
    k["C_cap"] = -np.abs(k["ca_p_ratio"] - 1.67)
    A0 = k[KRITERIA].values

    n = len(k)
    # per komposisi tereduksi: indeks entri tiap grup
    grup = k["komposisi_reduksi"]
    unik = pd.unique(grup)  # urutan kemunculan

    # statistik agregat
    akum_rank = {u: np.zeros(N_RUNS * len(WEIGHTS)) for u in unik}
    akum_top5 = {u: 0 for u in unik}
    akum_top10 = {u: 0 for u in unik}
    r = 0
    for wn, w_manual in WEIGHTS.items():
        alpha = w_manual * KONSENTRASI
        for _ in range(N_RUNS):
            w = rng.dirichlet(alpha)
            # noise prediksi: Eform & densitas (C1 & C2); Ca/P eksak
            A = A0.copy()
            A[:, 0] += rng.normal(0.0, SIGMA_EFORM, n)   # C_stabilitas = -Eform
            A[:, 1] += rng.normal(0.0, SIGMA_RHO, n)     # C_densitas (di dalam pita tetap 0)
            An = A / np.sqrt((A ** 2).sum(0))
            skor = topsis(An, w) + (-vikor(An, w))
            pr = (-skor).argsort().argsort() + 1  # peringkat entri 1..n (1 = terbaik)
            # per komposisi: ambil entri terbaik dalam grup
            for u in unik:
                idx = np.where(grup == u)[0]
                rmin = pr[idx].min()
                akum_rank[u][r] = rmin
                akum_top5[u] += (rmin <= 5)
                akum_top10[u] += (rmin <= 10)
            r += 1

    total = N_RUNS * len(WEIGHTS)
    stat = []
    for u in unik:
        rr = akum_rank[u]
        stat.append({
            "komposisi_reduksi": u,
            "median_rank": float(np.median(rr)),
            "p5_rank": float(np.percentile(rr, 5)),
            "p95_rank": float(np.percentile(rr, 95)),
            "pct_top5": akum_top5[u] / total * 100,
            "pct_top10": akum_top10[u] / total * 100,
        })
    st = pd.DataFrame(stat).merge(
        k[["komposisi_reduksi", "formula", "sumber", "kelompok", "Eform_eV_atom",
           "densitas_final_gcm3", "ca_p_ratio"]].groupby("komposisi_reduksi").first(),
        on="komposisi_reduksi", how="left").sort_values("median_rank")

    top15 = st.head(15)
    laporan = [f"# Laporan Monte Carlo MCDM — Propagasi Ketidakpastian\n"
               f"**Tanggal:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
               f"## Metode\n- {N_RUNS} run x {len(WEIGHTS)} skenario bobot = **{total} peringkat** "
               f"(TOPSIS+VIKOR, v=0.5; peringkat rata-rata keduanya).",
               f"- Bobot ~ Dirichlet(alpha = w_manual x {KONSENTRASI:.0f}) sekitar tiap skenario manual "
               f"{ {k_: [round(float(x),2) for x in v.tolist()] for k_, v in WEIGHTS.items()} }.",
               f"- Noise prediksi ML: Eform N(0, {SIGMA_EFORM}) eV/atom dan densitas N(0, {SIGMA_RHO}) "
               f"g/cm3 (MAE CV model komposisi murni) — mewakili ketidakpastian bila properti diprediksi "
               f"untuk komposisi baru; Ca/P eksak (stoikiometri).",
               f"- Peringkat per KOMPOSISI TEREDUKSI (polimorf/kelipatan satu grup): entri terbaik grup.",
               f"## Hasil Top-15 (median rank + interval 90%)\n",
               top15[["formula", "sumber", "kelompok", "median_rank", "p5_rank", "p95_rank",
                      "pct_top5", "pct_top10"]].round(1).to_markdown(index=False),
               f"\n## Gambar\n- `reports/figures/fig_rank_mc.png`"]
    (REPORTS / "laporan_montecarlo.md").write_text("\n".join(laporan), encoding="utf-8")

    # figur: interval rank top-15 (median + P5-P95), label formula pendek
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for i, row in enumerate(reversed(list(top15.itertuples()))):
        y = i
        ax.plot([row.p5_rank, row.p95_rank], [y, y], color=SEC, lw=4, alpha=0.55,
                solid_capstyle="round")
        ax.plot([row.median_rank], [y], "o", color=INK, ms=6)
    ax.set_yticks(range(len(top15)))
    ax.set_yticklabels([r.formula for r in reversed(list(top15.itertuples()))], fontsize=8)
    ax.set_xlabel("peringkat (1 = terbaik) — median + P5–P95 dari %d run" % total)
    ax.set_title("Ketidakpastian peringkat MCDM (bobot Dirichlet + noise MAE ML)")
    ax.axvspan(1, 5, color=BASE, alpha=0.25)
    ax.set_xlim(0.5, max(top15["p95_rank"]) * 1.08)
    fig.tight_layout()
    fig.savefig(FIGDIR / "fig_rank_mc.png", dpi=150)
    plt.close("all")
    print("\n".join(laporan).encode("ascii", "replace").decode("ascii"))


if __name__ == "__main__":
    main()
