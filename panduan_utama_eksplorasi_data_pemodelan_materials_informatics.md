# Panduan Utama: Eksplorasi Data dan Pemodelan *Materials Informatics*
**Topik Riset:** Penemuan Biomaterial Kalsium Fosfat untuk Scaffold Rekayasa Jaringan Tulang  
**Pendekatan:** *Data-Driven Material Discovery* & *Artificial Intelligence*  
**Research Group:** Advanced Materials and Renewable Energy Conversion (AMREC) — Universitas Airlangga

**Status Dokumen:** Rujukan utama — hasil penggabungan dua dokumen:
- `tahapan_eksplorasi_data_pemodelan_materials_informatics.md` (panduan pipeline 8 tahap)
- `tahapan_eksplorasi_data.md` (rencana operasional eksplorasi data, November 2026)

**Versi:** 1.0 — 4 November 2026

---

## 1. Ringkasan, Alur Utama, dan Fase Pelaksanaan

### 1.1 Ringkasan Riset

Kerusakan jaringan tulang akibat trauma, penyakit degeneratif, maupun kelainan kongenital masih menjadi tantangan bidang kesehatan. Biomaterial berbasis kalsium fosfat adalah kandidat scaffold yang menjanjikan karena biokompatibel, bioaktif, dan osteokonduktif, namun penemuan material baru melalui pendekatan eksperimen konvensional memerlukan waktu dan biaya yang besar. Dokumen ini menjadi panduan utama pelaksanaan kerangka *Materials Informatics* berbasis kecerdasan artifisial — dari akuisisi data hingga interpretasi hasil — untuk mempercepat penemuan kandidat biomaterial kalsium fosfat sebagai scaffold rekayasa jaringan tulang.

### 1.2 Alur Utama Pipeline (8 Tahap)

$$\text{Data Mining} \longrightarrow \text{Preprocessing} \longrightarrow \text{Feature Engineering} \longrightarrow \text{ML Modeling} \longrightarrow \text{Multi-Objective Selection} \longrightarrow \text{XAI Validation}$$

| Bagian | Tahap Pipeline | Periode (jadwal proposal) |
|---|---|---|
| 2 | Tahap 1: Akuisisi & integrasi data material | 15-08-2026 s.d. 30-09-2026 |
| 3 | Tahap 2: Prapemrosesan & validasi kualitas | 01-09-2026 s.d. 30-10-2026 |
| 4 | Tahap 3: Ekstraksi & seleksi deskriptor | 01-10-2026 s.d. 30-11-2026 |
| 5 | Tahap 4: Eksplorasi ruang desain material (kerangka MI) | 01-11-2026 s.d. 31-01-2027 |
| 6 | Sintesis eksplorasi & *hand-off* ke pemodelan | akhir November 2026 |
| 7 | Tahap 5: Pemodelan *Machine Learning* & evaluasi | 01-12-2026 s.d. 28-02-2027 |
| 8 | Tahap 6: Analisis multiobjektif & pemeringkatan (MCDM) | 01-02-2027 s.d. 31-03-2027 |
| 9 | Tahap 7: Interpretasi model (XAI) & validasi komputasional | 01-02-2027 s.d. 31-03-2027 |

### 1.3 Fokus Fase Eksplorasi (November 2026)

Fase eksplorasi berjalan pada November 2026, **menyambung tahap prapemrosesan dan sebelum pemodelan AI**. Detail operasionalnya tertanam pada Bagian 3–6 dokumen ini. Tujuannya:

1. Memahami isi, kualitas, dan sebaran dataset kalsium fosfat secara menyeluruh sebelum pemodelan.
2. Mengetahui hubungan antar deskriptor material dan menentukan deskriptor yang layak dipertahankan.
3. Memetakan ruang desain material (*materials design space*) dan pola kemiripan antar senyawa.
4. Menemukan risiko sejak dini: bias sumber data, data pencilan, ketimpangan kelas, dan potensi kebocoran data.
5. Menyiapkan dasar keputusan untuk pemilihan target prediksi dan kriteria multiobjektif.

