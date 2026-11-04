"""Patch manuskrip ronde 3 (final): sisa patch manuscript.tex yang gagal/terlewat
+ port lengkap angka ronde 3 ke manuscript_elsarticle.tex (format jurnal resmi).

Setiap replace memakai assertion (harus ketemu tepat 1x) — tidak ada kegagalan diam-diam.
"""
from pathlib import Path

MS = Path(r"D:\latex\prgf2027\data\reports\manuscript")


def baca(nama):
    return (MS / nama).read_text(encoding="utf-8")


def ganti(s, lama, baru, label):
    n = s.count(lama)
    assert n == 1, f"[{label}] ketemu {n}x (harus 1): {lama[:80]}..."
    return s.replace(lama, baru)


# ============================================================
# Bagian A: sisa manuscript.tex (replacement ronde 3 yang gagal + SHAP/XAI baru)
# ============================================================
t = baca("manuscript.tex")

# A1. Baris tab:bench (replacement ronde 3 gagal karena kolom densitas-eksp tak dihitung)
for (nama, exp_e, lama_e, exp_d, lama_d, lama_dd), (_, _, baru_e, _, baru_d, baru_dd) in zip(
        [("Hydroxyapatite", "$-3.159$", "$-2.890$", "3.16", "3.056", "$-0.104$"),
         (r"$\beta$-TCP", "$-3.285$", "$-2.936$", "3.07", "3.365", "$+0.295$"),
         (r"$\alpha$-TCP", "$-3.289$", "$-2.936$", "2.86", "3.365", "$+0.505$"),
         ("TTCP", "$-3.297$", "$-3.132$", "3.05", "3.060", "$+0.010$"),
         ("Monetite (DCPA)", "$-2.686$", "$-2.608$", "2.92", "2.836", "$-0.084$"),
         ("Brushite (DCPD)", "$-1.717$", "$-2.025$", "2.31", "2.247", "$-0.063$")],
        [("Hydroxyapatite", "$-3.159$", "$-3.176$", "3.16", "3.173", "$+0.013$"),
         (r"$\beta$-TCP", "$-3.285$", "$-3.214$", "3.07", "3.219", "$+0.149$"),
         (r"$\alpha$-TCP", "$-3.289$", "$-3.214$", "2.86", "3.219", "$+0.359$"),
         ("TTCP", "$-3.297$", "$-3.248$", "3.05", "3.110", "$+0.060$"),
         ("Monetite (DCPA)", "$-2.686$", "$-2.635$", "2.92", "2.919", "$-0.001$"),
         ("Brushite (DCPD)", "$-1.717$", "$-2.020$", "2.31", "2.412", "$+0.102$")]):
    t = ganti(t, f"{nama} & {exp_e} & {lama_e} & {exp_d} & {lama_d} & {lama_dd} \\\\",
              f"{nama} & {exp_e} & {baru_e} & {exp_d} & {baru_d} & {baru_dd} \\\\", f"A1 {nama}")

# A2. Silhouette/ARI (replacement ronde 3 gagal karena koma-sebelum-silhouette)
t = ganti(t,
          "K-means ($k=5$, silhouette 0.552) is highly consistent with hierarchical Ward clustering (ARI = 0.907)",
          "K-means ($k=5$, silhouette 0.502) is consistent with hierarchical Ward clustering (ARI = 0.884)",
          "A2 silhouette")

# A3. Kaption t-SNE + Discussion: 94% -> 88% (konsisten dengan laporan_eda.md 0.88)
t = ganti(t, "revealing source-driven separation (94\\% same-source nearest neighbors)",
          "revealing source-driven separation (88\\% same-source nearest neighbors)", "A3 t-SNE caption")
t = ganti(t, "The dataset is source-biased (94\\% same-source nearest neighbors)",
          "The dataset is source-biased (88\\% same-source nearest neighbors)", "A3 discussion")

# A4. Kalimat VIF di Results 3.1 (laporan_eda baru: tak ada pasangan |r|>0.85, VIF < 5)
t = ganti(t,
          "Correlation analysis identified two redundant descriptor pairs with EN$_\\mathrm{avg}$ ($r > 0.85$), confirmed by VIF values up to 24.",
          "Correlation analysis identified two descriptor pairs redundant with EN$_\\mathrm{avg}$ ($r > 0.85$, VIF up to 24), which were removed; in the retained descriptor set no pair exceeds $|r| = 0.85$ and all VIFs are below 5.",
          "A4 VIF")

