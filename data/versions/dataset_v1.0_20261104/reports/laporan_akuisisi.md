# Laporan Audit Akuisisi Dataset Biomaterial Kalsium Fosfat
**Tanggal audit:** 2026-11-04 07:15:45
**Tahapan:** Bagian 2–3 panduan utama (akuisisi + audit dataset)

## Ringkasan
- **Total baris/entri:** 2885
- **Komposisi kimia unik:** 900
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
| OQMD             |      280 |               34 |          280 |              0 |          280 |             0 |             0 |
| PubChem          |       10 |               10 |            0 |              0 |            0 |             0 |             0 |

## Kelengkapan Kolom Utama (%)
|               |     0 |
|:--------------|------:|
| formula       | 100   |
| densitas_gcm3 |  10.1 |
| Eform_eV_atom |  19.8 |
| bandgap_eV    |   4.3 |
| bulk_K_GPa    |   0.3 |
| volume_A3     |  99.6 |
| spacegroup    |  99.5 |

## Pemeriksaan Material Rujukan (kontrol positif)
- **Hidroksiapatit (Ca5P3O13H):** 63 entri dari {'COD': 51, 'MaterialsProject': 2, 'OQMD': 9, 'PubChem': 1}
- **Trikalsium fosfat (Ca3P2O8):** 34 entri dari {'AFLOW': 6, 'COD': 10, 'MaterialsProject': 5, 'OQMD': 12, 'PubChem': 1}

## Catatan Kualitas
- Data COD: eksperimental (parameter kisi + spacegroup), tanpa energi/sifat mekanik.
- Data MP/AFLOW: komputasional (energi, bandgap, modulus elastik VRH untuk AFLOW).
- Perbandingan antar basis data untuk komposisi sama dilakukan pada tahap eksplorasi (Bagian 5.4 panduan).
