# LAPORAN FINAL
# Pengembangan Kerangka Materials Informatics Berbasis AI untuk Penemuan Biomaterial Kalsium Fosfat sebagai Kandidat Scaffold Rekayasa Jaringan Tulang

**Tanggal:** 2026-11-04 04:59:09
**Research Group:** AMREC, Universitas Airlangga | Skema PRGF Discovery Research 2027

---

## 1. Ringkasan Eksekutif

Kerangka Materials Informatics berbasis kecerdasan artifisial berhasil dikembangkan secara end-to-end:
**akuisisi data (5 basis data) -> prapemrosesan -> deskriptor fisikokimia -> EDA/klaster -> pemodelan ML -> analisis multiobjektif (TOPSIS+VIKOR) -> interpretasi (SHAP)**.
Dataset terpadu berisi **2.605 entri / 903 komposisi unik** kalsium fosfat (target >= 500 terpenuhi).
Model Random Forest/SVR memprediksi energi pembentukan (R2 = 0.84) dan densitas (R2 = 0.92)
dengan validasi silang berbasis kelompok komposisi (anti-kebocoran).
Pemeringkatan multiobjektif menghasilkan **15 kandidat unik** yang didominasi keluarga apatit
(hidroksiapatit, fluorapatit, karbonat apatit), oktakalsium fosfat, dan tetrakalsium fosfat —
konsisten dengan literatur biomaterial tulang.

## 2. Alur Kerangka (Workflow)

`Data Mining -> Preprocessing -> Feature Engineering -> EDA/Clustering -> ML Modeling -> MCDM -> XAI`

