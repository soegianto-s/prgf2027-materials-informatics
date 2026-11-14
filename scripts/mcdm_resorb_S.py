"""Re-ranking resorbabilitas shortlist dengan kriteria S (kelarutan stoikiometrik).

Reviewer ronde 10: memakai -pKsp sebagai kriteria lintas stoikiometri berbeda tidak
sebanding (TTCP vs b-TCP; apatit vs TCP) — pakai S (mol/L) yang sudah dihitung
(kelarutan_ksp.csv). Kriteria: C_stabilitas = -Eform, C_cap = -|Ca/P-1.67|,
C_resorb = log10(S) (makin larut makin baik utk scaffold resorbabel); tiga skenario
bobot sama dengan mcdm_resorb.py. Output: data/processed/resorb_S_ringkasan.json
"""
import json

import numpy as np
import pandas as pd

from common import PROC
from mcdm import topsis, vikor

# peta fase -> baris kelarutan_ksp.csv
FASE_KE_CSV = {
    "CaPH5O6": "Brushite (DCPD)",
    "CaPHO4": "Monetite (DCPA)",
    "Ca3(PO4)2": "beta-TCP",
    "Ca4P2O9": "TTCP",
    "Ca8P6H12O29": "OCP",
    "Ca10P6O25": "Oxyapatite",
    "Ca5P3HO13": "Hydroxyapatite",
    "Ca5P3O12F": "Fluorapatite",
}


def main():
    ksp = pd.read_csv(PROC / "kelarutan_ksp.csv").set_index("fase")
    k = pd.read_csv(PROC / "kandidat_ranking.csv")
    k = k.sort_values("peringkat_rerata").drop_duplicates("komposisi_reduksi").copy()
    k["kunci_pksp"] = k["formula"].map(FASE_KE_CSV)
    sub = k[k["kunci_pksp"].notna()].copy()
    assert len(sub) == 8, f"shortlist {len(sub)} != 8"

    logS = sub["kunci_pksp"].map(ksp["log10_S"])
    sub["C_stabilitas"] = -sub["Eform_eV_atom"]
    rho = sub["densitas_final_gcm3"]
    sub["C_densitas"] = np.where(rho.between(1.0, 3.2), 0.0,
                                 -np.minimum((rho - 3.2).abs(), (rho - 1.0).abs()))
    sub["C_cap"] = -np.abs(sub["ca_p_ratio"] - 1.67)
    sub["C_resorb"] = logS  # lebih larut = lebih baik

    K3 = ["C_stabilitas", "C_cap", "C_resorb"]
    A = sub[K3].values
    An = A / np.sqrt((A ** 2).sum(0))
    W = {"W1_berimbang3": np.array([0.40, 0.20, 0.40]),
         "W2_stabilitas": np.array([0.60, 0.20, 0.20]),
         "W3_resorbabel": np.array([0.15, 0.15, 0.70])}
    skor = pd.DataFrame({f"TOPSIS_{wn}": topsis(An, w) for wn, w in W.items()} |
                        {f"VIKOR_{wn}": -vikor(An, w) for wn, w in W.items()}, index=sub.index)
    sub["peringkat_3k"] = skor.rank(ascending=False).mean(1)
    sub = sub.sort_values("peringkat_3k")

    # order lama (MC) diambil dari ranking_mc_ringkasan.json
    mc = json.loads((PROC / "ranking_mc_ringkasan.json").read_text(encoding="utf-8"))
    order_mc = {r["formula"]: r["order"] for r in mc["top15"]}
    ringkas = []
    for i, (_, r) in enumerate(sub.iterrows(), 1):
        ringkas.append({
            "formula": r["formula"],
            "order_mc": order_mc[r["formula"]],
            "order_resorb_S": i,
            "E_f": round(float(r["Eform_eV_atom"]), 2),
            "rho": round(float(r["densitas_final_gcm3"]), 2),
            "ca_p": round(float(r["ca_p_ratio"]), 2),
            "log10_S": round(float(logS[r.name]), 3),
            "S_mol_L": float(ksp.loc[r["kunci_pksp"], "S_mol_L"]),
            "pKsp": float(ksp.loc[r["kunci_pksp"], "pKsp"]),
        })
    out = PROC / "resorb_S_ringkasan.json"
    out.write_text(json.dumps({"rows": ringkas}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"OK -> {out}")
    for r in ringkas:
        print(f"  {r['order_resorb_S']}. {r['formula']:12s} (MC {r['order_mc']:2d}) "
              f"log10S {r['log10_S']:7.2f}  pKsp {r['pKsp']:6.1f}  Ef {r['E_f']:+.2f}  Ca/P {r['ca_p']:.2f}")


if __name__ == "__main__":
    main()
