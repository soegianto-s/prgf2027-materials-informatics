# Laporan Sensitivitas MCDM — Pembobotan Entropi
**Tanggal:** 2026-11-04 05:53:58

## Bobot Entropi (data-driven, 4 kriteria lengkap)
{'C_stabilitas': 0.005, 'C_densitas': 0.003, 'C_cap': 0.004, 'C_layak': 0.989}
- Catatan: C_modulus & C_bandgap diimputasi median sehingga DIKELUARKAN dari entropi
  (bobot manual 0.15/0.10 dipertahankan agar artefak imputasi tidak mendominasi).
- Entropi per kriteria: {'C_stabilitas': 0.998, 'C_densitas': 0.999, 'C_cap': 0.999, 'C_layak': 0.688}

## Konsistensi vs pembobotan manual (W1 berimbang)
- Korelasi Spearman peringkat: **0.937** (p = 0.00e+00)
- Interpretasi: PERINGKAT KONSISTEN terhadap pembobotan manual

## Top 10 versi entropi
| formula     | sumber           | kelompok        |
|:------------|:-----------------|:----------------|
| Ca5P3O12F   | MaterialsProject | apatit_hidroksi |
| Ca10P6CO27  | MaterialsProject | apatit_hidroksi |
| Ca5P3O12F   | MaterialsProject | apatit_hidroksi |
| Ca5P3HO13   | MaterialsProject | apatit_hidroksi |
| Ca5P3HO13   | MaterialsProject | apatit_hidroksi |
| Ca10F2O24P6 | AFLOW            | apatit_hidroksi |
| Ca10F2O24P6 | AFLOW            | apatit_hidroksi |
| Ca10F2O24P6 | AFLOW            | apatit_hidroksi |
| Ca10F2O24P6 | AFLOW            | apatit_hidroksi |
| Ca10F2O24P6 | AFLOW            | apatit_hidroksi |
