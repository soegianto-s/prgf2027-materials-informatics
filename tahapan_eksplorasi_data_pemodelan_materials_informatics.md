# Panduan Tahapan Eksplorasi Data dan Pemodelan *Materials Informatics*
**Topik Riset:** Penemuan Biomaterial Kalsium Fosfat untuk Scaffold Rekayasa Jaringan Tulang  
**Pendekatan:** *Data-Driven Material Discovery* & *Artificial Intelligence*

---

## 1. Akuisisi & Integrasi Data Material (*Data Mining*)

Tujuan utama dari tahapan ini adalah mengumpulkan data komprehensif terkait senyawa berbasis kalsium fosfat dari berbagai basis data terbuka (*open-access material databases*).

### 1.1 Sumber Basis Data
* **Materials Project:** Parameter struktur kristal, energi pembentukan (*formation energy*), bandgap, dan sifat elastisitas.
* **AFLOW (Automatic FLOW for Materials Discovery):** Parameter termodinamika dan sifat elektronik komputasional.
* **OQMD (Open Quantum Materials Database):** Stabilitas fase dan energi kristalografi ab-initio.
* **PubChem / Crystallography Open Database (COD):** Karakteristik kimia, formula molekul, dan data eksperimen pendukung.

### 1.2 Target Variabel & Senyawa
* **Cakupan Senyawa:** Senyawa berbasis Ca-P (misal: Hydroxyapatite, $\beta$-TCP, $\alpha$-TCP, DCPD, OCP, BCP, dan derivat terkation/teranion substituted).
* **Ukuran Dataset Target:** Minimal $\ge 500$ formulasi/struktur senyawa tervalidasi.

---

## 2. Prapemrosesan Data & Validasi Kualitas (*Data Preprocessing*)

Menjamin kebersihan dan konsistensi data sebelum dilakukan analisis fitur lanjutan (*Garbage In, Garbage Out prevention*).

### 2.1 Penanganan Missing Values & Outliers
* **Missing Value Imputation:** Pengisian data hilang menggunakan *K-Nearest Neighbors (KNN) Imputer* atau *Iterative Imputer* untuk parameter continuous jika nilai yang hilang $< 5\%$.
* **Outlier Detection:** Deteksi nilai ekstrem tak wajar menggunakan *Isolation Forest* atau *Z-Score* berdasar batas fisikokimia yang realistis.

### 2.2 Standardisasi & Normalisasi
* **Standardisasi Satuan:** Konversi seluruh parameter ke dalam satuan SI konstan (misal: GPa untuk Modulus Young, $\text{g/cm}^3$ untuk densitas, $\text{eV/atom}$ untuk energi pembentukan).
* **Feature Scaling:** Aplikasi *Min-Max Scaling* atau *RobustScaler* untuk menyelaraskan rentang skala antar atribut numerik.

---

## 3. Ekstraksi & Seleksi Deskriptor Material (*Feature Engineering*)

Mengubah data mentah menjadi deskriptor fisikokimia, struktural, dan termodinamika yang relevan secara biologis maupun mekanis untuk aplikasi *Bone Tissue Engineering*.

### 3.1 Kategori Deskriptor Utama
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

### 3.2 Seleksi Fitur & Penanganan Multikolinearitas
* **Correlation Matrix Analysis:** Eliminasi atribut dengan nilai korelasi Pearson/Spearman mendominasi ($r > 0.85$) untuk mencegah redundansi.
* **Feature Importance Ranking:** Penggunaan *Random Forest Feature Importance* dan *Recursive Feature Elimination (RFE)* untuk memilih 10–15 deskriptor paling berpengaruh.

---

## 4. Eksplorasi Ruang Desain Material (*Exploratory Data Analysis & Clustering*)

Memetakan dan memahami distribusi material dalam *materials design space*.

