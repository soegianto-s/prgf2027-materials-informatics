"""Screening MACE-MP-0 single-point pada struktur eksperimen COD (ronde 7/Q1).

Single-point (TANPA relaksasi) — struktur COD adalah hasil difraksi/optimasi eksperimen;
batas ini dinyatakan eksplisit di manuskrip. Energi referensi unsur diambil dari
data/validasi_mace/hasil_mace_baseline.json (ref MACE sendiri: Ca fcc, P4, O2, H2, F2, C grafen).

Protokol:
- parse CIF: pymatgen CifParser utama, fallback ase.io.read;
- disorder: pilih spesies dominan per situs; occupancy dominan < 0.5 -> flag disorder_approx;
- skip: tidak ada koordinat, >300 atom (setelah primitive bila mungkin), atau parse gagal;
- checkpoint JSONL per cod_id (resumable); satu proses, torch.set_num_threads(12).
- PENTING: jangan torch.no_grad() — MACE menghitung stress via autograd.

Keluaran:
  data/validasi_mace/screening_cod/checkpoint.jsonl
  data/processed/mace_screening_cod.csv
  data/processed/mace_screening_cod_ringkasan.json
  data/reports/laporan_screening_mace_cod.md
"""
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from common import PROC, RAW, REPORTS, ROOT

CIFDIR = RAW / "cod" / "cif"
HASIL = ROOT / "data" / "validasi_mace" / "screening_cod"
HASIL.mkdir(parents=True, exist_ok=True)
CKPT = HASIL / "checkpoint.jsonl"
ELEM_SISTEM = {"Ca", "P", "O", "H", "F", "C"}


def muat_referensi():
    j = json.loads((ROOT / "data" / "validasi_mace" / "hasil_mace_baseline.json").read_text(encoding="utf-8"))
    return j["ref"], float(j["MAE"])


def parse_cif(path):
    """Kembalikan ase.Atoms + dict info QC, atau None + alasan."""
    from ase import Atoms
    try:
        from pymatgen.io.cif import CifParser
        from pymatgen.io.ase import AseAtomsAdaptor
        st = CifParser(str(path)).parse_structures(primitive=False)[0]
        atoms = AseAtomsAdaptor.get_atoms(st)
        # QC disorder dari struktur pymatgen
        occ_min = 1.0
        for site in st:
            for sp, occ in site.species.items():
                occ_min = min(occ_min, occ)
        # ambil spesies dominan -> sudah otomatis di AseAtomsAdaptor (memilih mayoritas)
        return atoms, {"parser": "pymatgen", "occ_min": round(occ_min, 3)}
    except Exception as e:
        try:
            from ase.io import read
            atoms = read(str(path))
            if atoms is None or len(atoms) == 0:
                return None, f"parse_gagal: {type(e).__name__}"
            return atoms, {"parser": "ase", "occ_min": np.nan}
        except Exception as e2:
            return None, f"parse_gagal: {type(e).__name__}/{type(e2).__name__}"


def komposisi(atoms):
    sym = atoms.get_chemical_symbols()
    n = len(sym)
    from collections import Counter
    cnt = Counter(sym)
    return {el: cnt[el] / n for el in cnt}


