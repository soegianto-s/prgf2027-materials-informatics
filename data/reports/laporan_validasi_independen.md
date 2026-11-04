# Laporan Validasi Independen: Prediksi ML vs Eksperimen

**Tanggal:** 2026-11-04 07:27:31
**Konteks koreksi:** validasi sebelumnya membandingkan nilai database vs literatur (QC sumber data);
laporan ini menguji PREDIKSI MODEL (SVR Eform C=50 gamma=0.05; RF densitas) pada data eksperimen
murni yang TIDAK dipakai pelatihan (entalpi pembentukan standar Wagman/NBS; densitas literatur).

## Hasil

| fase                           |   Eform_exp_eV_atom |   Eform_pred_eV_atom |   selisih_eV_atom |   densitas_exp |   densitas_pred |   selisih_densitas |
|:-------------------------------|--------------------:|---------------------:|------------------:|---------------:|----------------:|-------------------:|
| Hidroksiapatit Ca10(PO4)6(OH)2 |              -3.159 |               -3.176 |            -0.017 |           3.16 |           3.173 |              0.013 |
| b-TCP Ca3(PO4)2                |              -3.285 |               -3.214 |             0.071 |           3.07 |           3.219 |              0.149 |
| a-TCP Ca3(PO4)2                |              -3.289 |               -3.214 |             0.074 |           2.86 |           3.219 |              0.359 |
| TTCP Ca4(PO4)2O                |              -3.297 |               -3.248 |             0.049 |           3.05 |           3.11  |              0.06  |
| DCPA (monetit) CaHPO4          |              -2.686 |               -2.635 |             0.051 |           2.92 |           2.919 |             -0.001 |
| DCPD (brushit) CaHPO4.2H2O     |              -1.717 |               -2.02  |            -0.302 |           2.31 |           2.412 |              0.102 |

- **MAE Eform = 0.094 eV/atom** (dari nilai eksperimen) — bandingkan dengan RMSE CV 0.395.
- **MAE densitas = 0.114 g/cm3** — bandingkan dengan RMSE CV 0.096.

## Interpretasi
- Prediksi Eform kini tervalidasi terhadap termokimia EKSPERIMEN (bukan database lain):
  KUAT (MAE <= 0.3 eV/atom).
- Densitas eksperimen 6 fase Ca-P diprediksi dengan MAE 0.114 g/cm3.

## Sumber
- Entalpi pembentukan: Wagman et al., NBS Tables of Chemical Thermodynamic Properties (1982);
  konsisten dengan kompilasi Dorozhkin (2012).
- Parameter kisi & densitas: kartu ICDD/PDF standar (HAp 09-432; b-TCP 09-169; a-TCP 09-348;
  TTCP 25-1137; monetit 09-0080; brushit 09-0077).
