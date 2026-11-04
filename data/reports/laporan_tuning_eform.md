> **SUPERSEDED (2026-11-04):** estimasi ini memakai CV datar non-nested & fitur struktur. Angka resmi: nested CV di `laporan_pemodelan.md` (R² 0,48 discovery / 0,58 dalam-fosfat).

# Laporan Tuning Eform (gap #2: target R2 >= 0.85)
**Tanggal:** 2026-11-04 05:54:37 | n = 291 | GroupKFold(10) berbasis komposisi

## Terbaik
- SVR {'C': 50, 'epsilon': 0.05, 'gamma': 0.05}: **R2 = 0.869** (RMSE 0.395, MAE 0.221)
- Target R2 >= 0.85: **TERCAPAI**

## 5 Teratas
| model   | param                                      |     R2 |   RMSE |    MAE |
|:--------|:-------------------------------------------|-------:|-------:|-------:|
| SVR     | {'C': 50, 'epsilon': 0.05, 'gamma': 0.05}  | 0.8687 | 0.3946 | 0.2205 |
| SVR     | {'C': 10, 'epsilon': 0.1, 'gamma': 0.05}   | 0.8635 | 0.3996 | 0.2182 |
| SVR     | {'C': 10, 'epsilon': 0.05, 'gamma': 0.05}  | 0.8633 | 0.3999 | 0.2231 |
| SVR     | {'C': 50, 'epsilon': 0.1, 'gamma': 0.05}   | 0.8618 | 0.4028 | 0.2216 |
| SVR     | {'C': 100, 'epsilon': 0.05, 'gamma': 0.05} | 0.8571 | 0.4117 | 0.2342 |
