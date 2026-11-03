# Laporan Prapemrosesan & Ekstraksi Deskriptor
**Tanggal:** 2026-11-04 05:49:26
**Tahapan:** Bagian 3–4 panduan utama

## Keputusan Prapemrosesan
- Densitas tak fisik dihapus (di-null-kan): 0 baris
- Volume sel tak fisik dihapus (di-null-kan): 4 baris

## Pencilan (IQR*3 / z>4) — prinsip: jangan hapus otomatis
- densitas_final_gcm3: 1 pencilan (batas [-1.59, 6.14]) -> DIPERTAHANKAN, ditandai di kolom pencilan_densitas_final_gcm3
- Eform_eV_atom: 1 pencilan (batas [-8.44, 5.33]) -> DIPERTAHANKAN, ditandai di kolom pencilan_Eform_eV_atom
- volume_A3: 109 pencilan (batas [-3631.73, 5976.42]) -> DIPERTAHANKAN, ditandai di kolom pencilan_volume_A3

## Missing Values — keputusan eksplisit
- Energi/bandgap/modulus hanya ada di sumber komputasional (MP, AFLOW, OQMD) -> subset pemodelan = MP+AFLOW(+OQMD), TERCATAT sebagai keputusan desain.
- Densitas COD diisi dari densitas teoritis (volume sel + berat molekul).
- Deskriptor dengan missing > 30% pada subset pemodelan akan disisihkan pada seleksi fitur.

## Statistik Deskriptor Utama
|                     |   count |     mean |      std |    min |     25% |     50% |      75% |       max |
|:--------------------|--------:|---------:|---------:|-------:|--------:|--------:|---------:|----------:|
| densitas_final_gcm3 |    2838 |    2.142 |    0.848 |  0.183 |   1.722 |   2.283 |    2.828 |     7.436 |
| Eform_eV_atom       |     571 |   -1.348 |    1.184 | -3.421 |  -2.538 |  -0.888 |   -0.57  |     7.391 |
| bandgap_eV          |     123 |    3.829 |    2.293 |  0     |   1.17  |   5.33  |    5.518 |     6.408 |
| young_E_GPa         |       4 |   86.761 |    4.706 | 82.686 |  82.686 |  86.761 |   90.836 |    90.836 |
| volume_A3           |    2869 | 1545.71  | 2051.81  |  8.299 | 486.047 | 613.569 | 1858.64  | 19209.5   |

## Distribusi Kelompok Material
| kelompok            |   count |
|:--------------------|--------:|
| fosfat_lain         |    1261 |
| monokalsium_fosfat  |     547 |
| dikalsium_fosfat    |     488 |
| apatit_hidroksi     |     322 |
| tetrakalsium_fosfat |      92 |
| oktakalsium_fosfat  |      86 |
| trikalsium_fosfat   |      78 |
| apatit_fluor        |      11 |
