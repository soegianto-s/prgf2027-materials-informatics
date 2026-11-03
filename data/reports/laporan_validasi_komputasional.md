# Laporan Validasi Komputasional Top-5 Kandidat (MLFF MACE-MP-0)

**Tanggal:** 2026-11-04 | **Tahapan:** Bagian 9.2 panduan utama (validasi komputasional)
**Metode:** MACE-MP-0 (medium, float64, CPU 20-core) — relaksasi sel+atom BFGS (fmax 0.05 eV/Å, maks 300 langkah) — konstanta elastik finite-difference (±0.005, 12 evaluasi stress, Voigt-Reuss-Hill)

## 1. Stabilitas Struktur (relaksasi)

| Kandidat | Atom | dV relaksasi | Interpretasi |
|---|---|---|---|
| Karbonat apatit Ca10P6CO27 | 44 | **+0,36%** | stabil |
| Fluorapatit Ca5P3O12F | 42 | **+0,27%** | stabil |
| OCP Ca8P6H12O29 | 110 | **−0,16%** | stabil |
| Apatit Ca10P6O25 | 41 | **+0,41%** | stabil |
| TTCP Ca16O36P8 | 60 | **+3,03%** | stabil tapi melonggar — perlu cek DFT |

Empat dari lima kandidat nyaris tidak berubah di bawah MLFF (|dV| ≤ 0,41%) → struktur basis data
sudah berada di minimum energi. TTCP menyusut/ekspansi +3% — perlu diverifikasi DFT (input QE siap).

## 2. Konstanta Elastik (kristal tunggal, MLFF)

| Kandidat | K (GPa) | G (GPa) | E (GPa) | ν |
|---|---|---|---|---|
| Karbonat apatit | 139,3 | 89,1 | **220,3** | 0,236 |
| Fluorapatit | 135,9 | 88,1 | **217,3** | 0,233 |
| Apatit Ca10P6O25 | 131,6 | 85,5 | **210,8** | 0,233 |
| TTCP | 127,1 | 83,8 | **206,1** | 0,230 |

- ν ≈ 0,23 konsisten dengan apatit literatur (0,22–0,28).
- E kristal tunggal 206–220 GPa — lebih tinggi dari HAp padat literatur (80–120 GPa); MLFF dikenal
  melebih-lebihkan kekakuan (trained pada DFT; DFT sendiri overbind). Interpretasi: ORDE & PERINGKAT
  dipakai, nilai absolut menunggu DFT.
- Keseragaman antar kandidat (127–139 K) khas keluarga apatit: scaffold dari kandidat ini punya
  perilaku mekanik serupa — pemilihan kandidat akhir lebih ditentukan stabilitas & bioaktivitas.

## 3. Analisis Porositas (Gibson–Ashby)

Target scaffold tulang kortikal: E_eff = 10–20 GPa. Dengan E_s ≈ 215 GPa (rerata MLFF):

$$P = 1 - \sqrt{E_{eff}/E_s}$$

| E_eff target (GPa) | Porositas yang diperlukan |
|---|---|
| 10 | ~78% |
| 15 | ~74% |
| 20 | ~70% |

**Rekomendasi desain:** scaffold dari kandidat apatit perlu porositas **70–78%** agar modulus
efektifnya masuk rentang tulang kortikal — angka yang konsisten dengan literatur fabrikasi scaffold
berpori (60–90%). Ini menjadi spesifikasi desain untuk tahap fabrikasi (3D printing).

## 4. Keterbatasan & Langkah Berikut

1. MLFF = pra-validasi; nilai absolut modulus harus dikonfirmasi DFT (input QE siap di `data/dft/`).
2. TTCP +3% volume → prioritas verifikasi DFT.
3. OCP (110 atom) dihitung elastiknya bila klaster tersedia (di PC ini relaksasinya saja 5 menit).
4. Hidroksiapatit rujukan dapat ditambahkan sebagai kalibrasi MLFF vs DFT/literatur.

## 5. Artefak

- `data/validasi_mlff/hasil_relaksasi_elastik.json` — data mentah
- `data/validasi_mlff/*_relaxed.cif` — struktur terelaksasi (bisa langsung jadi input DFT)