# A5. Abstract: MAE validasi independen (terlewat ronde 3)
t = ganti(t,
          "with MAE 0.25 eV/atom, and the density model reproduces experimental densities with MAE 0.18 g/cm$^3$",
          "with MAE 0.09 eV/atom, and the density model reproduces experimental densities with MAE 0.11 g/cm$^3$",
          "A5 abstract MAE")

# A6. Abstract: kalimat SHAP (fitur 4-DOF baru)
t = ganti(t,
          "SHAP analysis identifies the oxygen fraction and molecular weight as the dominant descriptors, with the caveat that part of their importance separates the phosphide and phosphate families.",
          "SHAP analysis identifies the phosphorus fraction and the Ca/P ratio as the dominant descriptors, with the caveat that part of their importance separates the phosphide and phosphate families.",
          "A6 abstract SHAP")

# A7. Results 3.4: paragraf SHAP (hasil XAI 4-DOF: frac_P, ca_p_ratio; corr densitas -0.43)
t = ganti(t,
          "SHAP analysis (Fig.~\\ref{fig:shap}) on the composition-only formation-energy model identifies the oxygen fraction and molecular weight as the dominant descriptors (confirmed by permutation importance); we caution that part of this importance reflects the separation of the phosphide and phosphate families rather than a mechanistic insight, consistent with the within-family results in Table~\\ref{tab:ml}. For the density model, average electronegativity and oxygen fraction dominate, and the SHAP correlation of Ca/P with predicted density is $+0.47$.",
          "SHAP analysis (Fig.~\\ref{fig:shap}) on the composition-only models identifies the phosphorus fraction and the Ca/P ratio as the dominant descriptors for both formation energy and density (confirmed by permutation importance, with the hydrogen fraction third); we caution that part of this importance reflects the separation of the phosphide and phosphate families rather than a mechanistic insight, consistent with the within-family results in Table~\\ref{tab:ml}. For the density model, the SHAP contribution of Ca/P correlates negatively with Ca/P itself ($-0.43$): higher Ca/P pushes density predictions downward, a direction we do not overinterpret given the near-zero composition-only predictive power.",
          "A7 SHAP paragraph")

# A8. Kapitalisasi lanjutan kalimat setelah "leaving {Ca/P, P, H, F fractions}."
t = ganti(t, "leaving {Ca/P, P, H, F fractions}. cell volume and density---",
          "leaving {Ca/P, P, H, F fractions}. Cell volume and density---", "A8 kapitalisasi")

(MS / "manuscript.tex").write_text(t, encoding="utf-8", newline="")
print("manuscript.tex selesai")

# ============================================================
# Bagian B: port lengkap ke manuscript_elsarticle.tex
# ============================================================
e = baca("manuscript_elsarticle.tex")

# B1. Abstract: kalimat model energi pembentukan
e = ganti(e,
          "The formation-energy model (nested SVR) attains $R^2 = 0.48$ (MAE 0.27 eV/atom) across all computed entries and $R^2 = 0.58$ within the phosphate family; applied to an external database at matching compositions, it attains $R^2 = 0.88$. The models reproduce experimental standard formation enthalpies and densities of six calcium phosphate phases with MAEs of 0.25 eV/atom and 0.18 g/cm$^3$, respectively.",
          "Composition descriptors of this five-element system carry exactly four independent degrees of freedom, and on those four the formation-energy model (nested SVR) attains $R^2 = 0.11$ (MAE 0.30 eV/atom) with no predictive power within the phosphate family alone ($R^2 < 0$); admitting structure-informed screening features (cell volume, density) raises this to $R^2 = 0.40$. The models nevertheless reproduce experimental standard formation enthalpies and densities of six phosphate phases with MAEs of 0.09 eV/atom and 0.11 g/cm$^3$, respectively.",
          "B1 abstract model")

