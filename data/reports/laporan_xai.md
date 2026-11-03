# Laporan Interpretasi Model (XAI)
**Tanggal:** 2026-11-04 05:54:00
**Tahapan:** Bagian 9 panduan utama

## SHAP: Eform_eV_atom (RandomForest, n=291)
- Dua fitur paling berpengaruh (|SHAP| rata-rata): frac_O, densitas_final_gcm3
- Permutation importance (cek silang): frac_O, densitas_final_gcm3, volume_A3
- Korelasi SHAP ca_p_ratio vs nilai ca_p_ratio: 0.08 (nilai Ca/P lebih tinggi -> prediksi lebih tinggi)
## SHAP: densitas_final_gcm3 (RandomForest, n=571)
- Dua fitur paling berpengaruh (|SHAP| rata-rata): EN_avg, volume_A3
- Permutation importance (cek silang): volume_A3, EN_avg, berat_molekul
- Korelasi SHAP ca_p_ratio vs nilai ca_p_ratio: 0.57 (nilai Ca/P lebih tinggi -> prediksi lebih tinggi)
## Gambar SHAP: reports/figures/fig_shap_*.png