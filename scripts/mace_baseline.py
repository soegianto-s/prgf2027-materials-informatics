"""Baseline model pretrained (reviewer ronde 6): energi pembentukan MACE-MP-0 vs eksperimen.

Eform_MACE(fase) = E_MACE(fase)/N - sum(el) c_el * e_el, dengan referensi unsur MACE:
Ca fcc, P4 (tetrahedron), O2, H2, F2 (molekul), C (grafen) — semuanya direlaksasi MACE-MP-0.
6 fase benchmark (Wagman/NBS): HA, beta-TCP, alpha-TCP, TTCP, monetite (DCPA), brushite (DCPD).
Keluaran: laporan_baseline_mace.md
"""
import json
import time

import numpy as np
from ase import Atoms
from ase.build import bulk, molecule
from ase.io import read, write
from ase.optimize import BFGS
from ase.filters import ExpCellFilter

from common import ROOT, REPORTS, mp_key
from siapkan_dft import DFT, ambil_struktur_mp, tulis_input

HASIL = ROOT / "data" / "validasi_mace"
HASIL.mkdir(exist_ok=True, parents=True)

# fase benchmark: (tag, formula, mp_id atau None); tag HA & beta-TCP memakai nama data/dft + validasi_mlff
FASE = [
    ("top6_Ca5P3HO13", "Ca5P3HO13", None),          # struktur terelaksasi MLFF tersedia
    ("top26_Ca3(PO4)2", "Ca3(PO4)2", None),         # struktur terelaksasi MLFF tersedia
    ("alphaTCP_Ca3(PO4)2", "Ca3(PO4)2", None),      # dicari: sg P21/a
    ("TTCP_Ca4P2O9", "Ca4P2O9", "mp-aaaaahul"),
    ("DCPA_CaPHO4", "CaPHO4", "mp-aaaabkcc"),
    ("DCPD_CaPH5O6", "CaPH5O6", "mp-aaaabkcb"),
]
E_EXP = {"top6_Ca5P3HO13": -3.159, "top26_Ca3(PO4)2": -3.285, "alphaTCP_Ca3(PO4)2": -3.289,
         "TTCP_Ca4P2O9": -3.297, "DCPA_CaPHO4": -2.686, "DCPD_CaPH5O6": -1.717}  # Wagman/NBS eV/atom

ELEM = {"Ca": None, "P": None, "O": None, "H": None, "F": None, "C": None}


def ambil_symetri(mid):
    import requests
    r = requests.get("https://api.materialsproject.org/materials/summary/",
                     params={"material_ids": mid, "_fields": "material_id,symmetry"},
                     headers={"x-api-key": mp_key()}, timeout=60)
    if r.status_code == 200 and r.json().get("data"):
        return r.json()["data"][0].get("symmetry", {})
    return {}


def struktur_alpha_tcp():
    """Cari entri MP Ca3(PO4)2 dengan spacegroup P21/a (14); fallback: pymatgen-style manual tidak ada."""
    ids = ["mp-aaacqdgz", "mp-aaabefse", "mp-aaabqwyx", "mp-aaabnavf", "mp-aaaaafed"]
    for mid in ids:
        sg = ambil_symetri(mid)
        if sg.get("number") == 14:
            st = ambil_struktur_mp(mid)
            if st:
                tulis_input("alphaTCP_Ca3(PO4)2", "Ca3(PO4)2", st["structure"])
                return True
    return False


def buat_referensi(calc):
    """Struktur referensi unsur MACE; return dict elemen -> energi/atom."""
    ref = {}
    # Ca fcc
    ca = bulk("Ca", "fcc", a=5.588, cubic=True)
    ca.calc = calc
    BFGS(ExpCellFilter(ca), logfile=None).run(fmax=0.01, steps=200)
    ref["Ca"] = ca.get_potential_energy() / len(ca)
    # molekul: O2, H2, F2 (jarak ikat literatur); sel kotak 8 A
    for el, d in [("O", 1.21), ("H", 0.74), ("F", 1.42)]:
        m = Atoms(el + "2", positions=[[0, 0, 0], [d, 0, 0]], cell=[8, 8, 8], pbc=False)
        m.calc = calc
        BFGS(m, logfile=None).run(fmax=0.01, steps=100)
        ref[el] = m.get_potential_energy() / 2
    # P4 tetrahedron (sisi 2.21 A -> u = d/(2 sqrt 2))
    u = 2.21 / (2 * np.sqrt(2))
    p4 = Atoms("P4", positions=[[u, u, u], [-u, -u, u], [-u, u, -u], [u, -u, -u]],
               cell=[10, 10, 10], pbc=False)
    p4.calc = calc
    BFGS(p4, logfile=None).run(fmax=0.01, steps=100)
    ref["P"] = p4.get_potential_energy() / 4
    # C grafen (sel 1x1, dibangun manual: 2 atom, sel heksagonal a=2.46, vakum 10 A)
    c = Atoms("C2", positions=[[0, 0, 5], [2.46 / 3, 2.46 * 0.57735027 / 3 * 0 + 2.46 * 0.57735027 / 3, 5]],
              cell=[2.46, 2.46 * 0.57735027, 10], pbc=[True, True, False])
    # posisi kedua: (2/3, 1/3, 0) fraksional
    c.positions[1] = [2.46 * 2 / 3, 2.46 * 0.57735027 / 3, 5]
    c.calc = calc
    BFGS(ExpCellFilter(c), logfile=None).run(fmax=0.01, steps=200)
    ref["C"] = c.get_potential_energy() / len(c)
    return ref


