"""Kalibrasi offset MACE -> MP GGA + hull + E_hull untuk COD in-system (ronde 7/Q1).

1. Kalibrasi: entri MP dalam ruang Ca-P-O-H-F-C (via mp_api.get_entries_in_chemsys)
   dihitung Eform single-point MACE (struktur MP, tanpa relaksasi, nsites<=200);
   offset = median(Eform_MP - Eform_MACE) + bootstrap CI; validasi eksternal pada
   6 fase Wagman/NBS (hasil_mace_baseline.json).
2. Hull: PhaseDiagram pymatgen dari entri MP GGA -> E_hull struktur COD in-system
   (energi MACE terkalibrasi) via PDEntry + get_e_above_hull.
3. Cross-check: E_hull PhaseDiagram vs API energy_above_hull untuk entri MP.

Keluaran:
  data/raw/mp/hull_entries_mp.json          (cache entri MP + energi MACE)
  data/processed/kalibrasi_mace_ringkasan.json
  data/processed/stabilitas_hull_q1.csv     (per cod_id in-system: E_hull dll)
  data/processed/mace_cod_energi.csv        (Eform terkalibrasi semua COD ok)
  data/reports/laporan_kalibrasi_hull.md
"""
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from common import PROC, RAW, REPORTS, ROOT, mp_key

CACHE_HULL = RAW / "mp" / "hull_entries_mp.json"
ELEM = ["Ca", "P", "O", "H", "F", "C"]
FIELDS_HULL = "material_id,formula_pretty,nsites,formation_energy_per_atom,energy_above_hull,is_stable"


def _semua_chemsys():
    """Semua sub-sistem non-kosong dari ELEM (63) + 6 unsur murni."""
    from itertools import combinations
    daftar = []
    for r in range(1, len(ELEM) + 1):
        for combo in combinations(sorted(ELEM), r):
            daftar.append("-".join(combo))
    return daftar


def ambil_entri_mp():
    """Semua entri MP di ruang Ca-P-O-H-F-C (REST materials/summary per chemsys)."""
    if CACHE_HULL.exists():
        j = json.loads(CACHE_HULL.read_text(encoding="utf-8"))
        print(f"cache entri MP: {len(j['entri'])} entri")
        return j
    import requests
    from common import mp_key
    hdr = {"x-api-key": mp_key()}
    data = []
    for sys_ in _semua_chemsys():
        skip, halaman = 0, 0
        while True:
            r = requests.get("https://api.materialsproject.org/materials/summary/",
                             params={"chemsys": sys_, "_fields": FIELDS_HULL,
                                     "_skip": skip, "_limit": 1000},
                             headers=hdr, timeout=120)
            if r.status_code != 200:
                print(f"  HTTP {r.status_code} pada {sys_} skip={skip}")
                break
            d = r.json()
            data.extend(d.get("data", []))
            n = len(d.get("data", []))
            total = d.get("meta", {}).get("total_doc") or 0
            halaman += 1
            if n == 0 or skip + n >= total:
                break
            skip += n
            time.sleep(0.3)
    # dedupe material_id
    unik = {}
    for x in data:
        unik[x["material_id"]] = x
    entri = [{
        "entry_id": x["material_id"], "formula": x.get("formula_pretty", ""),
        "nsites": x.get("nsites"), "energy_per_atom": x.get("formation_energy_per_atom"),
        "energy_above_hull": x.get("energy_above_hull"), "is_stable": x.get("is_stable"),
    } for x in unik.values() if x.get("formation_energy_per_atom") is not None]
    j = {"entri": entri, "tanggal": time.strftime("%Y-%m-%d %H:%M:%S")}
    CACHE_HULL.write_text(json.dumps(j), encoding="utf-8")
    print(f"entri MP diunduh: {len(entri)} entri")
    return j


def eform_mace_struktur(atoms, calc, ref):
    e_atom = atoms.get_potential_energy() / len(atoms)
    from collections import Counter
    cnt = Counter(atoms.get_chemical_symbols())
    n = len(atoms)
    e_ref = sum((c / n) * ref.get(el, 0.0) for el, c in cnt.items())
    return e_atom - e_ref