### 1.4 Alur Fase Eksplorasi (10 Tahap)

```
Audit dataset
   ↓
Profil deskriptor  →  Deteksi pencilan
   ↓
Hubungan antar deskriptor (korelasi, multikolinearitas)
   ↓
Eksplorasi per kelompok material  →  Pemeriksaan material rujukan
   ↓
Pemetaan ruang desain (reduksi dimensi + klaster)
   ↓
Pemeriksaan bias sumber dan kebocoran data
   ↓
Penetapan target dan kriteria multiobjektif
   ↓
Sintesis dan dokumentasi  →  masuk ke tahap pemodelan AI
```

### 1.5 Peta Dokumen

| Bagian | Isi |
|---|---|
| 1 | Ringkasan, alur utama, fase pelaksanaan |
| 2 | Tahap 1: Akuisisi & integrasi data material |
| 3 | Tahap 2: Prapemrosesan & validasi kualitas *(eksplorasi tahap 1 & 3)* |
| 4 | Tahap 3: Ekstraksi & seleksi deskriptor *(eksplorasi tahap 2 & 4)* |
| 5 | Tahap 4: Eksplorasi ruang desain material *(eksplorasi tahap 5–8)* |
| 6 | Sintesis eksplorasi & *hand-off* ke pemodelan *(eksplorasi tahap 10)* |
| 7 | Tahap 5: Pemodelan *Machine Learning* & evaluasi *(eksplorasi tahap 8 & 9)* |
| 8 | Tahap 6: Analisis multiobjektif & pemeringkatan kandidat *(eksplorasi tahap 9)* |
| 9 | Tahap 7: Interpretasi model & validasi komputasional |
| 10 | Daftar periksa penyelesaian |
| 11 | Keterkaitan dengan proposal, jadwal, dan tim |

---

## 2. Tahap 1: Akuisisi & Integrasi Data Material (*Data Mining*)

Tujuan utama tahap ini adalah mengumpulkan data komprehensif terkait senyawa berbasis kalsium fosfat dari berbagai basis data terbuka (*open-access material databases*).

### 2.1 Sumber Basis Data

* **Materials Project:** Parameter struktur kristal, energi pembentukan (*formation energy*), bandgap, dan sifat elastisitas.
* **AFLOW (Automatic FLOW for Materials Discovery):** Parameter termodinamika dan sifat elektronik komputasional.
* **OQMD (Open Quantum Materials Database):** Stabilitas fase dan energi kristalografi ab-initio.
* **PubChem / Crystallography Open Database (COD):** Karakteristik kimia, formula molekul, dan data eksperimen pendukung.

Catat versi, tanggal akses, dan lisensi tiap sumber data (dipakai pada audit dataset, Bagian 3.1).

### 2.2 Target Variabel & Senyawa

* **Cakupan Senyawa:** Senyawa berbasis Ca-P (misal: Hydroxyapatite, $\beta$-TCP, $\alpha$-TCP, DCPD, OCP, BCP, dan derivat terkation/teranion *substituted*).
* **Ukuran Dataset Target:** Minimal $\ge 500$ formulasi/struktur senyawa tervalidasi.

---

## 3. Tahap 2: Prapemrosesan Data & Validasi Kualitas (*Data Preprocessing*)

Menjamin kebersihan dan konsistensi data sebelum analisis fitur lanjutan (*Garbage In, Garbage Out prevention*).

### 3.1 Audit Dataset *(Eksplorasi Tahap 1)*

**Pertanyaan kunci:** Apa saja yang ada di dalam dataset, dan seberapa lengkap?

* Hitung jumlah senyawa total dan jumlah senyawa unik (cek duplikat antar basis data, termasuk polimorf dari komposisi yang sama).
* Rekap jumlah data per sumber basis data dan per kelompok komposisi.
* Tabulasi kelengkapan setiap atribut (persentase nilai kosong per deskriptor).
* Periksa konsistensi satuan dan rentang nilai yang masuk akal secara fisika.

