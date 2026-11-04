#!/bin/bash
cd "/root/dft/top26_Ca3(PO4)2"
for f in A B; do
  echo "== $f =="
  grep -m1 'bad line' "$f.out"
  grep -m1 'Error in routine' "$f.out"
  grep -c 'JOB DONE' "$f.out"
done
