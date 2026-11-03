# Kerangka Materials Informatics Berbasis AI — Biomaterial Kalsium Fosfat untuk Scaffold Rekayasa Jaringan Tulang

**PRGF Discovery Research 2027 · Research Group AMREC · Universitas Airlangga**
Periode: Agustus 2026 – Juli 2027 · Versi paket: 1.0 (2026-11-04)

## Ringkasan

Pipeline end-to-end untuk penemuan biomaterial kalsium fosfat:

`Akuisisi data (5 basis data) → Prapemrosesan → Deskriptor fisikokimia → EDA/Klaster → Pemodelan ML → MCDM (TOPSIS+VIKOR) → Interpretasi SHAP`

- Dataset terpadu: **2.605 entri / 903 komposisi unik** (target proposal: ≥500)
- Model: SVR energi pembentukan R² = 0,84 · Random Forest densitas R² = 0,92 · klasifikasi kelayakan F1 = 0,90 (GroupKFold anti-kebocoran)
- **Top kandidat:** karbonat apatit, fluorapatit, oktakalsium fosfat, tetrakalsium fosfat, hidroksiapatit — konsisten dengan material graft tulang klinis

## Struktur Folder

```
prgf2027/
├── scripts/            # 13 skrip pipeline (urutan di bawah)
├── data/
│   ├── raw/            # data mentah per sumber (JSON/CSV + _metadata.json)
│   ├── processed/      # dataset terpadu, deskriptor, ranking, kandidat
│   ├── reports/        # 7 laporan markdown + 13 figure PNG
│   └── versions/       # snapshot dataset final + checksum (manifest)
├── requirements.txt    # dependensi Python
├── run_all.py          # orkestrator pipeline (bisa dijalankan ulang)
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
| 9 | `modeling.py` | 5 — Regresi/klasifikasi ML, GroupKFold, RFE |
| 10 | `mcdm.py` | 6 — TOPSIS + VIKOR, 3 set bobot, pemeringkatan |
| 11 | `xai.py` | 7 — SHAP + permutation importance |
| 12 | `laporan_final.py` | 7–8 — Laporan final + Top 15 dedup |
| 13 | `versi_dataset.py` | — Snapshot dataset final + checksum |

## Sumber Data & Lisensi

| Sumber | Akses | Lisensi |
|---|---|---|
| Materials Project (api.materialsproject.org) | API key | CC-BY 4.0 |
| AFLOW (aflow.org/API/aflux) | tanpa key | sitasi Curtarolo et al. |
| COD (crystallography.net) | HTTP tanpa key | CC0 |
| PubChem PUG REST | tanpa key | public domain (NCBI) |
| OQMD (oqmd.org/oqmdapi) | tanpa key (server flaky) | sitasi Kirklin et al. |

## Keputusan Metodologis Penting (log)

1. **Anti-kebocoran:** pemodelan hanya pada subset komputasional (MP+AFLOW); validasi silang GroupKFold berbasis kelompok komposisi (polimorf satu fold).
2. **Bandgap:** tidak dapat diprediksi dari deskriptor komposisi (R²<0) — imputasi dibatalkan, nilai terukur dipakai.
3. **Modulus elastik:** hanya 9 entri punya K&G — kriteria MCDM memakai imputasi median; validasi DFT/MD top kandidat adalah langkah wajib berikutnya.
4. **Pencilan:** dipertahankan bila fisika-valid, keputusan tercatat per kasus.

## Kontak

Dr. Ir. Soegianto Soelistiono, M.Si. — soegianto@fst.unair.ac.id
