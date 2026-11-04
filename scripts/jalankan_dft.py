"""Driver DFT Quantum ESPRESSO via WSL Ubuntu (ronde 7/Q1) — top-5 + elastisitas.

QE berjalan di WSL membaca folder Windows langsung (/mnt/d/...), jadi tidak ada salinan.
Urutan per kandidat:
  1. salin UPF yang diperlukan ke <tag>/pseudo/ (pseudo_dir = './pseudo/'),
  2. mpirun pw.x -in relax.in (vc-relax, resume: lewati bila 'JOB DONE' sudah ada),
  3. elastisitas: 6 pola regangan +-1% (12 run SCF) -> tensor C_ij -> VRH K,G,E,nu.

Pemakaian:
  python scripts/jalankan_dft.py --tag top26_Ca3(PO4)2 --np 12   # satu kandidat
  python scripts/jalankan_dft.py --semua                        # berurutan (hari)
  python scripts/jalankan_dft.py --tag X --elastik              # hanya tahap elastik
"""
import argparse
import json
import subprocess
import time
from pathlib import Path

import numpy as np

from common import ROOT
from validasi_mlff import vrh

DFT = ROOT / "data" / "dft"
PSEUDO_DIR = DFT / "pseudo"
URUT = ["top26_Ca3(PO4)2", "top1_Ca5P3O12F", "top2_Ca10P6O25", "top5_Ca10P6CO27", "top6_Ca5P3HO13"]
STRAIN_POLA = [(1, 0, 0, 0, 0, 0), (0, 1, 0, 0, 0, 0), (0, 0, 1, 0, 0, 0),
               (0, 0, 0, 1, 0, 0), (0, 0, 0, 0, 1, 0), (0, 0, 0, 0, 0, 1)]  # komponen Voigt
AMP = 0.01
HASIL = ROOT / "data" / "validasi_dft"
HASIL.mkdir(exist_ok=True, parents=True)


