"""Patch manuskrip ronde 4 (reviewer: desain kriteria MCDM, stoikiometri, klaim judul).

Setiap replace ber-assertion (harus ketemu tepat 1x) — tidak ada kegagalan diam-diam.
Diterapkan pada manuscript.tex DAN manuscript_elsarticle.tex (isi identik).
"""
from pathlib import Path

MS = Path(r"D:\latex\prgf2026\data\reports\manuscript")


def baca(nama):
    return (MS / nama).read_text(encoding="utf-8")


def ganti(s, lama, baru, label, n=1):
    k = s.count(lama)
    assert k == n, f"[{label}] ketemu {k}x (harus {n}): {lama[:70]}..."
    return s.replace(lama, baru)


def patch(s, judul_lama, judul_baru, nama_file):
    # R14. Judul: "Accelerated Discovery" -> "Systematic Screening and Design"
    s = ganti(s, judul_lama, judul_baru, "R14 judul")

    # R1. Abstrak: klaim akselerasi
    s = ganti(s,
              "with artificial intelligence to accelerate the discovery of calcium phosphate biomaterials for bone tissue engineering scaffolds.",
              "with artificial intelligence to systematically screen and rank calcium phosphate compositions for bone tissue engineering scaffolds.",
              "R1 abstrak akselerasi")

    # R2. Abstrak: kalimat MCDM
    s = ganti(s,
              "Multi-objective ranking (TOPSIS and VIKOR under three weighting scenarios, with Shannon-entropy sensitivity analysis) places fluorapatite, carbonated apatite, $\\beta$-TCP, and hydroxyapatite among the leading candidates; the ranking criteria are deliberately derived from bone-tissue design requirements, and the analysis states explicitly that no resorption criterion is represented---so $\\beta$-TCP's clinical resorbability, though not rewarded, does not prevent its top placement on thermodynamic and compositional grounds.",
              "Multi-objective ranking (TOPSIS and VIKOR over three material-level criteria with pool-wide data coverage---formation energy, a clinically processable density band, and Ca/P ratio---combined with a charge-neutrality stoichiometry filter and a 3{,}000-run Monte Carlo propagation of weight and prediction uncertainty) places fluorapatite, oxyapatite, hydroxyapatite, and $\\beta$-TCP at the top with high rank stability. Scaffold-level properties (modulus) and criteria lacking pool-wide data (band gap, resorbability) are deliberately excluded from the ranking; resorbability---the property most relevant to a resorbable scaffold---is assessed post hoc from literature solubility data, and the stability--resorbability trade-off is made explicit. The framework makes no claim of accelerated discovery of new phases: it systematically screens and orders known composition space.",
              "R2 abstrak MCDM")

    # R3. "discovery platform" -> "screening platform" (2x: abstrak + diskusi)
    s = ganti(s, "AI-assisted biomaterial discovery platform",
              "AI-assisted biomaterial screening platform", "R3 platform", n=2)

    # R4. Methods MCDM: 3 kriteria + filter muatan + MC + alasan penarikan C4/C5
    s = ganti(s,
              "Five criteria were defined: (C1) thermodynamic stability (formation energy, lower is better); (C2) density within the clinically processable band $[1.0, 3.2]$ g/cm$^3$ (zero penalty inside; a scaffold reaches bone-like stiffness through porosity---Gibson--Ashby---not by matching bone density); (C3) Ca/P proximity to 1.67 (bone mineral); (C4) Young's modulus proximity to 15 GPa (mid-range of cortical bone), derived as $E = 9KG/(3K+G)$ where bulk and shear moduli were available and median-imputed otherwise (recorded decision); and (C5) band gap (capped at 5 eV, metallic entries penalized, measured values only). A classifier-derived suitability score was deliberately \\emph{excluded} because it is a semi-deterministic function of the same inputs as C1--C3 (double counting). Candidates were ranked with TOPSIS and VIKOR ($v=0.5$) under three weighting scenarios (balanced; stability-dominant; mechanics-dominant). Sensitivity was tested with Shannon-entropy weighting computed on the three imputation-free criteria, keeping manual weights for the imputed criteria; rank consistency was quantified with Spearman correlation.",
              "Three criteria were defined, deliberately restricted to material-level quantities that are available for the entire pool without imputation: (C1) thermodynamic stability (computed formation energy, lower is better, absolute scale; the documented AFLOW scale offset is treated as a source artifact); (C2) density within the clinically processable band $[1.0, 3.2]$ g/cm$^3$ (zero penalty inside; a scaffold reaches bone-like stiffness through porosity---Gibson--Ashby---not by matching bone density); and (C3) Ca/P proximity to 1.67 (bone mineral). Two earlier criteria were withdrawn on internal and reviewer scrutiny: (C4) Young's modulus proximity to 15 GPa, because bulk and shear moduli exist for only $n=9$ of 571 entries, so median imputation would have made the criterion a near-constant noise term, and because 15 GPa is a property of the \\emph{scaffold} (architecture and porosity), not of the dense material---scaffold-level stiffness is instead handled downstream (Section 3.4); and (C5) band gap, because bone scaffolds have no electronic function and 448 of 571 entries lack measured values. A classifier-derived suitability score was also \\emph{excluded} because it is a semi-deterministic function of the same inputs as C1--C3 (double counting). A stoichiometry filter was added: entries whose formal charge under standard oxidation states is non-zero (e.g., Ca$_5$P$_3$O$_{13}$, Ca$_5$(PO$_4$)$_3$) are removed, as are oxygen-free phosphides, which lie outside the calcium phosphate material class; 165 charge-neutral calcium phosphate entries remain in the candidate pool. Candidates were ranked with TOPSIS and VIKOR ($v=0.5$) under three weighting scenarios (balanced; stability-dominant; composition-dominant). Sensitivity was tested in two ways: Shannon-entropy weighting on the three criteria (an internal consistency check against the manual weights, Spearman 0.93), and a Monte Carlo propagation of uncertainty (1{,}000 runs per scenario: weights drawn from Dirichlet distributions centered on each manual set, and formation energies and densities perturbed by Gaussian noise with the cross-validated MAEs of the composition-only models, 0.297 eV/atom and 0.307 g/cm$^3$, representing the prediction error for a hypothetical new composition; Ca/P is exact stoichiometry). Resorbability is not a ranking criterion because solubility data exist only for known phases; it is assessed post hoc from literature for the shortlist (Section 3.3).",
              "R4 methods MCDM")

    # R5. Results ranking prose
    s = ganti(s,
              "TOPSIS and VIKOR were combined across three weighting scenarios (six rankings in total) to produce a robust average rank. Shannon-entropy weighting (computed on the three imputation-free criteria) yields a Spearman correlation of 0.974 with the manual weighting, confirming the robustness of the ranking. The top candidates after polymorph deduplication are listed in Table~\\ref{tab:top}: fluorapatite leads, followed by carbonated apatite, $\\beta$-TCP, and hydroxyapatite, with tetracalcium phosphate, monetite, and octacalcium phosphate completing the clinically relevant shortlist.",
              "TOPSIS and VIKOR were combined across three weighting scenarios (six rankings in total) to produce a robust average rank. Shannon-entropy weighting yields a Spearman correlation of 0.93 with the manual weighting---an internal consistency check between two weighting philosophies on the same criteria, not an independent validation. A Monte Carlo propagation of uncertainty (1{,}000 runs per scenario, Dirichlet-sampled weights around each manual set, formation energies and densities perturbed by Gaussian noise with the cross-validated model MAEs of 0.297 eV/atom and 0.307 g/cm$^3$) confirms that the top of the ranking is stable: fluorapatite, oxyapatite, hydroxyapatite, and $\\beta$-TCP sit in the top five in 86\\%, 71\\%, 67\\%, and 56\\% of runs, respectively, while carbonated apatite and tetracalcium phosphate contest the fifth slot (17\\% each). The top candidates after composition deduplication (polymorphs and formula multiples merged) are listed in Table~\\ref{tab:top}.",
              "R5 results prose")

    # R6. Kaption tab:top
    s = ganti(s,
              "\\caption{Top 15 candidate biomaterials (polymorphs deduplicated; average rank of TOPSIS and VIKOR across three weighting scenarios; lower rank is better).}",
              "\\caption{Top 15 candidate biomaterials (unique compositions after reduced-formula deduplication; charge-neutral calcium phosphates; average rank of TOPSIS and VIKOR across three weighting scenarios; lower rank is better).}",
              "R6 kaption tab:top")

    # R7. Baris tab:top (15 baris lama -> baru)
    baris_lama = [
        "Ca$_5$P$_3$O$_{12}$F & MP & fluorapatite & 1 & $-3.42$ & 3.10 & 1.67 \\\\",
        "Ca$_{10}$P$_6$CO$_{27}$ & MP & carbonated apatite & 2 & $-3.25$ & 3.05 & 1.67 \\\\",
        "Ca$_3$(PO$_4$)$_2$ & MP & $\\beta$-TCP & 3 & $-3.32$ & 2.98 & 1.50 \\\\",
        "Ca$_5$P$_3$HO$_{13}$ & MP & hydroxyapatite & 4 & $-3.22$ & 3.18 & 1.67 \\\\",
        "Ca$_{10}$F$_2$O$_{24}$P$_6$ & AFLOW & fluorapatite & 5 & $-3.03$ & 3.10 & 1.67 \\\\",
        "Ca$_4$P$_2$O$_9$ & MP & TTCP & 6 & $-3.33$ & 3.08 & 2.00 \\\\",
        "Ca$_2$P$_2$O$_7$ & MP & Ca-pyrophosphate & 7 & $-3.21$ & 2.95 & 1.00 \\\\",
        "Ca$_{10}$H$_2$O$_{26}$P$_6$ & AFLOW & hydroxyapatite & 8 & $-2.84$ & 3.05 & 1.67 \\\\",
        "Ca$_{16}$O$_{36}$P$_8$ & AFLOW & TTCP & 9 & $-2.94$ & 2.98 & 2.00 \\\\",
        "Ca$_{10}$P$_6$O$_{25}$ & MP & apatite & 10 & $-3.32$ & 2.98 & 1.67 \\\\",
        "Ca$_4$P$_6$O$_{19}$ & MP & polyphosphate & 11 & $-3.07$ & 2.90 & 0.67 \\\\",
        "CaPHO$_4$ & MP & monetite (DCPA) & 12 & $-2.80$ & 2.95 & 1.00 \\\\",
        "Ca$_3$O$_8$P$_2$ & AFLOW & $\\beta$-TCP & 13 & $-2.89$ & 3.36 & 1.50 \\\\",
        "Ca$_{16}$O$_{56}$P$_{16}$ & AFLOW & DCPA-type & 14 & $-2.80$ & 3.01 & 1.00 \\\\",
        "Ca$_8$P$_6$H$_{12}$O$_{29}$ & MP & OCP & 15 & $-2.62$ & 2.59 & 1.33 \\\\",
    ]
    baris_baru = [
        "Ca$_5$P$_3$O$_{12}$F & MP & fluorapatite & 1 & $-3.42$ & 3.10 & 1.67 \\\\",
        "Ca$_{10}$P$_6$O$_{25}$ & MP & oxyapatite & 2 & $-3.32$ & 2.98 & 1.67 \\\\",
        "Ca$_{10}$P$_6$CO$_{27}$ & MP & carbonated apatite & 3 & $-3.25$ & 3.05 & 1.67 \\\\",
        "Ca$_5$P$_3$HO$_{13}$ & MP & hydroxyapatite & 4 & $-3.22$ & 3.18 & 1.67 \\\\",
        "Ca$_3$(PO$_4$)$_2$ & MP & $\\beta$-TCP & 5 & $-3.33$ & 2.78 & 1.50 \\\\",
        "Ca$_4$P$_2$O$_9$ & MP & TTCP & 6 & $-3.33$ & 3.08 & 2.00 \\\\",
        "Ca$_2$P$_2$O$_7$ & MP & Ca-pyrophosphate & 7 & $-3.21$ & 2.95 & 1.00 \\\\",
        "Ca$_8$P$_6$H$_{12}$O$_{29}$ & MP & OCP & 8 & $-2.62$ & 2.59 & 1.33 \\\\",
        "CaPHO$_4$ & MP & monetite (DCPA) & 9 & $-2.80$ & 2.95 & 1.00 \\\\",
        "Ca$_2$P$_2$H$_4$O$_9$ & MP & DCP-related hydrate & 10 & $-2.52$ & 2.48 & 1.00 \\\\",
        "Ca$_4$P$_6$O$_{19}$ & MP & calcium polyphosphate & 11 & $-3.07$ & 2.90 & 0.67 \\\\",
        "Ca$_2$P$_2$H$_8$O$_{11}$ & MP & DCP-related hydrate & 12 & $-2.19$ & 2.19 & 1.00 \\\\",
        "Ca(PO$_3$)$_2$ & MP & calcium metaphosphate & 13 & $-2.97$ & 2.87 & 0.50 \\\\",
        "CaPH$_5$O$_6$ & MP & brushite (DCPD) & 14 & $-2.08$ & 2.28 & 1.00 \\\\",
        "CaP$_2$H$_2$O$_7$ & MP & calcium dihydrogen pyrophosphate & 15 & $-2.58$ & 2.42 & 0.50 \\\\",
    ]
    for i, (lama, baru) in enumerate(zip(baris_lama, baris_baru)):
        s = ganti(s, lama, baru, f"R7 baris {i + 1}")

    # R8. Paragraf "The ranking should be read..." + tabel resorbabilitas baru
    s = ganti(s,
              "The ranking should be read for what it is. The criteria encode bone-tissue design requirements---stability, a density band covering all clinically processable calcium phosphate ceramics, proximity of Ca/P to bone mineral, and stiffness---so the top ranks are apatitic \\emph{by construction}, not by surprise. We therefore make no claim of ``rediscovering'' the clinical hierarchy. What the ranking does deliver is a principled ordering within the design space, and it places clinically meaningful phases correctly: fluorapatite, carbonated apatite, $\\beta$-TCP (rank 3), and hydroxyapatite lead, while tetracalcium phosphate (rank 6) and monetite (rank 12)---the two setting components of the classic calcium phosphate cements---and octacalcium phosphate (rank 15) sit inside the shortlist. $\\beta$-TCP's presence in the top ranks rests on thermodynamic and compositional criteria; its distinctive clinical virtue, \\emph{resorbability}, is still not represented by any criterion, and no resorption-sensitive ordering should be inferred from this ranking. Biphasic calcium phosphate (BCP) is a composite of hydroxyapatite and $\\beta$-TCP rather than a single phase; both constituents are present in the candidate pool. Fluorapatite is standard in dental restoratives, and TTCP is the setting component of clinical calcium phosphate cements. The clearest framework limitation---and the most actionable direction for the next iteration---is therefore a resorption/solubility criterion derived from experiment or simulation, which would rank resorbable phases by their clinical merit rather than by stability alone.",
              "The ranking should be read for what it is. The criteria are deliberately limited to material-level quantities with full data coverage---stability, a density band covering all clinically processable calcium phosphate ceramics, and proximity of Ca/P to bone mineral---so the top ranks are apatitic \\emph{by construction}, not by surprise. We therefore make no claim of ``rediscovering'' the clinical hierarchy, and accordingly the phrase ``accelerated discovery'' has been removed from the title and framing of this work: the framework screens and orders known composition space rather than discovering new phases. What the ranking does deliver is a principled, uncertainty-quantified ordering within that space: fluorapatite, oxyapatite, hydroxyapatite, and $\\beta$-TCP occupy the top four with high Monte Carlo stability, and tetracalcium phosphate (rank 6) and monetite (rank 9)---the two setting components of the classic calcium phosphate cements---and octacalcium phosphate (rank 8) sit inside the shortlist; the tail (ranks 10--15) consists of acid and condensed calcium phosphates that rank poorly on stability. Biphasic calcium phosphate (BCP) is a composite of hydroxyapatite and $\\beta$-TCP rather than a single phase; both constituents are present in the candidate pool. Fluorapatite is standard in dental restoratives, and TTCP is the setting component of clinical calcium phosphate cements.\n\n\\textbf{Stability--resorbability trade-off.} Maximizing C1 (lowest formation energy) favors the least soluble phases, which is at odds with the resorbability a bone scaffold usually needs; the criteria themselves do not resolve this tension. Table~\\ref{tab:resorb} overlays literature solubility products (negative decadic logarithm, p$K_\\mathrm{sp}$, 25\\,$^\\circ$C) and degradation class~\\cite{elliott1994,dorozhkin2009,wang2008} onto the clinically established shortlist phases. The order is instructive: brushite and monetite are orders of magnitude more soluble than octacalcium phosphate, which in turn degrades faster than the TCPs, while the apatites (hydroxyapatite, fluorapatite, oxyapatite) are essentially insoluble under physiological pH. A resorbable scaffold therefore argues for $\\beta$-TCP or biphasic HA/$\\beta$-TCP---the clinical standard---whereas fluorapatite and oxyapatite suit permanent or low-turnover applications. We present this trade-off explicitly rather than folding solubility into the MCDM, because a defensible solubility criterion requires values for the \\emph{whole} candidate pool, which do not exist.\n\n\\begin{table}[ht]\n\\centering\\small\n\\caption{Literature resorbability overlay for the clinically established shortlist phases (25\\,$^\\circ$C); p$K_\\mathrm{sp}$ = negative decadic logarithm of the solubility product; degradation class after \\cite{dorozhkin2009}.}\n\\label{tab:resorb}\n\\begin{tabular}{lccll}\n\\toprule\nPhase & p$K_\\mathrm{sp}$ & Degradation class & Rank (tab:top) & Scaffold role \\\\\n\\midrule\nBrushite (DCPD) & 6.59 & fast & 14 & resorbable cement precursor \\\\\nMonetite (DCPA) & 6.90 & fast & 9 & resorbable cement precursor \\\\\nOCP & 96.6 & fast in vivo & 8 & HA precursor, resorbable \\\\\n$\\alpha$-TCP & 25.5 & resorbable & (same comp. as 5) & cement setting component \\\\\n$\\beta$-TCP & 28.9 & resorbable & 5 & resorbable scaffold (clinical) \\\\\nTTCP & $\\approx$38 & slowly resorbable & 6 & cement setting component \\\\\nHydroxyapatite & 116.8 & essentially insoluble & 4 & permanent/low-turnover \\\\\nFluorapatite & $\\approx$121 & essentially insoluble & 1 & dental, low-turnover \\\\\nOxyapatite & $\\approx$HA & essentially insoluble & 2 & high-temperature apatite \\\\\n\\bottomrule\n\\end{tabular}\n\\end{table}",
              "R8 ranking-read + tab:resorb")

    # R10. Paragraf MLFF (angka Top-5 baru)
    s = ganti(s,
              "\\textbf{MLFF structural validation.} All five top candidates were relaxed with the universal machine-learning force field MACE-MP-0 (medium, float64): four of five are essentially at their energy minimum (cell-volume change $\\leq 0.4\\%$; TTCP $+3.0\\%$), and the single-crystal stiffness falls in a narrow band ($E = 206$--$220$ GPa, $K = 127$--$139$ GPa, $\\nu \\approx 0.23$), consistent with dense apatitic ceramics (MLFF stiffness is known to be systematically high; definitive DFT runs await cluster resources). Applying Gibson--Ashby scaling, scaffolds fabricated from these candidates require roughly \\textbf{70--78\\% porosity} to match the 10--20 GPa modulus range of cortical bone---a concrete design specification for additive manufacturing.",
              "\\textbf{MLFF structural validation.} All five top candidates were relaxed with the universal machine-learning force field MACE-MP-0 (medium, float64): four of five are essentially at their energy minimum (cell-volume change $+0.27\\%$ fluorapatite, $+0.41\\%$ oxyapatite, $+0.36\\%$ carbonated apatite, $-0.39\\%$ $\\beta$-TCP; hydroxyapatite expands by $+4.3\\%$, flagged for priority DFT verification), and the single-crystal stiffness falls in a narrow band ($E = 204$--$220$ GPa, $K = 131$--$139$ GPa, $\\nu \\approx 0.23$--0.24), consistent with dense apatitic ceramics (MLFF stiffness is known to be systematically high; definitive DFT runs await cluster resources). Applying Gibson--Ashby scaling, scaffolds fabricated from these candidates require roughly \\textbf{70--78\\% porosity} to match the 10--20 GPa modulus range of cortical bone---a concrete design specification for additive manufacturing.",
              "R10 MLFF")

    # R11. Limitations: C4 imputasi -> ditarik + angka MLFF baru
    s = ganti(s,
              "\\emph{Data.} Computed elastic moduli are scarce ($n=9$), so criterion C4 relies on median imputation; an MLFF (MACE-MP-0) pre-validation confirms candidate stability and yields porosity design targets (70--78\\%), while definitive DFT validation awaits cluster resources (inputs prepared).",
              "\\emph{Data.} Computed elastic moduli are scarce ($n=9$), which is why the modulus criterion (C4) was withdrawn rather than median-imputed (Methods); an MLFF (MACE-MP-0) pre-validation of the top five confirms candidate stability (four of five with $|dV| \\leq 0.41\\%$; hydroxyapatite $+4.3\\%$, flagged for priority DFT) and yields porosity design targets (70--78\\%), while definitive DFT validation awaits cluster resources (inputs prepared).",
              "R11 limitations data")

    # R12. Limitations: tambah kalimat ketidakpastian ranking
    s = ganti(s,
              "The suitability label is a semi-deterministic function of its own features and was withdrawn as a predictive claim and as an MCDM criterion.",
              "The suitability label is a semi-deterministic function of its own features and was withdrawn as a predictive claim and as an MCDM criterion. \\emph{Ranking.} The three manual weighting scenarios are subjective; we mitigate this with entropy weighting (Spearman 0.93, an internal consistency check) and with a 3{,}000-run Monte Carlo over Dirichlet-sampled weights and ML-prediction noise (MAEs 0.297 eV/atom and 0.307 g/cm$^3$): the top four compositions are stable (top-5 membership 56--86\\%), the fifth slot is contested (17\\% each for carbonated apatite and tetracalcium phosphate), and rank intervals are reported rather than hidden.",
              "R12 limitations ranking")

    # R13. Conclusion
    s = ganti(s,
              "We developed an end-to-end, replicable Materials Informatics framework that integrates five open databases, descriptor engineering with multicollinearity control, leakage-resistant machine learning (reduced-formula grouping, nested cross-validation, composition-only descriptors), multi-objective ranking (TOPSIS/VIKOR with entropy-based sensitivity analysis), and SHAP-based interpretability. The framework assembles a dataset of 2{,}885 entries (950 unique compositions) and delivers models whose predictions reproduce experimental thermochemistry: formation energies of six calcium phosphate phases with MAE 0.09 eV/atom, and densities with MAE 0.11 g/cm$^3$. These accuracies are modest compared with graph-neural-network state of the art, and we report them together with the leakage analysis that defines them. The multi-objective ranking, whose criteria are explicitly derived from bone-tissue design requirements, places fluorapatite, carbonated apatite, hydroxyapatite, and tetracalcium phosphate (together with its cement co-component monetite) at the top of a transparent candidate list---$\\beta$-TCP enters the shortlist once its Ca/P and density are represented fairly---and the analysis exposes the framework's clearest gap: a missing resorption criterion. MLFF structural pre-validation confirms the stability of the top candidates and yields a porosity design target of 70--78\\% for cortical-bone stiffness; definitive DFT validation inputs are prepared. The framework's value is methodological: a trustworthy, auditable screening pipeline with explicit, quantified limitations, ready to absorb stronger surrogates (GNNs, MLFFs) and further criteria.",
              "We developed an end-to-end, replicable Materials Informatics framework that integrates five open databases, descriptor engineering with multicollinearity control, leakage-resistant machine learning (reduced-formula grouping, nested cross-validation, composition-only descriptors), multi-objective ranking (TOPSIS/VIKOR with entropy sensitivity and Monte Carlo uncertainty propagation), and SHAP-based interpretability. The framework assembles a dataset of 2{,}885 entries (950 unique compositions) and delivers models whose predictions reproduce experimental thermochemistry: formation energies of six calcium phosphate phases with MAE 0.09 eV/atom, and densities with MAE 0.11 g/cm$^3$. These accuracies are modest compared with graph-neural-network state of the art, and we report them together with the leakage analysis that defines them. The multi-objective ranking---restricted to material-level criteria with pool-wide coverage and guarded by a charge-neutrality stoichiometry filter---places fluorapatite, oxyapatite, hydroxyapatite, and $\\beta$-TCP at the top of a transparent, uncertainty-quantified candidate list, and a literature resorbability overlay makes the stability--resorbability trade-off explicit rather than hidden. The framework screens and orders known composition space; it makes no claim of accelerated discovery of new phases, and it says so in its title. MLFF structural pre-validation confirms the stability of the top candidates and yields a porosity design target of 70--78\\% for cortical-bone stiffness; definitive DFT validation inputs are prepared. The framework's value is methodological: a trustworthy, auditable screening pipeline with explicit, quantified limitations, ready to absorb stronger surrogates (GNNs, MLFFs) and further criteria.",
              "R13 conclusion")

    # R15. Bibitem baru (setelah bibitem dorozhkin 2012)
    s = ganti(s,
              "\\bibitem{dorozhkin} Dorozhkin SV. Calcium orthophosphates: applications in nature, biology, and medicine. \\textit{Pan Stanford Publishing}; 2012.",
              "\\bibitem{dorozhkin} Dorozhkin SV. Calcium orthophosphates: applications in nature, biology, and medicine. \\textit{Pan Stanford Publishing}; 2012.\n"
              "\\bibitem{dorozhkin2009} Dorozhkin SV. Calcium orthophosphates in nature, biology and medicine. \\textit{Materials}. 2009;2(2):399--498.\n"
              "\\bibitem{elliott1994} Elliott JC. Structure and Chemistry of the Apatites and Other Calcium Orthophosphates. Amsterdam: Elsevier; 1994.\n"
              "\\bibitem{wang2008} Wang L, Nancollas GH. Calcium orthophosphates: crystallization and dissolution. \\textit{Chem Rev}. 2008;108(11):4628--4669.",
              "R15 bibitem")

    (MS / nama_file).write_text(s, encoding="utf-8")
    return s


