from pathlib import Path

d = Path("/root/dft/top26_Ca3(PO4)2")
base_in = d / "relax2.in"
s = base_in.read_text()
base = s.split("ATOMIC_SPECIES")[0]
cards = "ATOMIC_SPECIES" + s.split("ATOMIC_SPECIES")[1]

# A: tanpa &IONS dan &CELL
a = base.replace("&IONS\n/\n", "").replace("&CELL\n  press = 0.0\n  cell_dofree = 'all'\n/\n", "")
(d / "A.in").write_text(a + cards)

# B: dengan &IONS, tanpa &CELL
b = base.replace("&CELL\n  press = 0.0\n  cell_dofree = 'all'\n/\n", "")
(d / "B.in").write_text(b + cards)

print("A.in IONS:", "&IONS" in a, "CELL:", "&CELL" in a)
print("B.in IONS:", "&IONS" in b, "CELL:", "&CELL" in b)
