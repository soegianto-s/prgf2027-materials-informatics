"""Sensitivitas kelarutan MCDM (reviewer ronde 6): kriteria pKsp literatur pada shortlist.

Fase shortlist yang punya pKsp literatur diranking ulang dengan 4 kriteria:
C1 stabilitas (Eform), C2 pita densitas, C3 Ca/P -> 1.67, C4 kelarutan = -pKsp
(makin larut makin baik untuk scaffold resorbabel). Tiga skenario bobot -> pergeseran
peringkat vs MCDM murni C1-C3. Keluaran: laporan_mcdm_resorb.md
"""
import time

import numpy as np
import pandas as pd

from common import PROC, REPORTS
from mcdm import topsis, vikor

# pKsp literatur (25 C; Elliott 1994, Dorozhkin 2009, Wang & Nancollas 2008)
PKSP = {"CaPH5O6": 6.59, "CaPHO4": 6.90, "Ca8P6H12O29": 96.6, "Ca3(PO4)2_a": 25.5,
        "Ca3(PO4)2_b": 28.9, "Ca4P2O9": 38.0, "Ca5P3HO13": 116.8, "Ca5P3O12F": 121.0,
        "Ca10P6O25": 116.8}  # oksiapatit ~ HA (Elliott)


def main():
    k = pd.read_csv(PROC / "kandidat_ranking.csv")
    k = k.sort_values("peringkat_rerata").drop_duplicates("komposisi_reduksi").copy()
    k["peringkat_lama"] = range(1, len(k) + 1)

    # peta fase shortlist -> kunci pKsp
    k["kunci_pksp"] = None
    for i, r in k.iterrows():
        f = r["formula"]
        if f == "Ca5P3HO13":
            k.loc[i, "kunci_pksp"] = "Ca5P3HO13"
        elif f == "Ca10P6O25":
            k.loc[i, "kunci_pksp"] = "Ca10P6O25"
        elif f == "Ca5P3O12F":
            k.loc[i, "kunci_pksp"] = "Ca5P3O12F"
        elif f == "Ca3(PO4)2":
            k.loc[i, "kunci_pksp"] = "Ca3(PO4)2_b"
        elif f in ("Ca4P2O9", "Ca8P6H12O29", "CaPHO4", "CaPH5O6"):
            k.loc[i, "kunci_pksp"] = f
    sub = k[k["kunci_pksp"].notna()].copy()
    sub["C_stabilitas"] = -sub["Eform_eV_atom"]
    rho = sub["densitas_final_gcm3"]
    sub["C_densitas"] = np.where(rho.between(1.0, 3.2), 0.0,
                                 -np.minimum((rho - 3.2).abs(), (rho - 1.0).abs()))
    sub["C_cap"] = -np.abs(sub["ca_p_ratio"] - 1.67)
    sub["C_resorb"] = -sub["kunci_pksp"].map(PKSP)

    # C_densitas non-diskriminatif di shortlist (semua dalam pita klinis) -> dikeluarkan
    K4 = ["C_stabilitas", "C_cap", "C_resorb"]
    A = sub[K4].values
    An = A / np.sqrt((A ** 2).sum(0))
    W = {"W1_berimbang3": np.array([0.40, 0.20, 0.40]),
         "W2_stabilitas": np.array([0.60, 0.20, 0.20]),
         "W3_resorbabel": np.array([0.15, 0.15, 0.70])}
    skor = pd.DataFrame({f"TOPSIS_{wn}": topsis(An, w) for wn, w in W.items()} |
                        {f"VIKOR_{wn}": -vikor(An, w) for wn, w in W.items()}, index=sub.index)
    sub["peringkat_4k"] = skor.rank(ascending=False).mean(1)

    # peringkat ulang hanya pada sub (9 fase)
    sub["rank_4k"] = sub["peringkat_4k"].rank()
    sub["rank_3k_di_sub"] = sub["peringkat_lama"].rank()
    sub["naik"] = sub["rank_3k_di_sub"] - sub["rank_4k"]

    kol = ["formula", "peringkat_lama", "rank_4k", "naik", "Eform_eV_atom",
           "densitas_final_gcm3", "ca_p_ratio", "kunci_pksp"]
    tabel = sub[["formula", "peringkat_lama", "rank_4k", "naik", "Eform_eV_atom",
                 "densitas_final_gcm3", "ca_p_ratio"]].round(2)
    tabel["pKsp"] = sub["kunci_pksp"].map(PKSP).round(1).values

    laporan = [f"# Sensitivitas MCDM + Kelarutan (pKsp literatur, shortlist 9 fase)\n"
               f"**Tanggal:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
               f"- C4 = -pKsp (makin larut makin baik utk scaffold resorbabel); C2 pita densitas non-diskriminatif "
               f"di shortlist (semua dalam pita) -> dikeluarkan; skenario: berimbang, stabilitas, resorbabel",
               f"- Fase tanpa pKsp literatur dikecualikan (alasan data), bukan kriteria atas seluruh kolam\n",
               tabel.sort_values("rank_4k").to_markdown(index=False),
               f"\n## Temuan",
               f"- {', '.join(sub.sort_values('naik', ascending=False).head(3)['formula'])} naik paling tinggi "
               f"saat kelarutan dipertimbangkan.",
               f"- {', '.join(sub.sort_values('naik', ascending=True).head(3)['formula'])} turun paling dalam "
               f"(stabilitas vs resorbabilitas berlawanan).",
               f"- Pergeseran kuantitatif ini mendukung narasi trade-off: scaffold resorbabel -> b-TCP/bifasik; "
               f"FAp/oksiapatit/HA untuk permanen/low-turnover."]
    (REPORTS / "laporan_mcdm_resorb.md").write_text("\n".join(laporan), encoding="utf-8")
    print("\n".join(laporan).encode("ascii", "replace").decode("ascii"))


if __name__ == "__main__":
    main()
