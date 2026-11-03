# Laporan Pemodelan Machine Learning
**Tanggal:** 2026-11-04 05:52:46
**Tahapan:** Bagian 7 panduan utama | Subset pemodelan: MP+AFLOW (komputasional)

## Regresi: Eform_eV_atom (n=291, GroupKFold berbasis komposisi)
| target        | model            |     R2 |   R2_std |   RMSE |   MAE |
|:--------------|:-----------------|-------:|---------:|-------:|------:|
| Eform_eV_atom | RandomForest     |  0.809 |    0.156 |  0.473 | 0.263 |
| Eform_eV_atom | XGBoost          | -0.221 |    2.756 |  0.848 | 0.434 |
| Eform_eV_atom | GradientBoosting |  0.715 |    0.343 |  0.541 | 0.288 |
| Eform_eV_atom | SVR              |  0.843 |    0.178 |  0.435 | 0.236 |
## Regresi: densitas_final_gcm3 (n=571, GroupKFold berbasis komposisi)
| target              | model            |     R2 |   R2_std |   RMSE |   MAE |
|:--------------------|:-----------------|-------:|---------:|-------:|------:|
| densitas_final_gcm3 | RandomForest     |  0.909 |    0.18  |  0.096 | 0.027 |
| densitas_final_gcm3 | XGBoost          | -0.548 |    4.473 |  0.204 | 0.094 |
| densitas_final_gcm3 | GradientBoosting |  0.758 |    0.667 |  0.1   | 0.031 |
| densitas_final_gcm3 | SVR              |  0.868 |    0.134 |  0.162 | 0.077 |
## Regresi: bandgap_eV (n=123, GroupKFold berbasis komposisi)
| target     | model            |        R2 |   R2_std |   RMSE |   MAE |
|:-----------|:-----------------|----------:|---------:|-------:|------:|
| bandgap_eV | RandomForest     | -3091.89  | 9275.25  |  1.884 | 1.539 |
| bandgap_eV | XGBoost          |   -78.128 |  234.225 |  1.785 | 1.441 |
| bandgap_eV | GradientBoosting |    -4.983 |   14.883 |  1.786 | 1.433 |
| bandgap_eV | SVR              | -1217.02  | 3651.16  |  1.671 | 1.248 |
## Uji Eksternal: model Eform (MP+AFLOW) diprediksi pada OQMD (n=280)
- R2 = 0.951, RMSE = 0.248 eV/atom -> transfer lintas basis data KUAT
- Catatan: skala Eform AFLOW berbeda sistematis dari MP/OQMD (hingga 0.8 eV untuk fosfida); MP~OQMD (selisih < 0.02 eV pada komposisi tumpang tindih) -> OQMD valid sebagai uji eksternal.
## Seleksi Fitur (RF importance + RFE pada Eform)
|                     |     0 |
|:--------------------|------:|
| frac_O              | 0.713 |
| densitas_final_gcm3 | 0.171 |
| volume_A3           | 0.043 |
| frac_Ca             | 0.018 |
| ca_p_ratio          | 0.017 |
| EN_avg              | 0.014 |
| berat_molekul       | 0.012 |
| frac_P              | 0.011 |
| frac_H              | 0.001 |
| frac_F              | 0     |
- Fitur terpilih RFE (8): ['ca_p_ratio', 'EN_avg', 'berat_molekul', 'volume_A3', 'densitas_final_gcm3', 'frac_Ca', 'frac_P', 'frac_O']
## Klasifikasi Kelayakan Scaffold (n=571, kelas 1 = 79)
- Definisi layak: Eform <= -2.5 eV/atom & Ca/P 1.2-2.1 & densitas 0.5-4.5 g/cm3
- Akurasi: 0.941 +/- 0.114 | F1: 0.596 +/- 0.487
- Confusion matrix (prediksi vs aktual):
```
[[492   0]
 [ 20  59]]
```
- Classification report:
              precision    recall  f1-score   support

           0       0.96      1.00      0.98       492
           1       1.00      0.75      0.86        79

    accuracy                           0.96       571
   macro avg       0.98      0.87      0.92       571
weighted avg       0.97      0.96      0.96       571
