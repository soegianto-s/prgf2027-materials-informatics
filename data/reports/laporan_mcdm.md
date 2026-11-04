# Laporan Analisis Multiobjektif (MCDM)
**Tanggal:** 2026-11-04 07:09:48
**Tahapan:** Bagian 8 panduan utama

## Kriteria & Arah
- C1 stabilitas (max), C2 densitas->2.0 (max), C3 Ca/P->1.67 (max), C4 modulus->15 GPa (max), C5 bandgap (max), C6 kelayakan ML (max)
- Imputasi median untuk C4/C5 yang hilang (keputusan tercatat).
- Bobot: {'W1_berimbang': array([0.35, 0.25, 0.15, 0.15, 0.1 ]), 'W2_stabilitas': array([0.5 , 0.15, 0.15, 0.1 , 0.1 ]), 'W3_mekanik': array([0.25, 0.2 , 0.1 , 0.35, 0.1 ])}
## Posisi Material Rujukan (peringkat rerata dari 6 skenario)
- HAp: | formula     |   peringkat_rerata |
|:------------|-------------------:|
| Ca5P3HO13   |            4.33333 |
| Ca5P3HO13   |            5.33333 |
| Ca10H2O26P6 |           27.3333  |
- TCP: | formula   |   peringkat_rerata |
|:----------|-------------------:|
| Ca3O8P2   |            40.1667 |
| Ca3O8P2   |            40.1667 |
| Ca3O8P2   |            42.1667 |
- Fluorapatit: | formula     |   peringkat_rerata |
|:------------|-------------------:|
| Ca5P3O12F   |            1.33333 |
| Ca5P3O12F   |            2.33333 |
| Ca10F2O24P6 |            7.16667 |
## Top 15 Kandidat (peringkat rerata TOPSIS+VIKOR x 3 bobot)

| formula     | sumber           | kelompok            |   peringkat_rerata |   kali_top10 |   Eform_eV_atom |   densitas_final_gcm3 |   ca_p_ratio |   young_E_deriv_GPa |   bandgap_eV |   layak |
|:------------|:-----------------|:--------------------|-------------------:|-------------:|----------------:|----------------------:|-------------:|--------------------:|-------------:|--------:|
| Ca5P3O12F   | MaterialsProject | apatit_hidroksi     |              1.333 |            6 |          -3.42  |                 3.104 |        1.667 |                 nan |        5.512 |       1 |
| Ca5P3O12F   | MaterialsProject | apatit_hidroksi     |              2.333 |            6 |          -3.421 |                 3.208 |        1.667 |                 nan |        5.517 |       1 |
| Ca10P6CO27  | MaterialsProject | apatit_hidroksi     |              3.333 |            6 |          -3.253 |                 3.053 |        1.667 |                 nan |        5.137 |       1 |
| Ca5P3HO13   | MaterialsProject | apatit_hidroksi     |              4.333 |            6 |          -3.223 |                 3.178 |        1.667 |                 nan |        5.198 |       1 |
| Ca5P3HO13   | MaterialsProject | apatit_hidroksi     |              5.333 |            6 |          -3.223 |                 3.18  |        1.667 |                 nan |        5.212 |       1 |
| Ca10F2O24P6 | AFLOW            | apatit_hidroksi     |              7.167 |            6 |          -3.032 |                 3.096 |        1.667 |                 nan |        5.518 |       1 |
| Ca10F2O24P6 | AFLOW            | apatit_hidroksi     |              8.167 |            6 |          -3.032 |                 3.097 |        1.667 |                 nan |        5.519 |       1 |
| Ca10F2O24P6 | AFLOW            | apatit_hidroksi     |              9.667 |            4 |          -3.032 |                 3.097 |        1.667 |                 nan |        5.518 |       1 |
| Ca10F2O24P6 | AFLOW            | apatit_hidroksi     |              9.667 |            4 |          -3.032 |                 3.097 |        1.667 |                 nan |        5.518 |       1 |
| Ca10F2O24P6 | AFLOW            | apatit_hidroksi     |             11.167 |            2 |          -3.032 |                 3.099 |        1.667 |                 nan |        5.514 |       1 |
| Ca10F2O24P6 | AFLOW            | apatit_hidroksi     |             12.167 |            0 |          -3.032 |                 3.101 |        1.667 |                 nan |        5.518 |       1 |
| Ca10F2O24P6 | AFLOW            | apatit_hidroksi     |             13.167 |            0 |          -3.032 |                 3.1   |        1.667 |                 nan |        5.519 |       1 |
| Ca10F2O24P6 | AFLOW            | apatit_hidroksi     |             14.667 |            0 |          -3.032 |                 3.101 |        1.667 |                 nan |        5.52  |       1 |
| Ca10F2O24P6 | AFLOW            | apatit_hidroksi     |             14.667 |            0 |          -3.032 |                 3.1   |        1.667 |                 nan |        5.521 |       1 |
| Ca4P2O9     | MaterialsProject | tetrakalsium_fosfat |             15.833 |            3 |          -3.326 |                 3.08  |        2     |                 nan |        4.484 |       1 |