"""Patch manuskrip: perbaikan inkonsistensi internal reviewer ronde 3 (satu pass)."""
p = r"D:\latex\prgf2026\data\reports\manuscript\manuscript.tex"
s = open(p, encoding="utf-8", newline="").read()
n0 = len(s)

# 1) Abstrak: angka model baru
s = s.replace(
 "The formation-energy model (nested SVR) attains $R^2 = 0.48$ (MAE 0.27 eV/atom) across all computed entries and $R^2 = 0.58$ within the phosphate family; applied to an external database at matching compositions, it attains $R^2 = 0.88$. The models reproduce experimental standard formation enthalpies and densities of six calcium phosphate phases with MAEs of 0.25 eV/atom and 0.18 g/cm$^3$, respectively.",
 "Composition descriptors of this five-element system carry exactly four independent degrees of freedom, and on those four the formation-energy model (nested SVR) attains $R^2 = 0.11$ (MAE 0.30 eV/atom) with no predictive power within the phosphate family alone ($R^2 < 0$); admitting structure-informed screening features (cell volume, density) raises this to $R^2 = 0.40$. The models nevertheless reproduce experimental standard formation enthalpies and densities of six phosphate phases with MAEs of 0.09 eV/atom and 0.11 g/cm$^3$, respectively.")
s = s.replace(
 "at matching compositions, the formation-energy model transfers across databases with $R^2 = 0.88$ (280 OQMD entries).",
 "at matching compositions, the formation-energy model transfers across databases with $R^2 = 0.83$ (280 OQMD entries).")

# 2) Methods 2.3: penjelasan 4-DOF + AFLOW dikecualikan
s = s.replace(
 "(iii) Discovery-appropriate features:} the headline model uses composition-only descriptors (Ca/P, average electronegativity, molecular weight, element fractions);",
 "(iii) Discovery-appropriate features:} the headline model uses composition-only descriptors. For this five-element system the composition itself has only four independent degrees of freedom (the five element fractions sum to one, and Ca/P then fixes the Ca fraction), and composition-derived quantities such as average electronegativity and molecular weight are exact linear functions of those four; all redundant descriptors (VIF $= \\infty$) were therefore removed, leaving {Ca/P, P, H, F fractions}.")
s = s.replace(
 "Because formation-energy scales differ systematically between databases (AFLOW deviates from Materials Project/OQMD by up to 0.8 eV/atom for phosphides, whereas the latter two agree within 0.02 eV/atom on overlapping compositions), the external test uses OQMD entries, whose compositions, however, all appear in the training sources;",
 "Because formation-energy scales differ systematically between databases (AFLOW deviates from Materials Project/OQMD by up to 0.8 eV/atom for phosphides, whereas the latter two agree within 0.02 eV/atom on overlapping compositions), the formation-energy models were trained on the scale-consistent Materials Project + OQMD subset ($n=337$) with AFLOW excluded; a structure-informed screening variant trained on Materials Project + AFLOW ($n=291$) is reported separately. The cross-database test trains on Materials Project alone ($n=57$) and predicts OQMD entries ($n=280$), whose compositions, however, all appear in the training sources;")

# 3) tab:ml angka baru
s = s.replace("Formation energy, all entries ($n=571$) & SVR (nested) & 0.483 & 0.465 & 0.265 \\\\",
              "Formation energy, composition-only ($n=337$) & SVR (nested) & 0.113 & 0.439 & 0.297 \\\\")
s = s.replace("Formation energy, phosphates only ($n=215$) & SVR & 0.580 & 0.284 & 0.176 \\\\",
              "Formation energy, phosphates only ($n=157$) & SVR & $-0.516$ & 0.191 & 0.139 \\\\")
s = s.replace("Formation energy, screening variant ($n=291$) & SVR (nested) & 0.489 & 0.448 & 0.242 \\\\",
              "Formation energy, screening variant ($n=291$) & SVR (nested) & 0.401 & 0.502 & 0.304 \\\\")
