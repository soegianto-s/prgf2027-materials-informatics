#!/bin/bash
# Setup + antrean DFT di VPS (CentOS Stream 10) — dijalankan di dalam tmux.
set -u
LOG=/root/prgf_dft/run.log
log() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

mkdir -p /root/prgf_dft

# 1. Miniconda + QE (idempoten)
if [ ! -x /root/miniconda3/bin/pw.x ]; then
  log "memasang miniconda..."
  [ -f /root/miniconda.sh ] || curl -sL https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /root/miniconda.sh
  [ -d /root/miniconda3 ] || bash /root/miniconda.sh -b -p /root/miniconda3 >> "$LOG" 2>&1
  log "memasang QE via conda-forge..."
  /root/miniconda3/bin/conda install -y -q -c conda-forge qe >> "$LOG" 2>&1
fi
QE=/root/miniconda3/bin/pw.x
PY=/root/miniconda3/bin/python3
log "QE: $($QE --version 2>&1 | head -1)"

buat_strain() {
"$PY" - "$1" <<'PYEOF'
import sys
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

# 2. antrean 4 apatit
TAGS="top1_Ca5P3O12F top2_Ca10P6O25 top5_Ca10P6CO27 top6_Ca5P3HO13"
for tag in $TAGS; do
  d="/root/prgf_dft/$tag"
  [ -d "$d" ] || { log "$tag: input belum disinkron, lewati"; continue; }
  cd "$d"
  log "=== $tag mulai ==="
  if grep -q "JOB DONE" relax.out 2>/dev/null; then
    log "$tag vc-relax sudah selesai, lewati"
  else
    mkdir -p out
    if [ -d "out/$tag.save" ]; then
      sed -i "/calculation = 'vc-relax'/a\  restart_mode = 'restart'" relax.in
    fi
    OMP_NUM_THREADS=8 "$QE" -in relax.in > relax.out 2>&1
    grep -q "JOB DONE" relax.out && log "$tag vc-relax SELESAI" || { log "$tag vc-relax GAGAL"; continue; }
  fi
  log "$tag regangan elastik (12 SCF)"
  buat_strain "$d"
  mkdir -p strain_out
  for i in 1 2 3 4 5 6; do
    for t in + -; do
      f="scf_elastik_${i}${t}.in"
      if ! grep -q "total   stress" "strain_out/${f}.out" 2>/dev/null; then
        OMP_NUM_THREADS=8 "$QE" -in "$f" > "strain_out/${f}.out" 2>&1
      fi
    done
    log "$tag regangan $i/6"
  done
  log "$tag SELESAI penuh"
done
log "SEMUA SELESAI"
