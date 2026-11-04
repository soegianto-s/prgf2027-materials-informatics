# Kerangka Materials Informatics Berbasis AI — Biomaterial Kalsium Fosfat untuk Scaffold Rekayasa Jaringan Tulang

**PRGF Discovery Research 2027 · Research Group AMREC · Universitas Airlangga**
Periode: Agustus 2026 – Juli 2027 · Versi paket: 1.0 (2026-11-04)

## Ringkasan

Pipeline end-to-end untuk penemuan biomaterial kalsium fosfat:

`Akuisisi data (5 basis data) → Prapemrosesan → Deskriptor fisikokimia → EDA/Klaster → Pemodelan ML (anti-leakage) → MCDM (TOPSIS+VIKOR) → Interpretasi SHAP`

- Dataset terpadu: **2.885 entri / 950 komposisi unik** (target proposal: ≥500)
- Model (protokol anti-kebocoran v2: grouping formula tereduksi + nested CV + 4 DOF komposisi murni — Ca/P, fraksi P, H, F): SVR Eform R² = 0,11 discovery (n=337 MP+OQMD) / −0,52 dalam-fosfat / 0,40 varian screening (benchmark eksperimen MAE 0,094 eV/atom); densitas komposisi-murni R² = 0,02 (benchmark MAE 0,114 g/cm³); transfer antar basis data sesama-komposisi R² = 0,83
- **Top kandidat:** fluorapatit, karbonat apatit, β-TCP, hidroksiapatit, TTCP (+monetit, OCP) — kriteria eksplisit dari kebutuhan desain; klaim 'penemuan ulang' tidak dipakai

## Struktur Folder

```
prgf2027/
├── scripts/            # skrip pipeline (urutan wajib di bawah) + skrip penunjang
├── data/
│   ├── raw/            # data mentah per sumber (JSON/CSV + _metadata.json)
│   ├── processed/      # dataset terpadu, deskriptor, ranking, kandidat
│   ├── reports/        # laporan markdown + figure PNG + manuskrip (IMRaD + elsarticle)
│   ├── versions/       # snapshot dataset final + checksum (manifest)
│   └── validasi_mlff/  # struktur terelaksasi MACE-MP-0
├── template_jurnal/    # template Elsevier elsarticle (sumber manuskrip resmi)
├── requirements.txt    # dependensi Python
├── scripts/run_all.py  # orkestrator pipeline (bisa dijalankan ulang)
├── run_all.bat         # wrapper Windows
└── panduan_utama_...md # rujukan metodologi utama
```

## Menjalankan Pipeline

### 1. Prasyarat

```bash
python -m pip install -r requirements.txt
```

Kunci Materials Project (`PMG_MAPI_KEY`) diletakkan di `~/.pmgrc.yaml` (format pymatgen)
atau env var `MP_API_KEY`. Sumber lain (AFLOW, COD, PubChem, OQMD) tanpa kunci.

### 2. Jalankan (seluruh tahap berurutan)

```bash
python scripts/run_all.py            # semua tahap
python scripts/run_all.py --from eda  # lanjut dari tahap tertentu
```

atau per skrip (urutan wajib):

| # | Skrip | Tahap (proposal) |
|---|---|---|
| 1 | `acquire_mp.py` | 1 — Akuisisi Materials Project (butuh key) |
| 2 | `acquire_aflow.py` | 1 — Akuisisi AFLOW (AFLUX REST) |
| 3 | `acquire_cod.py` | 1 — Akuisisi COD (via HTTP) |
| 4 | `acquire_pubchem.py` | 1 — Akuisisi PubChem |
| 5 | `acquire_oqmd.py` | 1 — Akuisisi OQMD (retry panjang, cache per komposisi, aman diulang) |
| 6 | `consolidate.py` | 2 — Konsolidasi + laporan audit akuisisi |
| 7 | `preprocess_descriptors.py` | 2–3 — QC, pencilan, deskriptor fisikokimia |
| 8 | `eda.py` | 4 — Korelasi, VIF, PCA, t-SNE, K-Means, bias sumber |
| 9 | `eda_lanjutan.py` | 4 — UMAP, HDBSCAN, hierarkis, validasi literatur |
| 10 | `modeling.py` | 5 — Regresi/klasifikasi ML, GroupKFold, RFE |
| 11 | `mcdm.py` | 6 — TOPSIS + VIKOR, 3 set bobot, pemeringkatan |
| 12 | `mcdm_entropi.py` | 6 — Sensitivitas: pembobotan entropi Shannon |
| 13 | `siapkan_dft.py` | 7 — Input DFT/QE (POSCAR+CIF+scf/relax) Top 5 |
| 14 | `xai.py` | 7 — SHAP + permutation importance (4 DOF komposisi) |
| 15 | `laporan_final.py` | 7–8 — Laporan final + Top 15 dedup (rank ordinal) |
| 16 | `versi_dataset.py` | — Snapshot dataset final + checksum |

Skrip penunjang (tidak berurutan): `tcp_alpha_beta.py` (validasi pemisahan α/β-TCP),
`tuning_eform.py` (tuning SVR Eform), `validasi_independen.py` (benchmark eksperimen),
`validasi_mlff.py` (pra-validasi MACE-MP-0 Top 5), `konversi_elsarticle.py` (konversi ke
format jurnal), `patch_manuskrip_ronde3*.py` (patch angka hasil review ronde 3).

## Sumber Data & Lisensi

| Sumber | Akses | Lisensi |
|---|---|---|
| Materials Project (api.materialsproject.org) | API key | CC-BY 4.0 |
| AFLOW (aflow.org/API/aflux) | tanpa key | sitasi Curtarolo et al. |
| COD (crystallography.net) | HTTP tanpa key | CC0 |
| PubChem PUG REST | tanpa key | public domain (NCBI) |
| OQMD (oqmd.org/oqmdapi) | tanpa key (server flaky) | sitasi Kirklin et al. |

## Keputusan Metodologis Penting (log)

1. **Anti-kebocoran (v2):** grouping formula TEREDUKSI (gcd) — polimorf & kelipatan formula satu fold; nested CV untuk SVR; fitur komposisi MURNI = 4 DOF (Ca/P, fraksi P, H, F — EN_avg & berat molekul adalah fungsi linear eksak fraksi unsur, VIF tak hingga, dibuang); volume/densitas hanya varian screening berlabel; classifier suitability ditarik (semi-deterministik) & tidak dipakai di MCDM. Temuan ronde 3: komposisi murni TIDAK punya daya prediksi dalam-keluarga fosfat (R² < 0) — argumen kuat untuk surrogate sadar-struktur; Eform dilatih pada MP+OQMD saja (n=337, AFLOW dikecualikan karena beda skala energi).
2. **Bandgap:** tidak dapat diprediksi dari deskriptor komposisi (R²<0) — imputasi dibatalkan, nilai terukur dipakai.
3. **Modulus elastik:** hanya 9 entri punya K&G — kriteria MCDM memakai imputasi median; validasi DFT/MD top kandidat adalah langkah wajib berikutnya.
4. **Pencilan:** dipertahankan bila fisika-valid, keputusan tercatat per kasus.

## Kontak

Dr. Ir. Soegianto Soelistiono, M.Si. — soegianto@fst.unair.ac.id