s = s.replace("Cross-database, same compositions ($n=280$) & SVR & 0.883 & 0.385 & 0.254 \\\\",
              "Cross-database, same compositions ($n=280$) & SVR & 0.833 & 0.460 & 0.268 \\\\")
s = s.replace("Density, composition-only ($n=571$) & Random forest & 0.174 & 0.400 & 0.264 \\\\",
              "Density, composition-only ($n=571$) & Random forest & 0.018 & 0.441 & 0.307 \\\\")

# 4) Paragraf 3.2 angka baru
s = s.replace(
 "With composition-only descriptors---the honest discovery setting---the nested SVR attains $R^2 = 0.483$ (MAE 0.265 eV/atom) across all 571 computed entries, and $R^2 = 0.580$ (MAE 0.176 eV/atom) within the phosphate family alone, confirming that part of the headline $R^2$ previously obtainable with structure-informed features reflected the trivial separation of phosphides from phosphates. A structure-informed variant (volume + density as features, valid only for screening existing database entries, $n=291$) attains $R^2 = 0.489$. The composition-only density model attains only $R^2 = 0.174$",
 "With the four independent composition descriptors---the honest discovery setting---the nested SVR attains $R^2 = 0.113$ (MAE 0.297 eV/atom) across the 337 scale-consistent entries (Materials Project + OQMD), and $R^2 = -0.516$ within the phosphate family alone: composition alone carries essentially no within-family predictive power, and earlier headline scores reflected the trivial phosphide--phosphate separation and structure features. A structure-informed variant (cell volume + density as features, valid only for screening existing database entries, $n=291$) attains $R^2 = 0.401$. The composition-only density model attains essentially zero ($R^2 = 0.018$)")
s = s.replace(
 "On the external OQMD database at matching compositions, the composition-only formation-energy model attains $R^2 = 0.883$ (MAE 0.254 eV/atom); we emphasize that all OQMD compositions also occur in the training sources, so this is a same-composition cross-database transfer test, not composition extrapolation.",
 "Trained on Materials Project alone ($n=57$) and tested on 280 OQMD entries at matching compositions, the model attains $R^2 = 0.833$ (MAE 0.268 eV/atom); we emphasize that this is a same-composition cross-database transfer test, not composition extrapolation.")

# 5) Benchmark paragraph + tab:bench
s = s.replace(
 "The formation-energy model reproduces experiment with MAE 0.254 eV/atom (best: monetite $+0.08$, TTCP $+0.16$ eV/atom; largest: $\\alpha$-TCP $+0.35$ eV/atom, reflecting the wide scatter of metastable-phase entries in the training sources). The composition-only density model reproduces experimental densities with MAE 0.177 g/cm$^3$---weaker than the formation-energy result, as expected for a packing-dominated property predicted from stoichiometry alone. In addition, at matching compositions the formation-energy model transfers across databases with $R^2 = 0.883$ (RMSE 0.385 eV/atom) on 280 OQMD entries.",
 "The formation-energy model reproduces experiment with MAE 0.094 eV/atom (largest error: brushite, a hydrated phase outside the effectively anhydrous training distribution), and the composition-only density model reproduces experimental densities with MAE 0.114 g/cm$^3$. We note that this benchmark covers six well-known phosphate phases and is therefore a narrow, same-family test; the grouped-CV numbers in Table~\\ref{tab:ml} remain the honest estimate of broad performance.")
rows_lama = [("$-2.890$", "3.056", "$-0.104$"), ("$-2.936$", "3.365", "$+0.295$"), ("$-2.936$", "3.365", "$+0.505$"),
             ("$-3.132$", "3.060", "$+0.010$"), ("$-2.608$", "2.836", "$-0.084$"), ("$-2.025$", "2.247", "$-0.063$")]
rows_baru = [("$-3.176$", "3.173", "$+0.013$"), ("$-3.214$", "3.219", "$+0.149$"), ("$-3.214$", "3.219", "$+0.359$"),
             ("$-3.248$", "3.110", "$+0.060$"), ("$-2.635$", "2.919", "$-0.001$"), ("$-2.020$", "2.412", "$+0.102$")]
