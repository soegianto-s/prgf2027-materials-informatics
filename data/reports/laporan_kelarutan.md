# Kelarutan Setimbang Stoikiometrik (S, mol/L) dari pKsp Literatur
**Tanggal:** 2026-11-04 11:38:19

- S = (Ksp/(nu+^nu+ * nu-^nu-))^(1/(nu++nu-)); asumsi: aktivitas ~ konsentrasi, tanpa efek ion senama; OCP kondisional pH 7.4 (Ksp' = Ksp/[H+]^2).
- S_mg_L hanyalah skala kasar (berat formula ~HA 310 g/mol) — jangan dipakai untuk klaim presisi.

| fase            | reaksi                                            |   nu_plus |   nu_minus |   anion_ekstra |   pKsp |   S_mol_L |   log10_S |   S_mmol_L |     S_mg_L | kelas                 | catatan                                                                  |
|:----------------|:--------------------------------------------------|----------:|-----------:|---------------:|-------:|----------:|----------:|-----------:|-----------:|:----------------------|:-------------------------------------------------------------------------|
| Brushite (DCPD) | CaHPO4.2H2O -> Ca2+ + HPO4(2-) + 2H2O             |         1 |          1 |              0 |   6.59 |  0.000507 |     -3.29 |   0.507    | 157        | fast                  | pKsp utk CaHPO4.2H2O                                                     |
| Monetite (DCPA) | CaHPO4 -> Ca2+ + HPO4(2-)                         |         1 |          1 |              0 |   6.9  |  0.000355 |     -3.45 |   0.355    | 110        | fast                  | pKsp utk CaHPO4                                                          |
| alpha-TCP       | Ca3(PO4)2 -> 3Ca2+ + 2PO4(3-)                     |         3 |          2 |              0 |  25.5  |  3.11e-06 |     -5.51 |   0.00311  |   0.966    | resorbable            | pKsp utk alpha-Ca3(PO4)2                                                 |
| TTCP            | Ca4(PO4)2O -> 4Ca2+ + 2PO4(3-) + O(2-)            |         4 |          2 |              1 |  38    |  1.38e-06 |     -5.86 |   0.00138  |   0.43     | slowly resorbable     | konvensi: [O(2-)] = S (anion oksida; terhidrolisis jadi 2OH- di larutan) |
| beta-TCP        | Ca3(PO4)2 -> 3Ca2+ + 2PO4(3-)                     |         3 |          2 |              0 |  28.9  |  6.51e-07 |     -6.19 |   0.000651 |   0.202    | resorbable            | pKsp utk beta-Ca3(PO4)2                                                  |
| OCP             | Ca8H2(PO4)6.5H2O -> 8Ca2+ + 2H+ + 6PO4(3-) + 5H2O |         8 |          6 |              0 |  96.6  |  2.03e-07 |     -6.69 |   0.000203 |   0.063    | fast in vivo          | Ksp kondisional memuat [H+]^2 -> Ksp' = Ksp/[H+]^2 pada pH tetap         |
| Oxyapatite      | Ca10(PO4)6O -> 10Ca2+ + 6PO4(3-) + O(2-)          |        10 |          6 |              1 | 117    |  1.85e-08 |     -7.73 |   1.85e-05 |   0.00573  | essentially insoluble | data terbatas; dipakai ~HA (Elliott) sebagai batas bawah kelarutan       |
| Hydroxyapatite  | Ca5(PO4)3OH -> 5Ca2+ + 3PO4(3-) + OH-             |         5 |          3 |              1 | 117    |  2.98e-14 |    -13.5  |   2.98e-11 |   9.26e-09 | essentially insoluble |                                                                          |
| Fluorapatite    | Ca5(PO4)3F -> 5Ca2+ + 3PO4(3-) + F-               |         5 |          3 |              1 | 121    |  1.02e-14 |    -14    |   1.02e-11 |   3.16e-09 | essentially insoluble | pKsp ~121 (Dorozhkin)                                                    |

## Temuan
- Urutan kelarutan: ['Brushite', 'Monetite', 'alpha-TCP', 'TTCP', 'beta-TCP', 'OCP', 'Oxyapatite', 'Hydroxyapatite', 'Fluorapatite']
- Rentang S: 0.000507 s.d. 1.02e-14 mol/L — rentang 10 orde besaran.
- S sebanding antar fase (ternormalisasi stoikiometri); tetap overlay post-hoc, bukan kriteria atas seluruh kolam (pKsp hanya ada untuk fase dikenal).