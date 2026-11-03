"""Sensitivitas MCDM: pembobotan entropi Shannon + uji konsistensi peringkat (Spearman)."""
import time

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from common import PROC, REPORTS

KRITERIA = ["C_stabilitas", "C_densitas", "C_cap", "C_modulus", "C_bandgap", "C_layak"]


def topsis(A, w):
    V = A * w
    ip, inn = V.max(0), V.min(0)
    dp = np.sqrt(((V - ip) ** 2).sum(1))
    dn = np.sqrt(((V - inn) ** 2).sum(1))
    return dn / (dp + dn + 1e-12)


def vikor(A, w, v=0.5):
    fstar, fworst = A.max(0), A.min(0)
    jarak = w * (fstar - A) / (fstar - fworst + 1e-12)
    S, R = jarak.sum(1), jarak.max(1)
    Q = v * (S - S.min()) / (S.max() - S.min() + 1e-12) + (1 - v) * (R - R.min()) / (R.max() - R.min() + 1e-12)
    return Q


def bobot_entropi(A):
    """Pembobotan entropi Shannon (hanya kriteria lengkap/tanpa imputasi).

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
    for c in ["bulk_K_GPa", "shear_G_GPa", "young_E_GPa", "bandgap_eV", "Eform_eV_atom",
              "densitas_final_gcm3", "ca_p_ratio"]:
        k[c] = pd.to_numeric(k[c], errors="coerce")
    k["young_E_deriv_GPa"] = np.where(
        k["bulk_K_GPa"].notna() & k["shear_G_GPa"].notna(),
        9 * k["bulk_K_GPa"] * k["shear_G_GPa"] / (3 * k["bulk_K_GPa"] + k["shear_G_GPa"]), np.nan)
    k["C_stabilitas"] = -k["Eform_eV_atom"]
    k["C_densitas"] = -np.abs(k["densitas_final_gcm3"] - 2.0)
    k["C_cap"] = -np.abs(k["ca_p_ratio"] - 1.67)
    k["C_modulus"] = -np.abs(k["young_E_deriv_GPa"] - 15)
    k["C_bandgap"] = np.clip(k["bandgap_eV"].fillna(-1), 0, 5) / 5.0
    k["C_layak"] = k["layak"].astype(float)
    med = k[KRITERIA].median()
    A = k[KRITERIA].fillna(med).values
    An = A / np.sqrt((A ** 2).sum(0))

    # entropi HANYA pada kriteria lengkap tanpa imputasi (C_modulus & C_bandgap diimputasi)
    KR_ENT = ["C_stabilitas", "C_densitas", "C_cap", "C_layak"]
    idx_ent = [KRITERIA.index(x) for x in KR_ENT]
    Aent = An[:, idx_ent]
    w_ent_4, e = bobot_entropi(Aent)
    # bobot penuh: kriteria imputasi diberi bobot manualnya (C_modulus 0.15, C_bandgap 0.10)
    # dinormalisasi ulang terhadap total entropi 4 kriteria
    w_penuh = np.array([0.0] * len(KRITERIA))
    for j, x in enumerate(KR_ENT):
        w_penuh[KRITERIA.index(x)] = w_ent_4[j]
    w_penuh[KRITERIA.index("C_modulus")] = 0.15
    w_penuh[KRITERIA.index("C_bandgap")] = 0.10
    w_penuh = w_penuh / w_penuh.sum()

    skor_ent_top = topsis(An, w_penuh)
    skor_ent_vik = -vikor(An, w_penuh)
    k["skor_entropi"] = (skor_ent_top + skor_ent_vik) / 2
    k["peringkat_entropi"] = k["skor_entropi"].rank(ascending=False)

    # bandingkan dengan peringkat W1 (TOPSIS+VIKOR berimbang) yang tersimpan
    lama = pd.read_csv(PROC / "kandidat_ranking.csv")
    k = k.merge(lama[["id", "peringkat_rerata"]], on="id", how="left")
    rho, p = spearmanr(k["peringkat_entropi"], k["peringkat_rerata"])

    top10_ent = k.sort_values("peringkat_entropi").head(10)[["formula", "sumber", "kelompok"]]
    laporan = f"""# Laporan Sensitivitas MCDM — Pembobotan Entropi
**Tanggal:** {time.strftime('%Y-%m-%d %H:%M:%S')}

## Bobot Entropi (data-driven, 4 kriteria lengkap)
{ {KR_ENT[i]: round(float(w_ent_4[i]), 3) for i in range(len(KR_ENT))} }
- Catatan: C_modulus & C_bandgap diimputasi median sehingga DIKELUARKAN dari entropi
  (bobot manual 0.15/0.10 dipertahankan agar artefak imputasi tidak mendominasi).
- Entropi per kriteria: { {KR_ENT[i]: round(float(e[i]), 3) for i in range(len(KR_ENT))} }

## Konsistensi vs pembobotan manual (W1 berimbang)
- Korelasi Spearman peringkat: **{rho:.3f}** (p = {p:.2e})
- Interpretasi: {'PERINGKAT KONSISTEN terhadap pembobotan manual' if rho > 0.8 else 'perbedaan berarti — kriteria perlu ditinjau'}

## Top 10 versi entropi
{top10_ent.to_markdown(index=False)}
"""
    (REPORTS / "laporan_sensitivitas.md").write_text(laporan, encoding="utf-8")
    print(laporan.encode("ascii", "replace").decode("ascii"))


if __name__ == "__main__":
    main()
