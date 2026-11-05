# Rencana Integrasi Hasil DFT VPS → Penelitian PRGF

**Dibuat:** 2026-11-06 — berlaku SETELAH produksi DFT di VPS selesai
(run.log menulis `SEMUA SELESAI` dengan gagal total 0: 4 material ×
[vc-relax + 12 strain ±1% + 1 SCF referensi]).

## Prasyarat & alur (sudah jalan di VPS)

1. Uji konvergensi k-mesh & ecut di top1 (tmux `ktest`, `konvergensi.log`) →
   mesh produksi dipilih dari `konvergensi_summary.txt`
   (kriteria: dE < 1 meV/atom & stress stabil antar mesh).
2. Produksi 4 material di tmux `prgf` (vps_setup.sh v3, K_GRID/ECUT ter-set):
   vc-relax → 12 SCF regangan → SCF referensi; tiap run terverifikasi
   (`total   stress`), idempoten — aman dijalankan ulang.

## Langkah integrasi (di komputer lokal, sesudah produksi selesai)

### 1. Tarik hasil
```
python scripts/sinkron_dft_vps.py tarik
```
→ `data/dft/vps_hasil/<tag>/strain_out/*.out` (tensor tegangan tiap regangan)
+ log & ringkasan.

### 2. Hitung konstanta elastik + tulis JSON (format identik top26)
```
python scripts/hitung_elastik_vps.py
```
- Baca 12 stress (konvensi QE: positif = kompresi) →
  `C[:,i] = (σ(−ε) − σ(+ε)) / 2ε`, ε = 0.01, simetrisasi.
- QA: tegangan SCF referensi harus ≈ 0 (residu kecil — cek konsistensi
  titik setimbang); assert 12 blok stress terbaca; C_ij simetris.
- VRH (`validasi_mlff.vrh`) → K, G, E, ν.
- Output: `data/validasi_dft/<tag>_elastik.json` + `hasil_dft.json`
  (digabung dengan entri top26_Ca3(PO4)2 yang sudah ada).

### 3. Bandingkan dengan MLFF (tabel manuskrip)
Target pembanding: `data/validasi_mlff/hasil_relaksasi_elastik.json`
(MACE-MP-0 medium) — fluorapatit E=217,3 / oksiapatit 210,8 / karbonat 220,3 /
HA 220,1 / beta-TCP 203,9 GPa. Acuan DFT: beta-TCP E=216,6 GPa (top26, sudah ada).
DFT = referensi definitif validasi MLFF; laporkan galat relatif per material.

### 4. Patch manuskrip (ronde 8 — pola ronde sebelumnya)
Buat `scripts/patch_manuskrip_ronde8_dft.py` mengikuti konvensi ronde 3–7:
- Setiap replace ber-assertion `count==1`, idempoten, diterapkan ke KEDUA file:
  `data/reports/manuscript/manuscript.tex` + `manuscript_elsarticle.tex`.
- Muatan: tabel DFT vs MLFF (K/G/E/ν per material + galat relatif),
  bagian metode (PBE, pseudopotensial PSL 1.0.0, mesh k konvergen — sebutkan
  nilai final dari konvergensi_summary.txt, konvensi regangan Voigt ±1%),
  dan kalimat validasi definitif top kandidat.

### 5. Jangan lupa konteks hilir (sudah ada, tidak disentuh DFT)
- Modulus scaffold 10–20 GPa = sifat arsitektur+porositas, ditangani
  Gibson-Ashby (porositas 70–78% dari MLFF) — DFT hanya modulus material padat.
- Trade-off stabilitas–resorbabilitas (pKsp) tidak dipengaruhi hasil ini.

### 6. Opsional lanjutan (bila reviewer meminta)
- E_hull dari energi total DFT (ada di relax.out) → kalibrasi/validasi MACE
  (`kalibrasi_hull_mace.py`).
- Band structure / DOS dari geometri terelaksasi (save `./out/` masih utuh).

### 7. Arsip & jejak
- Perbarui `data/dft/LOG_DFT.md`: tanggal selesai, mesh/ecut produksi,
  waktu komputasi, versi script.
- Commit dengan pola checkpoint (`Checkpoint sesi DFT: ...`).
- Snapshot `data/dft/vps_hasil/vps_snapshot.tar.gz` + checksum.