### 4.1 Pemetaan Ruang Sifat Material
* **Dimensionality Reduction:** Pemetaan ruang deskriptor tinggi ke 2D/3D menggunakan *Principal Component Analysis (PCA)* dan *t-Distributed Stochastic Neighbor Embedding (t-SNE)*.
* **Pattern & Cluster Discovery:** Penerapan algoritma *Unsupervised Learning* (seperti *K-Means Clustering* atau *Hierarchical Density-Based Spatial Clustering of Applications with Noise / HDBSCAN*) untuk mengelompokkan material berdasarkan kemiripan sifat fisikokimia.

---

## 5. Pemodelan Machine Learning & Evaluasi Prediktif

Membangun model kecerdasan artifisial untuk memprediksi sifat-sifat material target yang sulit diukur secara eksperimen.

### 5.1 Algoritma ML Terpilih
* **Regression Models:** *Random Forest Regressor*, *XGBoost*, *Gradient Boosting*, dan *Support Vector Regression (SVR)* untuk memprediksi Modulus Young, stabilitas termodinamika, dan densitas.
* **Classification Models:** *Logistic Regression* / *Random Forest Classifier* untuk mengklasifikasikan kandidat material (misal: "Stabil/Tinggi Kesesuaian" vs "Tidak Stabil/Rendah Kesesuaian").

### 5.2 Evaluasi Performa Model
* **Validasi Silang:** *10-Fold Cross-Validation* dan *Stratified K-Fold*.
* **Metrik Evaluasi Regresi:** 
  * Koefisien Determinasi ($R^2 \ge 0.85$)
  * Root Mean Square Error (RMSE)
  * Mean Absolute Error (MAE)

---

## 6. Analisis Multiobjektif & Pemeringkatan Kandidat (*MCDM*)

Menggabungkan berbagai kriteria sifat material yang saling bertolak belakang (*conflicting properties*) untuk menemukan kandidat scaffold ideal.

### 6.1 Formulasi Kriteria Target Scaffold Tulang
* Modulus Elastisitas ($E$): Mendekati tulang kortikal (10–20 GPa) atau tulang trabekular (0.1–2 GPa).
* Stabilitas Termodinamika: $E_{\text{hull}} \to 0\text{ eV/atom}$ (menandakan fase stabil).
* Rasio $\text{Ca/P}$: Berada pada rentang ideal biokompatibilitas ($1.5 - 2.0$).

### 6.2 Metode Decision Making
* **TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution):** Menghitung jarak relatif kandidat material terhadap solusi ideal positif dan ideal negatif.
* **VIKOR:** Menentukan skor kompromi terbaik dari alternatif kandidat biomaterial.
* **Hasil Tahapan:** Terbentuknya daftar **Top 10–15 Kandidat Prioritas** biomaterial kalsium fosfat.

---

## 7. Interpretasi Model & Validasi Komputasional

Menjelaskan alasan di balik rekomendasi model AI (*Explainable AI*) serta melakukan verifikasi komputasional tingkat lanjut.

### 7.1 Interpretabilitas Model (XAI)
* **SHAP (SHapley Additive exPlanations):** Menganalisis kontribusi positif/negatif masing-masing deskriptor terhadap skor kelayakan material.
* **Feature Dependence Plots:** Memahami interaksi antar-deskriptor kritis (misal: pengaruh rasio $\text{Ca/P}$ terhadap Modulus Young teoritis).

### 7.2 Validasi Komputasional
* **Density Functional Theory (DFT) / Molecular Dynamics (MD) Simulation Check:** Lakukan simulasi tingkat atomik singkat pada top kandidat hasil screening AI untuk memverifikasi akurasi prediksi stabilitas dan elastisitas.

---

## 8. Ringkasan *Workflow* Pemrosesan Data

$$\text{Data Mining} \longrightarrow \text{Preprocessing} \longrightarrow \text{Feature Engineering} \longrightarrow \text{ML Modeling} \longrightarrow \text{Multi-Objective Selection} \longrightarrow \text{XAI Validation}$$