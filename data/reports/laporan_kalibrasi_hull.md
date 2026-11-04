# Kalibrasi MACE -> MP GGA & E_hull COD in-system
**Tanggal:** 2026-11-04 13:19:13

- Offset median = 0.0861 eV/atom (CI95 [0.4116, 0.585]); MAE offset = 0.6723 eV/atom
- Validasi eksternal 6 fase Wagman/NBS: MAE Eform terkalibrasi = 0.3103 eV/atom
- Hull MP: cross-check E_hull vs API MAE = 0.0026310019440000617 eV/atom
- COD in-system: 180 -> E_hull terdefinisi 180; stabil (E_hull<=1e-6): 12

## 10 E_hull terendah (fase stabil kandidat)
|      cod_id | formula_meta           |   Eform_MACE_raw |   Eform_cal |     E_hull |
|------------:|:-----------------------|-----------------:|------------:|-----------:|
| 4.3394e+06  | - C40 H52 Ca O4 P2 -   |        -1.06699  |   -0.980886 | -0.616121  |
| 4.32976e+06 | - C40 H52 Ca O6 P2 -   |        -1.10544  |   -1.01934  | -0.590092  |
| 7.13447e+06 | - C44 H78 Ca O4 P4 -   |        -0.920193 |   -0.834093 | -0.495286  |
| 4.31693e+06 | - Bi Ca3 O12 P3 -      |        -2.27101  |   -2.18491  | -0.220162  |
| 7.2393e+06  | - C16 H20 Ca O12 P2 -  |        -1.32328  |   -1.23718  | -0.203104  |
| 7.01848e+06 | - C22 H24 Ca O10.5 P - |        -1.09661  |   -1.01051  | -0.167424  |
| 4.34653e+06 | - C12 H18 Ca2 O11 P3 - |        -1.42329  |   -1.33719  | -0.133407  |
| 7.0283e+06  | - C16 H20 Ca O12 P2 -  |        -1.19901  |   -1.11291  | -0.105709  |
| 4.34653e+06 | - C8 H16 Ca O9 P2 -    |        -1.3338   |   -1.2477   | -0.0848094 |
| 7.2393e+06  | - C16 H22 Ca O13 P2 -  |        -1.21257  |   -1.12647  | -0.0788792 |