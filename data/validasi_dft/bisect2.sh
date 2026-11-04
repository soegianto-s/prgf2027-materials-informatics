#!/bin/bash
set -u
cd "/root/dft/top26_Ca3(PO4)2"
python3 - <<'PYEOF'
from pathlib import Path
s = Path("A.in").read_text()
# C: namelist saja (tanpa kartu apapun)
c = s.split("ATOMIC_SPECIES")[0] + "ATOMIC_SPECIES\nK_POINTS gamma\n"
Path("C.in").write_text(c)
# D: hanya &CONTROL + &SYSTEM
d = c.split("&ELECTRONS")[0]
Path("D.in").write_text(d + "K_POINTS gamma\n")
print("C:", len(c.splitlines()), "baris; D:", len(d.splitlines()), "baris")
PYEOF
for f in C D; do
  OMP_NUM_THREADS=12 pw.x -in "$f.in" > "$f.out" 2>&1
  echo "== $f =="
  grep -m1 'bad line' "$f.out" || true
  grep -m1 'Error in routine' "$f.out" || true
done