| Tahap | Implementasi | Keluaran |
|---|---|---|
| Akuisisi | Materials Project API, AFLUX REST, COD HTTP, PubChem PUG, OQMD oqmdapi | data/raw/* |
| Prapemrosesan | QC tak-fisik, pencilan IQR/z (dipertahankan+tercatat), satuan SI | laporan_prapemrosesan.md |
| Deskriptor | Ca/P, EN rata-rata/selisih, VEC, berat molekul, densitas teoritis | dataset_deskriptor.csv |
| EDA | Korelasi Pearson+Spearman, VIF, PCA, t-SNE, K-Means (k=5, silhouette 0.55, ARI 1.0) | laporan_eda.md + figures |
| Pemodelan | RF/XGBoost/GBR/SVR, GroupKFold berbasis komposisi | laporan_pemodelan.md |
| MCDM | TOPSIS + VIKOR, 3 set bobot (analisis sensitivitas) | laporan_mcdm.md |
| XAI | SHAP + permutation importance + dependence plots | laporan_xai.md |

## 3. Hasil Pemodelan (GroupKFold, subset komputasional n=291)

| Target | Model terbaik | R2 | RMSE |
|---|---|---|---|
| Energi pembentukan (eV/atom) | SVR | 0.843 | 0.435 |
| Densitas (g/cm3) | Random Forest | 0.916 | 0.132 |
| Bandgap | — GAGAL (R2<0) — keputusan: tanpa imputasi, dipakai nilai terukur saja | | |
| Klasifikasi kelayakan scaffold | Random Forest | Akurasi 0.975, F1 0.90 | |

## 4. Top 15 Kandidat Biomaterial (dedup polimorf, TOPSIS+VIKOR x 3 bobot)

| formula     | sumber           | kelompok            |   peringkat_rerata |   Eform_eV_atom |   densitas_final_gcm3 |   ca_p_ratio |   bandgap_eV |
|:------------|:-----------------|:--------------------|-------------------:|----------------:|----------------------:|-------------:|-------------:|
| Ca10P6CO27  | MaterialsProject | apatit_hidroksi     |              9     |          -3.253 |                 3.053 |        1.667 |        5.137 |
| Ca5P3O12F   | MaterialsProject | apatit_hidroksi     |             11.333 |          -3.42  |                 3.104 |        1.667 |        5.512 |
| Ca8P6H12O29 | MaterialsProject | oktakalsium_fosfat  |             14.833 |          -2.621 |                 2.591 |        1.333 |        4.909 |
| Ca10F2O24P6 | AFLOW            | apatit_hidroksi     |             16.167 |          -3.032 |                 3.096 |        1.667 |        5.518 |
| Ca10P6O25   | MaterialsProject | apatit_hidroksi     |             17.5   |          -3.319 |                 2.978 |        1.667 |        3.148 |
| Ca16O36P8   | AFLOW            | tetrakalsium_fosfat |             21.333 |          -2.937 |                 2.976 |        2     |        4.48  |
| Ca4P2O9     | MaterialsProject | tetrakalsium_fosfat |             22.167 |          -3.326 |                 3.08  |        2     |        4.484 |
| Ca5P3HO13   | MaterialsProject | apatit_hidroksi     |             23     |          -3.223 |                 3.178 |        1.667 |        5.198 |
| Ca10O25P6   | AFLOW            | apatit_hidroksi     |             25.333 |          -2.924 |                 2.977 |        1.667 |        3.177 |
| Ca10H2O26P6 | AFLOW            | apatit_hidroksi     |             28.5   |          -2.84  |                 3.051 |        1.667 |        5.204 |
| Ca8P6O29    | MaterialsProject | oktakalsium_fosfat  |             34     |          -2.531 |                 2.621 |        1.333 |        0     |
| Ca5P3O13    | MaterialsProject | apatit_hidroksi     |             34.167 |          -3.243 |                 3.054 |        1.667 |        0.532 |
| Ca5P3CO12   | MaterialsProject | apatit_hidroksi     |             37.167 |          -2.893 |                 2.96  |        1.667 |        0.53  |
| CaP4O11     | MaterialsProject | fosfat_lain         |             40.833 |          -2.786 |                 2.2   |        0.25  |        5.342 |
| Ca2P6O17    | MaterialsProject | fosfat_lain         |             43.167 |          -2.856 |                 2.381 |        0.333 |        5.366 |

**Validasi material rujukan:** HAp MP rho = 3.18 g/cm3 (literatur 3.16, selisih <1%);
fluorapatit 3.10-3.21 (lit. 3.19); COD HAp rata-rata 3.07. Karbonat apatit, FAp, dan OCP
yang menempati peringkat teratas adalah bahan graft tulang yang dikenal di klinik
-> hasil kerangka konsisten dengan pengetahuan material.

## 5. Interpretasi (SHAP)

- Eform didorong oleh fraksi O dan densitas (permutation importance: frac_O, densitas, volume sel).
- Densitas didorong oleh volume sel, EN rata-rata, dan berat molekul; Ca/P berkorelasi positif (0.57) dengan densitas prediksi.
- Fitur redundan EN_diff & VEC disisihkan (r > 0.85 dengan EN_avg, VIF > 10).

## 6. Risiko, Keputusan, Keterbatasan

- **Bias sumber:** fraksi tetangga sesumber (k=5) = 0.94 -> klaster sebagian dibentuk oleh sumber data (COD eksperimental vs MP/AFLOW komputasional). Mitigasi: pemodelan hanya pada subset komputasional; split berbasis kelompok komposisi.
- **Modulus elastik:** hanya 9 entri punya K & G -> kriteria MCDM C4 memakai imputasi median (keputusan tercatat). Validasi DFT/MD pada top kandidat WAJIB (Bagian 9.2 panduan).
- **Bandgap:** tidak dapat diprediksi dari deskriptor komposisi (R2 < 0) -> imputasi dibatalkan, nilai terukur dipakai.
- **OQMD:** server tidak stabil; akuisisi berjalan dengan retry panjang; datanya melengkapi (icsd_id, energi) bila selesai.
- **Ketimpangan kelas:** klasifikasi 44/247 (15%) -> recall kelas layak 0.82.

## 7. Langkah Selanjutnya

1. Integrasikan OQMD bila akuisisi selesai (verifikasi stabilitas fase via icsd_id).
2. Validasi DFT/MD untuk Top 5 kandidat (stabilitas & modulus).
3. Analisis sensitivitas bobot yang lebih luas + pembobotan entropi.
4. Penyusunan artikel (target: Computational Materials Science, Elsevier Gold OA — sesuai RAB).
5. Platform AI-Assisted Biomaterial Discovery (roadmap AMREC).
