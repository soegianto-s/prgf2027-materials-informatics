# Laporan Prapemrosesan & Ekstraksi Deskriptor
**Tanggal:** 2026-11-04 04:52:00
**Tahapan:** Bagian 3–4 panduan utama

## Keputusan Prapemrosesan
- Densitas tak fisik dihapus (di-null-kan): 0 baris
- Volume sel tak fisik dihapus (di-null-kan): 4 baris

## Pencilan (IQR*3 / z>4) — prinsip: jangan hapus otomatis
- densitas_final_gcm3: 1 pencilan (batas [-1.73, 6.20]) -> DIPERTAHANKAN, ditandai di kolom pencilan_densitas_final_gcm3
- Eform_eV_atom: 1 pencilan (batas [-8.50, 5.56]) -> DIPERTAHANKAN, ditandai di kolom pencilan_Eform_eV_atom
- volume_A3: 86 pencilan (batas [-4155.12, 6767.21]) -> DIPERTAHANKAN, ditandai di kolom pencilan_volume_A3

## Missing Values — keputusan eksplisit
- Energi/bandgap/modulus hanya ada di sumber komputasional (MP, AFLOW, OQMD) -> subset pemodelan = MP+AFLOW(+OQMD), TERCATAT sebagai keputusan desain.
- Densitas COD diisi dari densitas teoritis (volume sel + berat molekul).
- Deskriptor dengan missing > 30% pada subset pemodelan akan disisihkan pada seleksi fitur.

## Statistik Deskriptor Utama
|                     |   count |     mean |      std |    min |     25% |     50% |      75% |       max |
|:--------------------|--------:|---------:|---------:|-------:|--------:|--------:|---------:|----------:|
| densitas_final_gcm3 |    2558 |    2.089 |    0.86  |  0.183 |   1.67  |   2.207 |    2.803 |     7.436 |
| Eform_eV_atom       |     291 |   -1.274 |    1.234 | -3.421 |  -2.477 |  -0.798 |   -0.469 |     7.391 |
| bandgap_eV          |     123 |    3.829 |    2.293 |  0     |   1.17  |   5.33  |    5.518 |     6.408 |
| young_E_GPa         |       4 |   86.761 |    4.706 | 82.686 |  82.686 |  86.761 |   90.836 |    90.836 |
| volume_A3           |    2589 | 1680.86  | 2112.22  |  8.299 | 525.878 | 729.8   | 2086.21  | 19209.5   |

## Distribusi Kelompok Material
| kelompok            |   count |
|:--------------------|--------:|
| fosfat_lain         |    1199 |
| monokalsium_fosfat  |     506 |
| dikalsium_fosfat    |     391 |
| apatit_hidroksi     |     301 |
| oktakalsium_fosfat  |      86 |
| trikalsium_fosfat   |      60 |
| tetrakalsium_fosfat |      54 |
| apatit_fluor        |       8 |
