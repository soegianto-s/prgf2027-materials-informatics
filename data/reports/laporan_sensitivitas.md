# Laporan Sensitivitas MCDM — Pembobotan Entropi
**Tanggal:** 2026-11-04 07:09:49

## Bobot Entropi (data-driven, 4 kriteria lengkap)
{'C_stabilitas': 0.508, 'C_densitas': 0.111, 'C_cap': 0.381}
- Catatan: C_modulus & C_bandgap diimputasi median sehingga DIKELUARKAN dari entropi
  (bobot manual 0.15/0.10 dipertahankan agar artefak imputasi tidak mendominasi).
- Entropi per kriteria: {'C_stabilitas': 0.998, 'C_densitas': 1.0, 'C_cap': 0.999}

## Konsistensi vs pembobotan manual (W1 berimbang)
- Korelasi Spearman peringkat: **0.990** (p = 0.00e+00)
- Interpretasi: PERINGKAT KONSISTEN terhadap pembobotan manual

## Top 10 versi entropi
| formula     | sumber           | kelompok        |
|:------------|:-----------------|:----------------|
| Ca5P3O12F   | MaterialsProject | apatit_hidroksi |
| Ca5P3O12F   | MaterialsProject | apatit_hidroksi |
| Ca10P6CO27  | MaterialsProject | apatit_hidroksi |
| Ca5P3HO13   | MaterialsProject | apatit_hidroksi |
| Ca5P3HO13   | MaterialsProject | apatit_hidroksi |
| Ca10F2O24P6 | AFLOW            | apatit_hidroksi |
| Ca10F2O24P6 | AFLOW            | apatit_hidroksi |
| Ca10F2O24P6 | AFLOW            | apatit_hidroksi |
| Ca10F2O24P6 | AFLOW            | apatit_hidroksi |
| Ca10F2O24P6 | AFLOW            | apatit_hidroksi |
