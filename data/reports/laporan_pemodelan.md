# Laporan Pemodelan Machine Learning
**Tanggal:** 2026-11-04 04:54:40
**Tahapan:** Bagian 7 panduan utama | Subset pemodelan: MP+AFLOW (komputasional)

## Regresi: Eform_eV_atom (n=291, GroupKFold berbasis komposisi)
| target        | model            |     R2 |   R2_std |   RMSE |   MAE |
|:--------------|:-----------------|-------:|---------:|-------:|------:|
| Eform_eV_atom | RandomForest     |  0.809 |    0.156 |  0.473 | 0.263 |
| Eform_eV_atom | XGBoost          | -0.221 |    2.756 |  0.848 | 0.434 |
| Eform_eV_atom | GradientBoosting |  0.715 |    0.343 |  0.541 | 0.288 |
| Eform_eV_atom | SVR              |  0.843 |    0.178 |  0.435 | 0.236 |
## Regresi: densitas_final_gcm3 (n=291, GroupKFold berbasis komposisi)
| target              | model            |    R2 |   R2_std |   RMSE |   MAE |
|:--------------------|:-----------------|------:|---------:|-------:|------:|
| densitas_final_gcm3 | RandomForest     | 0.916 |    0.132 |  0.132 | 0.034 |
| densitas_final_gcm3 | XGBoost          | 0.667 |    0.807 |  0.196 | 0.072 |
| densitas_final_gcm3 | GradientBoosting | 0.915 |    0.153 |  0.119 | 0.033 |
| densitas_final_gcm3 | SVR              | 0.844 |    0.218 |  0.186 | 0.083 |
## Regresi: bandgap_eV (n=123, GroupKFold berbasis komposisi)
| target     | model            |        R2 |   R2_std |   RMSE |   MAE |
|:-----------|:-----------------|----------:|---------:|-------:|------:|
| bandgap_eV | RandomForest     | -3091.89  | 9275.25  |  1.884 | 1.539 |
| bandgap_eV | XGBoost          |   -78.128 |  234.225 |  1.785 | 1.441 |
| bandgap_eV | GradientBoosting |    -4.983 |   14.883 |  1.786 | 1.433 |
| bandgap_eV | SVR              | -1217.02  | 3651.16  |  1.671 | 1.248 |
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
## Klasifikasi Kelayakan Scaffold (n=291, kelas 1 = 44)
- Definisi layak: Eform <= -2.5 eV/atom & Ca/P 1.2-2.1 & densitas 0.5-4.5 g/cm3
- Akurasi: 0.975 +/- 0.043 | F1: 0.902 +/- 0.185
- Confusion matrix (prediksi vs aktual):
```
[[247   0]
 [  8  36]]
```
- Classification report:
              precision    recall  f1-score   support

           0       0.97      1.00      0.98       247
           1       1.00      0.82      0.90        44

    accuracy                           0.97       291
   macro avg       0.98      0.91      0.94       291
weighted avg       0.97      0.97      0.97       291
