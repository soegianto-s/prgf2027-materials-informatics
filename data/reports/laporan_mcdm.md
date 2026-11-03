# Laporan Analisis Multiobjektif (MCDM)
**Tanggal:** 2026-11-04 05:53:56
**Tahapan:** Bagian 8 panduan utama

## Kriteria & Arah
- C1 stabilitas (max), C2 densitas->2.0 (max), C3 Ca/P->1.67 (max), C4 modulus->15 GPa (max), C5 bandgap (max), C6 kelayakan ML (max)
- Imputasi median untuk C4/C5 yang hilang (keputusan tercatat).
- Bobot: {'W1_berimbang': array([0.3 , 0.2 , 0.15, 0.15, 0.1 , 0.1 ]), 'W2_stabilitas': array([0.45, 0.15, 0.15, 0.1 , 0.05, 0.1 ]), 'W3_mekanik': array([0.2 , 0.25, 0.1 , 0.3 , 0.05, 0.1 ])}
## Posisi Material Rujukan (peringkat rerata dari 6 skenario)
- HAp: | formula     |   peringkat_rerata |
|:------------|-------------------:|
| Ca10H2O26P6 |            15.3333 |
| Ca10H2O26P6 |            16.3333 |
| Ca10H2O26P6 |            32.1667 |
- TCP: | formula   |   peringkat_rerata |
|:----------|-------------------:|
| Ca3O8P2   |            31.8333 |
| Ca3O8P2   |            31.8333 |
| Ca3O8P2   |            38.6667 |
- Fluorapatit: | formula     |   peringkat_rerata |
|:------------|-------------------:|
| Ca10F2O24P6 |            4.66667 |
| Ca10F2O24P6 |            5.66667 |
| Ca10F2O24P6 |            6.66667 |
## Top 15 Kandidat (peringkat rerata TOPSIS+VIKOR x 3 bobot)

| formula     | sumber   | kelompok            |   peringkat_rerata |   kali_top10 |   Eform_eV_atom |   densitas_final_gcm3 |   ca_p_ratio |   young_E_deriv_GPa |   bandgap_eV |   layak |
|:------------|:---------|:--------------------|-------------------:|-------------:|----------------:|----------------------:|-------------:|--------------------:|-------------:|--------:|
| Ca10F2O24P6 | AFLOW    | apatit_hidroksi     |              4.667 |            5 |          -3.032 |                 3.096 |        1.667 |                 nan |        5.518 |       1 |
| Ca10F2O24P6 | AFLOW    | apatit_hidroksi     |              5.667 |            5 |          -3.032 |                 3.097 |        1.667 |                 nan |        5.518 |       1 |
| Ca10F2O24P6 | AFLOW    | apatit_hidroksi     |              6.667 |            5 |          -3.032 |                 3.097 |        1.667 |                 nan |        5.518 |       1 |
| Ca10F2O24P6 | AFLOW    | apatit_hidroksi     |              7.667 |            5 |          -3.032 |                 3.097 |        1.667 |                 nan |        5.519 |       1 |
| Ca10F2O24P6 | AFLOW    | apatit_hidroksi     |              8.667 |            4 |          -3.032 |                 3.099 |        1.667 |                 nan |        5.514 |       1 |
| Ca10F2O24P6 | AFLOW    | apatit_hidroksi     |              9.667 |            4 |          -3.032 |                 3.1   |        1.667 |                 nan |        5.519 |       1 |
| Ca10F2O24P6 | AFLOW    | apatit_hidroksi     |             10.667 |            3 |          -3.032 |                 3.1   |        1.667 |                 nan |        5.521 |       1 |
| Ca16O36P8   | AFLOW    | tetrakalsium_fosfat |             11.333 |            3 |          -2.937 |                 2.976 |        2     |                 nan |        4.48  |       1 |
| Ca16O36P8   | AFLOW    | tetrakalsium_fosfat |             11.333 |            3 |          -2.937 |                 2.976 |        2     |                 nan |        4.48  |       1 |
| Ca10F2O24P6 | AFLOW    | apatit_hidroksi     |             11.667 |            3 |          -3.032 |                 3.101 |        1.667 |                 nan |        5.518 |       1 |
| Ca10F2O24P6 | AFLOW    | apatit_hidroksi     |             12.667 |            2 |          -3.032 |                 3.101 |        1.667 |                 nan |        5.52  |       1 |
| Ca10F2O24P6 | AFLOW    | apatit_hidroksi     |             13.667 |            2 |          -3.032 |                 3.101 |        1.667 |                 nan |        5.518 |       1 |
| Ca10F2O24P6 | AFLOW    | apatit_hidroksi     |             14.667 |            0 |          -3.032 |                 3.102 |        1.667 |                 nan |        5.518 |       1 |
| Ca10H2O26P6 | AFLOW    | apatit_hidroksi     |             15.333 |            2 |          -2.84  |                 3.051 |        1.667 |                 nan |        5.204 |       1 |
| Ca10F2O24P6 | AFLOW    | apatit_hidroksi     |             15.667 |            0 |          -3.032 |                 3.103 |        1.667 |                 nan |        5.522 |       1 |