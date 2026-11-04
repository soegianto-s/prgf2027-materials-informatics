# Laporan Interpretasi Model (XAI)
**Tanggal:** 2026-11-04 07:09:52
**Tahapan:** Bagian 9 panduan utama

## SHAP: Eform_eV_atom (RandomForest, n=291)
- Dua fitur paling berpengaruh (|SHAP| rata-rata): frac_O, berat_molekul
- Permutation importance (cek silang): frac_O, frac_Ca, berat_molekul
- Korelasi SHAP ca_p_ratio vs nilai ca_p_ratio: -0.26 (nilai Ca/P lebih tinggi -> prediksi lebih rendah)
## SHAP: densitas_final_gcm3 (RandomForest, n=571)
- Dua fitur paling berpengaruh (|SHAP| rata-rata): EN_avg, frac_O
- Permutation importance (cek silang): EN_avg, frac_O, frac_Ca
- Korelasi SHAP ca_p_ratio vs nilai ca_p_ratio: 0.47 (nilai Ca/P lebih tinggi -> prediksi lebih tinggi)
## Gambar SHAP: reports/figures/fig_shap_*.png