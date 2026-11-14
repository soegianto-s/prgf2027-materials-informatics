# Log Persiapan Validasi DFT
**Tanggal:** 2026-11-04 08:03:27
- top1_Ca5P3O12F: 42 atom, elemen ['Ca', 'F', 'O', 'P'] -> POSCAR+CIF+scf.in+relax.in
- top2_Ca10P6O25: 41 atom, elemen ['Ca', 'O', 'P'] -> POSCAR+CIF+scf.in+relax.in
- top5_Ca10P6CO27: 44 atom, elemen ['C', 'Ca', 'O', 'P'] -> POSCAR+CIF+scf.in+relax.in
- top6_Ca5P3HO13: 44 atom, elemen ['Ca', 'H', 'O', 'P'] -> POSCAR+CIF+scf.in+relax.in
- top26_Ca3(PO4)2: 13 atom, elemen ['Ca', 'O', 'P'] -> POSCAR+CIF+scf.in+relax.in

**Tanggal:** 2026-11-06 — pemulihan run VPS + jalur produksi baru
- VPS `/root/prgf_dft`: run pertama (4–5 Nov) gagal sebagian — top2/5/6 tanpa pseudo, 12 SCF
  regangan top1 crash (bug newline generator), posisi atom regangan belum terelaksasi.
- Perbaikan: `scripts/vps_setup.sh` v3 (newline, posisi final relax.out, prefix/outdir unik
  per strain, verifikasi `total stress`, cek pseudo, SCF referensi E0/sigma0) + pseudo top2/5/6
  disalin + H diunduh.
- Uji konvergensi k-mesh & ecut di top1: `scripts/konvergensi.sh` (tmux `ktest` di VPS,
  k222/k333/k444/e80) — kriteria dE < 1 meV/atom & stress stabil; hasil ke
  `konvergensi_summary.txt` (ditarik ke `data/dft/vps_hasil/logs/`).
- Setelah konvergen: set K_GRID/ECUT di `vps_setup.sh`, re-relax top1 di mesh produksi
  (backup relax.out -> relax.out.k222, hapus `out/*.save`), jalankan produksi 4 material
  (vc-relax + 12 strain ±1% + referensi) di tmux `prgf`.
- Sinkronisasi: `scripts/sinkron_dft_vps.py tarik|dorong|status` — hasil VPS masuk
  `data/dft/vps_hasil/` (di-gitignore). Status rinci: `/root/prgf_dft/PRGF_DFT_STATUS.md`.
- `scripts/jalankan_dft.py` (driver WSL lokal) juga dipatch prefix/outdir unik per strain —
  tetap kanonik bila dipakai ulang lokal.
- Rencana kelanjutan setelah produksi VPS selesai (tarik hasil → konstanta elastik →
  banding MLFF → patch manuskrip ronde 8 → arsip): **RENCANA_INTEGRASI.md** di folder ini;
  skrip pendukungnya `scripts/hitung_elastik_vps.py`.

**Tanggal:** 2026-11-09 — cek kesehatan pasca insiden tmux 8 Nov
- VPS TIDAK mati/restart: uptime 2 minggu 2 hari (terus menyala sejak ±26 Okt). Yang
  terputus hanya sesi tmux/SSH (SIGABRT 8 Nov 02:40, tekanan memori pm2) — job sempat
  mati ±5 menit, di-restart 02:45 via nohup+setsid; sejak itu run.log kontinu tanpa gap
  (22:41 → 23:33 → 00:22 → 02:09).
- Status produksi elastik: top1 13/13 SCF SELESAI PENUH; top2 7/13 (strain 4- berjalan);
  top5/top6 relax belum pernah selesai (relax.out lama/terpotong) — dibiarkan dulu,
  jangan ganggu sistem yang sedang berjalan; dievaluasi lagi setelah top2 tuntas.
- Info lokal di-refresh: `python scripts/sinkron_dft_vps.py tarik` (read-only di VPS) —
  log + PRGF_DFT_STATUS.md masuk `vps_hasil/` (snapshot 9 Nov 02:37).