**Keluaran:** tabel ringkasan dataset dan laporan kelengkapan data.
**Indikator:** jumlah data ≥ 500 senyawa; *missing value* < 5% pada deskriptor yang dipakai.

### 3.2 Penanganan *Missing Values*

* **Missing Value Imputation:** Pengisian data hilang menggunakan *K-Nearest Neighbors (KNN) Imputer* atau *Iterative Imputer* untuk parameter kontinu jika nilai yang hilang $< 5\%$.
* **Jika missing $\ge 5\%$** pada suatu deskriptor: ambil keputusan eksplisit (transformasi, pengisian dengan metode lain, atau penyisihan deskriptor) dan **catat alasannya** pada log keputusan (Bagian 6) — jangan biarkan keputusan implisit.

### 3.3 Deteksi & Evaluasi Pencilan *(Eksplorasi Tahap 3)*

**Pertanyaan kunci:** Mana nilai yang ekstrem, dan apakah itu kesalahan atau fenomena nyata?

* Identifikasi pencilan dengan aturan statistik (rentang antarkuartil, skor-z) dan pemeriksaan visual; gunakan *Isolation Forest* sebagai **pemeriksa silang** untuk hasil aturan statistik.
* Telusuri setiap pencilan ke asal datanya: kesalahan input, struktur tidak stabil, atau fase yang memang berbeda.
* **Jangan menghapus otomatis.** Putuskan per kasus dan catat alasannya.
* Pertahankan senyawa yang secara fisika valid meskipun nilainya ekstrem.

**Keluaran:** daftar pencilan beserta keputusan (dipertahankan, dikoreksi, atau dikeluarkan) dan alasannya.

### 3.4 Standardisasi & Normalisasi

* **Standardisasi Satuan:** Konversi seluruh parameter ke dalam satuan SI konstan (misal: GPa untuk Modulus Young, $\text{g/cm}^3$ untuk densitas, $\text{eV/atom}$ untuk energi pembentukan).
* **Feature Scaling:** Aplikasi *Min-Max Scaling* atau *RobustScaler* untuk menyelaraskan rentang skala antar atribut numerik.

---

## 4. Tahap 3: Ekstraksi & Seleksi Deskriptor Material (*Feature Engineering*)

Mengubah data mentah menjadi deskriptor fisikokimia, struktural, dan termodinamika yang relevan secara biologis maupun mekanis untuk aplikasi *Bone Tissue Engineering*.

### 4.1 Kategori Deskriptor Utama

1. **Deskriptor Komposisi & Kimia:**
   * Rasio atomik Calcium-to-Phosphorus ($\text{Ca/P}$ ratio).
   * Elektronegativitas rata-rata dan perbedaan elektronegativitas.
   * Valence electron concentration (VEC).
   * Berat molekul dan densitas teoritis.
2. **Deskriptor Kristalografi & Struktur:**
   * Sistem kristal dan space group.
   * Volume sel satuan (*unit cell volume*).
   * Packing fraction dan koordinasi atom.
3. **Deskriptor Termodinamika & Elektronik:**
   * Energi pembentukan per atom ($\Delta E_f$).
   * Energi lambung stabilitas (*Energy above hull* / $E_{\text{hull}}$).
   * Electronic bandgap ($E_g$).
4. **Deskriptor Mekanik Teoritis:**
   * Modulus Ruah (*Bulk Modulus*, $K$).
   * Modulus Geser (*Shear Modulus*, $G$).
   * Modulus Young ($E$) dan Rasio Poisson ($\nu$).

### 4.2 Profil Setiap Deskriptor — Analisis Univariat *(Eksplorasi Tahap 2)*

**Pertanyaan kunci:** Bagaimana sebaran masing-masing sifat?

