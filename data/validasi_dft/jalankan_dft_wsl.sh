#!/bin/bash
# Runner DFT mandiri di WSL (nohup) — tahan interupsi sesi Windows.
# Untuk tiap tag: vc-relax (skip bila JOB DONE) -> 12 SCF regangan +-1% -> salin hasil ke /mnt/d.
set -u
MNTSRC=/mnt/d/latex/prgf2026/data/dft
MNTLOG=/mnt/d/latex/prgf2026/data/validasi_dft/semua_wsl.log
TAGS="top1_Ca5P3O12F top2_Ca10P6O25 top5_Ca10P6CO27 top6_Ca5P3HO13"
AMP=0.01

log() { echo "[$(date '+%F %T')] $*" | tee -a "$MNTLOG"; }

buat_strain() {
python3 - "$1" <<'PYEOF'
import re, sys, subprocess
from pathlib import Path
d = Path(sys.argv[1])
t = (d / "relax.out").read_text(errors="replace")
sel = t.split("CELL_PARAMETERS (angstrom)")[-1].split("\n", 1)[1].split("\n\n")[0]
pos = t.split("ATOMIC_POSITIONS (crystal)")[-1].split("\n", 1)[1].split("\n\n")[0]
rel = (d / "relax.in").read_text()
kepala = rel.split("CELL_PARAMETERS angstrom")[0]
kp = "K_POINTS" + rel.split("K_POINTS")[1]
(d / "relax.in").write_text(kepala + "CELL_PARAMETERS angstrom\n" + sel + "\n"
                           "ATOMIC_POSITIONS crystal\n" + pos + "\n" + kp)
lat = [[float(x) for x in g.split()[:3]] for g in sel.strip().splitlines()[:3]]
POLA = [(1,0,0,0,0,0),(0,1,0,0,0,0),(0,0,1,0,0,0),(0,0,0,1,0,0),(0,0,0,0,1,0),(0,0,0,0,0,1)]
for i, p in enumerate(POLA, 1):
    for tanda in (1, -1):
        eps = [v * 0.01 * tanda for v in p]
        F = [[1+eps[0], eps[5]/2, eps[4]/2],
             [eps[5]/2, 1+eps[1], eps[3]/2],
             [eps[4]/2, eps[3]/2, 1+eps[2]]]
        lat2 = [[sum(lat[r][k]*F[k][c] for k in range(3)) for c in range(3)] for r in range(3)]
        baru = "\n".join("  %.10f  %.10f  %.10f" % tuple(lat2[r]) for r in range(3))
        teks = rel.split("CELL_PARAMETERS angstrom")[0] + "CELL_PARAMETERS angstrom\n" + baru \
               + "ATOMIC_POSITIONS" + rel.split("ATOMIC_POSITIONS")[1]
        teks = teks.replace("calculation = 'vc-relax'", "calculation = 'scf'")
        teks = teks.replace("conv_thr = 1.0d-6", "conv_thr = 1.0d-8")
        teks = teks.replace("  prefix =", "  tstress = .true.\n  prefix =")
        (d / f"scf_elastik_{i}{'+' if tanda > 0 else '-'}.in").write_text(teks)
PYEOF
}

for tag in $TAGS; do
  nat="/root/dft/$tag"
  mnt="$MNTSRC/$tag"
  log "=== $tag mulai ==="
  mkdir -p "$nat/out" "$nat/pseudo"
  cp "$mnt/relax.in" "$mnt/POSCAR" "$nat/" 2>/dev/null
  cp "$mnt/pseudo/"*.UPF "$nat/pseudo/" 2>/dev/null
  cd "$nat"
  if grep -q "JOB DONE" "$mnt/relax.out" 2>/dev/null; then
    log "$tag vc-relax sudah selesai, lewati"
    cp "$mnt/relax.out" "$nat/relax.out"
  else
    log "$tag vc-relax mulai"
    OMP_NUM_THREADS=12 pw.x -in relax.in > relax.out 2>&1
    cp relax.out "$mnt/relax.out"
    grep -q "JOB DONE" relax.out && log "$tag vc-relax SELESAI" || { log "$tag vc-relax GAGAL, lanjut tag berikut"; continue; }
  fi
  log "$tag regangan elastik (12 SCF)"
  buat_strain "$nat"
  for i in 1 2 3 4 5 6; do
    for t in + -; do
      f="scf_elastik_${i}${t}.in"
      if ! grep -q "total   stress" "$mnt/${f}.out" 2>/dev/null; then
        OMP_NUM_THREADS=12 pw.x -in "$f" > "${f}.out" 2>&1
        cp "${f}.out" "$mnt/${f}.out"
      fi
    done
    log "$tag regangan $i/6 selesai"
  done
  log "$tag SELESAI penuh"
done
log "SEMUA TAG SELESAI"
