# Laporan Analisis Multiobjektif (MCDM)
**Tanggal:** 2026-11-04 04:59:08
**Tahapan:** Bagian 8 panduan utama

## Kriteria & Arah
- C1 stabilitas (max), C2 densitas->2.0 (max), C3 Ca/P->1.67 (max), C4 modulus->15 GPa (max), C5 bandgap (max), C6 kelayakan ML (max)
- Imputasi median untuk C4/C5 yang hilang (keputusan tercatat).
- Bobot: {'W1_berimbang': array([0.3 , 0.2 , 0.15, 0.15, 0.1 , 0.1 ]), 'W2_stabilitas': array([0.45, 0.15, 0.15, 0.1 , 0.05, 0.1 ]), 'W3_mekanik': array([0.2 , 0.25, 0.1 , 0.3 , 0.05, 0.1 ])}
## Posisi Material Rujukan (peringkat rerata dari 6 skenario)
- HAp: | formula     |   peringkat_rerata |
|:------------|-------------------:|
| Ca5P3HO13   |            23      |
| Ca5P3HO13   |            24.8333 |
| Ca10H2O26P6 |            28.5    |
- TCP: | formula   |   peringkat_rerata |
|:----------|-------------------:|
| Ca3O8P2   |            59.3333 |
| Ca3O8P2   |            59.3333 |
| Ca3O8P2   |            61.3333 |
- Fluorapatit: | formula     |   peringkat_rerata |
|:------------|-------------------:|
| Ca5P3O12F   |            11.3333 |
| Ca10F2O24P6 |            16.1667 |
| Ca10F2O24P6 |            17.1667 |
## Top 15 Kandidat (peringkat rerata TOPSIS+VIKOR x 3 bobot)

| formula     | sumber           | kelompok            |   peringkat_rerata |   kali_top10 |   Eform_eV_atom |   densitas_final_gcm3 |   ca_p_ratio |   young_E_deriv_GPa |   bandgap_eV |   layak |
|:------------|:-----------------|:--------------------|-------------------:|-------------:|----------------:|----------------------:|-------------:|--------------------:|-------------:|--------:|
| Ca10P6CO27  | MaterialsProject | apatit_hidroksi     |              9     |            5 |          -3.253 |                 3.053 |        1.667 |                 nan |        5.137 |       1 |
| Ca5P3O12F   | MaterialsProject | apatit_hidroksi     |             11.333 |            5 |          -3.42  |                 3.104 |        1.667 |                 nan |        5.512 |       1 |
| Ca8P6H12O29 | MaterialsProject | oktakalsium_fosfat  |             14.833 |            3 |          -2.621 |                 2.591 |        1.333 |                 nan |        4.909 |       1 |
| Ca10F2O24P6 | AFLOW            | apatit_hidroksi     |             16.167 |            3 |          -3.032 |                 3.096 |        1.667 |                 nan |        5.518 |       1 |
| Ca10F2O24P6 | AFLOW            | apatit_hidroksi     |             17.167 |            3 |          -3.032 |                 3.097 |        1.667 |                 nan |        5.518 |       1 |
| Ca10P6O25   | MaterialsProject | apatit_hidroksi     |             17.5   |            2 |          -3.319 |                 2.978 |        1.667 |                 nan |        3.148 |       1 |
| Ca10F2O24P6 | AFLOW            | apatit_hidroksi     |             18.167 |            3 |          -3.032 |                 3.097 |        1.667 |                 nan |        5.518 |       1 |
| Ca10P6O25   | MaterialsProject | apatit_hidroksi     |             18.667 |            2 |          -3.318 |                 2.98  |        1.667 |                 nan |        3.078 |       1 |
| Ca10F2O24P6 | AFLOW            | apatit_hidroksi     |             19.167 |            3 |          -3.032 |                 3.097 |        1.667 |                 nan |        5.519 |       1 |
| Ca10F2O24P6 | AFLOW            | apatit_hidroksi     |             20.333 |            2 |          -3.032 |                 3.099 |        1.667 |                 nan |        5.514 |       1 |
| Ca10F2O24P6 | AFLOW            | apatit_hidroksi     |             21.333 |            0 |          -3.032 |                 3.1   |        1.667 |                 nan |        5.519 |       1 |
| Ca16O36P8   | AFLOW            | tetrakalsium_fosfat |             21.333 |            1 |          -2.937 |                 2.976 |        2     |                 nan |        4.48  |       1 |
| Ca16O36P8   | AFLOW            | tetrakalsium_fosfat |             21.333 |            1 |          -2.937 |                 2.976 |        2     |                 nan |        4.48  |       1 |
| Ca4P2O9     | MaterialsProject | tetrakalsium_fosfat |             22.167 |            2 |          -3.326 |                 3.08  |        2     |                 nan |        4.484 |       1 |
| Ca10F2O24P6 | AFLOW            | apatit_hidroksi     |             22.333 |            0 |          -3.032 |                 3.1   |        1.667 |                 nan |        5.521 |       1 |