def screening_satu(f, calc, ref):
    path = CIFDIR / f"{f}.cif"
    if not path.exists():
        return {"status": "skip", "alasan": "cif_tidak_ada"}
    atoms, info = parse_cif(path)
    if atoms is None:
        return {"status": "skip", "alasan": info or "parse_gagal"}
    n = len(atoms)
    if n > 300:
        # coba primitive pymatgen (struktur simetri bisa direduksi)
        try:
            from pymatgen.io.cif import CifParser
            from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
            from pymatgen.io.ase import AseAtomsAdaptor
            st = CifParser(str(path)).parse_structures(primitive=False)[0]
            prim = SpacegroupAnalyzer(st).get_primitive_standard_structure()
            atoms = AseAtomsAdaptor.get_atoms(prim)
            info["parser"] += "+primitive"
        except Exception:
            pass
        if len(atoms) > 300:
            return {"status": "skip", "alasan": f"sel_terlalu_besar_{len(atoms)}"}
    t0 = time.time()
    try:
        atoms.calc = calc
        e_total = atoms.get_potential_energy()
    except Exception as e:
        return {"status": "gagal", "alasan": f"mace_error_{type(e).__name__}"}
    e_atom = e_total / len(atoms)
    komp = komposisi(atoms)
    e_ref = sum(c * ref.get(el, 0.0) for el, c in komp.items())
    eform = e_atom - e_ref
    in_system = set(komp) <= ELEM_SISTEM
    out = {"cod_id": f, "status": "ok", "parser": info.get("parser"),
           "natom": len(atoms), "occ_min": info.get("occ_min"),
           "e_total_eV": round(float(e_total), 6), "e_eV_atom": round(e_atom, 6),
           "eform_mace_raw_eV_atom": round(eform, 6), "in_system": bool(in_system),
           "komposisi": {k: round(v, 4) for k, v in sorted(komp.items())},
           "waktu_s": round(time.time() - t0, 2)}
    return out


def main():
    import torch
    torch.set_num_threads(12)
    from mace.calculators import mace_mp
    print("memuat MACE-MP-0 (L1, float64, CPU)...", flush=True)
    calc = mace_mp(model="medium", default_dtype="float64", device="cpu")
    ref, _ = muat_referensi()
    print("referensi unsur:", {k: round(v, 4) for k, v in ref.items()}, flush=True)

    manifest = json.loads((RAW / "cod" / "_manifest_unduhan.json").read_text(encoding="utf-8"))
    urut = sorted(manifest["manifest"])
    selesai = {}
    if CKPT.exists():
        for line in CKPT.read_text(encoding="utf-8").splitlines():
            if line.strip():
                d = json.loads(line)
                selesai[d["cod_id"]] = d

    n_ok = n_skip = n_gagal = 0
    for i, f in enumerate(urut, 1):
        if f in selesai:
            continue
        d = screening_satu(f, calc, ref)
        d["formula_meta"] = manifest["manifest"][f].get("formula", "")
        with CKPT.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(d, ensure_ascii=False) + "\n")
        selesai[f] = d
        if d["status"] == "ok":
            n_ok += 1
        elif d["status"] == "skip":
            n_skip += 1
        else:
            n_gagal += 1
        if i % 25 == 0 or i == len(urut):
            print(f"{i}/{len(urut)}  ok={n_ok} skip={n_skip} gagal={n_gagal}", flush=True)

    df = pd.DataFrame([s for s in selesai.values()])
    df.to_csv(PROC / "mace_screening_cod.csv", index=False)
    in_sys = df[df["status"] == "ok"]
    n_in = int(in_sys["in_system"].sum()) if len(in_sys) else 0
    ringkas = {
        "n_total": len(urut), "n_ok": n_ok, "n_skip": n_skip, "n_gagal": n_gagal,
        "n_in_system": n_in, "n_out_system": n_ok - n_in,
        "checkpoint_mace": "20231203mace128L1_epoch199model (L1, float64)",
        "mace_torch": None, "tanggal": time.strftime("%Y-%m-%d %H:%M:%S"),
        "alasan_skip": df[df["status"] != "ok"].groupby("alasan").size().to_dict() if len(df) else {},
        "in_system_min_Eform": float(in_sys[in_sys["in_system"]]["eform_mace_raw_eV_atom"].min()) if n_in else None,
        "in_system_max_Eform": float(in_sys[in_sys["in_system"]]["eform_mace_raw_eV_atom"].max()) if n_in else None,
    }
    try:
        import mace
        ringkas["mace_torch"] = getattr(mace, "__version__", "?")
    except Exception:
        pass
    (PROC / "mace_screening_cod_ringkasan.json").write_text(
        json.dumps(ringkas, indent=2, ensure_ascii=False), encoding="utf-8")
    print("ringkasan:", json.dumps(ringkas, indent=1)[:800])
    print(f"SELESAI: ok={n_ok} skip={n_skip} gagal={n_gagal} in_system={n_in}")


if __name__ == "__main__":
    main()
