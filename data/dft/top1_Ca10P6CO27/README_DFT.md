# Validasi DFT — Ca10P6CO27 (top1_Ca10P6CO27)

Struktur: Materials Project (https://materialsproject.org), lisensi CC-BY 4.0.

## Pseudopotensial (wajib diunduh)
PSL 1.0.0 PBE dari http://pseudo-dojo.org -> folder `pseudo/`:
- C.pbe-n-rrkjus_psl.1.0.0.UPF
- Ca.pbe-spn-kjpaw_psl.1.0.0.UPF
- O.pbe-n-rrkjus_psl.1.0.0.UPF
- P.pbe-n-rrkjus_psl.1.0.0.UPF

## Cara menjalankan (Quantum ESPRESSO >= 7.0)
    mpirun -np N pw.x -in scf.in > scf.out
    mpirun -np N pw.x -in relax.in > relax.out   # vc-relax: verifikasi stabilitas kisi

## Target verifikasi (dari kerangka MI)
- Stabilitas: energi pembentukan tetap negatif setelah relaksasi (lihat laporan).
- Densitas pasca-relaksasi dibandingkan dengan prediksi (lihat data/processed/kandidat_top15_dedup.csv).
- Bila tersedia ph.x: modulus elastik untuk validasi kriteria C4 MCDM.
