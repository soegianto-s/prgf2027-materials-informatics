# Laporan Validasi Independen: Prediksi ML vs Eksperimen

**Tanggal:** 2026-11-04 06:57:30
**Konteks koreksi:** validasi sebelumnya membandingkan nilai database vs literatur (QC sumber data);
laporan ini menguji PREDIKSI MODEL (SVR Eform C=50 gamma=0.05; RF densitas) pada data eksperimen
murni yang TIDAK dipakai pelatihan (entalpi pembentukan standar Wagman/NBS; densitas literatur).

## Hasil

| fase                           |   Eform_exp_eV_atom |   Eform_pred_eV_atom |   selisih_eV_atom |   densitas_exp |   densitas_pred |   selisih_densitas |
|:-------------------------------|--------------------:|---------------------:|------------------:|---------------:|----------------:|-------------------:|
| Hidroksiapatit Ca10(PO4)6(OH)2 |              -3.159 |               -2.823 |             0.335 |           3.16 |           3.168 |              0.008 |
| b-TCP Ca3(PO4)2                |              -3.285 |               -2.519 |             0.767 |           3.07 |           3.061 |             -0.009 |
| a-TCP Ca3(PO4)2                |              -3.289 |               -2.876 |             0.413 |           2.86 |           2.856 |             -0.004 |
| TTCP Ca4(PO4)2O                |              -3.297 |               -3.344 |            -0.048 |           3.05 |           3.062 |              0.012 |
| DCPA (monetit) CaHPO4          |              -2.686 |               -2.749 |            -0.063 |           2.92 |           2.917 |             -0.003 |
| DCPD (brushit) CaHPO4.2H2O     |              -1.717 |               -2.211 |            -0.494 |           2.31 |           2.304 |             -0.006 |

- **MAE Eform = 0.353 eV/atom** (dari nilai eksperimen) — bandingkan dengan RMSE CV 0.395.
- **MAE densitas = 0.007 g/cm3** — bandingkan dengan RMSE CV 0.096.

## Interpretasi
- Prediksi Eform kini tervalidasi terhadap termokimia EKSPERIMEN (bukan database lain):
  sedang (MAE > 0.3 eV/atom) — catat keterbatasan.
- Densitas eksperimen 6 fase Ca-P diprediksi dengan MAE 0.007 g/cm3.

## Sumber
- Entalpi pembentukan: Wagman et al., NBS Tables of Chemical Thermodynamic Properties (1982);
  konsisten dengan kompilasi Dorozhkin (2012).
- Parameter kisi & densitas: kartu ICDD/PDF standar (HAp 09-432; b-TCP 09-169; a-TCP 09-348;
  TTCP 25-1137; monetit 09-0080; brushit 09-0077).
