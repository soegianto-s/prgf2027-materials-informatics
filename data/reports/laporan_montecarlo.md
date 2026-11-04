# Laporan Monte Carlo MCDM — Propagasi Ketidakpastian
**Tanggal:** 2026-11-04 08:08:43

## Metode
- 1000 run x 3 skenario bobot = **3000 peringkat** (TOPSIS+VIKOR, v=0.5; peringkat rata-rata keduanya).
- Bobot ~ Dirichlet(alpha = w_manual x 20) sekitar tiap skenario manual {'W1_berimbang': [0.4, 0.3, 0.3], 'W2_stabilitas': [0.6, 0.2, 0.2], 'W3_komposisi': [0.3, 0.3, 0.4]}.
- Noise prediksi ML: Eform N(0, 0.297) eV/atom dan densitas N(0, 0.307) g/cm3 (MAE CV model komposisi murni) — mewakili ketidakpastian bila properti diprediksi untuk komposisi baru; Ca/P eksak (stoikiometri).
- Peringkat per KOMPOSISI TEREDUKSI (polimorf/kelipatan satu grup): entri terbaik grup.
## Hasil Top-15 (median rank + interval 90%)

| formula     | sumber           | kelompok            |   median_rank |   p5_rank |   p95_rank |   pct_top5 |   pct_top10 |
|:------------|:-----------------|:--------------------|--------------:|----------:|-----------:|-----------:|------------:|
| Ca5P3O12F   | MaterialsProject | apatit_hidroksi     |             2 |         1 |          8 |       86.3 |        97.8 |
| Ca10P6O25   | MaterialsProject | apatit_hidroksi     |             3 |         1 |         13 |       70.7 |        90.8 |
| Ca5P3HO13   | MaterialsProject | apatit_hidroksi     |             4 |         1 |         13 |       67.3 |        89.5 |
| Ca3(PO4)2   | MaterialsProject | trikalsium_fosfat   |             5 |         1 |         17 |       55.9 |        82.1 |
| Ca4P2O9     | MaterialsProject | tetrakalsium_fosfat |            16 |         2 |         50 |       17.4 |        34.8 |
| Ca2P2O7     | MaterialsProject | dikalsium_fosfat    |            17 |         2 |         76 |       15.7 |        32.1 |
| Ca10P6CO27  | MaterialsProject | apatit_hidroksi     |            19 |         2 |         72 |       16.6 |        29.8 |
| CaPHO4      | MaterialsProject | dikalsium_fosfat    |            41 |         9 |         85 |        2.3 |         6.4 |
| Ca2P2H4O9   | MaterialsProject | dikalsium_fosfat    |            65 |        18 |        106 |        0.8 |         2.2 |
| Ca4P6O19    | MaterialsProject | fosfat_lain         |            73 |        17 |        121 |        1   |         2.5 |
| Ca(PO3)2    | MaterialsProject | monokalsium_fosfat  |            77 |        16 |        126 |        0.7 |         2.6 |
| Ca8P6H12O29 | MaterialsProject | oktakalsium_fosfat  |            78 |        18 |        142 |        1   |         2.2 |
| CaPH5O6     | MaterialsProject | dikalsium_fosfat    |            91 |        30 |        143 |        0.1 |         0.5 |
| CaP2H2O7    | MaterialsProject | monokalsium_fosfat  |           110 |        37 |        136 |        0.1 |         0.4 |
| CaP4O11     | MaterialsProject | fosfat_lain         |           114 |        36 |        149 |        0.1 |         0.4 |

## Gambar
- `reports/figures/fig_rank_mc.png`