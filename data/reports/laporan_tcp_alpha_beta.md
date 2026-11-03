# Laporan Pemisahan alpha/beta-TCP vs Literatur
**Tanggal:** 2026-11-04 05:26:07

- Materials Project: entri kelompok TCP = 1 (['Ca3P2']) -> TIDAK ADA fase TCP murni di MP API saat ini
## Ringkasan per Fasa
|                                 |   0 |
|:--------------------------------|----:|
| ('TCP-P21c (fase lain)', 'COD') |   2 |
| ('alpha-TCP', 'COD')            |   2 |
| ('beta-TCP', 'COD')             |   8 |
| ('beta-TCP (R-3m)', 'AFLOW')    |   6 |
| ('beta-TCP (R-3m)', 'COD')      |   4 |

## beta-TCP (n=8) — literatur R3c (161): a=10.44,  c=37.38, rho=3.07
- a = 10.449 +/- 0.017 A (selisih vs lit: +0.1%)
- c = 37.448 +/- 0.045 A (selisih vs lit: +0.2%)
- densitas = 3.035 +/- 0.018 g/cm3 (selisih vs lit: -1.1%)

## beta-TCP (R-3m) (n=10) — literatur R3c (161): a=10.44,  c=37.38, rho=3.07
- Catatan: geometry AFLOW/COD R-3m berada pada SETTING PRIMITIF rombohedral, sedangkan literatur beta-TCP memakai setting heksagonal -> parameter a/c TIDAK sebanding langsung; yang dibandingkan hanya densitas (independen setting).
- densitas = 3.405 +/- 0.052 g/cm3 (selisih vs lit: +10.9%)

## alpha-TCP (n=2) — literatur P21/a (14): a=12.89, b=27.28, c=15.22, rho=2.86
- a = 12.887 +/- 0.000 A (selisih vs lit: -0.0%)
- b = 27.280 +/- 0.000 A (selisih vs lit: +0.0%)
- c = 15.219 +/- 0.000 A (selisih vs lit: -0.0%)
- densitas = 2.863 +/- 0.000 g/cm3 (selisih vs lit: +0.1%)

## TCP monoklinik P21/c (bukan alpha-TCP; n=2)
| sumber   |      id |    a_A |   b_A |    c_A |
|:---------|--------:|-------:|------:|-------:|
| COD      | 2105285 | 12.835 | 9.096 | 12.836 |
| COD      | 2105285 | 12.835 | 9.096 | 12.836 |
- Catatan: fase P21/c (b ~ 9 A) berbeda dari alpha-TCP (P21/a, b ~ 27 A); tidak dibandingkan dengan literatur alpha-TCP.

## Kesimpulan
- beta-TCP (COD, R3c): parameter kisi cocok dengan literatur (a +0.1%, c +0.2%); densitas -1.1%.
- alpha-TCP (COD, P21/a): entri klasik 1977 (Mathew) cocok hampir eksak (a -0.03%, b 0.0%, c -0.01%); densitas +0.1%.
- AFLOW melaporkan TCP sebagai R-3m (#166) — relaksasi GGA ke supergrup R3c; densitas +10.9% (overbinding khas GGA), dicatat sebagai keterbatasan sumber.