# Laporan Interpretasi Model (XAI)
**Tanggal:** 2026-11-04 10:24:39
**Tahapan:** Bagian 9 panduan utama

## SHAP: Eform_eV_atom (RandomForest, n=337)
- Dua fitur paling berpengaruh (|SHAP| rata-rata): frac_P, ca_p_ratio
- Permutation importance (cek silang): frac_P, ca_p_ratio, frac_H
- Korelasi SHAP ca_p_ratio vs nilai ca_p_ratio: 0.03 (nilai Ca/P lebih tinggi -> prediksi lebih tinggi)
## SHAP: densitas_final_gcm3 (RandomForest, n=571)
- Dua fitur paling berpengaruh (|SHAP| rata-rata): frac_P, ca_p_ratio
- Permutation importance (cek silang): frac_P, ca_p_ratio, frac_H
- Korelasi SHAP ca_p_ratio vs nilai ca_p_ratio: -0.43 (nilai Ca/P lebih tinggi -> prediksi lebih rendah)
## Gambar SHAP: reports/figures/fig_shap_*.png