* Ringkasan statistik: rata-rata, median, simpangan baku, minimum, maksimum, kuartil.
* Periksa bentuk sebaran (simetris, miring, multimodal) dan kebutuhan transformasi.
* Kelompokkan deskriptor berdasarkan jenis: komposisi, struktur kristal, termodinamika, mekanik, elektronik, densitas.
* Tandai deskriptor dengan variasi sangat kecil (hampir konstan) karena kurang informatif.

**Keluaran:** profil statistik per deskriptor dan daftar deskriptor yang perlu transformasi atau disisihkan.

### 4.3 Hubungan Antar Deskriptor — Analisis Bivariat *(Eksplorasi Tahap 4)*

**Pertanyaan kunci:** Deskriptor mana yang saling berkaitan?

* Hitung matriks korelasi (linear **dan** berbasis peringkat untuk hubungan non-linear).
* Amati pola hubungan antar pasangan sifat, misalnya densitas terhadap modulus, atau stabilitas terhadap komposisi.
* **Correlation Matrix Analysis:** Eliminasi atribut dengan nilai korelasi Pearson/Spearman mendominasi ($r > 0.85$) untuk mencegah redundansi — tentukan satu wakil untuk tiap pasangan redundan.
* Periksa multikolinearitas dengan faktor inflasi varians (VIF).

**Keluaran:** peta korelasi, daftar pasangan deskriptor redundan, dan **usulan himpunan deskriptor awal** (kandidat masukan untuk seleksi fitur final).
**Indikator:** validasi korelasi dan multikolinearitas terdokumentasi.

### 4.4 Seleksi Fitur Final

* **Feature Importance Ranking:** Penggunaan *Random Forest Feature Importance* dan *Recursive Feature Elimination (RFE)* atas himpunan deskriptor awal (Bagian 4.3) untuk memilih **10–15 deskriptor paling berpengaruh**.

---

## 5. Tahap 4: Eksplorasi Ruang Desain Material (*Exploratory Data Analysis & Clustering*)

Memetakan dan memahami distribusi material dalam *materials design space*.

### 5.1 Eksplorasi Menurut Kelompok Material *(Eksplorasi Tahap 5)*

**Pertanyaan kunci:** Apakah pola berbeda antar keluarga senyawa?

* Kelompokkan senyawa berdasarkan rasio Ca/P, ada tidaknya gugus hidroksil, dan keberadaan unsur dopan.
* Bandingkan sebaran sifat antar kelompok (misalnya apatit, trikalsium fosfat, tetrakalsium fosfat, brushit/monetit, dan fase terdoping).
* Periksa jumlah data per kelompok untuk mengetahui kelompok yang terlalu sedikit sampelnya.
* Catat kelompok yang mendominasi dataset karena berpotensi membiaskan model.

**Keluaran:** perbandingan sifat antar kelompok dan catatan ketimpangan data.

### 5.2 Pemeriksaan Material Rujukan — Kontrol Positif *(Eksplorasi Tahap 6)*

**Pertanyaan kunci:** Apakah material yang sudah dikenal sebagai bahan tulang tampak wajar dalam data?

* Tandai hidroksiapatit, β-TCP, dan α-TCP sebagai titik rujukan.
* Periksa posisi dan nilai sifat ketiganya terhadap keseluruhan dataset.
* Bandingkan dengan nilai dari literatur eksperimen. Selisih besar menandakan masalah pada data atau metode perhitungan sumbernya.
* Gunakan titik rujukan ini sebagai patokan saat menafsirkan peta ruang desain.

**Keluaran:** tabel perbandingan material rujukan dan catatan kewajaran data.

### 5.3 Pemetaan Ruang Desain Material *(Eksplorasi Tahap 7)*

**Pertanyaan kunci:** Bagaimana senyawa tersebar dan mengelompok secara alami?