**Tanggal:** 2026-11-10 — evaluasi pasca top2 tuntas + snapshot lokal baru
- Evaluasi yang ditunggu (lihat entri 9 Nov): top2 SELESAI PENUH 12/12 strain + referensi
  (9 Nov 11:48 WIB). **TIDAK perlu restart manual** — pipeline v3 otomatis lanjut:
  top5_Ca10P6CO27 re-relax produksi (k=3 3 3 0 0 0, ecut=80/640) mulai 9 Nov 11:48 WIB.
- Status VPS (read-only check 10 Nov): pw.x top5 aktif (iterasi vc-relax #8, energi sudah
  stabil ~1e-9 Ry antar-iterasi), RAM aman (3,8 GB available), disk 39%, load ~7,6.
  Tidak ada intervensi — biarkan berjalan (nohup+setsid).
- Antrean tersisa: top5 (strain 12+1, belum mulai) → top6_Ca5P3HO13 (terakhir).
  Proyeksi kasar: top5 selesai ±12–13 Nov, top6 ±15 Nov.
- Snapshot lokal diperbarui via `sinkron_dft_vps.py tarik` (10 Nov): `vps_hasil/`
  terverifikasi — top1 13/13 & top2 13/13 lengkap di strain_out, top5 strain_out kosong.

**Tanggal:** 2026-11-12 — 3/4 material tuntas, top6 berjalan (cek `ssh cek-dft`)
- top5_Ca10P6CO27 SELESAI PENUH 12 Nov 00:37 WIB (12/12 strain + referensi OK; strain
  6- terakhir tuntas 11 Nov 21:56) — pipeline otomatis lanjut ke top6 tanpa intervensi.
- top6_Ca5P3HO13 mulai 12 Nov 00:37 — vc-relax berjalan (cek 02:49: bfgs-3, SCF iter-7,
  pw.x 627% CPU, RAM 1,6 GB). Proyeksi selesai ±13–14 Nov (13 run × ±2,5 jam).
- VPS sehat: uptime 2 minggu 5 hari, disk 47% (89G/192G), load aman. Tidak ada insiden
  sejak restart 8 Nov — nohup+setsid terbukti stabil.
- Alias lokal `ssh cek-dft` (jalan otomatis /root/prgf_dft/cek.sh) — cara termudah pantau.
- `PRGF_DFT_STATUS.md` (di folder ini) diperbarui dengan status 12 Nov.
**Tanggal:** 2026-11-14 — cek-dft sore + snapshot lokal "sampai saat ini"
- `ssh cek-dft` 18:49 WIB: pw.x aktif di top6 strain 6+ (jalan 55:55, CPU 718%,
  RAM 2,1 GB, input scf_elastik_6+.in). VPS uptime 2 hari 3 jam (reboot terakhir
  ±12 Nov 15:22 — pipeline resume otomatis, tanpa insiden).
- top1/top2/top5 tetap 13/13 SELESAI PENUH. top6: relax SELESAI + SCF regangan 10/13
  (1±..5± tuntas; 6+ mulai 17:53) — tersisa 6+, 6-, referensi → proyeksi top6 tuntas
  ±15 Nov dini hari (sesuai perkiraan 13–14 Nov, mundur sedikit karena reboot).
- Snapshot lokal diperbarui via `sinkron_dft_vps.py tarik` (14 Nov 18:48): run.log
  (s/d 17:53), output material, vps_snapshot.tar.gz → `vps_hasil/`. Output cek-dft
  disimpan di `vps_hasil/cek_dft_2026-11-14_1849.txt`.
- Catatan: PRGF_DFT_STATUS.md di VPS masih versi 8 Nov (belum di-update di sana);
  isi status terkini tercatat di log ini + file cek di atas.

