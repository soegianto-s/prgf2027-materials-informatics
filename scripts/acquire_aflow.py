"""Akuisisi AFLOW (AFLUX REST API) untuk sistem Ca-P: biner, terner, kuaterner + subset ICSD.

Keyword diambil dari ?schema AFLUX: ael_*_vrh (modulus), icsd/icsd_number, dll.
$paging(0) -> seluruh hasil sebagai JSON list.
"""
import time

import pandas as pd

from common import RAW, get, save_json

BASE = "https://aflow.org/API/aflux/?"

QUERIES = [
    ("species(Ca,P),nspecies(2)", "cap_biner"),
    ("species(Ca,P,O),nspecies(3)", "capo_terner"),
    ("species(Ca,P,O,H),nspecies(4)", "capoh_kuaterner"),
    ("species(Ca,P,O,F),nspecies(4)", "capof_kuaterner"),
    ("species(Ca,P),nspecies(2),catalog(icsd)", "cap_biner_icsd"),
    ("species(Ca,P,O),nspecies(3),catalog(icsd)", "capo_terner_icsd"),
]

PROPS = (
    "energy_atom,density,Egap,enthalpy_formation_atom,geometry,volume_cell,"
    "prototype,spacegroup_relax,Bravais_lattice_relax,lattice_system_relax,"
    "lattice_variation_relax,Pearson_symbol_relax,point_group_Hermann_Mauguin,"
    "ael_bulk_modulus_vrh,ael_shear_modulus_vrh,ael_youngs_modulus_vrh,"
    "ael_elastic_anisotropy,ael_pughs_modulus_ratio,catalog"
)

KEEP = [
    "compound", "auid", "aurl", "nspecies", "natoms", "species", "prototype",
    "spacegroup_relax", "Bravais_lattice_relax", "lattice_system_relax", "lattice_variation_relax",
    "Pearson_symbol_relax", "point_group_Hermann_Mauguin", "geometry", "volume_cell", "density",
    "energy_atom", "enthalpy_formation_atom", "Egap", "ael_bulk_modulus_vrh",
    "ael_shear_modulus_vrh", "ael_youngs_modulus_vrh", "ael_elastic_anisotropy",
    "ael_pughs_modulus_ratio", "catalog", "_query",
]


def fetch_all(q):
    url = f"{BASE}{q},{PROPS},$paging(0)"
    r = get(url, tries=4, pause=6, timeout=300)
    if r is None:
        return None
    try:
        j = r.json()
    except Exception as e:
        print("  json error:", e)
        return None
    if isinstance(j, list):
        return j
    if isinstance(j, dict):
        return list(j.values())
    return None


def main():
    rows_by = {}
    for q, tag in QUERIES:
        rows = fetch_all(q)
        if rows is None:
            print(f"  {tag}: GAGAL")
            continue
        print(f"  {tag}: {len(rows)} records")
        save_json(RAW / "aflow" / f"{tag}.json", rows)
        rows_by[tag] = rows
        time.sleep(2)

    frames = []
    for tag, rows in rows_by.items():
        if rows:
            df = pd.DataFrame(rows)
            df["_query"] = tag
            frames.append(df)
    if not frames:
        print("AFLOW: tidak ada data")
        return
    alld = pd.concat(frames, ignore_index=True)
    alld = alld.drop_duplicates(subset=["auid", "_query"])
    cols = [c for c in KEEP if c in alld.columns]
    alld[cols].to_csv(RAW / "aflow" / "aflow_cap.csv", index=False)
    save_json(
        RAW / "aflow" / "_metadata.json",
        {
            "sumber": "AFLOW (AFLUX REST API)",
            "tanggal_akses": time.strftime("%Y-%m-%d %H:%M:%S"),
            "lisensi": "bebas untuk riset akademik; wajib sitasi AFLOW (Curtarolo et al.)",
            "jumlah": {t: len(v) for t, v in rows_by.items()},
        },
    )
    print("AFLOW selesai. baris:", alld.shape)


if __name__ == "__main__":
    main()
