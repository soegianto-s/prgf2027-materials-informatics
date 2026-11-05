#!/bin/bash
# Uji konvergensi k-mesh & ecutwfc untuk PRGF DFT — pada top1 (geometri hasil relax 2x2x2).
# Hasil: konvergensi.log (proses) + konvergensi_summary.txt (energi & stress per konfigurasi).
set -u
LOG=/root/prgf_dft/konvergensi.log
SUM=/root/prgf_dft/konvergensi_summary.txt
log() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }
QE=/root/miniconda3/bin/pw.x
D=/root/prgf_dft/top1_Ca5P3O12F
cd "$D" || exit 1
: > "$SUM"

buat_ktest() { # $1=nama  $2=k-grid  $3=ecutwfc  $4=ecutrho
  local nama="$1" kgrid="$2" ecw="$3" ecr="$4"
  if grep -q "JOB DONE" "ktest_$nama.out" 2>/dev/null; then
    log "$nama sudah selesai, lewati"
    return
  fi
  sed -e "s/calculation = .*/calculation = 'scf'/" \
      -e "s/conv_thr = .*/conv_thr = 1.0d-8/" \
      -e "s/^ *[0-9]\+ [0-9]\+ [0-9]\+ 0 0 0 *$/  $kgrid/" \
      -e "s/ecutwfc = .*/ecutwfc = $ecw/" \
      -e "s/ecutrho = .*/ecutrho = $ecr/" \
      -e "s/  prefix =/  tstress = .true.\n  prefix =/" \
      -e "s/prefix = .*/prefix = 'top1_ktest_$nama'/" \
      -e "s|outdir = .*|outdir = './ktest_out/'|" \
      relax.in > "ktest_$nama.in"
  log "$nama mulai: k=$kgrid ecut=$ecw/$ecr"
  OMP_NUM_THREADS=8 "$QE" -in "ktest_$nama.in" > "ktest_$nama.out" 2>&1
  if grep -q "JOB DONE" "ktest_$nama.out"; then
    log "$nama SELESAI"
  else
    log "$nama GAGAL (lihat ktest_$nama.out)"
  fi
  {
    echo "### $nama  (k=$kgrid ecut=$ecw/$ecr)"
    grep "^!" "ktest_$nama.out" | tail -1
    grep -A3 "total   stress (Ry/bohr" "ktest_$nama.out" | tail -4
    echo
  } >> "$SUM"
}

mkdir -p ktest_out
buat_ktest k222 "2 2 2 0 0 0" 60 480
buat_ktest k333 "3 3 3 0 0 0" 60 480
buat_ktest k444 "4 4 4 0 0 0" 60 480
buat_ktest e80  "2 2 2 0 0 0" 80 640
log "KTEST SEMUA SELESAI — ringkasan di $SUM"