**Tanggal:** 2026-11-15 — ✅ PRODUKSI DFT TUNTAS + integrasi ronde 8 SELESAI
- `ssh cek-dft` 02:54 WIB: **SEMUA SELESAI (gagal total: 0)** — top6 tuntas
  15 Nov 01:36 (12/12 strain + referensi OK); 4 material 13/13. Output cek disimpan
  di `vps_hasil/cek_dft_2026-11-15_0254.txt`.
- Snapshot lokal diperbarui via `sinkron_dft_vps.py tarik` → 4×13 file strain_out
  terverifikasi lengkap.
- `hitung_elastik_vps.py` (QA lolos: σ referensi < 0,5 GPa, C_ij simetris positif):
  top1 FAp K=140,8 G=95,4 E=233,5 ν=0,224; top2 oksiapatit K=136,3 G=92,2 E=225,8 ν=0,224;
  top5 karbonat K=143,7 G=96,1 E=235,8 ν=0,226; top6 HA K=141,9 G=96,2 E=235,4 ν=0,223
  (+ top26 β-TCP K=134,7 G=87,9 E=216,6 ν=0,232 dari ronde sebelumnya) →
  `data/validasi_dft/hasil_dft.json` + 4 file `<tag>_elastik.json` baru.
- Temuan penting untuk manuskrip (ronde 8): (1) MACE-MP-0 *underestimate* modulus
  PBE-DFT secara konsisten — E −5,9..−6,9%, G −6,6..−7,7%, K −2,6..−3,5% (koreksi
  klaim lama "MLFF systematically high"); (2) volume HA +4,3% dari MLFF TERKONFIRMASI
  DFT vc-relax (547,60 vs 547,70 Å³, beda 0,02%) — relaksasi nyata struktur input
  teridealisasi, bukan artefak MLFF; (3) urutan 5 kandidat per E sama di DFT & MLFF;
  (4) target porositas Gibson–Ashby bergeser 70–78% → 70–79% (pita E padat 216,6–235,8).
- `patch_manuskrip_ronde8_dft.py` → kedua .tex (paragraf metode DFT + tabel
  tab:dft_elastik + koreksi klaim + abstrak/diskusi/kesimpulan + bibitem giannozzi2009);
  rebuild 2 PDF (manuscript 17 hal, elsarticle 24 hal) tanpa undefined reference;
  PDF submit root diperbarui.
- PRGF_DFT_STATUS.md (mirror lokal di vps_hasil/) diperbarui dengan status final;
  file asli di VPS belum di-update (biarkan — produksi selesai).

**Tanggal:** 2026-11-15 — ronde 8b: sinkronisasi menyeluruh isi makalah dengan data DFT
- `patch_manuskrip_ronde8b_sinkron.py`: keywords + "density functional theory; elastic
  constants"; kontribusi (v) intro; wording metode ("subsequent" → definitif); pita
  modulus DFT eksplisit di paragraf hasil (E 216,6–235,8 / K 134,7–143,7 GPa); dataset
  n=9 disilang ke tab:dft_elastik; data availability menyebut input/output DFT.
  Judul TIDAK diubah (tetap akurat). BUG tertangkap sebelum build: delimiter `$` hilang
  di pita angka (math mode tak seimbang) — diperbaiki di .tex + skrip.
- Rebuild 2 PDF (17+24 hal) tanpa undefined reference; PDF submit root diperbarui;
  verifikasi ekstraksi teks: keywords/pita/tabel terkonfirmasi di kedua PDF.