def wsl(cmd, timeout=3600):
    """Jalankan perintah bash di WSL Ubuntu; kembalikan (rc, stdout)."""
    r = subprocess.run(["wsl", "-d", "Ubuntu", "--", "bash", "-lc", cmd],
                       capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout + r.stderr


def siapkan_pseudo(tag):
    d = DFT / tag
    (d / "pseudo").mkdir(exist_ok=True)
    rel = (d / "relax.in").read_text(encoding="utf-8")
    for upf in PSEUDO_DIR.glob("*.UPF"):
        # hanya unsur yang dipakai (baris ATOMIC_SPECIES memuat nama file UPF)
        if upf.name.split(".")[0] in rel.split("ATOMIC_SPECIES")[1][:800]:
            tujuan = d / "pseudo" / upf.name
            if not tujuan.exists():
                tujuan.write_bytes(upf.read_bytes())


def sudah_selesai(path):
    if not path.exists():
        return False
    t = path.read_text(encoding="utf-8", errors="replace")
    return "JOB DONE" in t and "convergence has been achieved" in t


def vc_relax(tag, np_proc):
    """vc-relax di filesystem NATIVE WSL (/root/dft/...) lalu salin relax.out kembali.

    I/O /mnt/d (9p) terlalu lambat untuk wavefunction -> semua I/O QE di /root/dft.
    """
    d = DFT / tag
    siapkan_pseudo(tag)
    out = d / "relax.out"
    if sudah_selesai(out):
        print(f"{tag}: vc-relax sudah selesai, lewati")
        return True
    print(f"{tag}: memulai vc-relax ({np_proc} MPI x 6 OMP)...", flush=True)
    t0 = time.time()
    # quote wajib: tag memuat tanda kurung, mis. top26_Ca3(PO4)2
    mnt = f"'/mnt/d/latex/prgf2026/data/dft/{tag}'"
    nat = f"'/root/dft/{tag}'"
    rc, log = wsl(
        f"rm -rf {nat} && mkdir -p {nat}/out {nat}/pseudo && "
        f"cp {mnt}/relax.in {mnt}/POSCAR {nat}/ && cp {mnt}/pseudo/* {nat}/pseudo/ && "
        f"cd {nat} && "
        f"OMP_NUM_THREADS=12 pw.x -in relax.in > relax.out 2>&1; "
        f"cp relax.out {mnt}/relax.out",
        timeout=8 * 3600)
    print(f"{tag}: rc={rc} waktu={time.time()-t0:.0f}s", flush=True)
    if rc != 0:
        print(log[-500:])
    return sudah_selesai(out)


def sel_terelaksasi(tag):
    """Ambil sel + posisi FINAL dari relax.out -> perbarui relax.in (dasar regangan elastik)."""
    d = DFT / tag
    t = (d / "relax.out").read_text(encoding="utf-8", errors="replace")
    if "CELL_PARAMETERS (angstrom)" not in t or "ATOMIC_POSITIONS (crystal)" not in t:
        return False
    # blok final = kemunculan terakhir masing-masing
    sel = t.split("CELL_PARAMETERS (angstrom)")[-1].split("\n", 1)[1].split("\n\n")[0]
    pos = t.split("ATOMIC_POSITIONS (crystal)")[-1].split("\n", 1)[1].split("\n\n")[0]
    rel = (d / "relax.in").read_text(encoding="utf-8")
    kepala = rel.split("CELL_PARAMETERS angstrom")[0]
    kp = "K_POINTS" + rel.split("K_POINTS")[1]
    (d / "relax.in").write_text(
        kepala + "CELL_PARAMETERS angstrom\n" + sel + "\n"
        "ATOMIC_POSITIONS crystal\n" + pos + "\n" + kp)
    return True


def strain_input(tag, pola, tanda, nama):
    """Buat <nama>.in dengan regangan Voigt pola*AMP*tanda pada sel TERELAKSASI relax.in."""
    d = DFT / tag
    rel = (d / "relax.in").read_text(encoding="utf-8")
    sel = rel.split("CELL_PARAMETERS angstrom")[1].split("ATOMIC_POSITIONS")[0]
    garis = [g.split() for g in sel.strip().splitlines() if g.split()]
    lat = np.array([[float(x) for x in g] for g in garis[:3]])
    eps = np.array(pola) * AMP * tanda
    F = np.array([[1 + eps[0], eps[5] / 2, eps[4] / 2],
                  [eps[5] / 2, 1 + eps[1], eps[3] / 2],
                  [eps[4] / 2, eps[3] / 2, 1 + eps[2]]])
    lat2 = lat @ F.T
    baru = f"  {lat2[0][0]:.10f}  {lat2[0][1]:.10f}  {lat2[0][2]:.10f}\n" \
           f"  {lat2[1][0]:.10f}  {lat2[1][1]:.10f}  {lat2[1][2]:.10f}\n" \
           f"  {lat2[2][0]:.10f}  {lat2[2][1]:.10f}  {lat2[2][2]:.10f}\n"
    teks = rel.split("CELL_PARAMETERS angstrom")[0] + "CELL_PARAMETERS angstrom\n" + baru \
        + "ATOMIC_POSITIONS" + rel.split("ATOMIC_POSITIONS")[1]
    teks = teks.replace("calculation = 'vc-relax'", "calculation = 'scf'")
    teks = teks.replace("conv_thr = 1.0d-6", "conv_thr = 1.0d-8")
    teks = teks.replace("  prefix =", "  tstress = .true.\n  prefix =")
    (d / nama).write_text(teks, encoding="utf-8")
    return nama


def parse_stress(tag, nama_in, np_proc):
    d = DFT / tag
    out = d / f"{nama_in}.out"
    if "total   stress" not in (out.read_text(encoding="utf-8", errors="replace") if out.exists() else ""):
        mnt = f"'/mnt/d/latex/prgf2026/data/dft/{tag}'"
        nat = f"'/root/dft/{tag}'"
        rc, log = wsl(
            f"mkdir -p {nat}/out {nat}/pseudo && "
            f"cp {mnt}/{nama_in} {mnt}/relax.in {nat}/ && cp {mnt}/pseudo/* {nat}/pseudo/ && "
            f"cd {nat} && OMP_NUM_THREADS=12 pw.x -in {nama_in} > {nama_in}.out 2>&1; "
            f"cp {nama_in}.out {mnt}/{nama_in}.out",
            timeout=3600)
    t = out.read_text(encoding="utf-8", errors="replace")
    if "total   stress" not in t:
        return None
    blok = t.split("total   stress")[1].splitlines()[1:4]
    # 3 kolom pertama = Ry/bohr^3; konversi ke GPa: 1 Ry/bohr^3 = 14710.5 GPa
    s = np.array([[float(x) for x in g.split()[:3]] for g in blok]) * 14710.5
    return np.array([s[0, 0], s[1, 1], s[2, 2], s[1, 2], s[0, 2], s[0, 1]])


def elastik(tag, np_proc):
    d = DFT / tag
    sel_terelaksasi(tag)
    c = np.zeros((6, 6))
    for i, pola in enumerate(STRAIN_POLA):
        sp, sm = None, None
        for tanda in [+1, -1]:
            nama = strain_input(tag, pola, tanda, f"scf_elastik_{i + 1}{'+' if tanda > 0 else '-'}.in")
            s = parse_stress(tag, nama, np_proc)
            if s is None:
                print(f"{tag}: stress gagal {nama}, lewati regangan ini")
                break
            if tanda > 0:
                sp = s
            else:
                sm = s
        if sp is not None and sm is not None:
            # konvensi QE: tegangan positif = kompresi -> C = (sigma(-eps) - sigma(+eps)) / 2eps
            c[:, i] = (sm - sp) / (2 * AMP)
    c = (c + c.T) / 2
    k, g, e, nu = vrh(c)
    rec = {"tag": tag, "C_ij": np.round(c, 2).tolist(), "K_GPa": round(k, 1),
           "G_GPa": round(g, 1), "E_GPa": round(e, 1), "nu": round(nu, 3)}
    (HASIL / f"{tag}_elastik.json").write_text(json.dumps(rec, indent=2), encoding="utf-8")
    print(f"{tag} elastik DFT: K={k:.1f} G={g:.1f} E={e:.1f} nu={nu:.3f} GPa")
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default=None)
    ap.add_argument("--semua", action="store_true")
    ap.add_argument("--np", type=int, default=12)
    ap.add_argument("--elastik", action="store_true")
    args = ap.parse_args()

    tags = URUT if (args.semua or not args.tag) else [args.tag]
    hasil = {}
    for tag in tags:
        if args.elastik:
            hasil[tag] = elastik(tag, args.np)
        else:
            if vc_relax(tag, args.np):
                hasil[tag] = elastik(tag, args.np)
            else:
                print(f"{tag}: vc-relax TIDAK konvergen — periksa relax.out")
    (HASIL / "hasil_dft.json").write_text(json.dumps(hasil, indent=2, ensure_ascii=False), encoding="utf-8")
    print("selesai:", json.dumps(hasil, indent=1)[:800])


if __name__ == "__main__":
    main()
