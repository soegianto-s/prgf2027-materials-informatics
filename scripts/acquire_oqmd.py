"""Akuisisi OQMD via oqmdapi/formationenergy per-formula (server flaky -> retry panjang).

Daftar komposisi diambil dari dataset yang sudah terunduh (MP, AFLOW, COD) + daftar kurasi.
Jalankan ulang kapan saja: komposisi yang sudah berhasil akan dilewati (cache JSON per formula).
"""
import json
import re
import time

from common import RAW, get, save_json

CURATED = [
    "Ca3P2", "CaP", "Ca2P", "Ca5P8", "CaP3", "Ca4P2", "Ca2P4", "CaP2",
    "Ca3P2O8", "Ca2P2O7", "CaHPO4", "Ca4P2O9", "CaP2O6", "CaPO3",
    "Ca5P3HO13", "Ca10P6H2O25", "Ca5P3FO12",
]

FIELDS = (
    "name,entry_id,calculation_id,icsd_id,composition,composition_generic,prototype,"
    "spacegroup,volume,ntypes,natoms,unit_cell,delta_e,stability"
)


def formulas_from_csvs():
    """Kumpulkan formula kompak (mis. Ca3P2O8) dari CSV MP/AFLOW/COD yang ada."""
    import pandas as pd

    comps = set(CURATED)
    pairs = re.compile(r"([A-Z][a-z]?)(\d*\.?\d*)")

    def compact(f):
        f = f.strip().lstrip("-").strip()
        out = []
        for el, n in pairs.findall(f):
            out.append(f"{el}{n if n else '1'}")
        return "".join(out)

    for path in [RAW / "mp" / "mp_summary_cap.csv", RAW / "aflow" / "aflow_cap.csv"]:
        if not path.exists():
            continue
        try:
            df = pd.read_csv(path)
        except Exception:
            continue
        for col in ["formula_pretty", "compound"]:
            if col in df.columns:
                for v in df[col].dropna().astype(str):
                    c = compact(v)
                    if c and set(c) >= {"C", "a"} and "P" in c:
                        comps.add(c)
    return sorted(comps)


def main():
    comps = formulas_from_csvs()
    print(f"total komposisi akan dicoba: {len(comps)}")
    cache = RAW / "oqmd" / "formationenergy.json"
    if cache.exists():
        try:
            done = json.loads(cache.read_text(encoding="utf-8"))
        except Exception:
            done = {}
    else:
        done = {}
    todo = [c for c in comps if c not in done or not done[c]]
    print(f"belum berhasil: {len(todo)}")

    for i, comp in enumerate(todo):
        url = f"https://oqmd.org/oqmdapi/formationenergy?composition={comp}&fields={FIELDS}"
        r = get(url, tries=5, pause=25, timeout=120)
        if r is None:
            print(f"[{i + 1}/{len(todo)}] {comp}: GAGAL (dicoba lagi nanti)")
            continue
        try:
            data = r.json().get("data", [])
        except Exception as e:
            print(f"[{i + 1}/{len(todo)}] {comp}: json error {e}")
            continue
        if data:
            done[comp] = data
            print(f"[{i + 1}/{len(todo)}] {comp}: {len(data)} entri")
        else:
            done[comp] = []
            print(f"[{i + 1}/{len(todo)}] {comp}: 0 entri")
        save_json(cache, done)
        time.sleep(3)

    ok = {k: v for k, v in done.items() if v}
    save_json(RAW / "oqmd" / "_metadata.json", {
        "sumber": "OQMD (oqmdapi/formationenergy)",
        "tanggal_akses": time.strftime("%Y-%m-%d %H:%M:%S"),
        "lisensi": "riset akademik; wajib sitasi OQMD (Kirklin et al.)",
        "jumlah_komposisi_berhasil": len(ok),
        "jumlah_entri": sum(len(v) for v in ok.values()),
    })
    print(f"OQMD selesai. komposisi berhasil: {len(ok)}")


if __name__ == "__main__":
    main()
