# Laporan Validasi Independen: Prediksi ML vs Eksperimen

**Tanggal:** 2026-11-04 07:10:26
**Konteks koreksi:** validasi sebelumnya membandingkan nilai database vs literatur (QC sumber data);
laporan ini menguji PREDIKSI MODEL (SVR Eform C=50 gamma=0.05; RF densitas) pada data eksperimen
murni yang TIDAK dipakai pelatihan (entalpi pembentukan standar Wagman/NBS; densitas literatur).

## Hasil

| fase                           |   Eform_exp_eV_atom |   Eform_pred_eV_atom |   selisih_eV_atom |   densitas_exp |   densitas_pred |   selisih_densitas |
|:-------------------------------|--------------------:|---------------------:|------------------:|---------------:|----------------:|-------------------:|
| Hidroksiapatit Ca10(PO4)6(OH)2 |              -3.159 |               -2.89  |             0.268 |           3.16 |           3.056 |             -0.104 |
| b-TCP Ca3(PO4)2                |              -3.285 |               -2.936 |             0.349 |           3.07 |           3.365 |              0.295 |
| a-TCP Ca3(PO4)2                |              -3.289 |               -2.936 |             0.352 |           2.86 |           3.365 |              0.505 |
| TTCP Ca4(PO4)2O                |              -3.297 |               -3.132 |             0.164 |           3.05 |           3.06  |              0.01  |
| DCPA (monetit) CaHPO4          |              -2.686 |               -2.608 |             0.078 |           2.92 |           2.836 |             -0.084 |
| DCPD (brushit) CaHPO4.2H2O     |              -1.717 |               -2.025 |            -0.307 |           2.31 |           2.247 |             -0.063 |

- **MAE Eform = 0.254 eV/atom** (dari nilai eksperimen) — bandingkan dengan RMSE CV 0.395.
- **MAE densitas = 0.177 g/cm3** — bandingkan dengan RMSE CV 0.096.

## Interpretasi
- Prediksi Eform kini tervalidasi terhadap termokimia EKSPERIMEN (bukan database lain):
  KUAT (MAE <= 0.3 eV/atom).
- Densitas eksperimen 6 fase Ca-P diprediksi dengan MAE 0.177 g/cm3.

## Sumber
- Entalpi pembentukan: Wagman et al., NBS Tables of Chemical Thermodynamic Properties (1982);
  konsisten dengan kompilasi Dorozhkin (2012).
- Parameter kisi & densitas: kartu ICDD/PDF standar (HAp 09-432; b-TCP 09-169; a-TCP 09-348;
  TTCP 25-1137; monetit 09-0080; brushit 09-0077).
