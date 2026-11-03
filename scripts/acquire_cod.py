"""Akuisisi Crystallography Open Database (COD) untuk senyawa Ca-P via HTTP."""
import time

import pandas as pd

from common import RAW, get, save_json

BASE = "http://www.crystallography.net/cod/result?"

QUERIES = [
    ("el1=Ca&el2=P&nel=2&eltype=only", "cap_biner"),
    ("el1=Ca&el2=P&el3=O&nel=3&eltype=only", "capo_terner"),
    ("el1=Ca&el2=P&el3=O&el4=H&nel=4&eltype=only", "capoh_kuaterner"),
]

KEEP = [
    "file", "formula", "calcformula", "cellformula", "chemname", "mineral", "commonname",
    "a", "b", "c", "alpha", "beta", "gamma", "vol", "sg", "sgNumber", "sgHall", "Z", "Zprime",
    "year", "journal", "doi", "authors", "title", "Rall", "method", "radiation",
    "celltemp", "cellpressure", "_query",
]


def main():
    rows_by = {}
    for q, tag in QUERIES:
        r = get(BASE + q + "&format=json", tries=4, pause=8, timeout=240)
        if r is None:
            print(f"  {tag}: GAGAL")
            continue
        try:
            data = r.json()
        except Exception as e:
            print(f"  {tag}: json error {e}")
            continue
        if isinstance(data, dict):
            data = data.get("results", data.get("data", []))
        if not isinstance(data, list):
            data = [data]
        print(f"  {tag}: {len(data)} records")
        save_json(RAW / "cod" / f"{tag}.json", data)
        rows_by[tag] = data
        time.sleep(3)

    frames = [pd.DataFrame(v).assign(_query=k) for k, v in rows_by.items() if v]
    if not frames:
        print("COD: tidak ada data")
        return
    alld = pd.concat(frames, ignore_index=True).drop_duplicates(subset=["file", "_query"])
    cols = [c for c in KEEP if c in alld.columns]
    alld[cols].to_csv(RAW / "cod" / "cod_cap.csv", index=False)
    save_json(
        RAW / "cod" / "_metadata.json",
        {
            "sumber": "Crystallography Open Database (COD)",
            "tanggal_akses": time.strftime("%Y-%m-%d %H:%M:%S"),
            "lisensi": "CC0 (public domain)",
            "jumlah": {t: len(v) for t, v in rows_by.items()},
        },
    )
    print("COD selesai. baris:", alld.shape)


if __name__ == "__main__":
    main()
