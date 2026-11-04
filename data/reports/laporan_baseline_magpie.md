# Baseline Fitur Magpie (protokol identik modeling.py)
**Tanggal:** 2026-11-04 08:40:19

- Fitur: 40 (8 properti unsur x mean/avg_dev/range/max/min), elemen hadir saja
- Subset: Eform n=337 (MP+OQMD), densitas n=571
- Protokol: GroupKFold(10) atas formula tereduksi; SVR nested CV (grid {'C': [1, 10, 50], 'gamma': [0.01, 0.05, 0.1], 'epsilon': [0.05, 0.1]})

## Eform — SVR nested (fitur Magpie)
- R2 = -0.055, RMSE = 0.454, MAE = 0.317
- RF untuned: R2 = -0.052, RMSE = 0.429, MAE = 0.330
## Densitas — SVR nested (fitur Magpie)
- R2 = 0.273, RMSE = 0.385, MAE = 0.250
- RF untuned: R2 = 0.309, RMSE = 0.373, MAE = 0.244

## Pembanding (model 4-DOF komposisi, hasil ronde 3)
- Eform SVR-nested: R2 = 0.113, RMSE = 0.439, MAE = 0.297
- Densitas RF: R2 = 0.018, RMSE = 0.441, MAE = 0.307

## Interpretasi
- Fitur Magpie adalah fungsi komposisi -> tetap valid untuk skenario discovery (tanpa kebocoran).
- Eform: Magpie TIDAK membantu (R2 ~ 0 vs 0.113) — statistik non-linear properti unsur tidak menambah
  informasi energi pembentukan; konfirmasi independen bahwa komposisi saja nyaris tak berdaya prediksi.
- Densitas: Magpie JAUH lebih baik (R2 0.27-0.31 vs 0.018) — statistik kontras properti unsur
  (max/min EN, radius ionik) menangkap informasi kemasan (packing) yang tidak ada di mean 4-DOF.
- Model utama manuskrip tetap 4-DOF (set minimal lengkap-informasi + interpretabel); hasil ini
  dilaporkan sebagai perbandingan baseline deskriptor atas permintaan reviewer.