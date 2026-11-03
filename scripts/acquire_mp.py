"""Akuisisi Materials Project (api.materialsproject.org) untuk sistem Ca-P."""
import time

import pandas as pd
import requests

from common import RAW, mp_key, save_json

KEY = mp_key()
BASE = "https://api.materialsproject.org"
HDR = {"x-api-key": KEY}

# sistem kimia yang diambil: biner, terner, dengan OH (hidroksiapatit),
# dengan C (karbonat apatit), dengan F (fluorapatit)
SYSTEMS = ["Ca-P", "Ca-P-O", "Ca-P-H-O", "Ca-P-O-C", "Ca-P-O-F"]

FIELDS = (
    "material_id,formula_pretty,chemsys,nelements,elements,nsites,volume,density,band_gap,"
    "formation_energy_per_atom,energy_above_hull,is_stable,symmetry"
)


def paginate(endpoint, params, tag, outdir):
    rows, skip = [], 0
    while True:
        p = dict(params)
        p["_skip"] = skip
        p["_limit"] = 1000
        r = requests.get(f"{BASE}/{endpoint}", params=p, headers=HDR, timeout=120)
        if r.status_code != 200:
            print(f"  HTTP {r.status_code} pada {endpoint} {params}")
            break
        d = r.json()
        data = d.get("data", [])
        meta = d.get("meta", {})
        rows.extend(data)
        n = len(data)
        total = meta.get("total_doc")
        print(f"  {tag}: skip={skip} dapat={n} total={total}")
        save_json(outdir / f"{tag}_skip{skip:05d}.json", d)
        if n == 0 or skip + n >= (total or 0):
            break
        skip += n
        time.sleep(1)
    return rows


def main():
    out = RAW / "mp"
    # --- summary ---
    allrows = []
    for sys_ in SYSTEMS:
        allrows.extend(
            paginate(
                "materials/summary/",
                {"chemsys": sys_, "_fields": FIELDS},
                f"summary_{sys_.replace('-', '_')}",
                out,
            )
        )
    df = pd.DataFrame(allrows).drop_duplicates(subset="material_id")
    if "symmetry" in df.columns:
        sym = pd.json_normalize(df.pop("symmetry"))
        df["crystal_system"] = sym["crystal_system"]
        df["spacegroup_symbol"] = sym["symbol"]
        df["spacegroup_number"] = sym["number"]
        df["point_group"] = sym["point_group"]
    df.to_csv(out / "mp_summary_cap.csv", index=False)

    # --- elastisitas ---
    elas = []
    for sys_ in SYSTEMS:
        elas.extend(
            paginate(
                "materials/elasticity/",
                {
                    "chemsys": sys_,
                    "_fields": (
                        "material_id,formula_pretty,bulk_modulus,shear_modulus,"
                        "homogeneous_poisson,universal_anisotropy,elastic_tensor"
                    ),
                },
                f"elastic_{sys_.replace('-', '_')}",
                out,
            )
        )
    edf = pd.DataFrame(elas).drop_duplicates(subset="material_id")
    edf.to_csv(out / "mp_elastic_cap.csv", index=False)

    save_json(
        out / "_metadata.json",
        {
            "sumber": "Materials Project",
            "tanggal_akses": time.strftime("%Y-%m-%d %H:%M:%S"),
            "lisensi": "CC-BY 4.0",
            "api": BASE,
            "jumlah_entries": int(df.shape[0]),
            "jumlah_elastic": int(edf.shape[0]),
            "per_sistem": df["chemsys"].value_counts().to_dict(),
        },
    )
    print("MP selesai. entries:", df.shape, "elastic:", edf.shape)


if __name__ == "__main__":
    main()