**Tanggal:** 2026-11-15 — ronde 9: revisi menyeluruh atas umpan balik reviewer
- `patch_manuskrip_ronde9.py`: (1) abstrak ditulis ulang 210 kata (dari 658; batas
  Elsevier 250) fokus klaim utama; (2) jejak riwayat revisi dihapus — "withdrawn on
  reviewer scrutiny", "earlier headline scores", "R² 0,87→0,11", "phrase has been
  removed", "withdrawn as arbitrary", "recorded decision" semua hilang; (3) seksi
  substitusi + Tabel 9 DIPOTONG (keputusan user; Mg₃(PO₄)₂ issue ikut hilang);
  (4) sitasi diri soelistiono2026 + bibitem dorozhkin (buku) dihapus; (5) sitasi
  yang tadinya tak dikutip kini dikutip: jain2013/curtarolo2012/kirklin2015/
  grazulis2009/mathew1977/lundberg2017; (6) perbaikan kesalahan: density "0,493→0,293"
  → "0,226→0,293" (0,493 itu R² Eform, bukan density), "Rank (tab:top)" literal →
  Tab.~\ref (ter-render "Tab. 5"), tab:val dipindah sebelum tab:bench (urutan 9<10<11<12
  sesuai urutan pembahasan), duplikat "950 unique compositions" dihapus, klaim clustering
  diukur ulang (43% noise HDBSCAN dinyatakan jujur), data availability kini URL GitHub
  publik (akses saat review, bukan "upon acceptance").
- `regenerasi_figur_eda.py`: Fig 1 (PCA) & Fig 3 (t-SNE) digambar ulang pada dataset
  PENUH — lama disampling 1500 (legend 34/125/1183/158 ≠ Tabel 1). Kini n=2.829
  (2.885 − entri tanpa 5 deskriptor lengkap; PubChem 0), fraksi tetangga sesumber
  91,4% (bukan 88%), PCA 59,3% tetap; n dicetak di judul figur + caption dijelaskan.
- Rebuild 2 PDF (16+22 hal — menyusut karena substitusi dipotong), tanpa undefined
  reference/citation; abstrak PDF terukur 206 kata; urutan tabel terverifikasi di PDF;
  PDF submit root diperbarui.

**Tanggal:** 2026-11-15 — ronde 10: konsistensi internal (umpan balik reviewer lanjutan)
- Zenodo DIHAPUS; seksi "Data and code availability" ganda di elsarticle digabung
  jadi satu Data availability (tautan GitHub saja).
- Ranking disatukan: tab:top DIBANGUN ULANG dari Monte Carlo (laporan_montecarlo.md +
  kandidat_ranking.csv -> ranking_mc_ringkasan.json; tabel lama bertentangan — karbonat
  rank 3 padahal top-5 cuma 16,6%). Kolom: Order + Median rank [p5--p95] + E_f/rho/Ca-P
  rekaman terbaik. Narasi disesuaikan: TTCP (order 5), monetite (8), OCP (12); kontes
  slot-5 kini TTCP 17% / karbonat 17% / pirofosfat 16%; beta-TCP di luar top-10 phase-level
  diakui jujur. tab:top_q1 diramping (kolom rho/Ca-P dihapus — sumber ketidakkonsistenan
  3.13 vs 2.98, 1.70 vs 1.67).
- Resorbabilitas kini pakai S stoikiometrik (bukan -pKsp lintas stoikiometri):
  mcdm_resorb_S.py (C_resorb = log10 S; kelarutan_ksp.csv -> resorb_S_ringkasan.json).
  Hasil: b-TCP & TTCP tetap 2 besar; monetite 4, oksiapatit 3, OCP 5, brushite 6, HAp/FAp
  bawah. tab:resorb_rank + tab:resorb pakai kolom S + footnote oksiapatit (~HA tanpa
  literatur). Narasi trade-off diperbarui.
- Densitas HAp: klaim "+4,3% input tegang" DIKOREKSI -> overexpansion sistematis yang
  dibagi MACE & PBE (relax 547,6 Å³ -> rho 3,05 vs 3,16 eksperimen; input sendiri 3,18
  konsisten eksperimen) — bukan artefak MLFF.
- Rujukan seksi jadi label+ref (sec:ranking/kelarutan/validasi/diskusi); tab:kalibrasi
  dipindah ke Methods (urutan tabel 1-12 kini persis urutan pembahasan); bibliografi
  diurut per kemunculan pertama (konvensi Elsevier; terverifikasi 1..31 monoton di PDF).
- Rebuild 2 PDF (16+22 hal) tanpa undefined ref/citation; PDF submit root diperbarui.
