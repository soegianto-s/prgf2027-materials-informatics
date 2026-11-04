#!/bin/bash
set -u
cd "/root/dft/top26_Ca3(PO4)2"
python3 - <<'PYEOF'
from pathlib import Path
s = Path("/mnt/d/latex/prgf2026/data/dft/top26_Ca3(PO4)2/relax.in").read_text()
# bangun ulang dari nol: namelist kanonik + kartu kanonik, LF murni
nat = 13
inp = """&CONTROL
  calculation = 'vc-relax'
  etot_conv_thr = 1.0d-4
  forc_conv_thr = 1.0d-3
  pseudo_dir = './pseudo/'
  outdir = './out/'
/
&SYSTEM
  ibrav = 0
  nat = 13
  ntyp = 3
  ecutwfc = 60.0
  ecutrho = 480.0
  occupations = 'smearing'
  smearing = 'gaussian'
  degauss = 0.01
/
&ELECTRONS
  conv_thr = 1.0d-6
  mixing_beta = 0.7
/
&IONS
  ion_dynamics = 'bfgs'
/
&CELL
  cell_dynamics = 'bfgs'
  press = 0.0
/
""" + s.split("ATOMIC_SPECIES")[1]
# kartu: susun kanonik ATOMIC_SPECIES, CELL_PARAMETERS, ATOMIC_POSITIONS, K_POINTS
spec = inp.split("CELL_PARAMETERS")[0]
rest = "CELL_PARAMETERS" + inp.split("CELL_PARAMETERS")[1]
kp = "K_POINTS automatic\n2 2 2 0 0 0\n"
rest = rest.replace(kp, "")
inp2 = spec + rest + kp
inp2 = inp2.replace("ATOMIC_POS crystal", "ATOMIC_POSITIONS crystal")
Path("E.in").write_text(inp2.replace("\r\n", "\n"))
print("E: urutan:", [x for x in ["&CONTROL","&SYSTEM","&ELECTRONS","&IONS","&CELL","ATOMIC_SPECIES","CELL_PARAMETERS","ATOMIC_POSITIONS","K_POINTS"] if x in inp2])
PYEOF
OMP_NUM_THREADS=12 pw.x -in E.in > E.out 2>&1
grep -m1 'bad line' E.out || true
grep -m1 'Error in routine' E.out || true
grep -m1 'JOB DONE' E.out || echo "belum JOB DONE"