* **Dimensionality Reduction:** Pemetaan ruang deskriptor tinggi ke 2D/3D menggunakan *Principal Component Analysis (PCA)*, lalu metode non-linear seperti *t-SNE* atau *UMAP* sebagai pembanding.
* **Pattern & Cluster Discovery:** Penerapan *Unsupervised Learning* — *K-Means*, klastering hierarkis, dan berbasis kepadatan (*HDBSCAN*) — untuk mengelompokkan material berdasarkan kemiripan sifat fisikokimia; tentukan jumlah klaster dengan ukuran kualitas yang jelas.
* Warnai peta menurut sifat penting, kelompok material, dan sumber data untuk melihat apa yang membentuk pola.
* Uji kestabilan klaster dengan variasi pengaturan dan pengambilan ulang sampel.
* Identifikasi wilayah yang padat, wilayah yang jarang, dan senyawa yang terisolasi.

**Keluaran:** peta ruang desain, profil tiap klaster, dan daftar wilayah yang belum terwakili.
**Indikator:** klaster material terbentuk berdasarkan kemiripan sifat dan stabil terhadap variasi pengaturan.

### 5.4 Pemeriksaan Bias Sumber & Potensi Kebocoran Data *(Eksplorasi Tahap 8)*

**Pertanyaan kunci:** Apakah pola yang tampak nyata, atau hanya artefak data?

* Bandingkan sebaran sifat antar basis data untuk komposisi yang sama. Perbedaan sistematis menandakan perbedaan metode perhitungan.
* Periksa apakah klaster terbentuk karena sumber data, bukan karena sifat material.
* Identifikasi senyawa yang sangat mirip (polimorf atau komposisi serupa). Kelompok ini harus berada pada sisi yang sama saat data dibagi untuk pelatihan dan pengujian.
* Rancang **skema pembagian data berbasis kelompok komposisi** — rancangan ini wajib dipakai pada evaluasi model (Bagian 7.3).

**Keluaran:** laporan bias sumber, daftar kelompok senyawa mirip, dan rancangan skema pembagian data.

---

## 6. Sintesis Eksplorasi & *Hand-off* ke Pemodelan *(Eksplorasi Tahap 10)*

Gerbang penutup fase eksplorasi — selesaikan sebelum pemodelan dimulai (01-12-2026).

* Susun ringkasan temuan utama: kualitas data, deskriptor terpilih, pola ruang desain, dan risiko yang ditemukan.
* Catat semua keputusan analisis beserta alasannya (apa yang dibuang, ditransformasi, atau dipertahankan) — termasuk keputusan pencilan (Bagian 3.3) dan missing $\ge 5\%$ (Bagian 3.2).
* Simpan versi dataset hasil eksplorasi dengan penamaan yang jelas agar tahap pemodelan memakai data yang sama.
* Rumuskan hipotesis yang akan diuji pada tahap pemodelan dan analisis multiobjektif.
* Serahkan ke tahap berikutnya: dataset versi final, himpunan deskriptor final (10–15), rancangan split berbasis kelompok (Bagian 5.4), dan keputusan target & kriteria (Bagian 7.1 dan 8.1).

**Keluaran:** laporan eksplorasi, dataset versi final untuk pemodelan, dan daftar hipotesis.

---

## 7. Tahap 5: Pemodelan *Machine Learning* & Evaluasi Prediktif

Membangun model kecerdasan artifisial untuk memprediksi sifat-sifat material target yang sulit diukur secara eksperimen.

### 7.1 Penetapan Target Prediksi & Proksi Bioaktivitas *(Eksplorasi Tahap 9 — bagian target)*

* Tetapkan sifat yang tersedia langsung di data sebagai target utama: **stabilitas termodinamika, modulus elastik, densitas, sifat elektronik**.
* Tentukan proksi bioaktivitas dari literatur (misalnya rasio Ca/P dan kemiripan struktur dengan fase rujukan) dan **tulis secara eksplisit bahwa ini proksi** — bukan pengukuran bioaktivitas langsung.

### 7.2 Algoritma ML Terpilih