# B2. Abstract: validasi independen (MAE + transfer 0.88 -> 0.83)
e = ganti(e,
          "with MAE 0.25 eV/atom, and the density model reproduces experimental densities with MAE 0.18 g/cm$^3$; at matching compositions, the formation-energy model transfers across databases with $R^2 = 0.88$ (280 OQMD entries)",
          "with MAE 0.09 eV/atom, and the density model reproduces experimental densities with MAE 0.11 g/cm$^3$; at matching compositions, the formation-energy model transfers across databases with $R^2 = 0.83$ (280 OQMD entries)",
          "B2 abstract validasi")

# B3. Abstract: kalimat SHAP
e = ganti(e,
          "SHAP analysis identifies the oxygen fraction and molecular weight as the dominant descriptors, with the caveat that part of their importance separates the phosphide and phosphate families.",
          "SHAP analysis identifies the phosphorus fraction and the Ca/P ratio as the dominant descriptors, with the caveat that part of their importance separates the phosphide and phosphate families.",
          "B3 abstract SHAP")

# B4. Methods 2.3: 4-DOF + AFLOW dikecualikan
e = ganti(e,
          "(iii) Discovery-appropriate features:} the headline model uses composition-only descriptors (Ca/P, average electronegativity, molecular weight, element fractions); cell volume and density---which are unavailable for unknown materials, and which make the density ``model'' a near-tautology $\\rho = MZ/(N_A V)$---are used only in a clearly labeled screening scenario for ranking existing database entries. Because formation-energy scales differ systematically between databases (AFLOW deviates from Materials Project/OQMD by up to 0.8 eV/atom for phosphides, whereas the latter two agree within 0.02 eV/atom on overlapping compositions), the external test uses OQMD entries, whose compositions, however, all appear in the training sources; the test is therefore a same-composition cross-database transfer test, not a composition-extrapolation test, and is reported as such.",
          "(iii) Discovery-appropriate features:} the headline model uses composition-only descriptors. For this five-element system the composition itself has only four independent degrees of freedom (the five element fractions sum to one, and Ca/P then fixes the Ca fraction), and composition-derived quantities such as average electronegativity and molecular weight are exact linear functions of those four; all redundant descriptors (VIF $= \\infty$) were therefore removed, leaving {Ca/P, P, H, F fractions}. Cell volume and density---which are unavailable for unknown materials, and which make the density ``model'' a near-tautology $\\rho = MZ/(N_A V)$---are used only in a clearly labeled screening scenario for ranking existing database entries. Because formation-energy scales differ systematically between databases (AFLOW deviates from Materials Project/OQMD by up to 0.8 eV/atom for phosphides, whereas the latter two agree within 0.02 eV/atom on overlapping compositions), the formation-energy models were trained on the scale-consistent Materials Project + OQMD subset ($n=337$) with AFLOW excluded; a structure-informed screening variant trained on Materials Project + AFLOW ($n=291$) is reported separately. The cross-database test trains on Materials Project alone ($n=57$) and predicts OQMD entries ($n=280$), whose compositions, however, all appear in the training sources; the test is therefore a same-composition cross-database transfer test, not a composition-extrapolation test, and is reported as such.",
          "B4 methods 2.3")

# B5. Results 3.1: VIF + PCA 59.3 + silhouette + noise 1246
e = ganti(e,
          "Correlation analysis identified two redundant descriptor pairs with EN$_\\mathrm{avg}$ ($r > 0.85$), confirmed by VIF values up to 24.",
          "Correlation analysis identified two descriptor pairs redundant with EN$_\\mathrm{avg}$ ($r > 0.85$, VIF up to 24), which were removed; in the retained descriptor set no pair exceeds $|r| = 0.85$ and all VIFs are below 5.",
          "B5 VIF")
e = ganti(e, "captures 61.1\\% of the variance in the first two components",
          "captures 59.3\\% of the variance in the first two components", "B5 PCA")
e = ganti(e,
          "K-means ($k=5$, silhouette 0.552) is highly consistent with hierarchical Ward clustering (ARI = 0.907)",
          "K-means ($k=5$, silhouette 0.502) is consistent with hierarchical Ward clustering (ARI = 0.884)",
          "B5 silhouette")
e = ganti(e, "HDBSCAN identifies 17 dense clusters with 1{,}266 noise points",
          "HDBSCAN identifies 17 dense clusters with 1{,}246 noise points", "B5 HDBSCAN")