for (a, b, c), (x, y, z) in zip(rows_lama, rows_baru):
    s = s.replace(f"& {a} & {b} & {c} \\\\", f"& {x} & {y} & {z} \\\\", 1)
s = s.replace("MAE & & 0.254 & & & 0.177 \\\\", "MAE & & 0.094 & & & 0.114 \\\\")

# 6) QC paragraf: pengecualian densitas AFLOW TCP
s = s.replace("The agreement is good (densities within 2.9\\%;",
              "The agreement is good for densities (within 2.9\\%, except AFLOW TCP at $+10.9$\\%, a GGA artifact noted below;")

# 7) Fig 1 & Fig 2 caption + teks EDA
s = s.replace("mapped by PCA over seven physicochemical descriptors", "mapped by PCA over five non-collinear descriptors")
s = s.replace("captures 61.1\\% of the variance in the first two components", "captures 59.3\\% of the variance in the first two components")
s = s.replace("(silhouette 0.552) is highly consistent with hierarchical Ward clustering (ARI = 0.907)", "(silhouette 0.502) is consistent with hierarchical Ward clustering (ARI = 0.884)")
s = s.replace("HDBSCAN identifies 17 dense clusters with 1{,}266 noise points", "HDBSCAN identifies 17 dense clusters with 1{,}246 noise points")
s = s.replace("94\\% of the five nearest neighbors", "88\\% of the five nearest neighbors")
s = s.replace("Hydroxyapatite-family phases concentrate near 3.0--3.2 g/cm$^3$, close to bone mineral.",
              "Hydroxyapatite-family phases concentrate near 3.0--3.2 g/cm$^3$, i.e., the density of the bone-mineral phase itself; the MCDM density criterion (band 1.0--3.2 g/cm$^3$) admits all clinically processable ceramics.")

# 8) tab:top: rank ordinal 1-15
for lama, baru in [("1.3", "1"), ("4.3", "2"), ("4.8", "3"), ("5.5", "4"), ("9.7", "5"), ("19.0", "6"),
                   ("28.5", "7"), ("29.8", "8"), ("36.2", "9"), ("36.8", "10"), ("39.0", "11"),
                   ("40.3", "12"), ("41.7", "13"), ("41.8", "14"), ("44.5", "15")]:
    s = s.replace(f"& {lama} & $", f"& {baru} & $", 1)

# 9) Discussion: angka akurasi + temuan 4-DOF
s = s.replace(
 "The honest composition-only models reach MAE 0.27 eV/atom (formation energy) and 0.26 g/cm$^3$ (density)---well behind graph-neural-network state of the art",
 "The honest composition-only models reach MAE 0.30 eV/atom (formation energy) and 0.31 g/cm$^3$ (density)---well behind graph-neural-network state of the art")
s = s.replace(
 "Reduced-formula grouping, nested CV, and composition-only features materially lowered reported scores (e.g., formation-energy $R^2$ from 0.87 to 0.48 in the discovery setting)---we report the conservative numbers throughout.",
 "Reduced-formula grouping, nested CV, and the four-DOF composition feature set materially lowered reported scores (formation-energy $R^2$ from 0.87 to 0.11 in the discovery setting); a further structural finding is that composition alone has no within-phosphate predictive power ($R^2<0$), which argues strongly for structure-aware surrogates. We report the conservative numbers throughout.")

# 10) Kesimpulan angka
s = s.replace(
 "formation energies of six calcium phosphate phases with MAE 0.25 eV/atom, and densities with MAE 0.18 g/cm$^3$.",
 "formation energies of six calcium phosphate phases with MAE 0.09 eV/atom, and densities with MAE 0.11 g/cm$^3$.")

open(p, "w", encoding="utf-8", newline="").write(s)
print("manuskrip diperbarui; panjang:", n0, "->", len(s))
