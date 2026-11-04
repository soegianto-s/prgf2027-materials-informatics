"""Validasi komputasional Top-5 kandidat dengan MLFF universal MACE-MP-0 (medium, float64).

Tahap 1: relaksasi sel+atom (BFGS, fmax 0.05 eV/A) -> uji stabilitas + parameter kisi.
Tahap 2: konstanta elastik finite-difference (ASE) -> K, G, E, nu (Voigt-Reuss-Hill).

Catatan metodologis: MLFF = pra-validasi cepat (CPU); input Quantum ESPRESSO di data/dft/
tetap menjadi jalur DFT definitif di klaster.
"""
import argparse
import json
import sys
import time

import numpy as np
from ase.io import read, write

from common import ROOT, REPORTS

DFT = ROOT / "data" / "dft"
HASIL = ROOT / "data" / "validasi_mlff"
HASIL.mkdir(exist_ok=True, parents=True)

KANDIDAT = [
    ("top1_Ca5P3O12F", "fluorapatit", True),
    ("top2_Ca10P6O25", "oksiapatit", True),
    ("top5_Ca10P6CO27", "karbonat apatit", True),
    ("top6_Ca5P3HO13", "hidroksiapatit", True),
    ("top26_Ca3(PO4)2", "beta-TCP", True),
]


def elastik_fd(atoms, delta=0.005):
    """Tensor elastik finite-difference: C_ij = d(sigma_i)/d(epsilon_j), 12 evaluasi stress.

    Keluaran dalam GPa (stress ASE = eV/A^3 -> kali 160.21766).
    Catatan: atoms.copy() MENGHAPUS kalkulator -> simpan referensi calc dulu.
    """
    calc = atoms.calc
    e0 = atoms.copy()

    def stress_of(eps):
        a = e0.copy()
        f = np.array([[1 + eps[0], eps[5] / 2, eps[4] / 2],
                      [eps[5] / 2, 1 + eps[1], eps[3] / 2],
                      [eps[4] / 2, eps[3] / 2, 1 + eps[2]]])
        a.set_cell(e0.get_cell() @ f.T, scale_atoms=True)
        a.calc = calc
        return a.get_stress()

    c = np.zeros((6, 6))
    for i in range(6):
        eps = np.zeros(6)
        eps[i] = delta
        c[:, i] = (stress_of(eps) - stress_of(-eps)) / (2 * delta)
    return (c + c.T) / 2 * 160.21766


def vrh(c):
    """Voigt-Reuss-Hill K, G, E, nu (GPa) dari tensor 6x6 (GPa)."""
    c11, c22, c33 = c[0, 0], c[1, 1], c[2, 2]
    c12, c13, c23 = c[0, 1], c[0, 2], c[1, 2]
    c44, c55, c66 = c[3, 3], c[4, 4], c[5, 5]
    kv = (c11 + c22 + c33 + 2 * (c12 + c13 + c23)) / 9
    gv = (c11 + c22 + c33 - (c12 + c13 + c23) + 3 * (c44 + c55 + c66)) / 15
    s = np.linalg.inv(c)
    s11, s22, s33 = s[0, 0], s[1, 1], s[2, 2]
    s12, s13, s23 = s[0, 1], s[0, 2], s[1, 2]
    s44, s55, s66 = s[3, 3], s[4, 4], s[5, 5]
    kr = 1 / (s11 + s22 + s33 + 2 * (s12 + s13 + s23))
    gr = 15 / (4 * (s11 + s22 + s33) - 4 * (s12 + s13 + s23) + 3 * (s44 + s55 + s66))
    k = (kv + kr) / 2
    g = (gv + gr) / 2
    e = 9 * k * g / (3 * k + g)
    nu = (3 * k - 2 * g) / (6 * k + 2 * g)
    return k, g, e, nu