# B6. Bias sumber 94 -> 88 (prosa + kaption t-SNE + Discussion)
e = ganti(e, "94\\% of the five nearest neighbors", "88\\% of the five nearest neighbors", "B6 prosa")
e = ganti(e, "revealing source-driven separation (94\\% same-source nearest neighbors)",
          "revealing source-driven separation (88\\% same-source nearest neighbors)", "B6 t-SNE caption")
e = ganti(e, "The dataset is source-biased (94\\% same-source nearest neighbors)",
          "The dataset is source-biased (88\\% same-source nearest neighbors)", "B6 discussion")

# B7. Kaption figur: PCA + densitas
e = ganti(e, "mapped by PCA over seven physicochemical descriptors",
          "mapped by PCA over five non-collinear descriptors", "B7 PCA caption")
e = ganti(e, "Hydroxyapatite-family phases concentrate near 3.0--3.2 g/cm$^3$, close to bone mineral.",
          "Hydroxyapatite-family phases concentrate near 3.0--3.2 g/cm$^3$, i.e., the density of the bone-mineral phase itself; the MCDM density criterion (band 1.0--3.2 g/cm$^3$) admits all clinically processable ceramics.",
          "B7 densitas caption")

# B8. Paragraf 3.2 (angka model)
e = ganti(e,
          "With composition-only descriptors---the honest discovery setting---the nested SVR attains $R^2 = 0.483$ (MAE 0.265 eV/atom) across all 571 computed entries, and $R^2 = 0.580$ (MAE 0.176 eV/atom) within the phosphate family alone, confirming that part of the headline $R^2$ previously obtainable with structure-informed features reflected the trivial separation of phosphides from phosphates. A structure-informed variant (volume + density as features, valid only for screening existing database entries, $n=291$) attains $R^2 = 0.489$. The composition-only density model attains only $R^2 = 0.174$---expected, since crystal density is governed by packing, not stoichiometry; the $[M, V]$-based variant is a near-tautology ($\\rho = MZ/N_A V$, with $Z$ unobserved) and is reported as a data-consistency check, not a model. On the external OQMD database at matching compositions, the composition-only formation-energy model attains $R^2 = 0.883$ (MAE 0.254 eV/atom); we emphasize that all OQMD compositions also occur in the training sources, so this is a same-composition cross-database transfer test, not composition extrapolation.",
          "With the four independent composition descriptors---the honest discovery setting---the nested SVR attains $R^2 = 0.113$ (MAE 0.297 eV/atom) across the 337 scale-consistent entries (Materials Project + OQMD), and $R^2 = -0.516$ within the phosphate family alone: composition alone carries essentially no within-family predictive power, and earlier headline scores reflected the trivial phosphide--phosphate separation and structure features. A structure-informed variant (cell volume + density as features, valid only for screening existing database entries, $n=291$) attains $R^2 = 0.401$. The composition-only density model attains essentially zero ($R^2 = 0.018$)---expected, since crystal density is governed by packing, not stoichiometry; the $[M, V]$-based variant is a near-tautology ($\\rho = MZ/N_A V$, with $Z$ unobserved) and is reported as a data-consistency check, not a model. Trained on Materials Project alone ($n=57$) and tested on 280 OQMD entries at matching compositions, the model attains $R^2 = 0.833$ (MAE 0.268 eV/atom); we emphasize that this is a same-composition cross-database transfer test, not composition extrapolation.",
          "B8 paragraf 3.2")

# B9. tab:ml
e = ganti(e, "Formation energy, all entries ($n=571$) & SVR (nested) & 0.483 & 0.465 & 0.265 \\\\",
          "Formation energy, composition-only ($n=337$) & SVR (nested) & 0.113 & 0.439 & 0.297 \\\\", "B9 ml-1")
e = ganti(e, "Formation energy, phosphates only ($n=215$) & SVR & 0.580 & 0.284 & 0.176 \\\\",
          "Formation energy, phosphates only ($n=157$) & SVR & $-0.516$ & 0.191 & 0.139 \\\\", "B9 ml-2")
