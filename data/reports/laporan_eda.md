# Laporan Eksplorasi Ruang Desain Material
**Tanggal:** 2026-11-04 10:24:13 | **Tahapan:** Bagian 4-5 panduan utama

## Korelasi & Multikolinearitas
- Tidak ada pasangan dengan |r| > 0.85
## VIF (subset pemodelan, n=291)
- Eform_eV_atom: 3.1
- densitas_final_gcm3: 1.3
- volume_A3: 1.7
- EN_avg: 4.0
- berat_molekul: 1.7
- ca_p_ratio: 1.5
## PCA: PC1 32.5% + PC2 26.9% = 59.3% varians
## Bias sumber: fraksi tetangga-terdekat (k=5) sesumber = 0.88 (mendekati 1 = klaster terbentuk oleh sumber, bukan sifat)
## Klaster K-Means (silhouette): k=3:0.446, k=4:0.478, k=5:0.502, k=6:0.375, k=7:0.398, k=8:0.410
- k terbaik = 5; stabilitas ARI antar-seed = 0.989
## Profil Klaster (rerata deskriptor, kelompok dominan)
|   klaster |   densitas_final_gcm3 |   volume_A3 |   EN_avg |   berat_molekul |   ca_p_ratio | kelompok           |
|----------:|----------------------:|------------:|---------:|----------------:|-------------:|:-------------------|
|         0 |                  2.42 |     1080.91 |     2.85 |          511.13 |         1.32 | fosfat_lain        |
|         1 |                  1.99 |      474.15 |     3.03 |          285.24 |       130.83 | fosfat_lain        |
|         2 |                  0.54 |     4693.04 |     2.37 |          401.97 |         0.55 | monokalsium_fosfat |
|         3 |                  1.91 |     5942.97 |     2.98 |         3239.92 |         0.98 | fosfat_lain        |
|         4 |                  2.41 |      208.1  |     1.64 |          187.4  |         1.19 | fosfat_lain        |
## Densitas per Kelompok Material (g/cm3)
| kelompok            |   count |    mean |     std |
|:--------------------|--------:|--------:|--------:|
| apatit_hidroksi     |     321 |   3.082 |   0.097 |
| apatit_fluor        |      11 |   1.967 |   0.368 |
| trikalsium_fosfat   |      82 |   2.727 |   0.68  |
| tetrakalsium_fosfat |      92 |   2.278 |   0.616 |
| dikalsium_fosfat    |     482 |   2.117 |   0.821 |
| oktakalsium_fosfat  |      85 |   2.852 |   0.284 |
| pirofosfat          |     nan | nan     | nan     |
| monokalsium_fosfat  |     548 |   1.56  |   0.965 |
| fosfat_lain         |    1208 |   2.069 |   0.688 |
## Material Rujukan vs Literatur
- HAp (COD, n=266): densitas 3.07 g/cm3 (literatur 3.16); volume sel 598 A3
- TCP (COD, n=51): densitas 2.58 g/cm3 (literatur b-TCP 3.07); volume sel 1620 A3
- MaterialsProject: Ca3P2 rho=2.02, Eform=-1.12; Ca10P6O25 rho=2.98, Eform=-3.32; Ca10P6O25 rho=2.98, Eform=-3.32; Ca3(PO4)2 rho=3.51, Eform=-3.28; Ca3(PO4)2 rho=2.98, Eform=-3.32; Ca3(PO4)2 rho=2.81, Eform=-2.77; Ca3(PO4)2 rho=2.84, Eform=-3.25; Ca3(PO4)2 rho=2.78, Eform=-3.33; Ca5(PO4)3 rho=2.96, Eform=-3.25; Ca5P3O13 rho=3.05, Eform=-3.24; Ca5P3O13 rho=3.05, Eform=-3.24; Ca5P3O13 rho=3.06, Eform=-3.24; Ca5P3HO13 rho=3.18, Eform=-3.22; Ca5P3HO13 rho=3.18, Eform=-3.22; Ca10P6CO27 rho=3.05, Eform=-3.25; Ca5P3CO12 rho=2.96, Eform=-2.89; Ca5P3O12F rho=3.21, Eform=-3.42; Ca5P3O12F rho=3.10, Eform=-3.42
- AFLOW: Ca3P2 rho=1.98, Eform=-0.98; Ca10O25P6 rho=2.98, Eform=-2.92; Ca3O8P2 rho=3.37, Eform=-2.89; Ca3O8P2 rho=3.36, Eform=-2.89; Ca3O8P2 rho=3.36, Eform=-2.89; Ca10H2O26P6 rho=3.05, Eform=-2.73; Ca10H2O26P6 rho=3.05, Eform=-2.84; Ca10H2O26P6 rho=3.06, Eform=-2.84; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10F2O24P6 rho=3.11, Eform=-3.03; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10F2O24P6 rho=3.10, Eform=-3.03; Ca10O25P6 rho=2.98, Eform=-2.92; Ca3O8P2 rho=3.37, Eform=-2.89; Ca3O8P2 rho=3.36, Eform=-2.89; Ca3O8P2 rho=3.36, Eform=-2.89
## Perbandingan Antar Basis Data (bias sumber)
- 1.0-1.0-nan-nan-nan (CaP): selisih densitas antar sumber 21% -> periksa metode perhitungan
- 1.0-2.0-9.0-nan-nan (CaP2O9): selisih densitas antar sumber 16% -> periksa metode perhitungan
- 1.0-2.0-nan-nan-nan (Ca1P2): selisih densitas antar sumber 66% -> periksa metode perhitungan
- 1.0-8.0-nan-nan-nan (Ca1P8): selisih densitas antar sumber 31% -> periksa metode perhitungan
- 2.0-1.0-nan-nan-nan (Ca2P1): selisih densitas antar sumber 40% -> periksa metode perhitungan
- 2.0-2.0-nan-nan-nan (Ca2P2): selisih densitas antar sumber 50% -> periksa metode perhitungan
- 2.0-3.0-nan-nan-nan (Ca2P3): selisih densitas antar sumber 42% -> periksa metode perhitungan
- 2.0-4.0-nan-nan-nan (Ca2P4): selisih densitas antar sumber 35% -> periksa metode perhitungan
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