def kisi(atoms):
    return np.round(atoms.cell.cellpar(), 3), round(atoms.get_volume(), 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-elastik", action="store_true")
    ap.add_argument("--fmax", type=float, default=0.05)
    args = ap.parse_args()

    from mace.calculators import mace_mp

    print("memuat MACE-MP-0 (medium, float64, CPU)...", flush=True)
    calc = mace_mp(model="medium", default_dtype="float64", device="cpu")
    hasil = {}
    log = [f"# Log Validasi MLFF (MACE-MP-0 medium)\n**Mulai:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n"]

    for nama, label, elastik in KANDIDAT:
        poscar = DFT / nama / "POSCAR"
        if not poscar.exists():
            print(f"{nama}: POSCAR tidak ada, lewati", flush=True)
            continue
        print(f"\n=== {nama} ({label}) ===", flush=True)
        relaxed = HASIL / f"{nama}_relaxed.cif"
        if relaxed.exists() and not args.skip_elastik and elastik:
            # resume: relaksasi sudah ada
            atoms = read(relaxed)
            atoms.calc = calc
            print("  (memuat hasil relaksasi sebelumnya)", flush=True)
            akhir, vol_akhir = kisi(atoms)
            dv = None
            rec = {"nama": nama, "label": label, "natom": int(len(atoms)),
                   "kisi_akhir": akhir.tolist(), "vol_akhir_A3": vol_akhir}
            hasil[nama] = rec
        else:
            atoms = read(poscar)
            atoms.calc = calc
            awal, vol_awal = kisi(atoms)
            print(f"  atom: {len(atoms)} | kisi awal: {awal} | V={vol_awal} A3", flush=True)

            t0 = time.time()
            from ase.filters import ExpCellFilter
            from ase.optimize import BFGS

            opt = BFGS(ExpCellFilter(atoms), logfile=None)
            opt.run(fmax=args.fmax, steps=300)
            print(f"  relaksasi selesai {time.time() - t0:.0f} detik, {opt.get_number_of_steps()} langkah", flush=True)
            akhir, vol_akhir = kisi(atoms)
            dv = (vol_akhir - vol_awal) / vol_awal * 100
            print(f"  kisi akhir: {akhir} | V={vol_akhir} A3 | dV={dv:+.2f}%", flush=True)
            e_atom = atoms.get_potential_energy() / len(atoms)
            print(f"  energi/atom (MACE): {e_atom:.4f} eV", flush=True)
            write(relaxed, atoms)
            rec = {"nama": nama, "label": label, "natom": int(len(atoms)),
                   "kisi_awal": awal.tolist(), "kisi_akhir": akhir.tolist(),
                   "vol_awal_A3": vol_awal, "vol_akhir_A3": vol_akhir,
                   "delta_vol_pct": round(dv, 3), "energi_atom_eV": round(e_atom, 4),
                   "langkah": int(opt.get_number_of_steps())}
            hasil[nama] = rec
            log.append(f"- {label}: dV={dv:+.2f}%, energi/atom={e_atom:.4f} eV, {opt.get_number_of_steps()} langkah")

        if elastik and not args.skip_elastik:
            t0 = time.time()
            print("  menghitung konstanta elastik (finite difference, 12 evaluasi stress)...", flush=True)
            try:
                c = elastik_fd(atoms, delta=0.005)
                k, g, e, nu = vrh(c)
                print(f"  elastik: K={k:.1f} G={g:.1f} E={e:.1f} nu={nu:.3f} GPa ({time.time() - t0:.0f} detik)", flush=True)
                rec["K_GPa"], rec["G_GPa"], rec["E_GPa"], rec["nu"] = round(k, 1), round(g, 1), round(e, 1), round(nu, 3)
                rec["C_ij"] = np.round(c, 2).tolist()
                log.append(f"  - elastik VRH: K={k:.1f}, G={g:.1f}, E={e:.1f}, nu={nu:.3f} GPa")
            except Exception as ex:
                print(f"  elastik GAGAL: {ex}", flush=True)
                log.append(f"  - elastik GAGAL: {ex}")

    (HASIL / "hasil_relaksasi_elastik.json").write_text(
        json.dumps(hasil, indent=2, ensure_ascii=False), encoding="utf-8")
    (HASIL / "LOG_VALIDASI.md").write_text("\n".join(log), encoding="utf-8")
    print("\nselesai. hasil di data/validasi_mlff/", flush=True)


if __name__ == "__main__":
    main()
