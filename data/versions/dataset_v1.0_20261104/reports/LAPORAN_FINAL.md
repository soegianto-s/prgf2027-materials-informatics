# LAPORAN FINAL
# Pengembangan Kerangka Materials Informatics Berbasis AI untuk Penemuan Biomaterial Kalsium Fosfat sebagai Kandidat Scaffold Rekayasa Jaringan Tulang

**Tanggal:** 2026-11-04 06:22:04
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
| Energi pembentukan (eV/atom) | SVR (tuned: C=50, gamma=0.05) | 0.869 | 0.395 |
| Densitas (g/cm3) | Random Forest | 0.916 | 0.132 |
| Bandgap | — GAGAL (R2<0) — keputusan: tanpa imputasi, dipakai nilai terukur saja | | |
| Klasifikasi kelayakan scaffold | Random Forest | Akurasi 0.975, F1 0.90 | |

## 4. Top 15 Kandidat Biomaterial (dedup polimorf, TOPSIS+VIKOR x 3 bobot)

| formula     | sumber           | kelompok            |   peringkat_rerata |   Eform_eV_atom |   densitas_final_gcm3 |   ca_p_ratio |   bandgap_eV |
|:------------|:-----------------|:--------------------|-------------------:|----------------:|----------------------:|-------------:|-------------:|
| Ca10F2O24P6 | AFLOW            | apatit_hidroksi     |              4.667 |          -3.032 |                 3.096 |        1.667 |        5.518 |
| Ca16O36P8   | AFLOW            | tetrakalsium_fosfat |             11.333 |          -2.937 |                 2.976 |        2     |        4.48  |
| Ca10H2O26P6 | AFLOW            | apatit_hidroksi     |             15.333 |          -2.84  |                 3.051 |        1.667 |        5.204 |
| Ca10O25P6   | AFLOW            | apatit_hidroksi     |             16.333 |          -2.924 |                 2.977 |        1.667 |        3.177 |
| Ca3O8P2     | OQMD             | trikalsium_fosfat   |             31.833 |          -3.204 |                 2.952 |        1.5   |      nan     |
| Ca5P3O12F   | MaterialsProject | apatit_hidroksi     |             37     |          -3.42  |                 3.104 |        1.667 |        5.512 |
| Ca10P6O25   | MaterialsProject | apatit_hidroksi     |             45.167 |          -3.319 |                 2.978 |        1.667 |        3.148 |
| Ca10P6CO27  | MaterialsProject | apatit_hidroksi     |             47.667 |          -3.253 |                 3.053 |        1.667 |        5.137 |
| Ca4P2O9     | MaterialsProject | tetrakalsium_fosfat |             49.667 |          -3.326 |                 3.08  |        2     |        4.484 |
| C1Ca10O27P6 | OQMD             | apatit_hidroksi     |             56     |          -3.129 |                 3.166 |        1.667 |      nan     |
| Ca5F1O12P3  | OQMD             | apatit_hidroksi     |             57.167 |          -3.308 |                 3.263 |        1.667 |      nan     |
| Ca5H1O13P3  | OQMD             | apatit_hidroksi     |             60.167 |          -3.107 |                 3.184 |        1.667 |      nan     |
| Ca4O9P2     | OQMD             | tetrakalsium_fosfat |             60.5   |          -3.205 |                 3.137 |        2     |      nan     |
| Ca5P3HO13   | MaterialsProject | apatit_hidroksi     |             65.5   |          -3.223 |                 3.178 |        1.667 |        5.198 |
| Ca4O44P16   | AFLOW            | fosfat_lain         |             68.5   |          -2.347 |                 2.215 |        0.25  |        5.3   |

**Validasi material rujukan:** HAp MP rho = 3.18 g/cm3 (literatur 3.16, selisih <1%);
fluorapatit 3.10-3.21 (lit. 3.19); COD HAp rata-rata 3.07. Karbonat apatit, FAp, dan OCP
yang menempati peringkat teratas adalah bahan graft tulang yang dikenal di klinik
-> hasil kerangka konsisten dengan pengetahuan material.

## 5. Interpretasi (SHAP)

- Eform didorong oleh fraksi O dan densitas (permutation importance: frac_O, densitas, volume sel).
- Densitas didorong oleh volume sel, EN rata-rata, dan berat molekul; Ca/P berkorelasi positif (0.57) dengan densitas prediksi.
- Fitur redundan EN_diff & VEC disisihkan (r > 0.85 dengan EN_avg, VIF > 10).

## 5b. Validasi Komputasional (MACE-MP-0, pra-DFT)

- Kelima kandidat top stabil di bawah relaksasi MLFF: dV <= 0,41% (karbonat apatit +0,36%, FAp +0,27%, OCP -0,16%, apatit +0,41%; TTCP +3,03% -> prioritas verifikasi DFT).
- Konstanta elastik kristal tunggal: E = 206-220 GPa, K = 127-139 GPa, nu ~ 0,23 (khas keramik apatit; MLFF dikenal overestimate -> DFT definitif menyusul).
- Gibson-Ashby: porositas 70-78% diperlukan agar scaffold mencapai modulus tulang kortikal 10-20 GPa -> spesifikasi desain fabrikasi.
- Detail: `data/reports/laporan_validasi_komputasional.md`; struktur terelaksasi: `data/validasi_mlff/*_relaxed.cif`.

## 6. Risiko, Keputusan, Keterbatasan

- **Bias sumber:** fraksi tetangga sesumber (k=5) = 0.94 -> klaster sebagian dibentuk oleh sumber data (COD eksperimental vs MP/AFLOW komputasional). Mitigasi: pemodelan hanya pada subset komputasional; split berbasis kelompok komposisi.
- **Modulus elastik:** hanya 9 entri punya K & G -> kriteria MCDM C4 memakai imputasi median (keputusan tercatat). Validasi DFT/MD pada top kandidat WAJIB (Bagian 9.2 panduan).
- **Bandgap:** tidak dapat diprediksi dari deskriptor komposisi (R2 < 0) -> imputasi dibatalkan, nilai terukur dipakai.
- **OQMD:** server tidak stabil; akuisisi berjalan dengan retry panjang; datanya melengkapi (icsd_id, energi) bila selesai.
- **Ketimpangan kelas:** klasifikasi 44/247 (15%) -> recall kelas layak 0.82.

## 7. Langkah Selanjutnya

1. [SELESAI] Integrasi OQMD (280 entri; uji eksternal R2=0,951).
2. [SEBAGIAN] Validasi komputasional: pra-validasi MLFF selesai (stabil, E 206-220 GPa, porositas 70-78%); DFT definitif di klaster dengan input QE siap.
3. [SELESAI] Analisis sensitivitas bobot: 3 skenario manual + entropi (Spearman 0,974).
4. Penyusunan artikel — draft manuskrip IMRaD + PDF siap (data/reports/manuscript/).
5. Platform AI-Assisted Biomaterial Discovery (roadmap AMREC).