* **Regression Models:** *Random Forest Regressor*, *XGBoost*, *Gradient Boosting*, dan *Support Vector Regression (SVR)* untuk memprediksi Modulus Young, stabilitas termodinamika, dan densitas.
* **Classification Models:** *Logistic Regression* / *Random Forest Classifier* untuk mengklasifikasikan kandidat material (misal: "Stabil/Tinggi Kesesuaian" vs "Tidak Stabil/Rendah Kesesuaian").

### 7.3 Skema Pembagian Data & Evaluasi Performa Model

* **Skema pembagian data** mengikuti rancangan berbasis kelompok komposisi dari Bagian 5.4: senyawa yang sangat mirip (polimorf/komposisi serupa) harus berada pada sisi yang sama dalam setiap pembagian.
* **Validasi Silang:**
  * Regresi: *10-Fold Cross-Validation* **berbasis kelompok (GroupKFold)**.
  * Klasifikasi: *Stratified K-Fold*.
* **Metrik Evaluasi Regresi:**
  * Koefisien Determinasi ($R^2 \ge 0.85$)
  * Root Mean Square Error (RMSE)
  * Mean Absolute Error (MAE)

---

## 8. Tahap 6: Analisis Multiobjektif & Pemeringkatan Kandidat (*MCDM*)

Menggabungkan berbagai kriteria sifat material yang saling bertolak belakang (*conflicting properties*) untuk menemukan kandidat scaffold ideal.

### 8.1 Formulasi Kriteria Target Scaffold Tulang *(Eksplorasi Tahap 9 — bagian kriteria)*

*(FINAL, revisi ronde 4 — 2026-11-04)* Tiga kriteria level MATERIAL dengan cakupan data penuh (tanpa imputasi):
* C1 Stabilitas Termodinamika: $E_f$ makin negatif makin baik (skala absolut; offset AFLOW dicatat sebagai artefak sumber).
* C2 Densitas pita klinis $[1.0, 3.2]$ g/cm$^3$: nol penalti di dalam pita (scaffold meraih modulus tulang via POROSITAS — Gibson-Ashby — bukan dengan menyamakan densitas tulang).
* C3 Rasio $\text{Ca/P}$ mendekati 1.67 (mineral tulang).

Kriteria yang DITARIK (tercatat): Modulus Young — hanya n=9 punya K&G sehingga imputasi median = konstanta/noise, dan modulus 10–20 GPa adalah sifat SCAFFOLD (arsitektur+porositas), bukan material (ditangani di Bagian 9.2); Bandgap — tanpa fungsi elektronik pada scaffold tulang; skor kelayakan classifier — semi-deterministik (double counting C1–C3).
Filter stoikiometri: muatan formal ≠ 0 (oksidasi standar; P = +5 dalam fosfat, −3 tanpa O) dibuang; fosfida (tanpa O) di luar kelas material kalsium fosfat. Kolam akhir: 165 entri netral.
* Telusuri *trade-off* antar kriteria: stabilitas vs resorbabilitas — resorbabilitas dinilai POST-HOC dari literatur (pKsp) karena data hanya ada untuk fase dikenal, bukan kriteria atas seluruh kolam.
* Sensitivitas: 3 skenario bobot manual + entropi Shannon (cek konsistensi internal) + Monte Carlo (bobot Dirichlet + noise MAE prediksi, lihat `mcdm_montecarlo.py`).

**Keluaran:** keputusan target prediksi, daftar kriteria penilaian, dan rentang bobot awal.

### 8.2 Metode Decision Making

* **TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution):** Menghitung jarak relatif kandidat material terhadap solusi ideal positif dan ideal negatif.
* **VIKOR:** Menentukan skor kompromi terbaik dari alternatif kandidat biomaterial.
* **Hasil Tahapan:** Terbentuknya daftar **Top 10–15 Kandidat Prioritas** biomaterial kalsium fosfat.

---

## 9. Tahap 7: Interpretasi Model & Validasi Komputasional

