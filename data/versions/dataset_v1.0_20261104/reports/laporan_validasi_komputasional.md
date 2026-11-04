# Laporan Validasi Komputasional Top-5 Kandidat (MLFF MACE-MP-0)

**Tanggal:** 2026-11-04 (ronde 4 — Top-5 baru pasca perombakan MCDM)
**Metode:** MACE-MP-0 (medium, float64, CPU) — relaksasi sel+atom BFGS (fmax 0.05 eV/Å, maks 300 langkah) — konstanta elastik finite-difference (±0.005, 12 evaluasi stress, Voigt-Reuss-Hill)

## 1. Stabilitas Struktur (relaksasi)

| Kandidat | Atom | dV relaksasi | Interpretasi |
|---|---|---|---|
| Fluorapatit Ca5P3O12F | 42 | **+0,27%** | stabil |
| Oksiapatit Ca10P6O25 | 41 | **+0,41%** | stabil |
| Karbonat apatit Ca10P6CO27 | 44 | **+0,36%** | stabil |
| Hidroksiapatit Ca5P3HO13 | 44 | **+4,34%** | melonggar — prioritas verifikasi DFT |
| β-TCP Ca3(PO4)2 | 13 | **−0,39%** | stabil |

Empat dari lima kandidat nyaris tidak berubah di bawah MLFF (|dV| ≤ 0,41%) → struktur basis data
sudah berada di minimum energi. HA berekspansi +4,3% — ditandai untuk verifikasi DFT prioritas
(input QE siap di data/dft/).

## 2. Konstanta Elastik (kristal tunggal, MLFF)

| Kandidat | K (GPa) | G (GPa) | E (GPa) | ν |
|---|---|---|---|---|
| Karbonat apatit | 139,3 | 89,1 | **220,3** | 0,236 |
| Hidroksiapatit | 137,6 | 89,2 | **220,1** | 0,233 |
| Fluorapatit | 135,9 | 88,1 | **217,3** | 0,233 |
| Oksiapatit | 131,6 | 85,5 | **210,8** | 0,233 |
| β-TCP | 131,2 | 82,1 | **203,9** | 0,241 |

- ν ≈ 0,23–0,24 konsisten dengan apatit literatur (0,22–0,28).
- E kristal tunggal 204–220 GPa — lebih tinggi dari HAp padat literatur (80–120 GPa); MLFF dikenal
  melebih-lebihkan kekakuan (trained pada DFT; DFT sendiri overbind). Interpretasi: ORDE & PERINGKAT
  relatif antar kandidat, bukan nilai absolut — DFT definitif menyusul di klaster.

## 3. Spesifikasi Desain (Gibson-Ashby)

Untuk mencapai modulus scaffold 10–20 GPa (tulang kortikal), diperlukan porositas ≈ **70–78%**
((ρs/ρb)² = Etarget/Ebulk dengan Ebulk 204–220 GPa) — spesifikasi konkret untuk fabrikasi aditif.

## 4. Keluaran

- `data/validasi_mlff/hasil_relaksasi_elastik.json` — kisi awal/akhir, dV, energi/atom, K/G/E/ν, C_ij per kandidat
- `data/validasi_mlff/LOG_VALIDASI.md` — log run
- `data/validasi_mlff/*_relaxed.cif` — struktur terelaksasi (5 kandidat baru)
- `data/dft/top*_*/` — POSCAR + scf.in + relax.in (input QE/VASP untuk DFT definitif)
