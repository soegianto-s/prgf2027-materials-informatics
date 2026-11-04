# Laporan Pemodelan ML v2 (anti-leakage, metrik jujur)
**Tanggal:** 2026-11-04 07:09:02
**Grouping:** formula tereduksi (gcd) | **CV:** GroupKFold(10) | **SVR:** nested CV (inner 5-fold pilih hiperparameter)

## Eform (eV/atom) — fitur KOMPOSISI MURNI, semua sumber n=571
| model      |    R2 |   RMSE |   MAE |
|:-----------|------:|-------:|------:|
| RF         | 0.2   |  0.533 | 0.344 |
| GBR        | 0.28  |  0.507 | 0.329 |
| XGB        | 0.424 |  0.55  | 0.353 |
| SVR-nested | 0.483 |  0.465 | 0.265 |
- Hiperparameter terpilih (outer): [{'C': 50, 'epsilon': 0.1, 'gamma': 0.05}, {'C': 10, 'epsilon': 0.1, 'gamma': 0.01}, {'C': 1, 'epsilon': 0.05, 'gamma': 0.01}] ...
## Eform — skenario SCREENING (fitur termasuk volume+densitas, MP+AFLOW n=291)
- SVR nested: R2 = 0.489, RMSE = 0.448, MAE = 0.242 (catatan: TIDAK berlaku untuk material baru — densitas/volume tak diketahui)
## Eform DALAM KELUARGA FOSFAT (ada O, n=215) — SVR C=50
- R2 = 0.580, RMSE = 0.284, MAE = 0.176
- Catatan: rentang fosfida vs fosfat bimodal TIDAK lagi mengatrol R2 di sini.
## Densitas — [berat molekul + volume] = IDENTITAS KRISTALOGRAFI (bukan klaim prediktif)
- R2 = -1.052 (konsistensi data; rho = MZ/(NA V))
## Densitas — fitur KOMPOSISI MURNI (prediksi nyata, n=571)
- R2 = 0.174, RMSE = 0.400, MAE = 0.264
## Uji eksternal — OQMD PENUH (komposisi bisa tumpang tindih dgn latih) (n=280)
- R2 = 0.883, RMSE = 0.385, MAE = 0.254
- OQMD BEBAS TUMPANG TINDIH (strict): kosong
## Classifier suitability — CEK KONSISTENSI LABEL (bukan klaim prediktif)
- Label adalah fungsi semi-deterministik dari fitur (pita Ca/P & densitas ada di fitur; hanya Eform yang perlu dipelajari) -> akurasi tinggi DIHARAPKAN dan tidak informatif.
- Keputusan: skor ini TIDAK dipakai sebagai kriteria MCDM (double counting dengan C1-C3).