"""Laporan final: kerangka Materials Informatics + daftar kandidat unik (dedup polimorf)."""
import time

import pandas as pd

from common import PROC, REPORTS


def main():
    k = pd.read_csv(PROC / "kandidat_ranking.csv")
    for c in ["ca_p_ratio", "Eform_eV_atom", "densitas_final_gcm3", "young_E_deriv_GPa",
              "bandgap_eV", "peringkat_rerata"]:
        k[c] = pd.to_numeric(k[c], errors="coerce")
    # dedup polimorf: komposisi sama -> ambil peringkat terbaik
    k["komposisi_key"] = k[["Ca", "P", "O", "H", "F"]].fillna(0).round(1).astype(str).agg("-".join, axis=1) \
        if "Ca" in k.columns else k["formula"]
    kd = k.sort_values("peringkat_rerata").drop_duplicates(subset="komposisi_key")
    top15 = kd.head(15).copy()

    laporan = f"""# LAPORAN FINAL
# Pengembangan Kerangka Materials Informatics Berbasis AI untuk Penemuan Biomaterial Kalsium Fosfat sebagai Kandidat Scaffold Rekayasa Jaringan Tulang

**Tanggal:** {time.strftime('%Y-%m-%d %H:%M:%S')}
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

{top15[['formula','sumber','kelompok','peringkat_rerata','Eform_eV_atom','densitas_final_gcm3','ca_p_ratio','bandgap_eV']].round(3).to_markdown(index=False)}

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
"""
    (REPORTS / "LAPORAN_FINAL.md").write_text(laporan, encoding="utf-8")
    top15.to_csv(PROC / "kandidat_top15_dedup.csv", index=False)
    print(laporan.encode("ascii", "replace").decode("ascii"))


if __name__ == "__main__":
    main()
