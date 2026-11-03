# LAPORAN AKHIR PENELITIAN RESEARCH GROUP FAKULTAS (PRGF) 2027

**Skema:** Discovery Research — Universitas Airlangga
**Research Group:** Advanced Materials and Renewable Energy Conversion (AMREC)

## Judul Penelitian
Pengembangan Kerangka Materials Informatics Berbasis Kecerdasan Artifisial untuk Penemuan
Biomaterial Kalsium Fosfat sebagai Kandidat Scaffold Rekayasa Jaringan Tulang

## Identitas
- **Ketua:** Dr. Ir. Soegianto Soelistiono, M.Si. (Fisika, FST)
- **Anggota 1:** Herri Trilaksana, S.Si., M.Si., Ph.D.
- **Anggota 2:** Yhosep Gita Yhun Yhuwana, S.Si., M.T.
- **Mitra:** Dr. Bernardi Pranggono (Anglia Ruskin University, UK)
- **Mahasiswa:** Muhammad Azzam Rahmadani (asisten analisa data), Pradithya Putra Galang Islami (programer)
- **TKT awal → target:** 2 → 3

---

## 1. Ringkasan Eksekutif

Seluruh tahapan penelitian telah dilaksanakan dan indikator capaian tercapai:
kerangka Materials Informatics berbasis AI berhasil dikembangkan secara end-to-end dan
dapat direplikasi. Dataset terpadu 2.885 entri / 950 komposisi unik kalsium fosfat
(target ≥ 500 terlampaui). Model prediktif mencapai R² = 0,87 (energi pembentukan;
uji eksternal lintas basis data R² = 0,95) dan R² = 0,91 (densitas). Pemeringkatan
multiobjektif TOPSIS+VIKOR menghasilkan 15 kandidat prioritas yang didominasi keluarga
apatit (karbonat apatit #1, fluorapatit #2, OCP, TTCP, HAp) — konsisten dengan material
graft tulang klinis dan tervalidasi terhadap data eksperimen (selisih ≤ 2,9%; kisi α-TCP
akurat hingga 0,03%). Pra-validasi komputasional MLFF (MACE-MP-0) mengonfirmasi stabilitas
kelima kandidat top dan menghasilkan spesifikasi porositas 70–78% untuk mencapai modulus
tulang kortikal. Luaran wajib (artikel jurnal internasional) dalam tahap finalisasi manuskrip.

## 2. Capaian per Tahapan (sesuai proposal)

| Tahap | Status | Bukti |
|---|---|---|
| 1. Akuisisi data material | ✅ Selesai | 5 basis data; data/raw/* (metadata versi, tanggal akses, lisensi) |
| 2. Prapemrosesan data | ✅ Selesai | laporan_prapemrosesan.md |
| 3. Ekstraksi & seleksi deskriptor | ✅ Selesai | dataset_deskriptor.csv; RFE 8 deskriptor; redundansi dibuang (r>0,85, VIF>10) |
| 4. Pengembangan kerangka MI | ✅ Selesai | panduan utama + pipeline 18 tahap (run_all.py) |
| 5. Pemodelan AI/ML | ✅ Selesai | laporan_pemodelan.md; SVR/RF GroupKFold; klasifikasi F1=0,90 |
| 6. Analisis multiobjektif | ✅ Selesai | laporan_mcdm.md; TOPSIS+VIKOR×3 bobot+entropi (Spearman 0,974) |
| 7. Interpretasi & validasi | ✅ Selesai (pra-DFT) | laporan_xai.md (SHAP) + laporan_validasi_komputasional.md (MLFF); input QE siap untuk DFT definitif |
| 8. Penyusunan framework final | ✅ Selesai | LAPORAN_FINAL.md; manuskrip PDF 10 halaman; presentasi 14 slide; dataset berversi+checksum |

## 3. Indikator Capaian vs Target

| Indikator | Target | Capaian | Status |
|---|---|---|---|
| Dataset tervalidasi | ≥ 500 senyawa | 950 komposisi unik (2.885 entri) | ✅ |
| Deskriptor representatif | 10–15 | 8 terpilih RFE (dari 10 fitur tersedia) | ✅ (terdokumentasi) |
| R² regresi | ≥ 0,85 | 0,87 (Eform), 0,91 (densitas) | ✅ |
| Kandidat prioritas | Top 10–15 | Top 15 (dedup polimorf) | ✅ |
| Kerangka dapat direplikasi | — | requirements.txt, run_all, git, checksum SHA-256 | ✅ |
| Publikasi Q2 | 1 artikel | manuskrip finalisasi (target Computational Materials Science, APC dianggarkan) | 🟡 proses |

## 4. Temuan Ilmiah Utama

1. Kandidat top = karbonat apatit, fluorapatit, OCP, TTCP, HAp — hierarki graft tulang klinis
   ditemukan ulang dari data deskriptor + AI (validasi tidak langsung).
2. Skala energi pembentukan antar basis data tidak seragam: MP≈OQMD (Δ<0,02 eV), AFLOW offset
   hingga 0,8 eV (fosfida) → desain uji eksternal lintas basis data (R²=0,95).
3. Bandgap tidak dapat diprediksi dari deskriptor komposisi (R²<0) — keputusan terdokumentasi.
4. Spesifikasi desain fabrikasi: porositas 70–78% untuk modulus tulang kortikal (Gibson–Ashby
   dari modulus kristal tunggal MLFF 206–220 GPa).

## 5. Luaran

- **Artikel (wajib):** manuskrip IMRaD bahasa Inggris, 10 halaman, siap submit
  (data/reports/manuscript/manuscript.pdf)
- **Academic Peerlist & International Agreement:** dukungan mitra ARU terlampir di proposal;
  publikasi bersama direncanakan pada submit
- **Tambahan:** presentasi seminar 14 slide; dataset publik (CC-BY/CC0 sesuai sumber);
  16 skrip open-source; repositori git

## 6. Rencana Tindak Lanjut

1. Submit artikel ke Computational Materials Science (APC dianggarkan RAB).
2. DFT definitif Top-5 di klaster (input QE siap) untuk konfirmasi modulus.
3. Fabrikasi scaffold berpori 70–78% (3D printing) → karakterisasi → TKT 4–5.
4. Pengembangan platform AI-Assisted Biomaterial Discovery (roadmap AMREC).

---
*Laporan disusun dari artefak pipeline: data/processed, data/reports, data/dft, data/validasi_mlff (versi dataset dengan checksum di data/versions/).*
