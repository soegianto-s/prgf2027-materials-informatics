# LAPORAN FINAL
# Pengembangan Kerangka Materials Informatics Berbasis AI untuk Penemuan Biomaterial Kalsium Fosfat sebagai Kandidat Scaffold Rekayasa Jaringan Tulang

**Tanggal:** 2026-11-04 08:16:40
**Research Group:** AMREC, Universitas Airlangga | Skema PRGF Discovery Research 2027

---

## 1. Ringkasan Eksekutif

Kerangka Materials Informatics berbasis kecerdasan artifisial berhasil dikembangkan secara end-to-end:
**akuisisi data (5 basis data) -> prapemrosesan -> deskriptor fisikokimia -> EDA/klaster -> pemodelan ML -> analisis multiobjektif (TOPSIS+VIKOR) -> interpretasi (SHAP)**.
Dataset terpadu berisi **2.885 entri / 950 komposisi unik** kalsium fosfat (target >= 500 terpenuhi).
Model SVR (nested CV, 4 DOF komposisi murni: Ca/P, fraksi P, H, F) memprediksi energi pembentukan
dengan R2 = 0,113 (n=337 MP+OQMD, skala konsisten; AFLOW dikecualikan) dan densitas R2 = 0,018
(komposisi murni, n=571) dengan validasi silang berbasis kelompok komposisi (anti-kebocoran).
Varian screening berstruktur (volume+densitas) mencapai R2 = 0,401; transfer antar basis data
sesama-komposisi (latih MP n=57 -> uji OQMD n=280) R2 = 0,833. Dalam keluarga fosfat saja,
komposisi murni TIDAK punya daya prediksi (R2 = -0,516) — temuan struktural ronde 3.
Pemeringkatan multiobjektif (TOPSIS+VIKOR, 3 kriteria level material: stabilitas, pita densitas
[1.0, 3.2], Ca/P->1.67; filter kenetralan muatan; kolam 165 kalsium fosfat netral) menghasilkan
**15 kandidat unik** yang dipuncaki fluorapatit, oksiapatit, karbonat apatit, hidroksiapatit,
dan b-TCP. Monte Carlo 3.000 run (bobot Dirichlet + noise MAE model) menegaskan stabilitas top-4
(masuk top-5 pada 56–86% run); slot ke-5 diperebutkan karbonat apatit vs TTCP (17% masing-masing).
Overlay resorbabilitas literatur (pKsp) membuat trade-off stabilitas–resorbabilitas eksplisit;
klaim 'accelerated discovery' dicabut — kerangka = penyaringan sistematis ruang komposisi dikenal.

**Ronde 6 (baseline pembanding atas permintaan reviewer, 2026-11-04):** (a) 40 fitur Magpie — Eform
tetap ≈ nol (R2 = −0,055) tetapi densitas naik ke R2 0,273–0,309 (statistik kontras unsur menangkap
info kemasan); (b) pretrained MACE-MP-0 (float64, model L1) — Eform 6 fase benchmark Wagman/NBS
MAE 0,253 eV/atom (vs 0,094 model komposisi: pada benchmark sempit ini surrogate terlatih-basis-data
tidak terlampaui; keunggulan MLFF = generalitas untuk fase di luar distribusi latih);
(c) re-ranking sensitivitas pKsp — β-TCP/TTCP/monetit naik ke 3 besar, FAp/oksiapatit/HA turun
(trade-off terkuantifikasi).

## 2. Alur Kerangka (Workflow)

`Data Mining -> Preprocessing -> Feature Engineering -> EDA/Clustering -> ML Modeling -> MCDM -> XAI`

