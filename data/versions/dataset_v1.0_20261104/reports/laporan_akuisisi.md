# Laporan Audit Akuisisi Dataset Biomaterial Kalsium Fosfat
**Tanggal audit:** 2026-11-04 04:51:59
**Tahapan:** Bagian 2–3 panduan utama (akuisisi + audit dataset)

## Ringkasan
- **Total baris/entri:** 2605
- **Komposisi kimia unik:** 903
- **Indikator target:** >= 500 senyawa tervalidasi → TERPENUHI
- **Sumber & lisensi:**
  - Materials Project (API, CC-BY 4.0) — diakses 2026-11-04
  - AFLOW (AFLUX REST, sitasi Curtarolo et al.) — diakses 2026-11-04
  - COD (HTTP, CC0 public domain) — diakses 2026-11-04
  - PubChem (PUG REST, public domain NCBI) — diakses 2026-11-04
  - OQMD (oqmdapi, sitasi Kirklin et al.) — proses berjalan (server flaky)

## Jumlah per Sumber & Kelengkapan Deskriptor
| sumber           |   jumlah |   komposisi_unik |   ada_energi |   ada_densitas |   ada_volume |   ada_elastik |   ada_bandgap |
|:-----------------|---------:|-----------------:|-------------:|---------------:|-------------:|--------------:|--------------:|
| AFLOW            |      234 |               65 |          234 |            234 |          234 |             4 |            66 |
| COD              |     2304 |              820 |            0 |              0 |         2302 |             0 |             0 |
| MaterialsProject |       57 |               40 |           57 |             57 |           57 |             5 |            57 |
| PubChem          |       10 |               10 |            0 |              0 |            0 |             0 |             0 |

## Kelengkapan Kolom Utama (%)
|               |     0 |
|:--------------|------:|
| formula       | 100   |
| densitas_gcm3 |  11.2 |
| Eform_eV_atom |  11.2 |
| bandgap_eV    |   4.7 |
| bulk_K_GPa    |   0.3 |
| volume_A3     |  99.5 |
| spacegroup    |  99.5 |

## Pemeriksaan Material Rujukan (kontrol positif)
- **Hidroksiapatit (Ca5P3O13H):** 54 entri dari {'COD': 51, 'MaterialsProject': 2, 'PubChem': 1}
- **Trikalsium fosfat (Ca3P2O8):** 17 entri dari {'AFLOW': 6, 'COD': 10, 'PubChem': 1}

## Catatan Kualitas
- Data COD: eksperimental (parameter kisi + spacegroup), tanpa energi/sifat mekanik.
- Data MP/AFLOW: komputasional (energi, bandgap, modulus elastik VRH untuk AFLOW).
- Perbandingan antar basis data untuk komposisi sama dilakukan pada tahap eksplorasi (Bagian 5.4 panduan).
