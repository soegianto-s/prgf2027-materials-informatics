# Kerangka Materials Informatics Berbasis AI — Biomaterial Kalsium Fosfat untuk Scaffold Rekayasa Jaringan Tulang

**PRGF Discovery Research 2027 · Research Group AMREC · Universitas Airlangga**
Periode: Agustus 2026 – Juli 2027 · Versi paket: 1.0 (2026-11-04)

## Ringkasan

Pipeline end-to-end untuk penemuan biomaterial kalsium fosfat:

`Akuisisi data (5 basis data) → Prapemrosesan → Deskriptor fisikokimia → EDA/Klaster → Pemodelan ML (anti-leakage) → MCDM (TOPSIS+VIKOR + entropi + Monte Carlo) → Interpretasi SHAP`

- Dataset terpadu: **2.885 entri / 950 komposisi unik** (target proposal: ≥500)
- Model (protokol anti-kebocoran v2: grouping formula tereduksi + nested CV + 4 DOF komposisi murni — Ca/P, fraksi P, H, F): SVR Eform R² = 0,11 discovery (n=337 MP+OQMD) / −0,52 dalam-fosfat / 0,40 varian screening (benchmark eksperimen MAE 0,094 eV/atom); densitas komposisi-murni R² = 0,02 (benchmark MAE 0,114 g/cm³); transfer antar basis data sesama-komposisi R² = 0,83
- **Top kandidat (MCDM ronde 4):** fluorapatit, oksiapatit, karbonat apatit, hidroksiapatit, β-TCP, TTCP, pirofosfat, OCP, monetit — 3 kriteria level material (stabilitas, pita densitas [1.0, 3.2], Ca/P→1.67) + filter kenetralan muatan (165 entri netral) + Monte Carlo 3.000 run (top-4 stabil, top-5 56–86%); overlay resorbabilitas pKsp literatur; klaim 'accelerated discovery' dicabut dari judul
- **Baseline ronde 6 (atas permintaan reviewer):** (a) 40 fitur Magpie — Eform tetap ≈0 (R² −0,055 vs 0,113) tetapi densitas naik ke R² 0,273–0,309 (vs 0,018): statistik kontras unsur menangkap info kemasan, bukan energi; (b) pretrained MACE-MP-0 (float64, model L1) — Eform 6 fase Wagman MAE **0,253** eV/atom vs 0,094 model komposisi: pada benchmark sempit sesama-keluarga ini surrogate terlatih-basis-data tidak terlampaui (keunggulan MLFF = generalitas, bukan akurasi di sini); (c) re-ranking sensitivitas pKsp (8 komposisi shortlist) — β-TCP/TTCP/monetit naik ke 3 besar, FAp/oksiapatit/HA turun (trade-off terkuantifikasi). Deskripsi model MACE dikoreksi 'medium'→'float64'

## Struktur Folder

```
prgf2026/
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
| 13 | `mcdm_montecarlo.py` | 6 — Monte Carlo: ketidakpastian bobot + prediksi ML |
| 14 | `siapkan_dft.py` | 7 — Input DFT/QE (POSCAR+CIF+scf/relax) Top 5 |
| 15 | `xai.py` | 7 — SHAP + permutation importance (4 DOF komposisi) |
| 16 | `laporan_final.py` | 7–8 — Laporan final + Top 15 dedup (rank ordinal) |
| 17 | `versi_dataset.py` | — Snapshot dataset final + checksum |
| 18 | `acquire_cod_cif.py` | Q1 — Unduh 928 CIF COD unik (resumable, QC koordinat) |
| 19 | `screening_mace_cod.py` | Q1 — Ef MACE-MP-0 single-point struktur COD (checkpoint/cod_id) |
| 20 | `kalibrasi_hull_mace.py` | Q1 — Kalibrasi offset MACE→MP GGA + E_hull COD in-system |
| 21 | `ekstrak_fitur_struktur.py` | Q1 — Q^n fosfat, CN Ca, SOAP |
| 22 | `modeling_struktur.py` | Q1 — Model structure-informed (screening, PCA dalam fold) |
| 23 | `perluasan_kandidat_mp.py` | Q1 — Kandidat substitusi Sr/Mg/Zn/Si (MP, 2 tier) |
| 24 | `konversi_ksp.py` | Q1 — Kelarutan stoikiometrik S (mol/L) dari pKsp |
| 25 | `mcdm_q1.py` | Q1 — MCDM C1 = −E_hull (phase-level, Monte Carlo) |

Skrip penunjang (tidak berurutan): `tcp_alpha_beta.py` (validasi pemisahan α/β-TCP),
`tuning_eform.py` (tuning SVR Eform), `validasi_independen.py` (benchmark eksperimen),
`validasi_mlff.py` (pra-validasi MACE-MP-0 Top 5), `magpie_baseline.py` (baseline
deskriptor Magpie), `mace_baseline.py` (baseline pretrained MACE-MP-0, resumable),
`mcdm_resorb.py` (sensitivitas MCDM+pKsp), `jalankan_dft.py` (driver QE via WSL:
vc-relax top-5 + elastisitas regangan ±1%), `konversi_elsarticle.py` (konversi ke
format jurnal), `patch_manuskrip_ronde3*.py`, `patch_manuskrip_ronde4.py`,
`patch_manuskrip_ronde5.py`, `patch_manuskrip_ronde6.py`, `patch_manuskrip_ronde7.py`
(patch angka hasil review, ber-assertion — tidak ada kegagalan diam-diam).

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
2. **Bandgap:** tidak dapat diprediksi dari deskriptor komposisi (R²<0) — imputasi dibatalkan; sebagai KRITERIA MCDM ditarik total (ronde 4): tanpa fungsi elektronik pada scaffold tulang.
3. **Modulus elastik:** hanya 9 entri punya K&G — kriteria C4 DITARIK dari MCDM (ronde 4): imputasi median = praktis konstanta + modulus 10–20 GPa adalah sifat SCAFFOLD (arsitektur+porositas), bukan material; ditangani hilir via Gibson-Ashby (porositas 70–78% dari MLFF). Validasi DFT definitif top kandidat adalah langkah wajib berikutnya.
4. **MCDM (ronde 4):** 3 kriteria + filter kenetralan muatan (398 muatan≠0 + 356 fosfida dibuang → 165 entri) + Monte Carlo 3.000 run (top-4 stabil 56–86%, slot ke-5 diperebutkan); resorbabilitas = overlay pKsp literatur, bukan kriteria; judul tanpa "accelerated discovery".
4. **Pencilan:** dipertahankan bila fisika-valid, keputusan tercatat per kasus.
5. **Baseline pembanding (ronde 6):** Magpie — Eform tak tertolong (R² −0,055), densitas naik ke R² 0,273–0,309 (statistik unsur menangkap info kemasan); MACE-MP-0 float64 (model L1, bukan 'medium' — bobot float64 mace-torch = L1) MAE 0,253 eV/atom pada 6 fase Wagman, tidak mengalahkan model komposisi (0,094) pada benchmark sempit ini — dilaporkan jujur; re-ranking pKsp shortlist membuktikan trade-off stabilitas-resorbabilitas secara kuantitatif. Koreksi jalur: seluruh skrip menunjuk `D:\latex\prgf2026` (folder proyek direname dari prgf2027).

## Kontak

Dr. Ir. Soegianto Soelistiono, M.Si. — soegianto@fst.unair.ac.id