e = ganti(e, "Formation energy, screening variant ($n=291$) & SVR (nested) & 0.489 & 0.448 & 0.242 \\\\",
          "Formation energy, screening variant ($n=291$) & SVR (nested) & 0.401 & 0.502 & 0.304 \\\\", "B9 ml-3")
e = ganti(e, "Cross-database, same compositions ($n=280$) & SVR & 0.883 & 0.385 & 0.254 \\\\",
          "Cross-database, same compositions ($n=280$) & SVR & 0.833 & 0.460 & 0.268 \\\\", "B9 ml-4")
e = ganti(e, "Density, composition-only ($n=571$) & Random forest & 0.174 & 0.400 & 0.264 \\\\",
          "Density, composition-only ($n=571$) & Random forest & 0.018 & 0.441 & 0.307 \\\\", "B9 ml-5")

# B10. tab:top: rank ordinal 1-15
for lama, baru in [("1.3", "1"), ("4.3", "2"), ("4.8", "3"), ("5.5", "4"), ("9.7", "5"),
                   ("19.0", "6"), ("28.5", "7"), ("29.8", "8"), ("36.2", "9"), ("36.8", "10"),
                   ("39.0", "11"), ("40.3", "12"), ("41.7", "13"), ("41.8", "14"), ("44.5", "15")]:
    e = ganti(e, f"& {lama} & $", f"& {baru} & $", f"B10 rank {lama}")

# B11. QC paragraf
e = ganti(e, "The agreement is good (densities within 2.9\\%;",
          "The agreement is good for densities (within 2.9\\%, except AFLOW TCP at $+10.9$\\%, a GGA artifact noted below;",
          "B11 QC")

# B12. Paragraf validasi independen
e = ganti(e,
          "The formation-energy model reproduces experiment with MAE 0.254 eV/atom (best: monetite $+0.08$, TTCP $+0.16$ eV/atom; largest: $\\alpha$-TCP $+0.35$ eV/atom, reflecting the wide scatter of metastable-phase entries in the training sources). The composition-only density model reproduces experimental densities with MAE 0.177 g/cm$^3$---weaker than the formation-energy result, as expected for a packing-dominated property predicted from stoichiometry alone. In addition, at matching compositions the formation-energy model transfers across databases with $R^2 = 0.883$ (RMSE 0.385 eV/atom) on 280 OQMD entries.",
          "The formation-energy model reproduces experiment with MAE 0.094 eV/atom (largest error: brushite, a hydrated phase outside the effectively anhydrous training distribution), and the composition-only density model reproduces experimental densities with MAE 0.114 g/cm$^3$. We note that this benchmark covers six well-known phosphate phases and is therefore a narrow, same-family test; the grouped-CV numbers in Table~\\ref{tab:ml} remain the honest estimate of broad performance.",
          "B12 validasi independen")

# B13. tab:bench rows
for (nama, exp_e, lama_e, exp_d, lama_d, lama_dd), (_, _, baru_e, _, baru_d, baru_dd) in zip(
        [("Hydroxyapatite", "$-3.159$", "$-2.890$", "3.16", "3.056", "$-0.104$"),
         (r"$\beta$-TCP", "$-3.285$", "$-2.936$", "3.07", "3.365", "$+0.295$"),
         (r"$\alpha$-TCP", "$-3.289$", "$-2.936$", "2.86", "3.365", "$+0.505$"),
         ("TTCP", "$-3.297$", "$-3.132$", "3.05", "3.060", "$+0.010$"),
         ("Monetite (DCPA)", "$-2.686$", "$-2.608$", "2.92", "2.836", "$-0.084$"),
         ("Brushite (DCPD)", "$-1.717$", "$-2.025$", "2.31", "2.247", "$-0.063$")],
        [("Hydroxyapatite", "$-3.159$", "$-3.176$", "3.16", "3.173", "$+0.013$"),
         (r"$\beta$-TCP", "$-3.285$", "$-3.214$", "3.07", "3.219", "$+0.149$"),
         (r"$\alpha$-TCP", "$-3.289$", "$-3.214$", "2.86", "3.219", "$+0.359$"),
         ("TTCP", "$-3.297$", "$-3.248$", "3.05", "3.110", "$+0.060$"),
         ("Monetite (DCPA)", "$-2.686$", "$-2.635$", "2.92", "2.919", "$-0.001$"),
         ("Brushite (DCPD)", "$-1.717$", "$-2.020$", "2.31", "2.412", "$+0.102$")]):
    e = ganti(e, f"{nama} & {exp_e} & {lama_e} & {exp_d} & {lama_d} & {lama_dd} \\\\",
              f"{nama} & {exp_e} & {baru_e} & {exp_d} & {baru_d} & {baru_dd} \\\\", f"B13 {nama}")
