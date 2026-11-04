"""Sensitivitas MCDM: pembobotan entropi Shannon + uji konsistensi peringkat (Spearman).

Revisi ronde 4: 3 kriteria saja (C4/C5 ditarik) + filter kenetralan muatan yang
SAMA dengan mcdm.py (kolam kandidat identik). Entropi dihitung pada 3 kriteria
lengkap (tanpa imputasi — kini memang tidak ada imputasi). Korelasi Spearman
terhadap pembobotan manual adalah uji konsistensi INTERNAL, bukan validasi
independen; uji ketidakpastian sesungguhnya ada di mcdm_montecarlo.py.
"""
import time

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from common import PROC, REPORTS
from mcdm import KRITERIA, muatan_formula, topsis, vikor


def bobot_entropi(A):
    """Pembobotan entropi Shannon.

    p_ij = proporsi tiap kolom (jumlah = 1) -> e_j = -sum(p ln p)/ln(n) in [0,1].
    """
    A = np.where(A, A, 0.0)
    amin, amax = A.min(0), A.max(0)
    P = (A - amin) / (amax - amin + 1e-12)
    P = np.clip(P, 1e-12, 1.0)
    p = P / P.sum(0)
    e = -(p * np.log(p)).sum(0) / np.log(len(A))
    d = np.clip(1 - e, 0.0, None)
    return d / d.sum(), e


def main():
    k = pd.read_csv(PROC / "kandidat_scaffold.csv")
    for c in ["Eform_eV_atom", "densitas_final_gcm3", "ca_p_ratio"]:
        k[c] = pd.to_numeric(k[c], errors="coerce")

    # filter identik dengan mcdm.py: muatan netral + mengandung O
    q = k["formula"].map(muatan_formula)
    tak_dikenal = q.isna()
    tak_netral = q.notna() & (q.abs() > 1e-6)
    tanpa_o = ~k["ada_O"].fillna(False).astype(bool)
    k = k[~(tak_dikenal | tak_netral | tanpa_o)].copy()
    n_kolam = len(k)

    k["C_stabilitas"] = -k["Eform_eV_atom"]
    rho = k["densitas_final_gcm3"]
    k["C_densitas"] = np.where(rho.between(1.0, 3.2), 0.0,
                               -np.minimum((rho - 3.2).abs(), (rho - 1.0).abs()))
    k["C_cap"] = -np.abs(k["ca_p_ratio"] - 1.67)
    A = k[KRITERIA].values
    An = A / np.sqrt((A ** 2).sum(0))

    w_ent, e = bobot_entropi(An)
    skor_ent_top = topsis(An, w_ent)
    skor_ent_vik = -vikor(An, w_ent)
    k["skor_entropi"] = (skor_ent_top + skor_ent_vik) / 2
    k["peringkat_entropi"] = k["skor_entropi"].rank(ascending=False)

    # bandingkan dengan peringkat manual (TOPSIS+VIKOR, 3 skenario) yang tersimpan
    lama = pd.read_csv(PROC / "kandidat_ranking.csv")
    k = k.merge(lama.drop_duplicates("id")[["id", "peringkat_rerata"]], on="id", how="left")
    rho, p = spearmanr(k["peringkat_entropi"], k["peringkat_rerata"])

    top10_ent = k.sort_values("peringkat_entropi").head(10)[["formula", "sumber", "kelompok"]]
    laporan = f"""# Laporan Sensitivitas MCDM — Pembobotan Entropi
**Tanggal:** {time.strftime('%Y-%m-%d %H:%M:%S')}

## Bobot Entropi (data-driven, 3 kriteria lengkap tanpa imputasi)
{ {KRITERIA[i]: round(float(w_ent[i]), 3) for i in range(len(KRITERIA))} }
- Entropi per kriteria: { {KRITERIA[i]: round(float(e[i]), 3) for i in range(len(KRITERIA))} }
- Kolam kandidat sama dengan mcdm.py (filter muatan + fosfat): {n_kolam} entri.

## Konsistensi vs pembobotan manual (peringkat rerata 3 skenario)
- Korelasi Spearman peringkat: **{rho:.3f}** (p = {p:.2e})
- Interpretasi: {'PERINGKAT KONSISTEN terhadap pembobotan manual' if rho > 0.8 else 'perbedaan berarti — kriteria perlu ditinjau'}
- Catatan jujur: ini uji konsistensi INTERNAL (dua cara pembobotan pada kriteria yang
  sama), bukan validasi independen. Ketidakpastian bobot + prediksi dipropagasi di
  laporan_montecarlo.md.

## Top 10 versi entropi
{top10_ent.to_markdown(index=False)}
"""
    (REPORTS / "laporan_sensitivitas.md").write_text(laporan, encoding="utf-8")
    print(laporan.encode("ascii", "replace").decode("ascii"))


if __name__ == "__main__":
    main()
