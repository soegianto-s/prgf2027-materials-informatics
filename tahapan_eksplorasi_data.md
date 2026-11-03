# Tahapan Eksplorasi Data
**Kerangka Materials Informatics Berbasis AI untuk Penemuan Biomaterial Kalsium Fosfat**

Periode pelaksanaan: November 2026 (menyambung tahap prapemrosesan, sebelum pemodelan AI)

---

## Tujuan Eksplorasi

1. Memahami isi, kualitas, dan sebaran dataset kalsium fosfat secara menyeluruh sebelum pemodelan.
2. Mengetahui hubungan antar deskriptor material dan menentukan deskriptor yang layak dipertahankan.
3. Memetakan ruang desain material (*materials design space*) dan pola kemiripan antar senyawa.
4. Menemukan risiko sejak dini: bias sumber data, data pencilan, ketimpangan kelas, dan potensi kebocoran data.
5. Menyiapkan dasar keputusan untuk pemilihan target prediksi dan kriteria multiobjektif.

---

## Tahap 1. Audit Dataset

**Pertanyaan kunci:** Apa saja yang ada di dalam dataset, dan seberapa lengkap?

- Hitung jumlah senyawa total dan jumlah senyawa unik (cek duplikat antar basis data, termasuk polimorf dari komposisi yang sama).
- Rekap jumlah data per sumber basis data dan per kelompok komposisi.
- Tabulasi kelengkapan setiap atribut (persentase nilai kosong per deskriptor).
- Catat versi, tanggal akses, dan lisensi tiap sumber data.
- Periksa konsistensi satuan dan rentang nilai yang masuk akal secara fisika.

**Keluaran:** tabel ringkasan dataset dan laporan kelengkapan data.
**Indikator:** jumlah data ≥ 500 senyawa; *missing value* < 5% pada deskriptor yang dipakai.

---

## Tahap 2. Profil Setiap Deskriptor (Analisis Univariat)

**Pertanyaan kunci:** Bagaimana sebaran masing-masing sifat?

- Ringkasan statistik: rata-rata, median, simpangan baku, minimum, maksimum, kuartil.
- Periksa bentuk sebaran (simetris, miring, multimodal) dan kebutuhan transformasi.
- Kelompokkan deskriptor berdasarkan jenis: komposisi, struktur kristal, termodinamika, mekanik, elektronik, densitas.
- Tandai deskriptor dengan variasi sangat kecil (hampir konstan) karena kurang informatif.

**Keluaran:** profil statistik per deskriptor dan daftar deskriptor yang perlu transformasi atau disisihkan.

---

## Tahap 3. Deteksi dan Evaluasi Pencilan

**Pertanyaan kunci:** Mana nilai yang ekstrem, dan apakah itu kesalahan atau fenomena nyata?

- Identifikasi pencilan dengan aturan statistik (rentang antarkuartil, skor-z) dan pemeriksaan visual.
- Telusuri setiap pencilan ke asal datanya: kesalahan input, struktur tidak stabil, atau fase yang memang berbeda.
- Jangan menghapus otomatis. Putuskan per kasus dan catat alasannya.
- Pertahankan senyawa yang secara fisika valid meskipun nilainya ekstrem.

**Keluaran:** daftar pencilan beserta keputusan (dipertahankan, dikoreksi, atau dikeluarkan) dan alasannya.

---

## Tahap 4. Hubungan Antar Deskriptor (Analisis Bivariat)

**Pertanyaan kunci:** Deskriptor mana yang saling berkaitan?

- Hitung matriks korelasi (linear dan berbasis peringkat untuk hubungan non-linear).
- Amati pola hubungan antar pasangan sifat, misalnya densitas terhadap modulus, atau stabilitas terhadap komposisi.
- Telusuri deskriptor yang berkorelasi sangat tinggi (redundan) dan tentukan satu wakil.
- Periksa multikolinearitas dengan faktor inflasi varians (VIF).

**Keluaran:** peta korelasi, daftar pasangan deskriptor redundan, dan usulan himpunan deskriptor awal.
**Indikator:** validasi korelasi dan multikolinearitas terdokumentasi.

---

## Tahap 5. Eksplorasi Menurut Kelompok Material

**Pertanyaan kunci:** Apakah pola berbeda antar keluarga senyawa?

- Kelompokkan senyawa berdasarkan rasio Ca/P, ada tidaknya gugus hidroksil, dan keberadaan unsur dopan.
- Bandingkan sebaran sifat antar kelompok (misalnya apatit, trikalsium fosfat, tetrakalsium fosfat, brushit/monetit, dan fase terdoping).
- Periksa jumlah data per kelompok untuk mengetahui kelompok yang terlalu sedikit sampelnya.
- Catat kelompok yang mendominasi dataset karena berpotensi membiaskan model.

**Keluaran:** perbandingan sifat antar kelompok dan catatan ketimpangan data.

---

## Tahap 6. Pemeriksaan Material Rujukan (Kontrol Positif)

**Pertanyaan kunci:** Apakah material yang sudah dikenal sebagai bahan tulang tampak wajar dalam data?

