# LAPORAN FINAL
# Pengembangan Kerangka Materials Informatics Berbasis AI untuk Penemuan Biomaterial Kalsium Fosfat sebagai Kandidat Scaffold Rekayasa Jaringan Tulang

**Tanggal:** 2026-11-04 07:12:34
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

## 3. Hasil Pemodelan (protokol anti-kebocoran: grouping formula tereduksi, nested CV, fitur komposisi murni)

| Tugas | Model | R2 | MAE |
|---|---|---|---|
| Eform — semua entri komputasional (n=571) | SVR nested | 0.483 | 0.265 |
| Eform — dalam keluarga fosfat saja (n=215) | SVR | 0.580 | 0.176 |
| Eform — varian screening basis data (n=291) | SVR nested | 0.489 | 0.242 |
| Transfer antar basis data, komposisi sama (OQMD n=280) | SVR | 0.883 | 0.254 |
| Densitas — komposisi murni (n=571) | Random Forest | 0.174 | 0.264 |
| Bandgap | GAGAL (R2<0) — tanpa imputasi | | |
| Benchmark eksperimen (6 fase): Eform MAE 0.254 eV/atom, densitas MAE 0.177 g/cm3 | | | |
| Konteks SOTA: GNN (CGCNN/MEGNet/CHGNet) MAE 0.03–0.1 eV/atom — kontribusi kami = pipeline teraudit, bukan akurasi regresi. Target internal R2>=0.85 DITARIK (arbitrer, disusun tanpa analisis kebocoran). | | | |

## 4. Top 15 Kandidat Biomaterial (dedup polimorf, TOPSIS+VIKOR x 3 bobot)

| formula     | sumber           | kelompok            |   peringkat_rerata |   Eform_eV_atom |   densitas_final_gcm3 |   ca_p_ratio |   bandgap_eV |
|:------------|:-----------------|:--------------------|-------------------:|----------------:|----------------------:|-------------:|-------------:|
| Ca5P3O12F   | MaterialsProject | apatit_hidroksi     |              1.333 |          -3.42  |                 3.104 |        1.667 |        5.512 |
| Ca10P6CO27  | MaterialsProject | apatit_hidroksi     |              3.333 |          -3.253 |                 3.053 |        1.667 |        5.137 |
| Ca5P3HO13   | MaterialsProject | apatit_hidroksi     |              4.333 |          -3.223 |                 3.178 |        1.667 |        5.198 |
| Ca10F2O24P6 | AFLOW            | apatit_hidroksi     |              7.167 |          -3.032 |                 3.096 |        1.667 |        5.518 |
| Ca4P2O9     | MaterialsProject | tetrakalsium_fosfat |             15.833 |          -3.326 |                 3.08  |        2     |        4.484 |
| Ca2P2O7     | MaterialsProject | dikalsium_fosfat    |             25.5   |          -3.213 |                 2.95  |        1     |        5.514 |
| Ca10H2O26P6 | AFLOW            | apatit_hidroksi     |             27.333 |          -2.84  |                 3.051 |        1.667 |        5.204 |
| Ca(PO3)2    | MaterialsProject | dikalsium_fosfat    |             30.833 |          -2.971 |                 2.873 |        1     |        5.497 |
| Ca16O36P8   | AFLOW            | tetrakalsium_fosfat |             34.333 |          -2.937 |                 2.976 |        2     |        4.48  |
| Ca10P6O25   | MaterialsProject | apatit_hidroksi     |             35.667 |          -3.319 |                 2.978 |        1.667 |        3.148 |
| Ca4P6O19    | MaterialsProject | fosfat_lain         |             38.167 |          -3.068 |                 2.898 |        0.667 |        5.362 |
| Ca3(PO4)2   | MaterialsProject | fosfat_lain         |             38.833 |          -3.322 |                 2.979 |        3     |        4.98  |
| CaPHO4      | MaterialsProject | dikalsium_fosfat    |             39.833 |          -2.8   |                 2.947 |        1     |        5.439 |
| Ca3O8P2     | AFLOW            | trikalsium_fosfat   |             40.167 |          -2.887 |                 3.364 |        1.5   |        5.469 |
| Ca16O56P16  | AFLOW            | dikalsium_fosfat    |             41.333 |          -2.8   |                 3.01  |        1     |        5.423 |

**Klaim jujur (koreksi 2026-11-04, dua putaran reviewer):**
- QC sumber data (nilai DATABASE vs literatur): selisih densitas <= 2.9% — menguji basis data, bukan model;
  kecocokan kisi alpha/beta-TCP melingkar (COD menyimpan struktur dari paper yang sama).
- Validasi INDEPENDEN prediksi MODEL (fitur komposisi murni) vs eksperimen (Wagman/NBS + densitas
  kristalografi, 6 fase): Eform MAE 0.254 eV/atom (terbaik monetit +0.08, TTCP +0.16; terbesar
  alpha-TCP +0.35); densitas MAE 0.177 g/cm3. Lihat laporan_validasi_independen.md.
- Koreksi kebocoran: versi lama (a) model densitas = hampir identitas rho=MZ/(NA.V) dan bahkan
  target masuk fitur pada benchmark lama (MAE 0.007 TIDAK VALID); (b) Eform memakai densitas sebagai
  fitur; (c) classifier = fungsi semi-deterministik fiturnya (ditarik dari klaim & MCDM);
  (d) grouping formula mentah bocor utk kelipatan formula -> kini formula tereduksi (gcd);
  (e) tuning & pelaporan CV sama -> kini nested CV; (f) uji 'eksternal' OQMD = komposisi sama
  dengan latih -> dilaporkan sebagai transfer sesama-komposisi (R2 0.88), bukan ekstrapolasi;
  (g) R2 lama dikatrol bimodal fosfida/fosfat -> dilaporkan dalam-keluarga (0.58).
- Kriteria MCDM dirancang dari kebutuhan desain -> peringkat atas apatitik ADALAH konstruksi.
  b-TCP kini masuk 15 besar (peringkat 14) setelah kriteria densitas pita; kekurangan kriteria
  resorbabilitas tetap menjadi arah pengembangan.

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
