# Laporan EDA Lanjutan
**Tanggal:** 2026-11-04 07:25:06

## Perbandingan Metode Klaster (n=2829)
- HDBSCAN (min_cluster=30): 17 klaster + 1246 titik noise
- Hierarkis ward k=5: ARI vs K-Means = 0.884
- Silhouette hierarkis: 0.492 (K-Means: 0.552)
- Kesimpulan stabilitas: struktur klaster K-Means vs hierarkis KONSISTEN
## Validasi Top Kandidat vs Literatur Eksperimen

| formula     | kelompok            |   rho_kita |   rho_literatur |   selisih_% |   Eform_kita |   Eform_lit_eV_atom |
|:------------|:--------------------|-----------:|----------------:|------------:|-------------:|--------------------:|
| Ca5P3O12F   | apatit_hidroksi     |      3.104 |            3.19 |        -2.7 |       -3.42  |               -3.39 |
| Ca10P6CO27  | apatit_hidroksi     |      3.053 |            3    |         1.8 |       -3.253 |              nan    |
| Ca3(PO4)2   | trikalsium_fosfat   |      2.979 |          nan    |       nan   |       -3.322 |              nan    |
| Ca5P3HO13   | apatit_hidroksi     |      3.178 |            3.16 |         0.6 |       -3.223 |               -3.15 |
| Ca10F2O24P6 | apatit_hidroksi     |      3.096 |            3.19 |        -2.9 |       -3.032 |               -3.39 |
| Ca4P2O9     | tetrakalsium_fosfat |      3.08  |            3.05 |         1   |       -3.326 |              nan    |
| Ca2P2O7     | dikalsium_fosfat    |      2.95  |          nan    |       nan   |       -3.213 |              nan    |
| Ca10H2O26P6 | apatit_hidroksi     |      3.051 |            3.16 |        -3.4 |       -2.84  |               -3.15 |

*Literatur: nilai densitas standar (kristalografi); Eform literatur dari entalpi pembentukan standar (per atom).*