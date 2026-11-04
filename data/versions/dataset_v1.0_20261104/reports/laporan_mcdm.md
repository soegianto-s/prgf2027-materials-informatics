# Laporan Analisis Multiobjektif (MCDM)
**Tanggal:** 2026-11-04 07:59:46
**Tahapan:** Bagian 8 panduan utama (revisi ronde 4)

## Kriteria & Arah
- C1 stabilitas (max), C2 densitas pita [1.0, 3.2] g/cm3 (max), C3 Ca/P->1.67 (max)
- C4 modulus & C5 bandgap DITARIK (reviewer ronde 4): C4 imputasi median utk 98% entri (n=9) = praktis konstanta + salah level (sifat scaffold, bukan material); C5 tanpa fungsi elektronik pada scaffold tulang. C6 (kelayakan ML) sudah ditarik sebelumnya.
- Filter kenetralan muatan (stoikiometri): 398 entri muatan != 0 dibuang (contoh: Ca5P8, CaP, CaP3, Ca(PO4)2, Ca2P2O11, Ca4P2O, Ca5(PO4)3, Ca5P3O13); 0 entri berunsur di luar sistem dan 356 fosfida (tanpa O, di luar kelas material kalsium fosfat) dibuang. Kolam akhir: 165 entri.
- Bobot: {'W1_berimbang': array([0.4, 0.3, 0.3]), 'W2_stabilitas': array([0.6, 0.2, 0.2]), 'W3_komposisi': array([0.3, 0.3, 0.4])}
## Posisi Material Rujukan (peringkat rerata dari 6 skenario)
- HAp: | formula     |   peringkat_rerata |
|:------------|-------------------:|
| Ca5P3HO13   |            6.66667 |
| Ca5P3HO13   |            7.66667 |
| Ca10H2O26P6 |           58.5     |
- TCP: | formula   |   peringkat_rerata |
|:----------|-------------------:|
| Ca3O8P2   |            36.1667 |
| Ca3O8P2   |            36.1667 |
| Ca3O8P2   |            39.6667 |
- Fluorapatit: | formula     |   peringkat_rerata |
|:------------|-------------------:|
| Ca5P3O12F   |            1       |
| Ca5P3O12F   |            4.66667 |
| Ca10F2O24P6 |           31.5     |
## Top 15 Kandidat (peringkat rerata TOPSIS+VIKOR x 3 bobot)

| formula    | sumber           | kelompok        |   peringkat_rerata |   kali_top10 |   Eform_eV_atom |   densitas_final_gcm3 |   ca_p_ratio |   layak |
|:-----------|:-----------------|:----------------|-------------------:|-------------:|----------------:|----------------------:|-------------:|--------:|
| Ca5P3O12F  | MaterialsProject | apatit_hidroksi |              1     |            6 |          -3.42  |                 3.104 |        1.667 |       1 |
| Ca10P6O25  | MaterialsProject | apatit_hidroksi |              2.667 |            6 |          -3.319 |                 2.978 |        1.667 |       1 |
| Ca10P6O25  | MaterialsProject | apatit_hidroksi |              3.667 |            6 |          -3.318 |                 2.98  |        1.667 |       1 |
| Ca5P3O12F  | MaterialsProject | apatit_hidroksi |              4.667 |            5 |          -3.421 |                 3.208 |        1.667 |       1 |
| Ca10P6CO27 | MaterialsProject | apatit_hidroksi |              5.5   |            6 |          -3.253 |                 3.053 |        1.667 |       1 |
| Ca5P3HO13  | MaterialsProject | apatit_hidroksi |              6.667 |            5 |          -3.223 |                 3.178 |        1.667 |       1 |
| Ca5P3HO13  | MaterialsProject | apatit_hidroksi |              7.667 |            5 |          -3.223 |                 3.18  |        1.667 |       1 |
| Ca10O25P6  | OQMD             | apatit_hidroksi |              9.333 |            5 |          -3.201 |                 3.132 |        1.667 |       1 |
| Ca10O25P6  | OQMD             | apatit_hidroksi |              9.333 |            5 |          -3.201 |                 3.132 |        1.667 |       1 |
| Ca10O25P6  | OQMD             | apatit_hidroksi |             11.333 |            1 |          -3.2   |                 3.118 |        1.667 |       1 |
| Ca10O25P6  | OQMD             | apatit_hidroksi |             11.333 |            1 |          -3.2   |                 3.118 |        1.667 |       1 |
| Ca10O25P6  | OQMD             | apatit_hidroksi |             13.333 |            0 |          -3.199 |                 3.142 |        1.667 |       1 |
| Ca10O25P6  | OQMD             | apatit_hidroksi |             13.333 |            0 |          -3.199 |                 3.142 |        1.667 |       1 |
| Ca10O25P6  | OQMD             | apatit_hidroksi |             15.333 |            0 |          -3.197 |                 3.144 |        1.667 |       1 |
| Ca10O25P6  | OQMD             | apatit_hidroksi |             15.333 |            0 |          -3.197 |                 3.144 |        1.667 |       1 |