# Laporan Pemodelan ML v2 (anti-leakage, metrik jujur)
**Tanggal:** 2026-11-04 07:15:47
**Grouping:** formula tereduksi (gcd) | **CV:** GroupKFold(10) | **SVR:** nested CV (inner 5-fold pilih hiperparameter)

## Eform (eV/atom) — fitur KOMPOSISI MURNI, semua sumber n=571
| model      |    R2 |   RMSE |   MAE |
|:-----------|------:|-------:|------:|
| RF         | 0.144 |  0.557 | 0.361 |
| GBR        | 0.235 |  0.529 | 0.347 |
| XGB        | 0.394 |  0.55  | 0.367 |
| SVR-nested | 0.47  |  0.465 | 0.267 |
- Hiperparameter terpilih (outer): [{'C': 50, 'epsilon': 0.05, 'gamma': 0.01}, {'C': 10, 'epsilon': 0.1, 'gamma': 0.01}, {'C': 1, 'epsilon': 0.05, 'gamma': 0.01}] ...
## Eform — skenario SCREENING (fitur termasuk volume+densitas, MP+AFLOW n=291)
- SVR nested: R2 = 0.544, RMSE = 0.446, MAE = 0.241 (catatan: TIDAK berlaku untuk material baru — densitas/volume tak diketahui)
## Eform DALAM KELUARGA FOSFAT (ada O, n=215) — SVR C=50
- R2 = -0.072, RMSE = 0.306, MAE = 0.206
- Catatan: rentang fosfida vs fosfat bimodal TIDAK lagi mengatrol R2 di sini.
## Densitas — [berat molekul + volume] = IDENTITAS KRISTALOGRAFI (bukan klaim prediktif)
- R2 = -0.918 (konsistensi data; rho = MZ/(NA V))
## Densitas — fitur KOMPOSISI MURNI (prediksi nyata, n=571)
- R2 = 0.227, RMSE = 0.390, MAE = 0.253
## Uji eksternal — OQMD PENUH (komposisi bisa tumpang tindih dgn latih) (n=280)
- R2 = 0.887, RMSE = 0.378, MAE = 0.234
## Uji eksternal — OQMD BEBAS TUMPANG TINDIH (strict) (n=1)
- R2 = nan, RMSE = 0.430, MAE = 0.430
## Classifier suitability — CEK KONSISTENSI LABEL (bukan klaim prediktif)
- Label adalah fungsi semi-deterministik dari fitur (pita Ca/P & densitas ada di fitur; hanya Eform yang perlu dipelajari) -> akurasi tinggi DIHARAPKAN dan tidak informatif.
- Keputusan: skor ini TIDAK dipakai sebagai kriteria MCDM (double counting dengan C1-C3).