| Tahap | Implementasi | Keluaran |
|---|---|---|
| Akuisisi | Materials Project API, AFLUX REST, COD HTTP, PubChem PUG, OQMD oqmdapi | data/raw/* |
| Prapemrosesan | QC tak-fisik, pencilan IQR/z (dipertahankan+tercatat), satuan SI | laporan_prapemrosesan.md |
| Deskriptor | Ca/P, EN rata-rata/selisih, VEC, berat molekul, densitas teoritis; pemodelan discovery: 4 DOF komposisi (Ca/P, P, H, F) | dataset_deskriptor.csv |
| EDA | Korelasi Pearson+Spearman, VIF, PCA, t-SNE, K-Means (k=5, silhouette 0.50, ARI 0.88) | laporan_eda.md + figures |
| Pemodelan | RF/XGBoost/GBR/SVR, GroupKFold berbasis komposisi | laporan_pemodelan.md |
| MCDM | TOPSIS + VIKOR, 3 kriteria + filter muatan + entropi + Monte Carlo | laporan_mcdm.md + laporan_montecarlo.md |
| XAI | SHAP + permutation importance + dependence plots | laporan_xai.md |

## 3. Hasil Pemodelan (protokol anti-kebocoran: grouping formula tereduksi, nested CV, 4 DOF komposisi murni)

| Tugas | Model | R2 | MAE |
|---|---|---|---|
| Eform — komposisi murni (n=337, MP+OQMD skala konsisten) | SVR nested | 0.113 | 0.297 |
| Eform — dalam keluarga fosfat saja (n=157) | SVR | -0.516 | 0.139 |
| Eform — varian screening basis data (n=291, volume+densitas) | SVR nested | 0.401 | 0.304 |
| Transfer antar basis data, komposisi sama (latih MP n=57 -> OQMD n=280) | SVR | 0.833 | 0.268 |
| Densitas — komposisi murni (n=571) | Random Forest | 0.018 | 0.307 |
| Bandgap | GAGAL (R2<0) — tanpa imputasi | | |
| Benchmark eksperimen (6 fase): Eform MAE 0.094 eV/atom, densitas MAE 0.114 g/cm3 | | | |
| Baseline Magpie (40 fitur statistik unsur, protokol identik): Eform R2=-0.055; densitas R2=0.273 (SVR)/0.309 (RF) — kontras properti unsur menangkap info kemasan (densitas), bukan energi | | | |
| Baseline pretrained MACE-MP-0 (float64, model L1): Eform 6 fase Wagman/NBS MAE 0.253 eV/atom (vs 0.094 model komposisi) — pada benchmark sempit ini MLFF tidak mengungguli surrogate terlatih-basis-data | | | |
| Sensitivitas MCDM+pKsp (shortlist 8 komposisi, 3 skenario bobot): b-TCP/TTCP/monetit naik ke 3 besar; FAp/oksiapatit/HA turun — trade-off stabilitas-resorbabilitas kuantitatif | | | |
| Konteks SOTA: GNN (CGCNN/MEGNet/CHGNet) MAE 0.03–0.1 eV/atom — kontribusi kami = pipeline teraudit, bukan akurasi regresi. Target internal R2>=0.85 DITARIK (arbitrer, disusun tanpa analisis kebocoran). | | | |

## 4. Top 15 Kandidat Biomaterial (komposisi unik tereduksi; 3 kriteria + filter muatan; TOPSIS+VIKOR x 3 bobot)

| formula     | sumber           | kelompok            |   peringkat |   peringkat_rerata |   Eform_eV_atom |   densitas_final_gcm3 |   ca_p_ratio |   bandgap_eV |
|:------------|:-----------------|:--------------------|------------:|-------------------:|----------------:|----------------------:|-------------:|-------------:|
| Ca5P3O12F   | MaterialsProject | apatit_hidroksi     |           1 |              1     |          -3.42  |                 3.104 |        1.667 |        5.512 |
| Ca10P6O25   | MaterialsProject | apatit_hidroksi     |           2 |              2.667 |          -3.319 |                 2.978 |        1.667 |        3.148 |
| Ca10P6CO27  | MaterialsProject | apatit_hidroksi     |           3 |              5.5   |          -3.253 |                 3.053 |        1.667 |        5.137 |
| Ca5P3HO13   | MaterialsProject | apatit_hidroksi     |           4 |              6.667 |          -3.223 |                 3.178 |        1.667 |        5.198 |
| Ca3(PO4)2   | MaterialsProject | trikalsium_fosfat   |           5 |             29.333 |          -3.326 |                 2.781 |        1.5   |        4.912 |
| Ca4P2O9     | MaterialsProject | tetrakalsium_fosfat |           6 |             50.333 |          -3.326 |                 3.08  |        2     |        4.484 |
| Ca2P2O7     | MaterialsProject | dikalsium_fosfat    |           7 |             67.333 |          -3.213 |                 2.95  |        1     |        5.514 |
| Ca8P6H12O29 | MaterialsProject | oktakalsium_fosfat  |           8 |             72.667 |          -2.621 |                 2.591 |        1.333 |        4.909 |
| CaPHO4      | MaterialsProject | dikalsium_fosfat    |           9 |             89.167 |          -2.8   |                 2.947 |        1     |        5.439 |
| Ca2P2H4O9   | MaterialsProject | dikalsium_fosfat    |          10 |            101.333 |          -2.523 |                 2.478 |        1     |        5.069 |
| Ca4P6O19    | MaterialsProject | fosfat_lain         |          11 |            108.333 |          -3.068 |                 2.898 |        0.667 |        5.362 |
| Ca2P2H8O11  | MaterialsProject | dikalsium_fosfat    |          12 |            114.167 |          -2.189 |                 2.189 |        1     |        4.854 |
| Ca(PO3)2    | MaterialsProject | monokalsium_fosfat  |          13 |            115.333 |          -2.971 |                 2.873 |        0.5   |        5.497 |
| CaPH5O6     | MaterialsProject | dikalsium_fosfat    |          14 |            118.167 |          -2.083 |                 2.282 |        1     |        5.402 |
| CaP2H2O7    | MaterialsProject | monokalsium_fosfat  |          15 |            124.333 |          -2.582 |                 2.419 |        0.5   |        5.706 |

**Klaim jujur (koreksi 2026-11-04, tiga putaran reviewer):**
- QC sumber data (nilai DATABASE vs literatur): selisih densitas <= 2.9% — menguji basis data, bukan model;
  kecocokan kisi alpha/beta-TCP melingkar (COD menyimpan struktur dari paper yang sama).
- Validasi INDEPENDEN prediksi MODEL (4 DOF komposisi murni) vs eksperimen (Wagman/NBS + densitas
  kristalografi, 6 fase): Eform MAE 0.094 eV/atom (terbesar brushit -0.302, fase terhidrasi di
  luar distribusi latih anhidrat); densitas MAE 0.114 g/cm3. Catatan: benchmark 6 fase terkenal =
  uji sempit sesama-keluarga; angka CV berkelompok tetap estimasi jujur. Lihat laporan_validasi_independen.md.
- Koreksi kebocoran: versi lama (a) model densitas = hampir identitas rho=MZ/(NA.V) dan bahkan
  target masuk fitur pada benchmark lama (MAE 0.007 TIDAK VALID); (b) Eform memakai densitas sebagai
  fitur; (c) classifier = fungsi semi-deterministik fiturnya (ditarik dari klaim & MCDM);
  (d) grouping formula mentah bocor utk kelipatan formula -> kini formula tereduksi (gcd);
  (e) tuning & pelaporan CV sama -> kini nested CV; (f) uji 'eksternal' OQMD = komposisi sama
  dengan latih -> kini latih MP saja (n=57) -> uji OQMD (n=280), dilaporkan sebagai transfer
  sesama-komposisi (R2 0.833), bukan ekstrapolasi;
  (g) R2 lama dikatrol bimodal fosfida/fosfat + deskriptor redundan (EN_avg & berat molekul =
  fungsi linear eksak fraksi unsur, VIF tak hingga) -> kini 4 DOF komposisi (Ca/P, P, H, F);
  R2 dalam-keluarga NEGATIF (-0.516): komposisi murni tidak punya daya prediksi dalam-keluarga,
  Eform hanya melatih MP+OQMD (n=337, AFLOW dikecualikan karena beda skala energi).
- Kriteria MCDM (ronde 4): hanya 3 kriteria level material dengan cakupan data penuh (stabilitas,
  pita densitas [1.0, 3.2], Ca/P->1.67). C4 modulus & C5 bandgap DITARIK: C4 cuma n=9 -> imputasi
  median = praktis konstanta + mencampur level scaffold vs material (kekakuan scaffold ditangani
  hilir via porositas Gibson-Ashby); C5 tanpa fungsi elektronik pada scaffold tulang. Filter
  stoikiometri membuang 398 entri muatan != 0 (contoh Ca5P3O13) + 356 fosfida -> kolam 165.
  b-TCP kini peringkat 5. Resorbabilitas dinilai POST-HOC dari literatur (pKsp), bukan kriteria
  (data hanya ada untuk fase dikenal) — trade-off stabilitas vs resorbabilitas eksplisit.
- Ketidakpastian (ronde 4): Monte Carlo 3.000 run (bobot Dirichlet + noise MAE Eform 0.297 /
  densitas 0.307) — top-4 stabil (top-5 56-86%), slot ke-5 diperebutkan (karbonat apatit & TTCP
  17% masing-masing); entropi Shannon (Spearman 0.93) dinyatakan sebagai cek konsistensi INTERNAL,
  bukan validasi independen.
- Klaim 'accelerated discovery' DICABUT dari judul & abstrak (kandidat teratas = fase yang sudah
  dikenal); kerangka = penyaringan & pemeringkatan sistematis ruang komposisi yang dikenal.

## 5. Interpretasi (SHAP, fitur komposisi 4-DOF: Ca/P, fraksi P, H, F)

- Eform (RF, n=337 MP+OQMD): frac_P dan ca_p_ratio paling berpengaruh (permutation importance:
  frac_P, ca_p_ratio, frac_H); korelasi SHAP Ca/P vs nilai Ca/P +0.03 (arah lemah).
- Densitas (RF, n=571): frac_P dan ca_p_ratio dominan (permutation importance: frac_P, ca_p_ratio,
  frac_H); korelasi SHAP Ca/P vs nilai Ca/P -0.43 — Ca/P tinggi mendorong prediksi densitas turun
  (deskriptif model, tidak diinterpretasikan berlebihan mengingat R2 komposisi murni ~nol).
- Fitur redundan disisihkan: EN_diff & VEC (r > 0.85 dengan EN_avg, VIF > 10) pada tahap
  deskriptor; EN_avg & berat molekul disisihkan pada tahap pemodelan (fungsi linear eksak fraksi
  unsur, VIF tak hingga).

## 5b. Validasi Komputasional (MACE-MP-0, pra-DFT, Top-5 ronde 4)

- Top-5 baru (FAp, oksiapatit, karbonat apatit, HA, b-TCP) direlaksasi MACE-MP-0: FAp +0,27%, oksiapatit +0,41%, karbonat apatit +0,36%, b-TCP -0,39% (|dV| <= 0,41% -> stabil); HA +4,34% -> prioritas verifikasi DFT.
- Konstanta elastik kristal tunggal: E = 204-220 GPa, K = 131-139 GPa, nu ~ 0,23-0,24 (khas keramik apatit; MLFF dikenal overestimate -> DFT definitif menyusul).
- Gibson-Ashby: porositas 70-78% diperlukan agar scaffold mencapai modulus tulang kortikal 10-20 GPa -> spesifikasi desain fabrikasi.
- Detail: `data/reports/laporan_validasi_komputasional.md`; struktur terelaksasi: `data/validasi_mlff/*_relaxed.cif`.
- Baseline pretrained MACE-MP-0 (float64, model L1) untuk Eform 6 fase benchmark (Wagman/NBS):
  MAE 0,253 eV/atom vs 0,094 model komposisi (ronde 6). Pada benchmark sempit sesama-keluarga ini
  MLFF tidak mengungguli surrogate terlatih-basis-data (skala energi GGA yang sama); nilai MLFF =
  generalitas untuk fase arbitrer. Struktur terelaksasi: `data/validasi_mace/*_relaxed.cif`;
  detail: `laporan_baseline_mace.md`. (Catatan: deskripsi model dikoreksi 'medium' -> 'float64'
  karena bobot float64 mace-torch = model L1.)

## 5c. Overlay Resorbabilitas (pKsp literatur, 25 C) — bukan kriteria MCDM

| Fase | pKsp | Kelas degradasi | Peran scaffold |
|---|---|---|---|
| Brushite (DCPD) | 6,59 | cepat | prekursor semen resorbabel |
| Monetite (DCPA) | 6,90 | cepat | prekursor semen resorbabel |
| OCP | 96,6 | cepat in vivo | prekursor HA, resorbabel |
| a-TCP | 25,5 | resorbabel | komponen setting semen |
| b-TCP | 28,9 | resorbabel | scaffold resorbabel (standar klinis) |
| TTCP | ~38 | lambat | komponen setting semen |
| Hidroksiapatit | 116,8 | praktis tidak larut | permanen/low-turnover |
| Fluorapatit | ~121 | praktis tidak larut | dental, low-turnover |
| Oksiapatit | ~HA | praktis tidak larut | apatit suhu tinggi |

Memaksimalkan C1 (Eform terendah) memihak fase paling tidak larut — berlawanan dengan
resorbabilitas scaffold. Trade-off ini dinyatakan eksplisit; scaffold resorbabel menyarankan
b-TCP atau bifasik HA/b-TCP. Data kelarutan hanya ada untuk fase dikenal, sehingga tidak bisa
menjadi kriteria atas seluruh kolam (165 entri) — ini alasan jujur overlay post-hoc.

- **Sensitivitas re-ranking (ronde 6, `mcdm_resorb.py`):** 8 komposisi shortlist ber-pKsp diranking
  ulang (stabilitas + Ca/P→1.67 + resorbabilitas = −pKsp; 3 skenario bobot). β-TCP, TTCP, monetit
  naik ke 3 besar; fluorapatit (1→6), oksiapatit (2→4), HA (4→7) turun — trade-off terkuantifikasi.
  Tetap sensitivitas, bukan kriteria kolam penuh. Lihat `laporan_mcdm_resorb.md`.

## 6. Risiko, Keputusan, Keterbatasan

- **Bias sumber:** fraksi tetangga sesumber (k=5) = 0.88 -> klaster sebagian dibentuk oleh sumber data (COD eksperimental vs MP/AFLOW komputasional). Mitigasi: pemodelan hanya pada subset komputasional; split berbasis kelompok komposisi.
- **Modulus elastik:** hanya 9 entri punya K & G -> kriteria C4 DITARIK dari MCDM (imputasi median = praktis konstanta + mencampur level material/scaffold); kekakuan scaffold ditangani hilir via porositas Gibson-Ashby (70-78%). Validasi DFT definitif pada top kandidat WAJIB (input QE siap).
- **Bandgap:** tidak dapat diprediksi dari deskriptor komposisi (R2 < 0) -> imputasi dibatalkan, nilai terukur dipakai.
- **OQMD:** server tidak stabil; akuisisi berjalan dengan retry panjang; datanya melengkapi (icsd_id, energi) bila selesai.
- **Ketimpangan kelas:** klasifikasi 44/247 (15%) -> recall kelas layak 0.82.

## 7. Langkah Selanjutnya

1. [SELESAI] Integrasi OQMD (280 entri; uji transfer sesama-komposisi R2=0,833).
2. [SEBAGIAN] Validasi komputasional: pra-validasi MLFF Top-5 baru selesai (4 stabil |dV|<=0,41%, HA +4,3% -> prioritas, E 204-220 GPa, porositas 70-78%); DFT definitif di klaster dengan input QE siap.
3. [SELESAI] Analisis sensitivitas bobot: 3 skenario manual + entropi (Spearman 0,93, cek internal) + Monte Carlo 3.000 run (propagasi ketidakpastian bobot & prediksi).
4. Penyusunan artikel — draft manuskrip IMRaD + PDF siap (data/reports/manuscript/).
5. Platform AI-Assisted Biomaterial Discovery (roadmap AMREC).
6. [SELESAI] Baseline pembanding ronde 6 (Magpie, MACE-MP-0, re-ranking pKsp) — terintegrasi ke manuskrip (`patch_manuskrip_ronde6.py`), laporan, dan dokumen panduan.
