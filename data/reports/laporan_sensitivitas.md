# Laporan Sensitivitas MCDM — Pembobotan Entropi
**Tanggal:** 2026-11-04 08:07:28

## Bobot Entropi (data-driven, 3 kriteria lengkap tanpa imputasi)
{'C_stabilitas': 0.107, 'C_densitas': 0.115, 'C_cap': 0.778}
- Entropi per kriteria: {'C_stabilitas': 0.995, 'C_densitas': 0.995, 'C_cap': 0.963}
- Kolam kandidat sama dengan mcdm.py (filter muatan + fosfat): 165 entri.

## Konsistensi vs pembobotan manual (peringkat rerata 3 skenario)
- Korelasi Spearman peringkat: **0.926** (p = 6.53e-71)
- Interpretasi: PERINGKAT KONSISTEN terhadap pembobotan manual
- Catatan jujur: ini uji konsistensi INTERNAL (dua cara pembobotan pada kriteria yang
  sama), bukan validasi independen. Ketidakpastian bobot + prediksi dipropagasi di
  laporan_montecarlo.md.

## Top 10 versi entropi
| formula    | sumber           | kelompok        |
|:-----------|:-----------------|:----------------|
| Ca5P3O12F  | MaterialsProject | apatit_hidroksi |
| Ca10P6O25  | MaterialsProject | apatit_hidroksi |
| Ca10P6O25  | MaterialsProject | apatit_hidroksi |
| Ca5P3O12F  | MaterialsProject | apatit_hidroksi |
| Ca10P6CO27 | MaterialsProject | apatit_hidroksi |
| Ca5P3HO13  | MaterialsProject | apatit_hidroksi |
| Ca5P3HO13  | MaterialsProject | apatit_hidroksi |
| Ca10O25P6  | OQMD             | apatit_hidroksi |
| Ca10O25P6  | OQMD             | apatit_hidroksi |
| Ca10O25P6  | OQMD             | apatit_hidroksi |
