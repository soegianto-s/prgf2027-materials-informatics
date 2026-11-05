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