Menjelaskan alasan di balik rekomendasi model AI (*Explainable AI*) serta melakukan verifikasi komputasional tingkat lanjut.

### 9.1 Interpretabilitas Model (XAI)

* **SHAP (SHapley Additive exPlanations):** Menganalisis kontribusi positif/negatif masing-masing deskriptor terhadap skor kelayakan material.
* **Feature Dependence Plots:** Memahami interaksi antar-deskriptor kritis (misal: pengaruh rasio $\text{Ca/P}$ terhadap Modulus Young teoritis).

### 9.2 Validasi Komputasional

* **Density Functional Theory (DFT) / Molecular Dynamics (MD) Simulation Check:** Lakukan simulasi tingkat atomik singkat pada top kandidat hasil *screening* AI untuk memverifikasi akurasi prediksi stabilitas dan elastisitas.

---

## 10. Daftar Periksa Penyelesaian

**Fase eksplorasi (November 2026):**

- [ ] Ringkasan dataset dan laporan kelengkapan data selesai (Bagian 3.1)
- [ ] Profil statistik semua deskriptor selesai (Bagian 4.2)
- [ ] Pencilan ditelusuri dan keputusannya tercatat (Bagian 3.3)
- [ ] Matriks korelasi dan hasil VIF selesai (Bagian 4.3)
- [ ] Perbandingan antar kelompok material selesai (Bagian 5.1)
- [ ] Posisi material rujukan (HAp, β-TCP, α-TCP) diperiksa (Bagian 5.2)
- [ ] Peta ruang desain dan profil klaster selesai (Bagian 5.3)
- [ ] Bias sumber data dan kelompok senyawa mirip diperiksa (Bagian 5.4)
- [ ] Target prediksi dan kriteria multiobjektif ditetapkan (Bagian 7.1, 8.1)
- [ ] Laporan eksplorasi dan dataset versi final tersimpan (Bagian 6)

**Fase pemodelan & seleksi (Desember 2026 – Maret 2027):**

- [ ] Himpunan deskriptor final 10–15 terpilih (RFE/RF importance, Bagian 4.4)
- [ ] Model regresi mencapai $R^2 \ge 0.85$ dengan CV berbasis kelompok (Bagian 7.3)
- [ ] Model klasifikasi tervalidasi dengan *Stratified K-Fold* (Bagian 7.3)
- [ ] Analisis sensitivitas bobot kriteria MCDM selesai (Bagian 8.1)
- [ ] Daftar Top 10–15 kandidat prioritas tersusun (Bagian 8.2)
- [ ] Interpretasi SHAP dan dependence plots selesai (Bagian 9.1)
- [ ] Validasi DFT/MD pada top kandidat selesai (Bagian 9.2)

---

## 11. Keterkaitan dengan Proposal, Jadwal, dan Tim

### 11.1 Kaitan Tahapan Proposal dengan Dokumen Ini

| Elemen proposal | Periode | Bagian dokumen terkait |
|---|---|---|
| Tahap 1: Akuisisi data material | 15-08 s.d. 30-09-2026 | Bagian 2 |
| Tahap 2: Prapemrosesan data | 01-09 s.d. 30-10-2026 | Bagian 3 |
| Tahap 3: Ekstraksi dan seleksi deskriptor | 01-10 s.d. 30-11-2026 | Bagian 4 |
| Tahap 4: Pengembangan kerangka Materials Informatics | 01-11-2026 s.d. 31-01-2027 | Bagian 5, 6 |
| Tahap 5: Pemodelan kecerdasan artifisial | 01-12-2026 s.d. 28-02-2027 | Bagian 7 |
| Tahap 6: Analisis multiobjektif | 01-02 s.d. 31-03-2027 | Bagian 8 |
| Tahap 7: Interpretasi hasil dan validasi komputasional | 01-02 s.d. 31-03-2027 | Bagian 9 |
| Tahap 8: Penyusunan framework Materials Informatics final | 01-03 s.d. 30-04-2027 | Bagian 6 + 9 |

