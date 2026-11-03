# Laporan EDA Lanjutan
**Tanggal:** 2026-11-04 05:10:02

## Perbandingan Metode Klaster (n=2549)
- HDBSCAN (min_cluster=30): 17 klaster + 1266 titik noise
- Hierarkis ward k=5: ARI vs K-Means = 0.907
- Silhouette hierarkis: 0.554 (K-Means: 0.552)
- Kesimpulan stabilitas: struktur klaster K-Means vs hierarkis KONSISTEN
## Validasi Top Kandidat vs Literatur Eksperimen

| formula     | kelompok            |   rho_kita |   rho_literatur |   selisih_% |   Eform_kita |   Eform_lit_eV_atom |
|:------------|:--------------------|-----------:|----------------:|------------:|-------------:|--------------------:|
| Ca10P6CO27  | apatit_hidroksi     |      3.053 |            3    |         1.8 |       -3.253 |              nan    |
| Ca5P3O12F   | apatit_hidroksi     |      3.104 |            3.19 |        -2.7 |       -3.42  |               -3.39 |
| Ca8P6H12O29 | oktakalsium_fosfat  |      2.591 |          nan    |       nan   |       -2.621 |              nan    |
| Ca10F2O24P6 | apatit_hidroksi     |      3.096 |            3.19 |        -2.9 |       -3.032 |               -3.39 |
| Ca10P6O25   | apatit_hidroksi     |      2.978 |          nan    |       nan   |       -3.319 |              nan    |
| Ca16O36P8   | tetrakalsium_fosfat |      2.976 |            3.05 |        -2.4 |       -2.937 |              nan    |
| Ca4P2O9     | tetrakalsium_fosfat |      3.08  |            3.05 |         1   |       -3.326 |              nan    |
| Ca5P3HO13   | apatit_hidroksi     |      3.178 |            3.16 |         0.6 |       -3.223 |               -3.15 |

*Literatur: nilai densitas standar (kristalografi); Eform literatur dari entalpi pembentukan standar (per atom).*