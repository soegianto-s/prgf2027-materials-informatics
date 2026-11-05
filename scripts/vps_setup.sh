#!/bin/bash
# Setup + antrean DFT di VPS (CentOS Stream 10) — dijalankan di dalam tmux.
# v2 (2026-11-06): perbaikan bug newline & posisi atom final di buat_strain,
#   outdir/prefix unik per strain, verifikasi hasil tiap run, cek pseudo.
set -u
# Parameter produksi (ditentukan dari hasil uji konvergensi konvergensi.sh)
K_GRID="${K_GRID:-3 3 3 0 0 0}"
ECUT_WFC="${ECUT_WFC:-60}"
ECUT_RHO="${ECUT_RHO:-480}"
LOG=/root/prgf_dft/run.log
log() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

mkdir -p /root/prgf_dft

# 1. Miniconda + QE (idempoten)
if [ ! -x /root/miniconda3/bin/pw.x ]; then
  log "memasang miniconda..."
  [ -f /root/miniconda.sh ] || curl -sL https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /root/miniconda.sh
  [ -d /root/miniconda3 ] || bash /root/miniconda.sh -b -p /root/miniconda3 >> "$LOG" 2>&1
  log "memasang QE via conda-forge (override-channels: lewati ToS anaconda.com)..."
  /root/miniconda3/bin/conda install -y -q -c conda-forge --override-channels qe >> "$LOG" 2>&1
fi
QE=/root/miniconda3/bin/pw.x
PY=/root/miniconda3/bin/python3
[ -x "$QE" ] || { log "QE GAGAL TERPASANG — periksa $LOG"; exit 1; }
log "QE: $($QE --version 2>&1 | head -1)"

buat_strain() {
"$PY" - "$1" <<'PYEOF'
import sys, re
from pathlib import Path
d = Path(sys.argv[1])
t = (d / "relax.out").read_text(errors="replace")
# sel & posisi FINAL hasil relax (bagian "Begin final coordinates" di relax.out)
sel = t.split("CELL_PARAMETERS (angstrom)")[-1].split("\n", 1)[1].split("\n\n")[0].strip()
pos = t.split("ATOMIC_POSITIONS (crystal)")[-1].split("\n", 1)[1].split("\n\n")[0].strip()
rel = (d / "relax.in").read_text()
kepala = rel.split("CELL_PARAMETERS angstrom")[0].rstrip()
kp = "K_POINTS" + rel.split("K_POINTS")[1]
# tulis balik relax.in dengan struktur final (sel + posisi hasil relax)
(d / "relax.in").write_text(kepala + "\n\nCELL_PARAMETERS angstrom\n" + sel + "\n\n"
                           "ATOMIC_POSITIONS crystal\n" + pos + "\n\n" + kp)
m = re.search(r"prefix\s*=\s*'([^']+)'", kepala)
pref = m.group(1) if m else "calc"
lat = [[float(x) for x in g.split()[:3]] for g in sel.splitlines()[:3]]
POLA = [(1,0,0,0,0,0),(0,1,0,0,0,0),(0,0,1,0,0,0),(0,0,0,1,0,0),(0,0,0,0,1,0),(0,0,0,0,0,1)]
for i, p in enumerate(POLA, 1):
    for tanda in (1, -1):
        eps = [v * 0.01 * tanda for v in p]
        F = [[1+eps[0], eps[5]/2, eps[4]/2],
             [eps[5]/2, 1+eps[1], eps[3]/2],
             [eps[4]/2, eps[3]/2, 1+eps[2]]]
        lat2 = [[sum(lat[r][k]*F[k][c] for k in range(3)) for c in range(3)] for r in range(3)]
        baru = "\n".join("  %.10f  %.10f  %.10f" % tuple(lat2[r]) for r in range(3))
        tag = f"{i}{'+' if tanda > 0 else '-'}"
        # kepala + sel terdeformasi + POSISI FINAL hasil relax + K_POINTS (newline rapi)
        teks = (kepala + "\n\nCELL_PARAMETERS angstrom\n" + baru + "\n\n"
                "ATOMIC_POSITIONS crystal\n" + pos + "\n\n" + kp)
        teks = teks.replace("calculation = 'vc-relax'", "calculation = 'scf'")
        teks = teks.replace("conv_thr = 1.0d-6", "conv_thr = 1.0d-8")
        teks = teks.replace("  prefix =", "  tstress = .true.\n  prefix =")
        teks = teks.replace(f"prefix = '{pref}'", f"prefix = '{pref}_el{tag}'")
        # outdir unik per strain: save hasil relax di ./out/ tetap utuh
        teks = teks.replace("outdir = './out/'", "outdir = './strain_out/'")
        (d / f"scf_elastik_{tag}.in").write_text(teks)
# referensi tanpa regangan (E0, sigma0) pada mesh produksi — sel final hasil relax
teks_ref = (kepala + "\n\nCELL_PARAMETERS angstrom\n" + sel + "\n\n"
            "ATOMIC_POSITIONS crystal\n" + pos + "\n\n" + kp)
teks_ref = teks_ref.replace("calculation = 'vc-relax'", "calculation = 'scf'")
teks_ref = teks_ref.replace("conv_thr = 1.0d-6", "conv_thr = 1.0d-8")
teks_ref = teks_ref.replace("  prefix =", "  tstress = .true.\n  prefix =")
teks_ref = teks_ref.replace(f"prefix = '{pref}'", f"prefix = '{pref}_ref'")
teks_ref = teks_ref.replace("outdir = './out/'", "outdir = './strain_out/'")
(d / "scf_referensi.in").write_text(teks_ref)
PYEOF
}

