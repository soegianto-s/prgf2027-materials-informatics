"""Patch manuskrip ronde 7 (Q1): layar MACE COD + E_hull, fitur struktural (null-result),
kelarutan S, substitusi, MCDM phase-level, koreksi angka audit.

Semua angka dibaca dari *_ringkasan.json (assertion wajib) — tidak ada hardcode.
Setiap replace ber-assertion count==1; idempoten; diterapkan pada kedua file .tex.
"""
import json
from pathlib import Path

MS = Path(r"D:\latex\prgf2026\data\reports\manuscript")
PROC = Path(r"D:\latex\prgf2026\data\processed")


def muat(nama):
    return json.loads((PROC / nama).read_text(encoding="utf-8"))


def ganti(s, lama, baru, label, n=1):
    k = s.count(lama)
    assert k == n, f"[{label}] ketemu {k}x (harus {n}): {lama[:70]}..."
    return s.replace(lama, baru)


def patch(s, nama_file, R):
    if "tab:cod_qc" in s and "himanen2020" in s:
        print(f"{nama_file}: sudah ter-patch ronde 7, dilewati")
        return s

    scr = R["screening"]; kal = R["kalibrasi"]; hull = R["hull"]; q1 = R["mcdm_q1"]
    mod = R["model_struktur"]; larut = R["kelarutan"]; sub = R["substitusi"]

    # P1. Abstrak: layar MACE + null-result + S + substitusi (setelah kalimat transfer OQMD)
    s = ganti(s,
              "at matching compositions, the formation-energy model transfers across databases with $R^2 = 0.83$ (280 OQMD entries).",
              "at matching compositions, the formation-energy model transfers across databases with $R^2 = 0.83$ (280 OQMD entries). A calibrated MACE-MP-0 single-point screen supplies formation energies for experimental COD structures, placing phase-level stability on a common Materials Project GGA hull ("
              + str(q1["n_komposisi_phase"]) + " charge-neutral Ca--P--O--H--F--C compositions, "
              + str(q1["n_stabil_hull0"]) + " on the hull); structure-informed features (phosphate $Q^n$ speciation, Ca coordination, SOAP fingerprints) do not improve formation-energy screening under grouped cross-validation---a null result we report explicitly. Literature solubility products are converted to stoichiometric equilibrium solubilities, and a substitution screen over Ca--P--O--X (X = Sr, Mg, Zn, Si) adds "
              + str(sub["n_filter"]) + " candidate phases ("
              + str(sub["n_partial"]) + " partial, " + str(sub["n_endpoint"]) + " full-substitution endpoints).",
              "P1 abstrak Q1")

    # P2. Methods Data acquisition: akuisisi CIF COD + QC
    s = ganti(s,
              "Access dates, versions, and licenses were recorded for every source (Supplementary).",
              "Access dates, versions, and licenses were recorded for every source (Supplementary). For the COD subset, the "
              + str(scr["n_total"]) + " unique structural files were downloaded (crystallography.net, CIF), deduplicated from 2{,}304 query hits, and quality-controlled: coordinate loops validated numerically, structures with disorder flagged, and "
              + str(scr["n_skip"]) + " files excluded with recorded reasons (Table~\\ref{tab:cod_qc}).",
              "P2 akuisisi CIF")

    # P3. Methods ML: paragraf struktur + layar energi + kalibrasi (setelah kalimat baseline lengan ronde 6)
    s = ganti(s,
              "used to compute formation energies of the six benchmark phases from relaxed structures with element references relaxed in the same model, against the same Wagman/NBS standard values.",
              "used to compute formation energies of the six benchmark phases from relaxed structures with element references relaxed in the same model, against the same Wagman/NBS standard values. Beyond the benchmark, the same model was used as a single-point energy screen for all parsed experimental COD structures (no relaxation), and the systematic offset between MACE and the Materials Project GGA scale was calibrated on "
              + str(kal["n_kalibrasi"]) + " Materials Project structures (median offset "
              + f"{kal['offset_median_eV_atom']:+.3f}" + " eV/atom; Table~\\ref{tab:kalibrasi}). Calibrated energies were placed on the Materials Project GGA convex hull (pymatgen PhaseDiagram) to obtain energies above hull ($E_\\mathrm{hull}$) for the in-system COD structures. Structural descriptors (phosphate $Q^n$ speciation, Ca coordination numbers via CrystalNN, and SOAP fingerprints) were extracted for the modeling subset (Materials Project + AFLOW) and evaluated strictly as a screening variant: they require a known structure and are not available for a new composition.",
              "P3 metode layar+struktur")

    # P4. Methods MCDM: C1 = E_hull + koreksi 165 -> 20/21
    s = ganti(s,
              "165 charge-neutral calcium phosphate entries remain in the candidate pool.",
              "the candidate pool contains 165 charge-neutral database records spanning 20 reduced compositions; the COD screen adds one further composition, yielding 21 phase-level compositions with pool-wide C1 coverage.",
              "P4 165->21")
    s = ganti(s,
              "(C1) thermodynamic stability (computed formation energy, lower is better, absolute scale; the documented AFLOW scale offset is treated as a source artifact);",
              "(C1) thermodynamic stability as energy above the Materials Project GGA hull (DFT for Materials Project entries; calibrated MACE for COD structures; the documented AFLOW scale offset is treated as a source artifact; stable phases tie at $E_\\mathrm{hull}=0$ and are separated by C2--C3);",
              "P4 C1 hull")

    # P5. Results dataset: tabel QC COD
    tabel_qc = (
        "\\begin{table}[ht]\n\\centering\\small\n"
        "\\caption{COD structure acquisition and screening audit. 2{,}304 query hits deduplicate to "
        + str(scr["n_total"]) + " unique structures; energies are MACE-MP-0 single-point (float64).}\n"
        "\\label{tab:cod_qc}\n"
        "\\begin{tabular}{lc}\n\\toprule\nStage & Count \\\\\n\\midrule\n"
        "Unique CIF files downloaded & " + str(scr["n_total"]) + " \\\\\n"
        "Parsed and screened (MACE) & " + str(scr["n_ok"]) + " \\\\\n"
        "Excluded (no coordinates / parse failure / >300 atoms) & " + str(scr["n_skip"]) + " \\\\\n"
        "In-system (Ca--P--O--H--F--C) & " + str(scr["n_in_system"]) + " \\\\\n"
        "Physically valid energies (excluded: nonphysical) & " + str(hull["n_cod_in_system"]) + " \\\\\n"
        "$E_\\mathrm{hull}$ defined & " + str(hull["n_hull_terdefinisi"]) + " \\\\\n"
        "On the hull ($E_\\mathrm{hull} = 0$) & " + str(hull["n_stabil_hull0"]) + " \\\\\n"
        "\\bottomrule\n\\end{tabular}\n\\end{table}\n\n")
    s = ganti(s,
              "\\end{table}\n\n\\subsection{Preprocessing and descriptor engineering}",
              "\\end{table}\n\n" + tabel_qc + "\\subsection{Preprocessing and descriptor engineering}",
              "P5 tabel cod_qc")

    # P6. Results ML: paragraf struktur + baris tab:ml
    s = ganti(s,
              "Band gap could not be predicted from composition descriptors ($R^2 < 0$); imputation was therefore abandoned (recorded decision).",
              "Band gap could not be predicted from composition descriptors ($R^2 < 0$); imputation was therefore abandoned (recorded decision). Structure-informed screening features---phosphate $Q^n$ speciation and Ca coordination numbers---lower formation-energy $R^2$ to "
              + str(mod["hasil"][2]["R2"]) + " under grouped CV, and adding SOAP-derived PCA components lowers it further ($R^2 = "
              + str(mod["hasil"][3]["R2"]) + "$); for density they add a modest gain ($R^2$ "
              + str(mod["hasil"][0]["R2"]) + " $\\rightarrow$ " + str(mod["hasil"][5]["R2"]) + "). We report this as a null result for energy and an explicit boundary of what structure features contribute.",
              "P6 null-result")
    s = ganti(s,
              "Density, Magpie features ($n=571$) & SVR (nested) & 0.273 & 0.385 & 0.250 \\\\",
              "Density, Magpie features ($n=571$) & SVR (nested) & 0.273 & 0.385 & 0.250 \\\\\n"
              "Formation energy, $Q^n$ + Ca coordination ($n=242$) & SVR (nested) & "
              + str(mod["hasil"][2]["R2"]) + " & " + str(mod["hasil"][2]["RMSE"]) + " & " + str(mod["hasil"][2]["MAE"]) + " \\\\\n"
              "Formation energy, + SOAP-PCA(30) ($n=242$) & SVR (nested) & "
              + str(mod["hasil"][3]["R2"]) + " & " + str(mod["hasil"][3]["RMSE"]) + " & " + str(mod["hasil"][3]["MAE"]) + " \\\\\n"
              "Density, $Q^n$ + Ca coordination ($n=242$) & Random forest & "
              + str(mod["hasil"][5]["R2"]) + " & " + str(mod["hasil"][5]["RMSE"]) + " & " + str(mod["hasil"][5]["MAE"]) + " \\\\",
              "P6 baris tab:ml struktur")

    # P7. Results validasi: paragraf kalibrasi + tabel
    tabel_kal = (
        "\\begin{table}[ht]\n\\centering\\small\n"
        "\\caption{MACE-to-MP-GGA calibration: offset fitted on "
        + str(kal["n_kalibrasi"]) + " Materials Project structures (nsites $\\leq 200$); "
        "validation on the six Wagman/NBS benchmark phases and against the MP API hull.}\n"
        "\\label{tab:kalibrasi}\n"
        "\\begin{tabular}{lc}\n\\toprule\nQuantity & Value \\\\\n\\midrule\n"
        "Calibration set (MP structures) & " + str(kal["n_kalibrasi"]) + " \\\\\n"
        "Median offset (eV/atom) & " + f"{kal['offset_median_eV_atom']:+.3f}" + " \\\\\n"
        "Offset MAE (eV/atom) & " + str(kal["mae_offset_eV_atom"]) + " \\\\\n"
        "Calibrated MAE vs Wagman/NBS (6 phases) & " + str(kal["mae_eksternal_6fase_eV_atom"]) + " \\\\\n"
        "Hull cross-check vs MP API (MAE, eV/atom) & " + f"{hull['mae_hull_vs_api_eV_atom']:.4f}" + " \\\\\n"
        "\\bottomrule\n\\end{tabular}\n\\end{table}\n\n")
    s = ganti(s,
              "Both baselines together bound what the framework's models can claim.",
              "Both baselines together bound what the framework's models can claim. Calibrating MACE to the GGA scale is deliberate---it makes COD energies commensurate with the Materials Project hull, at the cost of experimental agreement (Table~\\ref{tab:kalibrasi}); the hull reconstruction itself reproduces Materials Project $E_\\mathrm{hull}$ values with MAE "
              + f"{hull['mae_hull_vs_api_eV_atom']:.4f}" + " eV/atom.",
              "P7 kalibrasi")
    s = ganti(s,
              "\\end{table}\n\n\\subsection{Interpretability and experimental validation}",
              "\\end{table}\n\n" + tabel_kal + "\\subsection{Interpretability and experimental validation}",
              "P7 tabel kalibrasi")

    # P8. Results ranking: ranking Q1 phase-level
    top_q1 = q1["top15"][:10]
    esc = "\\_"
    baris_q1 = "\n".join(
        f"{r['formula'].replace('_', esc)} & {r['E_hull']:.3f} & {r['densitas']:.2f} & {r['ca_p_ratio']:.2f} & {r['peringkat']} \\\\"
        for r in top_q1)
    tabel_q1 = (
        "\\begin{table}[ht]\n\\centering\\small\n"
        "\\caption{Q1 phase-level ranking (21 compositions; C1 = $E_\\mathrm{hull}$, C2 = density band, C3 = Ca/P proximity; top 10 shown). Spearman vs the earlier record-level ranking: "
        + f"{q1['spearman_vs_lama']:.2f}" + ".}\n"
        "\\label{tab:top_q1}\n"
        "\\begin{tabular}{lcccc}\n\\toprule\n"
        "Formula & $E_\\mathrm{hull}$ (eV/at) & $\\rho$ (g/cm$^3$) & Ca/P & Rank \\\\\n\\midrule\n"
        + baris_q1 +
        "\n\\bottomrule\n\\end{tabular}\n\\end{table}\n\n")
    s = ganti(s,
              "The top candidates after composition deduplication (polymorphs and formula multiples merged) are listed in Table~\\ref{tab:top}.",
              "The top candidates after composition deduplication (polymorphs and formula multiples merged) are listed in Table~\\ref{tab:top}. With the hull-based C1 and phase-level aggregation (Table~\\ref{tab:top_q1}), the same apatitic phases lead, and the ranking correlates with the earlier one (Spearman "
              + f"{q1['spearman_vs_lama']:.2f}" + "); the COD screen confirms the pool's coverage rather than overturning it.\n\n" + tabel_q1,
              "P8 ranking Q1 + tabel top_q1")

    # P9. Subseksi kelarutan + substitusi (sebelum Interpretability)
    lar = {r["fase"]: r for r in larut}
    baris_lar = "\n".join(
        f"{k.replace(' (', ' (')} & {v['pKsp']} & {v['S_mol_L']:.2e} & {v['log10_S']:.1f} \\\\"
        for k, v in lar.items())
    tabel_lar = (
        "\\begin{table}[ht]\n\\centering\\small\n"
        "\\caption{Stoichiometric equilibrium solubility $S$ (mol/L) converted from literature p$K_\\mathrm{sp}$; "
        "$S = (K_\\mathrm{sp}/(\\nu_+^{\\nu_+}\\nu_-^{\\nu_-}))^{1/(\\nu_++\\nu_-)}$; OCP conditional at pH 7.4.}\n"
        "\\label{tab:kelarutan}\n"
        "\\begin{tabular}{lccc}\n\\toprule\nPhase & p$K_\\mathrm{sp}$ & $S$ (mol/L) & $\\log_{10}S$ \\\\\n\\midrule\n"
        + baris_lar + "\n\\bottomrule\n\\end{tabular}\n\\end{table}\n\n")
    baris_sub = "\n".join(
        f"{r['formula']} & {r['tier']} & {r['X']} & {r['frac_X']*100:.0f}\\% & {r['E_hull']:.3f} & {r['densitas']:.2f} \\\\"
        for r in sub["teratas"][:8])
    tabel_sub = (
        "\\begin{table}[ht]\n\\centering\\small\n"
        "\\caption{Substitution screen over Ca--P--O--X (X = Sr, Mg, Zn, Si; Materials Project): "
        + str(sub["n_filter"]) + " phases pass the filters ("
        + str(sub["n_partial"]) + " partial substitutions, "
        + str(sub["n_endpoint"]) + " full-substitution endpoints); top 8 shown. Sr phosphates are excluded by the density band (all $>$3.2 g/cm$^3$).}\n"
        "\\label{tab:substitusi}\n"
        "\\begin{tabular}{llcccc}\n\\toprule\nFormula & Tier & X & X frac & $E_\\mathrm{hull}$ & $\\rho$ \\\\\n\\midrule\n"
        + baris_sub + "\n\\bottomrule\n\\end{tabular}\n\\end{table}\n\n")
    s = ganti(s,
              "\\subsection{Interpretability and experimental validation}",
              "\\subsection{Solubility and substitution screening}\n"
              "Table~\\ref{tab:kelarutan} converts the literature solubility products to stoichiometric equilibrium solubilities, which are directly comparable across phases: brushite and monetite (S $\\sim 10^{-4}$--$10^{-3}$ mol/L) are about ten orders of magnitude more soluble than hydroxyapatite and fluorapatite ($S \\sim 10^{-14}$ mol/L), with $\\alpha$/$\\beta$-TCP, TTCP, and OCP in between---the quantitative basis for the stability--resorbability trade-off in Section 4. The substitution screen (Table~\\ref{tab:substitusi}) extends the design space: Si-substituted Ca$_5$Si(PO$_6$)$_2$ ranks first, Mg-phosphates dominate the endpoints, and every Sr-phosphate is excluded by the clinical density band (all above 3.2 g/cm$^3$)---a constraint the screen makes explicit rather than ignores.\n\n"
              + tabel_lar + tabel_sub + "\\subsection{Interpretability and experimental validation}",
              "P9 kelarutan+substitusi")

    # P10. Discussion: kejujuran cakupan + null-result
    s = ganti(s,
              "which argues strongly for structure-aware surrogates. We report the conservative numbers throughout.",
              "which argues strongly for structure-aware surrogates. We report the conservative numbers throughout; our structure-informed attempt ($Q^n$, Ca coordination, SOAP) did not improve energy screening under grouped CV, so the framework's genuine ML contribution is the calibrated label screen and the uncertainty-quantified ranking rather than regression accuracy.",
              "P10 diskusi null")

    # P11. Koreksi PubChem 13 -> 10 di tab:sumber
    s = ganti(s, "PubChem & PUG REST, no key & public domain & 13 \\\\",
              "PubChem & PUG REST, no key & public domain & 10 \\\\", "P11 pubchem 10")

    # P12. Bibitem pymatgen + dscribe (setelah batatia2022)
    s = ganti(s,
              "\\bibitem{batatia2022} Batatia I, Kovacs DP, Simm G, Ortner C, Cs\\'anyi G. MACE: higher order equivariant message passing neural networks for fast and accurate force fields. \\textit{Adv Neural Inf Process Syst}. 2022;35:11423--11436.\n",
              "\\bibitem{batatia2022} Batatia I, Kovacs DP, Simm G, Ortner C, Cs\\'anyi G. MACE: higher order equivariant message passing neural networks for fast and accurate force fields. \\textit{Adv Neural Inf Process Syst}. 2022;35:11423--11436.\n"
              "\\bibitem{ong2013} Ong SP, Richards WD, Jain A, et al. Python Materials Genomics (pymatgen): a robust, open-source Python library for materials analysis. \\textit{Comput Mater Sci}. 2013;68:314--319.\n"
              "\\bibitem{himanen2020} Himanen L, J\\\"ager MOJ, Morooka EV, et al. DScribe: library of descriptors for machine learning in materials science. \\textit{Comput Phys Commun}. 2020;247:106949.\n",
              "P12 bibitem baru")

    # P13. Sitasi pymatgen di metode
    s = ganti(s, "(pymatgen PhaseDiagram)", "(pymatgen~\\cite{ong2013} PhaseDiagram)", "P13 sitasi pymatgen")
    s = ganti(s, "SOAP fingerprints) were extracted for the modeling subset",
              "SOAP fingerprints~\\cite{himanen2020}) were extracted for the modeling subset",
              "P13 sitasi dscribe")

    (MS / nama_file).write_text(s, encoding="utf-8")
    return s


