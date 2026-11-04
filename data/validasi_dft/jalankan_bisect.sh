#!/bin/bash
set -u
cd "/root/dft/top26_Ca3(PO4)2"
python3 /mnt/d/latex/prgf2026/data/validasi_dft/buat_bisect.py
for f in A B; do
  OMP_NUM_THREADS=12 pw.x -in "$f.in" > "$f.out" 2>&1
  echo "== $f =="
  grep -m1 'bad line' "$f.out" || true
  grep -m1 'Error in routine' "$f.out" || true
  grep -m1 -c 'JOB DONE' "$f.out" || true
done
