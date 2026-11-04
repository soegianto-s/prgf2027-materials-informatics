# Baseline MACE-MP-0: Energi Pembentukan 6 Fase Benchmark
**Tanggal:** 2026-11-04 10:04:55

Referensi unsur (MACE): {'Ca': -2.0097, 'O': -4.8446, 'H': -3.2622, 'F': -1.9919, 'P': -5.1881, 'C': -6.7274}

| Fase | E/atom MACE | Eform MACE | Eform exp (Wagman/NBS) | selisih |
|---|---|---|---|---|
| Ca5P3HO13 | -7.0872 | -2.912 | -3.159 | +0.247 |
| Ca3(PO4)2 | -7.1754 | -2.932 | -3.285 | +0.353 |
| Ca3(PO4)2 | -7.2424 | -2.999 | -3.289 | +0.290 |
| Ca4P2O9 | -7.1382 | -3.004 | -3.297 | +0.293 |
| CaPHO4 | -6.7785 | -2.516 | -2.686 | +0.170 |
| CaPH5O6 | -5.9255 | -1.881 | -1.717 | -0.164 |

**MAE = 0.253 eV/atom** (vs MAE model komposisi 0.094 pada 6 fase yang sama)

Catatan: Eform MACE memakai referensi unsur hasil relaksasi MACE sendiri;
kesalahan sistematik referensi ikut terhitung — ini perbandingan baseline, bukan benchmark MACE.