e = ganti(e, "MAE & & 0.254 & & & 0.177 \\\\", "MAE & & 0.094 & & & 0.114 \\\\", "B13 MAE")

# B14. Paragraf SHAP Results 3.4
e = ganti(e,
          "SHAP analysis (Fig.~\\ref{fig:shap}) on the composition-only formation-energy model identifies the oxygen fraction and molecular weight as the dominant descriptors (confirmed by permutation importance); we caution that part of this importance reflects the separation of the phosphide and phosphate families rather than a mechanistic insight, consistent with the within-family results in Table~\\ref{tab:ml}. For the density model, average electronegativity and oxygen fraction dominate, and the SHAP correlation of Ca/P with predicted density is $+0.47$.",
          "SHAP analysis (Fig.~\\ref{fig:shap}) on the composition-only models identifies the phosphorus fraction and the Ca/P ratio as the dominant descriptors for both formation energy and density (confirmed by permutation importance, with the hydrogen fraction third); we caution that part of this importance reflects the separation of the phosphide and phosphate families rather than a mechanistic insight, consistent with the within-family results in Table~\\ref{tab:ml}. For the density model, the SHAP contribution of Ca/P correlates negatively with Ca/P itself ($-0.43$): higher Ca/P pushes density predictions downward, a direction we do not overinterpret given the near-zero composition-only predictive power.",
          "B14 SHAP")

# B15. Discussion: akurasi + leakage controls
e = ganti(e,
          "The honest composition-only models reach MAE 0.27 eV/atom (formation energy) and 0.26 g/cm$^3$ (density)---well behind graph-neural-network state of the art",
          "The honest composition-only models reach MAE 0.30 eV/atom (formation energy) and 0.31 g/cm$^3$ (density)---well behind graph-neural-network state of the art",
          "B15 akurasi")
e = ganti(e,
          "Reduced-formula grouping, nested CV, and composition-only features materially lowered reported scores (e.g., formation-energy $R^2$ from 0.87 to 0.48 in the discovery setting)---we report the conservative numbers throughout.",
          "Reduced-formula grouping, nested CV, and the four-DOF composition feature set materially lowered reported scores (formation-energy $R^2$ from 0.87 to 0.11 in the discovery setting); a further structural finding is that composition alone has no within-phosphate predictive power ($R^2<0$), which argues strongly for structure-aware surrogates. We report the conservative numbers throughout.",
          "B15 leakage controls")

# B16. Conclusion: MAE benchmark
e = ganti(e,
          "formation energies of six calcium phosphate phases with MAE 0.25 eV/atom, and densities with MAE 0.18 g/cm$^3$.",
          "formation energies of six calcium phosphate phases with MAE 0.09 eV/atom, and densities with MAE 0.11 g/cm$^3$.",
          "B16 conclusion")

(MS / "manuscript_elsarticle.tex").write_text(e, encoding="utf-8", newline="")
print("manuscript_elsarticle.tex selesai")

# ============================================================
# Verifikasi: tidak ada sisa angka lama di kedua file
# ============================================================
for nama, teks in [("manuscript.tex", t), ("manuscript_elsarticle.tex", e)]:
    sisa = []
    for pola in ["0.483", "0.580", "0.489", "0.883", "0.174", "0.254", "0.177",
                 "0.48 ", "0.58 ", "0.88 ", "0.25 eV", "0.18 g", "0.552", "0.907",
                 "1{,}266", "94\\%", "61.1\\%", "VIF values up to 24",
                 "oxygen fraction and molecular weight", "$-2.890$", "$-2.025$",
                 "MAE 0.27", "MAE 0.26"]:
        if pola in teks:
            sisa.append(pola)
    print(f"{nama}: sisa pola lama -> {sisa if sisa else 'TIDAK ADA (bersih)'}")
