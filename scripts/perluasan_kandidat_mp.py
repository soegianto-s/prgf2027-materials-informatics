"""Perluasan ruang kandidat substitusi (ronde 7/Q1): Ca-P-O-X, X = Sr, Mg, Zn, Si.

Hanya Materials Project API (keputusan pengguna). Kandidat difilter fisika-kimia
(fraksi X 1-30%, rasio (Ca+Sr+Mg+Zn)/(P+Si) dalam [1.2, 2.2], densitas 1.0-3.2 g/cm3,
E_hull <= 0.2 eV/atom, muatan formal netral), lalu diranking TOPSIS+VIKOR dengan
C1 = -E_hull, C2 = pita densitas, C3 = -|rasio - 1.67|.
"""
import time

import numpy as np
import pandas as pd

from acquire_mp import BASE, FIELDS, HDR, paginate
from common import RAW, REPORTS, save_json
from consolidate import parse_formula
from mcdm import topsis, vikor

OUT = RAW / "mp" / "substitusi"
OUT.mkdir(parents=True, exist_ok=True)
# tier partial: kuarterner Ca-P-O-X (substitusi 1-30%)
# tier endpoint: fosfat Sr/Mg/Zn/Si TANPA Ca (titik akhir substitusi penuh, mis. Sr-apatit)
SYSTEMS = ["Ca-P-O-Sr", "Ca-P-O-Mg", "Ca-P-O-Zn", "Ca-P-O-Si",
           "Ca-P-O-H-Sr", "Ca-P-O-F-Sr", "Ca-P-O-H-Mg", "Ca-P-O-F-Mg",
           "Ca-P-O-H-Zn", "Ca-P-O-F-Zn", "Ca-P-O-H-Si", "Ca-P-O-F-Si",
           "Sr-P-O", "Sr-P-O-H", "Sr-P-O-F", "Mg-P-O", "Mg-P-O-H", "Mg-P-O-F",
           "Zn-P-O", "Zn-P-O-H", "Si-P-O"]
OXID_SUB = {"Ca": 2, "Sr": 2, "Mg": 2, "Zn": 2, "Si": 4, "P": 5, "O": -2, "H": 1, "F": -1, "C": 4}


def muatan_sub(f):
    cnt = parse_formula(f)
    if not cnt or set(cnt) - set(OXID_SUB):
        return None
    p_ox = 5.0 if "O" in cnt else -3.0
    return sum(n * (p_ox if e == "P" else OXID_SUB[e]) for e, n in cnt.items())


def main():
    semua = []
    for sys_ in SYSTEMS:
        semua.extend(paginate("materials/summary/", {"chemsys": sys_, "_fields": FIELDS},
                              f"sub_{sys_.replace('-', '_')}", OUT))
    df = pd.DataFrame(semua).drop_duplicates(subset="material_id")
    df.to_csv(OUT / "substitusi_cap.csv", index=False)
    print(f"MP substitusi: {len(df)} entri mentah dari {len(SYSTEMS)} sistem")

    # filter
    rows = []
    for _, r in df.iterrows():
        cnt = parse_formula(str(r["formula_pretty"]))
        tot = sum(cnt.values())
        if tot == 0 or "P" not in cnt or "O" not in cnt:
            continue
        x_el = [e for e in ["Sr", "Mg", "Zn", "Si"] if e in cnt]
        if not x_el:
            continue
        tier = "partial" if "Ca" in cnt else "endpoint"
        frac_x = sum(cnt[e] for e in x_el) / tot
        if tier == "partial" and not (0.01 <= frac_x <= 0.30):
            continue
        ca_sr = sum(cnt.get(e, 0) for e in ["Ca", "Sr", "Mg", "Zn"])
        p_si = cnt.get("P", 0) + cnt.get("Si", 0)
        if p_si == 0:
            continue
        rasio = ca_sr / p_si
        if not (1.2 <= rasio <= 2.2):
            continue
        dens = r.get("density")
        if dens is None or np.isnan(dens) or not (1.0 <= dens <= 3.2):
            continue
        ehull = r.get("energy_above_hull")
        if ehull is None or np.isnan(ehull):
            continue
        if ehull > 0.2:
            continue
        if muatan_sub(str(r["formula_pretty"])) not in (0, 0.0):
            continue
        rows.append({
            "material_id": r["material_id"], "formula": r["formula_pretty"],
            "chemsys": r["chemsys"], "X": ",".join(x_el), "frac_X": round(frac_x, 4),
            "tier": tier, "rasio": round(rasio, 3), "E_hull": round(float(ehull), 4),
            "Eform_eV_atom": r.get("formation_energy_per_atom"),
            "densitas": round(float(dens), 3), "is_stable": r.get("is_stable"),
            "nsites": r.get("nsites"),
            "spacegroup": (r.get("symmetry") or {}).get("symbol", ""),
        })
    k = pd.DataFrame(rows)
    k.to_csv(OUT / "kandidat_substitusi_mp.csv", index=False)
    print(f"setelah filter: {len(k)} kandidat substitusi")

    if len(k) == 0:
        ringkas = {"n_mentah": int(len(df)), "n_filter": 0}
        save_json(OUT / "substitusi_ringkasan.json", ringkas)
        print("TIDAK ADA kandidat lolos filter")
        return

    # ranking: C1 = -E_hull, C2 = pita densitas, C3 = -|rasio-1.67|
    k["C_stabilitas"] = -k["E_hull"]
    k["C_densitas"] = np.where(k["densitas"].between(1.0, 3.2), 0.0,
                              -np.minimum((k["densitas"] - 3.2).abs(), (k["densitas"] - 1.0).abs()))
    k["C_cap"] = -np.abs(k["rasio"] - 1.67)
    A = k[["C_stabilitas", "C_densitas", "C_cap"]].values
    norm = np.sqrt((A ** 2).sum(0))
    norm[norm == 0] = 1.0  # kolom konstanta (mis. semua di dalam pita densitas) -> jangan bagi nol
    An = A / norm
    W = {"W1_berimbang": np.array([0.40, 0.20, 0.40]),
         "W2_stabilitas": np.array([0.60, 0.20, 0.20]),
         "W3_komposisi": np.array([0.20, 0.20, 0.60])}
    skor = pd.DataFrame({f"TOPSIS_{wn}": topsis(An, w) for wn, w in W.items()} |
                        {f"VIKOR_{wn}": -vikor(An, w) for wn, w in W.items()}, index=k.index)
    k["peringkat_rerata"] = skor.rank(ascending=False).mean(1)
    k = k.sort_values("peringkat_rerata")
    k["peringkat"] = range(1, len(k) + 1)
    top15 = k.head(15)
    k.to_csv(OUT / "kandidat_substitusi_ranking.csv", index=False)
    top15.to_csv(OUT / "kandidat_substitusi_top15.csv", index=False)

    ringkas = {
        "n_mentah": int(len(df)), "n_filter": int(len(k)), "n_top15": int(len(top15)),
        "n_partial": int((k["tier"] == "partial").sum()), "n_endpoint": int((k["tier"] == "endpoint").sum()),
        "sistem": SYSTEMS,
        "teratas": top15[["formula", "tier", "X", "frac_X", "rasio", "E_hull", "densitas"]].to_dict("records"),
        "rentang_E_hull": [float(k["E_hull"].min()), float(k["E_hull"].max())],
    }
    save_json(OUT / "substitusi_ringkasan.json", ringkas)
    print(top15[["formula", "tier", "X", "frac_X", "rasio", "E_hull", "densitas", "peringkat"]].to_markdown(index=False))


if __name__ == "__main__":
    main()