# 2. antrean 4 apatit
TAGS="top1_Ca5P3O12F top2_Ca10P6O25 top5_Ca10P6CO27 top6_Ca5P3HO13"
GAGAL_TOTAL=0
for tag in $TAGS; do
  d="/root/prgf_dft/$tag"
  [ -d "$d" ] || { log "$tag: input belum disinkron, lewati"; continue; }
  cd "$d" || continue
  log "=== $tag mulai (k=$K_GRID ecut=$ECUT_WFC/$ECUT_RHO) ==="
  # terapkan k-mesh & ecut produksi (idempoten)
  sed -i -E "s/^ *[0-9]+ [0-9]+ [0-9]+ 0 0 0 *$/  $K_GRID/" relax.in
  sed -i "s/ecutwfc = .*/ecutwfc = $ECUT_WFC/" relax.in
  sed -i "s/ecutrho = .*/ecutrho = $ECUT_RHO/" relax.in
  # cek pseudo lengkap sebelum relax
  HILANG=""
  while read -r p; do
    [ -f "$d/pseudo/$p" ] || HILANG="$HILANG $p"
  done < <(grep -o '[A-Za-z0-9._-]*\.UPF' "$d/relax.in")
  if [ -n "$HILANG" ]; then
    log "$tag: pseudo hilang:$HILANG — GAGAL"
    GAGAL_TOTAL=$((GAGAL_TOTAL+1)); continue
  fi
  if grep -q "JOB DONE" relax.out 2>/dev/null; then
    log "$tag vc-relax sudah selesai, lewati"
  else
    rm -f CRASH
    mkdir -p out
    if [ -d "out/$tag.save" ]; then
      grep -q "restart_mode" relax.in || sed -i "/calculation = 'vc-relax'/a\  restart_mode = 'restart'" relax.in
    fi
    log "$tag vc-relax mulai"
    OMP_NUM_THREADS=8 "$QE" -in relax.in > relax.out 2>&1
    grep -q "JOB DONE" relax.out && log "$tag vc-relax SELESAI" || { log "$tag vc-relax GAGAL (lihat relax.out/CRASH)"; GAGAL_TOTAL=$((GAGAL_TOTAL+1)); continue; }
  fi
  log "$tag regangan elastik (12 SCF)"
  buat_strain "$d"
  mkdir -p strain_out
  gagal_strain=0
  for i in 1 2 3 4 5 6; do
    for t in + -; do
      f="scf_elastik_${i}${t}.in"
      if grep -q "total   stress" "strain_out/${f}.out" 2>/dev/null; then
        log "$tag strain ${i}${t} sudah ada, lewati"
        continue
      fi
      log "$tag strain ${i}${t} mulai"
      OMP_NUM_THREADS=8 "$QE" -in "$f" > "strain_out/${f}.out" 2>&1
      if grep -q "total   stress" "strain_out/${f}.out"; then
        log "$tag strain ${i}${t} OK"
      else
        gagal_strain=$((gagal_strain+1))
        log "$tag strain ${i}${t} GAGAL"
      fi
    done
  done
  # referensi tanpa regangan (E0, sigma0) pada mesh produksi
  if grep -q "total   stress" "strain_out/scf_referensi.in.out" 2>/dev/null; then
    log "$tag referensi sudah ada, lewati"
  else
    log "$tag referensi tanpa regangan mulai"
    OMP_NUM_THREADS=8 "$QE" -in scf_referensi.in > "strain_out/scf_referensi.in.out" 2>&1
    if grep -q "total   stress" "strain_out/scf_referensi.in.out"; then
      log "$tag referensi OK"
    else
      gagal_strain=$((gagal_strain+1))
      log "$tag referensi GAGAL"
    fi
  fi
  if [ "$gagal_strain" -eq 0 ]; then
    log "$tag SELESAI penuh (12/12 strain + referensi OK)"
  else
    GAGAL_TOTAL=$((GAGAL_TOTAL+1))
    log "$tag SELESAI DENGAN $gagal_strain run GAGAL (12 strain + referensi)"
  fi
done
log "SEMUA SELESAI (gagal total: $GAGAL_TOTAL)"