JUDUL_LAMA_MS = "\\title{\\bfseries An Artificial-Intelligence-Based Materials Informatics Framework for the Accelerated Discovery of Calcium Phosphate Biomaterials as Candidate Scaffolds for Bone Tissue Engineering}"
JUDUL_BARU_MS = "\\title{\\bfseries An Artificial-Intelligence-Based Materials Informatics Framework for the Systematic Screening and Design of Calcium Phosphate Biomaterials as Candidate Scaffolds for Bone Tissue Engineering}"
JUDUL_LAMA_EL = "\\title{An Artificial-Intelligence-Based Materials Informatics Framework for the Accelerated Discovery of Calcium Phosphate Biomaterials as Candidate Scaffolds for Bone Tissue Engineering}"
JUDUL_BARU_EL = "\\title{An Artificial-Intelligence-Based Materials Informatics Framework for the Systematic Screening and Design of Calcium Phosphate Biomaterials as Candidate Scaffolds for Bone Tissue Engineering}"

t = patch(baca("manuscript.tex"), JUDUL_LAMA_MS, JUDUL_BARU_MS, "manuscript.tex")
e = patch(baca("manuscript_elsarticle.tex"), JUDUL_LAMA_EL, JUDUL_BARU_EL, "manuscript_elsarticle.tex")

# Verifikasi sisa pola lama
for nama, teks in [("manuscript.tex", t), ("manuscript_elsarticle.tex", e)]:
    sisa = [p for p in ["Accelerated Discovery", "0.974", "mechanics-dominant",
                        "C4) Young's modulus proximity", "no resorption criterion is represented",
                        "discovery platform", "TTCP $+3.0$", "K = 127$"] if p in teks]
    print(f"{nama}: sisa pola lama -> {sisa if sisa else 'TIDAK ADA (bersih)'}")