def komposisi(atoms):
    sym = atoms.get_chemical_symbols()
    n = len(sym)
    from collections import Counter
    cnt = Counter(sym)
    return {el: cnt[el] / n for el in cnt}


def main():
    from mace.calculators import mace_mp
    print("memuat MACE-MP-0 (medium, float64, CPU)...", flush=True)
    calc = mace_mp(model="medium", default_dtype="float64", device="cpu")

    # resume: muat hasil fase & referensi yang sudah selesai
    baris, ref = [], None
    if (HASIL / "hasil_mace_baseline.json").exists():
        lama = json.loads((HASIL / "hasil_mace_baseline.json").read_text(encoding="utf-8"))
        baris = [tuple(b) for b in lama.get("baris", [])]
        ref = lama.get("ref")
        print(f"resume: {len(baris)} fase sudah ada, ref {'ada' if ref else 'tidak ada'}", flush=True)

    # siapkan struktur yang belum ada
    if not struktur_alpha_tcp():
        print("PERINGATAN: struktur alpha-TCP (P21/a) tidak ditemukan di MP; fase dilewati", flush=True)
    for tag, formula, mid in FASE:
        d = DFT / tag
        if mid and not (d / "POSCAR").exists():
            st = ambil_struktur_mp(mid)
            if st:
                tulis_input(tag, formula, st["structure"])
                print(f"{tag}: struktur MP diunduh", flush=True)

    # referensi unsur (hanya elemen yang belum ada)
    print("merelaksasi referensi unsur...", flush=True)
    ref = ref or buat_referensi(calc)
    print("referensi:", {k: round(v, 4) for k, v in ref.items()}, flush=True)

    def simpan():
        mae = float(np.mean([abs(b[5]) for b in baris if not np.isnan(b[5])]))
        (HASIL / "hasil_mace_baseline.json").write_text(
            json.dumps({"ref": ref, "baris": [list(b) for b in baris], "MAE": mae}, indent=2),
            encoding="utf-8")

    sudah = {b[0] for b in baris}
    for tag, formula, mid in FASE:
        if tag in sudah:
            print(f"{tag}: sudah ada di hasil sebelumnya, lewati", flush=True)
            continue
        poscar = DFT / tag / "POSCAR"
        if not poscar.exists():
            print(f"{tag}: POSCAR tidak ada, lewati", flush=True)
            continue
        # pakai struktur terelaksasi MLFF bila tersedia (HA, beta-TCP)
        rel = ROOT / "data" / "validasi_mlff" / f"{tag}_relaxed.cif"
        if not rel.exists():
            rel = HASIL / f"{tag}_relaxed.cif"
        if rel.exists():
            a = read(rel)
            a.calc = calc
            print(f"{tag}: memakai struktur terelaksasi {rel.name}", flush=True)
        else:
            a = read(poscar)
            a.calc = calc
            if len(a) > 100:
                # sel sangat besar (mis. alpha-TCP konvensional 312 atom): relaksasi atom-saja
                # tanpa cell-filter agar praktis di CPU; sel MP sudah terelaksasi DFT.
                print(f"{tag}: merelaksasi {len(a)} atom (sel besar: BFGS atom-saja, fmax 0.1, 150 langkah)...", flush=True)
                BFGS(a, logfile=None).run(fmax=0.1, steps=150)
            else:
                print(f"{tag}: merelaksasi {len(a)} atom (BFGS cell filter, fmax 0.05, 300 langkah)...", flush=True)
                BFGS(ExpCellFilter(a), logfile=None).run(fmax=0.05, steps=300)
            write(HASIL / f"{tag}_relaxed.cif", a)
        e_atom = a.get_potential_energy() / len(a)
        komp = komposisi(a)
        e_ref = sum(c * ref.get(el, 0.0) for el, c in komp.items())
        eform = e_atom - e_ref
        exp = E_EXP.get(tag)
        selisih = eform - exp if exp is not None else float("nan")
        baris.append((tag, formula, e_atom, eform, exp, selisih))
        simpan()  # simpan inkremental agar aman diulang
        print(f"{tag}: E/atom={e_atom:.4f} Eform_MACE={eform:.3f} exp={exp} d={selisih:+.3f}", flush=True)

    mae = float(np.mean([abs(b[5]) for b in baris if not np.isnan(b[5])]))
    laporan = [f"# Baseline MACE-MP-0: Energi Pembentukan 6 Fase Benchmark\n"
               f"**Tanggal:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
               f"Referensi unsur (MACE): { {k: round(v, 4) for k, v in ref.items()} }\n",
               "| Fase | E/atom MACE | Eform MACE | Eform exp (Wagman/NBS) | selisih |",
               "|---|---|---|---|---|"]
    for tag, formula, ea, ef, ex, d in baris:
        laporan.append(f"| {formula} | {ea:.4f} | {ef:.3f} | {ex} | {d:+.3f} |")
    laporan.append(f"\n**MAE = {mae:.3f} eV/atom** (vs MAE model komposisi 0.094 pada 6 fase yang sama)")
    laporan.append("\nCatatan: Eform MACE memakai referensi unsur hasil relaksasi MACE sendiri;")
    laporan.append("kesalahan sistematik referensi ikut terhitung — ini perbandingan baseline, bukan benchmark MACE.")
    (REPORTS / "laporan_baseline_mace.md").write_text("\n".join(laporan), encoding="utf-8")
    (HASIL / "hasil_mace_baseline.json").write_text(
        json.dumps({"ref": ref, "baris": [list(b) for b in baris], "MAE": mae}, indent=2), encoding="utf-8")
    print("\n".join(laporan).encode("ascii", "replace").decode("ascii"))


if __name__ == "__main__":
    main()