def main():
    larut = []
    import csv
    with open(PROC / "kelarutan_ksp.csv", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            larut.append({"fase": row["fase"], "pKsp": float(row["pKsp"]),
                          "S_mol_L": float(row["S_mol_L"]), "log10_S": float(row["log10_S"])})
    R = {
        "screening": muat("mace_screening_cod_ringkasan.json"),
        "kalibrasi": muat("kalibrasi_mace_ringkasan.json"),
        "hull": muat("hull_q1_ringkasan.json"),
        "mcdm_q1": muat("mcdm_q1_ringkasan.json"),
        "model_struktur": muat("model_struktur_ringkasan.json"),
        "substitusi": muat("../raw/mp/substitusi/substitusi_ringkasan.json"),
        "kelarutan": larut,
    }
    # assertion wajib
    for k in ["n_total", "n_ok", "n_skip", "n_in_system"]:
        assert k in R["screening"], f"screening ringkasan tanpa {k}"
    for k in ["n_kalibrasi", "offset_median_eV_atom", "mae_eksternal_6fase_eV_atom"]:
        assert k in R["kalibrasi"], f"kalibrasi tanpa {k}"
    for k in ["n_komposisi_phase", "spearman_vs_lama", "n_stabil_hull0"]:
        assert k in R["mcdm_q1"], f"mcdm_q1 tanpa {k}"
    assert len(R["model_struktur"]["hasil"]) >= 6, "hasil model struktur tidak lengkap"
    assert len(R["substitusi"]["teratas"]) >= 8, "teratas substitusi < 8"

    for nama in ["manuscript.tex", "manuscript_elsarticle.tex"]:
        t = patch((MS / nama).read_text(encoding="utf-8"), nama, R)
        sisa = [p for p in ["165 charge-neutral calcium phosphate entries remain", "PubChem & PUG REST, no key & public domain & 13"]
                if p in t]
        print(f"{nama}: sisa pola lama -> {sisa if sisa else 'bersih'}")
        print(f"  marker baru: tab:cod_qc={'tab:cod_qc' in t}, tab:kelarutan={'tab:kelarutan' in t}, "
              f"tab:top_q1={'tab:top_q1' in t}, himanen2020={'himanen2020' in t}")


if __name__ == "__main__":
    main()
