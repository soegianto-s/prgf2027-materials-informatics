# Laporan Model Structure-Informed (ronde 7/Q1)
**Tanggal:** 2026-11-04 13:50:55

- Label: HANYA DFT basis data (MP+AFLOW). MACE/COD tidak dipakai sebagai label latih.
- Fitur struktural membutuhkan struktur dikenal -> varian SCREENING, bukan discovery.
- SOAP: PCA 30 komponen di-dalam-fold (tidak bocor).

## Eform — MP+AFLOW (n=291), semua fitur dihitung di dalam CV
| fitur                                   | target   |     R2 |   RMSE |   MAE |
|:----------------------------------------|:---------|-------:|-------:|------:|
| F0 komposisi (4-DOF)                    | Eform    |  0.493 |  0.483 | 0.265 |
| F1 + volume + densitas (screening lama) | Eform    |  0.401 |  0.502 | 0.304 |
| F2 + Q^n + CN Ca (n=242)                | Eform    |  0.35  |  0.5   | 0.316 |
| F3 + SOAP-PCA(30) (n=242)               | Eform    | -0.658 |  0.799 | 0.588 |
| F0 komposisi (n=291)                    | Densitas |  0.226 |  0.384 | 0.252 |
| F2 + Q^n + CN Ca (n=242)                | Densitas |  0.293 |  0.305 | 0.222 |

- Gain R2 Eform F2 vs F0 = -0.143 (dibandingkan F1 vs F0 = -0.092)