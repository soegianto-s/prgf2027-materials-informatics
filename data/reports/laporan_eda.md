# Laporan Eksplorasi Ruang Desain Material
**Tanggal:** 2026-11-04 04:53:56 | **Tahapan:** Bagian 4-5 panduan utama

## Korelasi & Multikolinearitas
- EN_avg vs EN_diff: r = 0.889 -> redundan (pilih satu wakil)
- EN_avg vs VEC: r = 0.902 -> redundan (pilih satu wakil)
## VIF (subset pemodelan, n=291)
- Eform_eV_atom: 3.9
- densitas_final_gcm3: 1.6
- volume_A3: 1.7
- EN_avg: 24.0
- EN_diff: 13.5
- VEC: 11.1
- berat_molekul: 1.7
- ca_p_ratio: 2.6
## PCA: PC1 36.4% + PC2 24.6% = 61.1% varians
## Bias sumber: fraksi tetangga-terdekat (k=5) sesumber = 0.94 (mendekati 1 = klaster terbentuk oleh sumber, bukan sifat)
## Klaster K-Means (silhouette): k=3:0.519, k=4:0.537, k=5:0.552, k=6:0.315, k=7:0.342, k=8:0.349
- k terbaik = 5; stabilitas ARI antar-seed = 1.000
## Profil Klaster (rerata deskriptor, kelompok dominan)
|   klaster |   densitas_final_gcm3 |   volume_A3 |   EN_avg |   EN_diff |   VEC |   berat_molekul |   ca_p_ratio | kelompok           |
|----------:|----------------------:|------------:|---------:|----------:|------:|----------------:|-------------:|:-------------------|
|         0 |                  0.55 |     4456.46 |     2.37 |      2.44 |  1.96 |          381.45 |         0.55 | monokalsium_fosfat |
|         1 |                  2.4  |     1123.14 |     2.85 |      2.53 |  4.86 |          520.07 |         1.35 | fosfat_lain        |
|         2 |                  1.99 |      474.15 |     3.03 |      2.58 |  5.13 |          285.24 |       130.83 | fosfat_lain        |
|         3 |                  2.26 |      347.17 |     1.65 |      1.22 |  3.62 |          229.5  |         1.23 | fosfat_lain        |
|         4 |                  1.8  |     6384.05 |     2.97 |      2.48 |  4.95 |         2989    |         0.87 | fosfat_lain        |
## Densitas per Kelompok Material (g/cm3)
| kelompok            |   count |    mean |     std |
|:--------------------|--------:|--------:|--------:|
| apatit_hidroksi     |     299 |   3.075 |   0.096 |
| apatit_fluor        |       8 |   1.788 |   0.244 |
| trikalsium_fosfat   |      59 |   2.638 |   0.718 |
| tetrakalsium_fosfat |      54 |   2.246 |   0.649 |
| dikalsium_fosfat    |     388 |   2.005 |   0.863 |
| oktakalsium_fosfat  |      85 |   2.852 |   0.284 |
| pirofosfat          |     nan | nan     | nan     |
| monokalsium_fosfat  |     504 |   1.479 |   0.935 |
| fosfat_lain         |    1152 |   2.039 |   0.689 |
## Material Rujukan vs Literatur
- HAp (COD, n=266): densitas 3.07 g/cm3 (literatur 3.16); volume sel 598 A3
- TCP (COD, n=51): densitas 2.58 g/cm3 (literatur b-TCP 3.07); volume sel 1620 A3
- MaterialsProject: Ca3P2 rho=2.02, Eform=-1.12; Ca10P6O25 rho=2.98, Eform=-3.32; Ca10P6O25 rho=2.98, Eform=-3.32; Ca5P3O13 rho=3.05, Eform=-3.24; Ca5P3O13 rho=3.05, Eform=-3.24; Ca5P3O13 rho=3.06, Eform=-3.24; Ca5P3HO13 rho=3.18, Eform=-3.22; Ca5P3HO13 rho=3.18, Eform=-3.22; Ca10P6CO27 rho=3.05, Eform=-3.25; Ca5P3CO12 rho=2.96, Eform=-2.89; Ca5P3O12F rho=3.21, Eform=-3.42; Ca5P3O12F rho=3.10, Eform=-3.42
- AFLOW: Ca3P2 rho=1.98, Eform=-0.98; Ca10O25P6 rho=2.98, Eform=-2.92; Ca3O8P2 rho=3.37, Eform=-2.89; Ca3O8P2 rho=3.36, Eform=-2.89; Ca3O8P2 rho=3.36, Eform=-2.89; Ca10H2O26P6 rho=3.05, Eform=-2.73; Ca10H2O26P6 rho=3.05, Eform=-2.84; Ca10H2O26P6 rho=3.06, Eform=-2.84; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10F2O24P6 rho=3.11, Eform=-3.03; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10O25P6 rho=2.98, Eform=-2.92; Ca3O8P2 rho=3.37, Eform=-2.89; Ca3O8P2 rho=3.36, Eform=-2.89; Ca3O8P2 rho=3.36, Eform=-2.89
## Perbandingan Antar Basis Data (bias sumber)
- 1.0-1.0-nan-nan-nan (CaP): selisih densitas antar sumber 22% -> periksa metode perhitungan
- 1.0-2.0-9.0-nan-nan (CaP2O9): selisih densitas antar sumber 16% -> periksa metode perhitungan
- 1.0-2.0-nan-nan-nan (Ca1P2): selisih densitas antar sumber 64% -> periksa metode perhitungan
- 2.0-1.0-nan-nan-nan (Ca2P1): selisih densitas antar sumber 41% -> periksa metode perhitungan
- 2.0-2.0-nan-nan-nan (Ca2P2): selisih densitas antar sumber 50% -> periksa metode perhitungan
- 2.0-3.0-nan-nan-nan (Ca2P3): selisih densitas antar sumber 42% -> periksa metode perhitungan
- 2.0-4.0-nan-nan-nan (Ca2P4): selisih densitas antar sumber 35% -> periksa metode perhitungan
- 3.0-1.0-nan-nan-nan (Ca3P1): selisih densitas antar sumber 22% -> periksa metode perhitungan
- 4.0-5.0-nan-nan-nan (Ca4P5): selisih densitas antar sumber 17% -> periksa metode perhitungan
## Hipotesis untuk Pemodelan
- H1: Eform berkorelasi dengan EN_diff dan ca_p_ratio (stabilitas ditentukan komposisi).
- H2: Densitas dapat diprediksi dari berat molekul, volume sel, dan EN_avg.
- H3: Kelompok apatit_hidroksi memiliki densitas paling dekat ke tulang kortikal.

## Gambar
- korelasi: `reports/figures/fig_korelasi.png`
- PCA: `reports/figures/fig_pca_kelompok.png`
- t-SNE sumber: `reports/figures/fig_tsne_sumber.png`
- silhouette: `reports/figures/fig_silhouette.png`
- densitas kelompok: `reports/figures/fig_densitas_kelompok.png`