> Fase eksplorasi November 2026 (Bagian 3–6) menutup tahap proposal 2–3 dan membuka tahap proposal 4–5.

### 11.2 Jadwal Pelaksanaan Penelitian

| Nama Kegiatan | Mulai | Selesai |
|---|---|---|
| Studi literatur dan penyusunan rencana penelitian | 01-08-2026 | 31-08-2026 |
| Akuisisi data biomaterial dari basis data material terbuka | 15-08-2026 | 30-09-2026 |
| Prapemrosesan dan validasi dataset biomaterial | 01-09-2026 | 30-10-2026 |
| Ekstraksi dan seleksi deskriptor material | 01-10-2026 | 30-11-2026 |
| Pengembangan framework Materials Informatics | 01-11-2026 | 31-01-2027 |
| Pengembangan dan optimasi model AI/Machine Learning | 01-12-2026 | 28-02-2027 |
| Analisis multiobjektif dan penentuan kandidat biomaterial | 01-02-2027 | 31-03-2027 |
| Interpretasi hasil dan validasi komputasional | 01-02-2027 | 31-03-2027 |
| Penyusunan framework Materials Informatics final | 01-03-2027 | 30-04-2027 |
| Penyusunan artikel ilmiah untuk jurnal internasional bereputasi | 01-04-2027 | 31-05-2027 |
| Diseminasi hasil penelitian (seminar/presentasi) | 01-05-2027 | 30-06-2027 |
| Penyusunan laporan akhir penelitian | 05-06-2027 | 31-07-2027 |

> Baris 7–8 (multiobjektif dan interpretasi) tercetak berbagi rentang tanggal pada proposal; sesuaikan bila diperlukan.

### 11.3 Pembagian Tugas Tim Peneliti

| Peran | Nama | Bidang Tugas |
|---|---|---|
| Ketua Peneliti | Dr. Ir. Soegianto Soelistiono, M.Si. | Perancangan penelitian, pengembangan kerangka Materials Informatics, analisis multiobjektif, integrasi hasil, koordinasi, penyusunan publikasi |
| Anggota 2 | Yhosep Gita Yhun Yhuwana, S.Si., M.T. | Prapemrosesan data, pengembangan & evaluasi model AI/Machine Learning, analisis prediktif biomaterial |
| Anggota 1 | Herri Trilaksana, S.Si., M.Si., Ph.D. | Analisis karakteristik material, interpretasi sifat fisikokimia dan struktur kristal, validasi ilmiah kandidat |
| Mitra | Dr. Bernardi Pranggono (Anglia Ruskin University, UK) | *Scientific advisor*: evaluasi metodologi AI/ML, validasi pendekatan komputasional, interpretasi hasil, penyusunan publikasi internasional |
| Mahasiswa | Muhammad Azzam Rahmadani | Asisten pengawal analisa data |
| Mahasiswa | Pradithya Putra Galang Islami | Programer |

---

## Catatan Penyelarasan (v1.0)

Penyatuan dua dokumen ini sekaligus menyambungkan tiga titik yang sebelumnya belum selaras:

1. **Skema pembagian data:** rancangan split berbasis kelompok komposisi (eksplorasi tahap 8, kini Bagian 5.4) kini eksplisit diwajibkan dipakai pada evaluasi model (Bagian 7.3); *Stratified K-Fold* dibatasi hanya untuk klasifikasi, regresi memakai *GroupKFold*.
2. **Deteksi pencilan:** *Isolation Forest* dan aturan statistik (IQR/z-score) disatukan sebagai metode deteksi + pemeriksa silang, dengan prinsip keputusan per kasus tanpa penghapusan otomatis (Bagian 3.3).
3. **Jumlah deskriptor final:** himpunan deskriptor awal dari analisis bivariat (Bagian 4.3) kini eksplisit dipersempit menjadi 10–15 deskriptor melalui RFE/RF importance (Bagian 4.4).
