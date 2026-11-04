# Laporan Pemodelan ML v2 (anti-leakage, metrik jujur)
**Tanggal:** 2026-11-04 07:26:26
**Grouping:** formula tereduksi (gcd) | **CV:** GroupKFold(10) | **SVR:** nested CV (inner 5-fold pilih hiperparameter)

## Eform (eV/atom) — fitur KOMPOSISI MURNI, MP+OQMD (skala konsisten) n=337
- AFLOW DIKECUALIKAN dari pelatihan Eform (offset skala hingga 0.8 eV/atom, terdokumentasi).
- VIF fitur komposisi (setelah frac_Ca dibuang): {'ca_p_ratio': 1.7, 'frac_P': 2.0, 'frac_H': 1.6, 'frac_F': 1.0}
| model      |     R2 |   RMSE |   MAE |
|:-----------|-------:|-------:|------:|
| RF         | -0.7   |  0.694 | 0.501 |
| GBR        | -0.549 |  0.664 | 0.476 |
| XGB        | -1.071 |  0.734 | 0.533 |
| SVR-nested |  0.113 |  0.439 | 0.297 |
- Hiperparameter terpilih (outer): [{'C': 50, 'epsilon': 0.05, 'gamma': 0.1}, {'C': 50, 'epsilon': 0.05, 'gamma': 0.01}, {'C': 50, 'epsilon': 0.05, 'gamma': 0.01}] ...
## Eform — skenario SCREENING (fitur termasuk volume+densitas, MP+AFLOW n=291)
- SVR nested: R2 = 0.401, RMSE = 0.502, MAE = 0.304 (catatan: TIDAK berlaku untuk material baru — densitas/volume tak diketahui)
## Eform DALAM KELUARGA FOSFAT (ada O, n=157) — SVR C=50
- R2 = -0.516, RMSE = 0.191, MAE = 0.139
- Catatan: rentang fosfida vs fosfat bimodal TIDAK lagi mengatrol R2 di sini.
## Densitas — [berat molekul + volume] = IDENTITAS KRISTALOGRAFI (bukan klaim prediktif)
- R2 = -0.918 (konsistensi data; rho = MZ/(NA V))
## Densitas — fitur KOMPOSISI MURNI (prediksi nyata, n=571)
- R2 = 0.018, RMSE = 0.441, MAE = 0.307
## Uji antar basis data — latih MP SAJA (n=57) -> uji OQMD (n=280)
- R2 = 0.833, RMSE = 0.460, MAE = 0.268
- Catatan: uji ini pada komposisi SAMA (transfer sesama-komposisi, bukan ekstrapolasi).
## Classifier suitability — CEK KONSISTENSI LABEL (bukan klaim prediktif)
- Label adalah fungsi semi-deterministik dari fitur (pita Ca/P & densitas ada di fitur; hanya Eform yang perlu dipelajari) -> akurasi tinggi DIHARAPKAN dan tidak informatif.
- Keputusan: skor ini TIDAK dipakai sebagai kriteria MCDM (double counting dengan C1-C3).