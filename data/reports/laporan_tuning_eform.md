# Laporan Tuning Eform (gap #2: target R2 >= 0.85)
**Tanggal:** 2026-11-04 05:26:26 | n = 291 | GroupKFold(10) berbasis komposisi

## Terbaik
- SVR {'C': 50, 'epsilon': 0.05, 'gamma': 0.05}: **R2 = 0.869** (RMSE 0.395, MAE 0.221)
- Target R2 >= 0.85: **TERCAPAI**

## 5 Teratas
| model   | param                                       |     R2 |   RMSE |    MAE |
|:--------|:--------------------------------------------|-------:|-------:|-------:|
| SVR     | {'C': 1, 'epsilon': 0.05, 'gamma': 'scale'} | 0.8058 | 0.4801 | 0.2671 |
| SVR     | {'C': 1, 'epsilon': 0.05, 'gamma': 0.01}    | 0.8064 | 0.4874 | 0.2809 |
| SVR     | {'C': 1, 'epsilon': 0.05, 'gamma': 0.05}    | 0.8176 | 0.4691 | 0.262  |
| SVR     | {'C': 1, 'epsilon': 0.05, 'gamma': 0.1}     | 0.8058 | 0.4801 | 0.2671 |
| SVR     | {'C': 1, 'epsilon': 0.1, 'gamma': 'scale'}  | 0.8062 | 0.4782 | 0.2624 |