- Tandai hidroksiapatit, β-TCP, dan α-TCP sebagai titik rujukan.
- Periksa posisi dan nilai sifat ketiganya terhadap keseluruhan dataset.
- Bandingkan dengan nilai dari literatur eksperimen. Selisih besar menandakan masalah pada data atau metode perhitungan sumbernya.
- Gunakan titik rujukan ini sebagai patokan saat menafsirkan peta ruang desain.

**Keluaran:** tabel perbandingan material rujukan dan catatan kewajaran data.

---

## Tahap 7. Pemetaan Ruang Desain Material

**Pertanyaan kunci:** Bagaimana senyawa tersebar dan mengelompok secara alami?

- Lakukan reduksi dimensi (PCA, lalu metode non-linear seperti t-SNE atau UMAP sebagai pembanding) untuk memvisualisasikan sebaran.
- Lakukan klastering (misalnya k-means, hierarkis, dan berbasis kepadatan) dan tentukan jumlah klaster dengan ukuran kualitas yang jelas.
- Warnai peta menurut sifat penting, kelompok material, dan sumber data untuk melihat apa yang membentuk pola.
- Uji kestabilan klaster dengan variasi pengaturan dan pengambilan ulang sampel.
- Identifikasi wilayah yang padat, wilayah yang jarang, dan senyawa yang terisolasi.

**Keluaran:** peta ruang desain, profil tiap klaster, dan daftar wilayah yang belum terwakili.
**Indikator:** klaster material terbentuk berdasarkan kemiripan sifat dan stabil terhadap variasi pengaturan.

---

## Tahap 8. Pemeriksaan Bias Sumber dan Potensi Kebocoran Data

**Pertanyaan kunci:** Apakah pola yang tampak nyata, atau hanya artefak data?

- Bandingkan sebaran sifat antar basis data untuk komposisi yang sama. Perbedaan sistematis menandakan perbedaan metode perhitungan.
- Periksa apakah klaster terbentuk karena sumber data, bukan karena sifat material.
- Identifikasi senyawa yang sangat mirip (polimorf atau komposisi serupa). Kelompok ini harus berada pada sisi yang sama saat data dibagi untuk pelatihan dan pengujian.
- Rancang skema pembagian data berbasis kelompok komposisi untuk tahap pemodelan.

**Keluaran:** laporan bias sumber, daftar kelompok senyawa mirip, dan rancangan skema pembagian data.

---

## Tahap 9. Eksplorasi Awal Target dan Kriteria Multiobjektif

**Pertanyaan kunci:** Apa yang layak diprediksi, dan bagaimana kandidat akan dinilai?

- Tetapkan sifat yang tersedia langsung di data sebagai target utama (stabilitas termodinamika, modulus elastik, densitas, sifat elektronik).
- Tentukan proksi bioaktivitas dari literatur (misalnya rasio Ca/P dan kemiripan struktur dengan fase rujukan) dan tulis secara eksplisit bahwa ini proksi.
- Telusuri apakah kriteria yang dipilih saling bertentangan (*trade-off*) dengan memeriksa sebaran dan hubungan antar kriteria.
- Susun rentang bobot awal untuk kriteria sebagai bahan analisis sensitivitas di tahap berikutnya.

**Keluaran:** keputusan target prediksi, daftar kriteria penilaian, dan rentang bobot awal.

---

## Tahap 10. Sintesis dan Dokumentasi Hasil Eksplorasi

- Susun ringkasan temuan utama: kualitas data, deskriptor terpilih, pola ruang desain, dan risiko yang ditemukan.
- Catat semua keputusan analisis beserta alasannya (apa yang dibuang, ditransformasi, atau dipertahankan).
- Simpan versi dataset hasil eksplorasi dengan penamaan yang jelas agar tahap pemodelan memakai data yang sama.
- Rumuskan hipotesis yang akan diuji pada tahap pemodelan dan analisis multiobjektif.

**Keluaran:** laporan eksplorasi, dataset versi final untuk pemodelan, dan daftar hipotesis.

---

## Alur Ringkas

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

---

## Daftar Periksa Penyelesaian

- [ ] Ringkasan dataset dan laporan kelengkapan data selesai
- [ ] Profil statistik semua deskriptor selesai
- [ ] Pencilan ditelusuri dan keputusannya tercatat
- [ ] Matriks korelasi dan hasil VIF selesai
- [ ] Perbandingan antar kelompok material selesai
- [ ] Posisi material rujukan (HAp, β-TCP, α-TCP) diperiksa
- [ ] Peta ruang desain dan profil klaster selesai
- [ ] Bias sumber data dan kelompok senyawa mirip diperiksa
- [ ] Target prediksi dan kriteria multiobjektif ditetapkan
- [ ] Laporan eksplorasi dan dataset versi final tersimpan

---

## Kaitan dengan Proposal

| Elemen proposal | Tahap eksplorasi terkait |
|---|---|
| Tahap 2: Prapemrosesan data | Tahap 1, 3 |
| Tahap 3: Ekstraksi dan seleksi deskriptor | Tahap 2, 4 |
| Tahap 4: Pengembangan kerangka Materials Informatics | Tahap 5, 6, 7 |
| Tahap 5: Pemodelan kecerdasan artifisial | Tahap 8, 9 |
| Tahap 6: Analisis multiobjektif | Tahap 9 |