def kalibrasi():
    from mace.calculators import mace_mp
    import torch
    torch.set_num_threads(12)
    calc = mace_mp(model="medium", default_dtype="float64", device="cpu")
    ref = json.loads((ROOT / "data" / "validasi_mace" / "hasil_mace_baseline.json")
                     .read_text(encoding="utf-8"))["ref"]

    j = ambil_entri_mp()
    entri = [e for e in j["entri"] if e.get("nsites") and e["nsites"] <= 200]
    # MACE single-point per struktur MP (struktur diambil live + cache; satu per entry_id)
    from pymatgen.core import Structure
    from pymatgen.io.ase import AseAtomsAdaptor
    from siapkan_dft import ambil_struktur_mp
    cache_struktur = RAW / "struktur" / "mp"
    cache_struktur.mkdir(parents=True, exist_ok=True)
    baris = []
    for i, e in enumerate(entri, 1):
        try:
            cache = cache_struktur / f"{e['entry_id']}.json"
            if cache.exists():
                st = Structure.from_dict(json.loads(cache.read_text(encoding="utf-8")))
            else:
                d = ambil_struktur_mp(e["entry_id"])
                if not d or not d.get("structure"):
                    continue
                cache.write_text(json.dumps(d["structure"], ensure_ascii=False), encoding="utf-8")
                st = Structure.from_dict(d["structure"])
            atoms = AseAtomsAdaptor.get_atoms(st)
            atoms.calc = calc
            em = eform_mace_struktur(atoms, calc, ref)
            if abs(em) > 10.0:
                continue  # energi tak-fisis (struktur rusak)
            baris.append({"entry_id": e["entry_id"], "formula": e["formula"],
                          "Eform_MP": e["energy_per_atom"], "Eform_MACE_raw": em,
                          "selisih": e["energy_per_atom"] - em})
        except Exception:
            continue
        if i % 50 == 0:
            print(f"  MACE MP {i}/{len(entri)}", flush=True)
    df = pd.DataFrame(baris)
    df.to_csv(PROC / "kalibrasi_mace_mp.csv", index=False)
    d = df["selisih"]
    offset = float(d.median())
    # bootstrap CI 95%
    rng = np.random.default_rng(0)
    boot = np.array([rng.choice(d.values, size=len(d), replace=True).mean() for _ in range(2000)])
    ci_lo, ci_hi = float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))
    mae_offset = float((d - offset).abs().mean())
    rmse_offset = float(np.sqrt(((d - offset) ** 2).mean()))

    # validasi eksternal: 6 fase Wagman/NBS
    jm = json.loads((ROOT / "data" / "validasi_mace" / "hasil_mace_baseline.json").read_text(encoding="utf-8"))
    v = []
    for b in jm["baris"]:
        tag, formula, ea, ef_raw, exp, selisih = b
        ef_cal = float(ef_raw) + offset
        v.append({"fase": formula, "Eform_MACE_raw": float(ef_raw),
                  "Eform_cal": ef_cal, "Eform_exp": float(exp), "selisih_cal": ef_cal - float(exp)})
    mae_eksternal = float(np.mean([abs(x["selisih_cal"]) for x in v]))
    ringkas = {
        "n_kalibrasi": int(len(df)), "offset_median_eV_atom": round(offset, 4),
        "offset_CI95": [round(ci_lo, 4), round(ci_hi, 4)],
        "mae_offset_eV_atom": round(mae_offset, 4), "rmse_offset_eV_atom": round(rmse_offset, 4),
        "mae_eksternal_6fase_eV_atom": round(mae_eksternal, 4),
        "validasi_eksternal": v,
        "tanggal": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    (PROC / "kalibrasi_mace_ringkasan.json").write_text(json.dumps(ringkas, indent=2, ensure_ascii=False), encoding="utf-8")
    return df, ringkas, calc, ref


def hull_cod(ringkas_kal):
    from pymatgen.analysis.phase_diagram import PhaseDiagram
    from pymatgen.entries.computed_entries import ComputedEntry
    from pymatgen.core import Composition
    j = ambil_entri_mp()
    entries = []
    for e in j["entri"]:
        try:
            comp = Composition(e["formula"])
            entries.append(ComputedEntry(comp, e["energy_per_atom"] * comp.num_atoms,
                                         entry_id=e["entry_id"]))
        except Exception:
            continue
    pd_ = PhaseDiagram(entries)
    print(f"hull MP: {len(entries)} entri, {len(pd_.stable_entries)} stabil")

    # cross-check E_hull API vs PhaseDiagram (entri MP dari mp_summary_cap.csv)
    cap = pd.read_csv(RAW / "mp" / "mp_summary_cap.csv")
    cek = []
    for _, r in cap.iterrows():
        try:
            comp = Composition(r["formula_pretty"])
            ee = ComputedEntry(comp, float(r["formation_energy_per_atom"]) * comp.num_atoms)
            eh = pd_.get_e_above_hull(ee, allow_negative=True)
            cek.append((float(r["energy_above_hull"]), float(eh)))
        except Exception:
            continue
    selisih = [abs(a - b) for a, b in cek if not np.isnan(b)]
    mae_hull = float(np.mean(selisih)) if selisih else None

    # E_hull COD in-system
    ckpt = pd.read_csv(PROC / "mace_screening_cod.csv")
    ok = ckpt[(ckpt["status"] == "ok") & (ckpt["in_system"])].copy()
    # filter fisika: energi tak-fisis (parse fallback ASE -> geometri sampah, MACE meledak)
    # batas lebar +-10 eV/atom untuk Eform MACE mentah; sisanya ditandai & dikeluarkan
    ok["fisika_valid"] = ok["eform_mace_raw_eV_atom"].abs() <= 10.0
    n_absurd = int((~ok["fisika_valid"]).sum())
    ok = ok[ok["fisika_valid"]].copy()
    offset = ringkas_kal["offset_median_eV_atom"]
    rows = []
    for _, r in ok.iterrows():
        komp = json.loads(r["komposisi"].replace("'", '"'))
        ef_cal = float(r["eform_mace_raw_eV_atom"]) + offset
        try:
            comp = Composition({k: v for k, v in komp.items()})
            ee = ComputedEntry(comp, ef_cal * comp.num_atoms)
            eh = float(pd_.get_e_above_hull(ee, allow_negative=True))
        except Exception:
            eh = np.nan
        rows.append({"cod_id": r["cod_id"], "formula_meta": r["formula_meta"],
                     "Eform_MACE_raw": r["eform_mace_raw_eV_atom"], "Eform_cal": ef_cal, "E_hull": eh})
    dfh = pd.DataFrame(rows)
    dfh.to_csv(PROC / "stabilitas_hull_q1.csv", index=False)
    ok.to_csv(PROC / "mace_cod_energi.csv", index=False)
    n_hull = int(dfh["E_hull"].notna().sum())
    ringkas = {
        "n_cod_in_system": int(len(ok)), "n_hull_terdefinisi": n_hull,
        "n_hull_undefined": int(len(ok)) - n_hull,
        "n_energi_tak_fisis_dibuang": n_absurd,
        "mae_hull_vs_api_eV_atom": mae_hull,
        "min_E_hull": float(dfh["E_hull"].min()) if n_hull else None,
        "max_E_hull": float(dfh["E_hull"].max()) if n_hull else None,
        "n_stabil_hull0": int((dfh["E_hull"] <= 1e-6).sum()) if n_hull else 0,
        "tanggal": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    (PROC / "hull_q1_ringkasan.json").write_text(json.dumps(ringkas, indent=2, ensure_ascii=False), encoding="utf-8")
    return dfh, ringkas


def main():
    _, ringkas_kal, _, _ = kalibrasi()
    print("kalibrasi:", json.dumps({k: v for k, v in ringkas_kal.items() if k != "validasi_eksternal"}, indent=1))
    dfh, ringkas_h = hull_cod(ringkas_kal)
    print("hull:", json.dumps(ringkas_h, indent=1))

    laporan = [f"# Kalibrasi MACE -> MP GGA & E_hull COD in-system\n**Tanggal:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
               f"- Offset median = {ringkas_kal['offset_median_eV_atom']} eV/atom "
               f"(CI95 {ringkas_kal['offset_CI95']}); MAE offset = {ringkas_kal['mae_offset_eV_atom']} eV/atom",
               f"- Validasi eksternal 6 fase Wagman/NBS: MAE Eform terkalibrasi = {ringkas_kal['mae_eksternal_6fase_eV_atom']} eV/atom",
               f"- Hull MP: cross-check E_hull vs API MAE = {ringkas_h['mae_hull_vs_api_eV_atom']} eV/atom",
               f"- COD in-system: {ringkas_h['n_cod_in_system']} -> E_hull terdefinisi {ringkas_h['n_hull_terdefinisi']}; "
               f"stabil (E_hull<=1e-6): {ringkas_h['n_stabil_hull0']}",
               f"\n## 10 E_hull terendah (fase stabil kandidat)",
               dfh.sort_values("E_hull").head(10).to_markdown(index=False)]
    (REPORTS / "laporan_kalibrasi_hull.md").write_text("\n".join(laporan), encoding="utf-8")
    print("\n".join(laporan))


if __name__ == "__main__":
    main()
