# Laporan EDA Lanjutan
**Tanggal:** 2026-11-04 10:24:36

## Perbandingan Metode Klaster (n=2829)
- HDBSCAN (min_cluster=30): 17 klaster + 1246 titik noise
- Hierarkis ward k=5: ARI vs K-Means = 0.884
- Silhouette hierarkis: 0.492 (K-Means: 0.552)
- Kesimpulan stabilitas: struktur klaster K-Means vs hierarkis KONSISTEN
## Validasi Top Kandidat vs Literatur Eksperimen

| formula     | kelompok            |   rho_kita |   rho_literatur |   selisih_% |   Eform_kita |   Eform_lit_eV_atom |
|:------------|:--------------------|-----------:|----------------:|------------:|-------------:|--------------------:|
| Ca5P3O12F   | apatit_hidroksi     |      3.104 |            3.19 |        -2.7 |       -3.42  |               -3.39 |
| Ca10P6O25   | apatit_hidroksi     |      2.978 |          nan    |       nan   |       -3.319 |              nan    |
| Ca10P6CO27  | apatit_hidroksi     |      3.053 |            3    |         1.8 |       -3.253 |              nan    |
| Ca5P3HO13   | apatit_hidroksi     |      3.178 |            3.16 |         0.6 |       -3.223 |               -3.15 |
| Ca3(PO4)2   | trikalsium_fosfat   |      2.781 |          nan    |       nan   |       -3.326 |              nan    |
| Ca4P2O9     | tetrakalsium_fosfat |      3.08  |            3.05 |         1   |       -3.326 |              nan    |
| Ca2P2O7     | dikalsium_fosfat    |      2.95  |          nan    |       nan   |       -3.213 |              nan    |
| Ca8P6H12O29 | oktakalsium_fosfat  |      2.591 |          nan    |       nan   |       -2.621 |              nan    |

*Literatur: nilai densitas standar (kristalografi); Eform literatur dari entalpi pembentukan standar (per atom).*