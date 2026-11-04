"""Patch manuskrip ronde 6 (reviewer: baseline jujur + trade-off resorbabilitas kuantitatif).

Integrasi tiga analisis baru:
1. Baseline deskriptor Magpie (40 fitur) — Eform tetap ~0, densitas naik ke R2 0.27-0.31.
2. Baseline pretrained MACE-MP-0 (float64) — Eform 6 fase benchmark vs Wagman/NBS.
3. Sensitivitas MCDM + pKsp — re-ranking shortlist 8 komposisi (trade-off stabilitas-resorbabilitas).

Angka MACE dibaca dari data/validasi_mace/hasil_mace_baseline.json (assert ada & lengkap 6 fase).
Koreksi jujur: deskripsi model MACE "medium" -> "float64" (bobot float64 mace-torch = model L1).
Setiap replace ber-assertion — tidak ada kegagalan diam-diam.
Diterapkan pada manuscript.tex DAN manuscript_elsarticle.tex (isi identik).
"""
import json
from pathlib import Path

MS = Path(r"D:\latex\prgf2026\data\reports\manuscript")
ROOT = Path(r"D:\latex\prgf2026")

HASIL_MACE = ROOT / "data" / "validasi_mace" / "hasil_mace_baseline.json"


def muat_mace():
    assert HASIL_MACE.exists(), f"Jalankan dulu scripts/mace_baseline.py -> {HASIL_MACE.name} belum ada"
    j = json.loads(HASIL_MACE.read_text(encoding="utf-8"))
    baris = {b[0]: b for b in j["baris"]}
    wajib = ["top6_Ca5P3HO13", "top26_Ca3(PO4)2", "alphaTCP_Ca3(PO4)2",
             "TTCP_Ca4P2O9", "DCPA_CaPHO4", "DCPD_CaPH5O6"]
    for w in wajib:
        assert w in baris, f"fase {w} tidak ada di hasil MACE"
    mae = float(j["MAE"])
    return baris, mae


def ganti(s, lama, baru, label, n=1):
    k = s.count(lama)
    assert k == n, f"[{label}] ketemu {k}x (harus {n}): {lama[:70]}..."
    return s.replace(lama, baru)


def patch(s, nama_file, baris, mae):
    if "tab:resorb_rank" in s and "batatia2022" in s:
        print(f"{nama_file}: sudah ter-patch ronde 6, dilewati")
        return s
    fm = f"{mae:.3f}"

    # P1. Methods ML: dua lengan baseline tambahan (Magpie + MACE-MP-0)
    s = ganti(s,
              "All four model families were evaluated under identical grouped cross-validation; only the SVR received hyperparameter tuning (nested CV), while the tree-based models served as untuned reference baselines.",
              "All four model families were evaluated under identical grouped cross-validation; only the SVR received hyperparameter tuning (nested CV), while the tree-based models served as untuned reference baselines. Two further reference baselines were evaluated against established materials-informatics practice: (i) Magpie descriptor statistics~\\cite{ward2016} (40 elemental-property features---mean, average deviation, range, and extrema of atomic properties such as electronegativity and ionic radius---computed over the elements present, under the identical grouped-CV protocol), and (ii) the pretrained universal machine-learned force field MACE-MP-0~\\cite{batatia2022} (float64), used to compute formation energies of the six benchmark phases from relaxed structures with element references relaxed in the same model, against the same Wagman/NBS standard values.",
              "P1 baseline lengan")

    # P2. Methods MCDM: skenario sensitivitas pKsp
    s = ganti(s,
              "Resorbability is not a ranking criterion because solubility data exist only for known phases; it is assessed post hoc from literature for the shortlist (Section 3.3).",
              "Resorbability is not a ranking criterion because solubility data exist only for known phases; it is assessed post hoc from literature for the shortlist (Section 3.3). As a quantitative sensitivity exercise, the shortlist compositions with literature solubility products ($n=8$ unique formulas) were re-ranked on three criteria---stability, Ca/P proximity, and resorbability ($-\\mathrm{p}K_\\mathrm{sp}$; more soluble is better for a resorbable scaffold)---under three weighting scenarios (balanced; stability-dominant; resorbability-dominant). This is reported as a sensitivity analysis only, because $\\mathrm{p}K_\\mathrm{sp}$ values exist for known phases alone and cannot be generalized to the full candidate pool.",
              "P2 mcdm pKsp")

    # P3. Results ML: paragraf baseline Magpie
    s = ganti(s,
              "we report these negative values as evidence for the low information content of the four-DOF composition features rather than as model failures.",
              "we report these negative values as evidence for the low information content of the four-DOF composition features rather than as model failures. Replacing the four composition descriptors with 40 Magpie descriptor statistics does not lift formation-energy prediction (nested SVR $R^2 = -0.055$ vs.\\ 0.113; Table~\\ref{tab:ml})---an independent confirmation that composition-level information, however elaborated, cannot predict formation energy in this family---but substantially improves the density model ($R^2 = 0.273$ nested SVR, 0.309 untuned random forest, vs.\\ 0.018), because elemental-property contrasts capture packing-related information that the composition fractions do not. The headline models therefore remain the interpretable four-DOF set; the Magpie comparison quantifies what descriptor statistics can add for a structure-governed property.",
              "P3 magpie paragraf")

    # P4. Tabel ML: dua baris Magpie
    s = ganti(s,
              "Density, composition-only ($n=571$) & Random forest & 0.018 & 0.441 & 0.307 \\\\",
              "Density, composition-only ($n=571$) & Random forest & 0.018 & 0.441 & 0.307 \\\\\n"
              "Formation energy, Magpie features ($n=337$) & SVR (nested) & $-0.055$ & 0.454 & 0.317 \\\\\n"
              "Density, Magpie features ($n=571$) & SVR (nested) & 0.273 & 0.385 & 0.250 \\\\",
              "P4 tabel ML magpie")

    # P5. Results ranking: kalimat re-ranking resorbabilitas
    s = ganti(s,
              "while carbonated apatite and tetracalcium phosphate contest the fifth slot (17\\% each).",
              "while carbonated apatite and tetracalcium phosphate contest the fifth slot (17\\% each). A resorbability-weighted sensitivity analysis (Table~\\ref{tab:resorb_rank}) re-ranks the eight shortlist compositions with literature $\\mathrm{p}K_\\mathrm{sp}$ on three criteria (stability, Ca/P proximity, resorbability) under three weighting scenarios: $\\beta$-TCP, tetracalcium phosphate, and monetite climb to the top three, while fluorapatite, oxyapatite, and hydroxyapatite drop the most, making the stability--resorbability trade-off quantitatively explicit.",
              "P5 ranking resorb")

    # P6. Tabel re-ranking resorbabilitas (setelah tab:top)
    tabel_resorb = (
        "\\begin{table}[ht]\n"
        "\\centering\\small\n"
        "\\caption{Resorbability-weighted re-ranking of the shortlist: three criteria (stability, Ca/P proximity, resorbability $= -\\mathrm{p}K_\\mathrm{sp}$) under three weighting scenarios (balanced; stability-dominant; resorbability-dominant). Only compositions with literature solubility products (25\\,$^\\circ$C) are included; the density-band criterion is non-discriminative on this shortlist and is dropped.}\n"
        "\\label{tab:resorb_rank}\n"
        "\\begin{tabular}{llcccc}\n"
        "\\toprule\n"
        "Formula & Family & Rank (Tab.~\\ref{tab:top}) & Rank (+resorb.) & Ca/P & p$K_\\mathrm{sp}$ \\\\\n"
        "\\midrule\n"
        "Ca$_3$(PO$_4$)$_2$ & $\\beta$-TCP & 5 & 1 & 1.50 & 28.9 \\\\\n"
        "Ca$_4$P$_2$O$_9$ & TTCP & 6 & 2 & 2.00 & 38.0 \\\\\n"
        "CaPHO$_4$ & monetite (DCPA) & 9 & 3 & 1.00 & 6.9 \\\\\n"
        "Ca$_{10}$P$_6$O$_{25}$ & oxyapatite & 2 & 4 & 1.67 & 116.8 \\\\\n"
        "CaPH$_5$O$_6$ & brushite (DCPD) & 14 & 5 & 1.00 & 6.6 \\\\\n"
        "Ca$_5$P$_3$O$_{12}$F & fluorapatite & 1 & 6 & 1.67 & 121.0 \\\\\n"
        "Ca$_5$P$_3$HO$_{13}$ & hydroxyapatite & 4 & 7 & 1.67 & 116.8 \\\\\n"
        "Ca$_8$P$_6$H$_{12}$O$_{29}$ & OCP & 8 & 8 & 1.33 & 96.6 \\\\\n"
        "\\bottomrule\n"
        "\\end{tabular}\n"
        "\\end{table}\n\n")
    s = ganti(s,
              "\\end{table}\n\n\\subsection{Interpretability and experimental validation}",
              "\\end{table}\n\n" + tabel_resorb + "\\subsection{Interpretability and experimental validation}",
              "P6 tabel resorb_rank")

    # P7. Paragraf baseline MACE sebelum tab:bench (wording kondisional: MAE vs 0.094 komposisi)
    if mae < 0.094:
        kal7 = ("attaining MAE " + fm + " eV/atom---quantifying the headroom between the "
                "composition-only surrogate and structure-aware pretrained models.")
    else:
        kal7 = ("attaining MAE " + fm + " eV/atom---on this narrow same-family benchmark the "
                "database-trained composition surrogate is not exceeded, because its training data share "
                "the GGA energy scales of the databases; the value of a pretrained force field lies in its "
                "generality to arbitrary phases rather than in superior accuracy here. Both baselines "
                "together bound what the framework's models can claim.")
    s = ganti(s,
              "We note that this benchmark covers six well-known phosphate phases and is therefore a narrow, same-family test; the grouped-CV numbers in Table~\\ref{tab:ml} remain the honest estimate of broad performance.",
              "We note that this benchmark covers six well-known phosphate phases and is therefore a narrow, same-family test; the grouped-CV numbers in Table~\\ref{tab:ml} remain the honest estimate of broad performance. As a further baseline, the pretrained universal force field MACE-MP-0 (float64) computes formation energies for the same six phases from relaxed structures (element references Ca, P$_4$, O$_2$, H$_2$, F$_2$ relaxed in the same model; Table~\\ref{tab:bench}), "
              + kal7,
              "P7 mace paragraf")

    # P8. Tabel bench: kolom MACE + caption
    s = ganti(s,
              "\\begin{tabular}{lccccc}\n\\toprule\nPhase & E$_f^{\\mathrm{exp}}$ (eV/at) & E$_f^{\\mathrm{pred}}$ & Density$^{\\mathrm{exp}}$ & Density$^{\\mathrm{pred}}$ & $\\Delta$Density \\\\",
              "\\begin{tabular}{lcccccc}\n\\toprule\nPhase & E$_f^{\\mathrm{exp}}$ (eV/at) & E$_f^{\\mathrm{pred}}$ & E$_f^{\\mathrm{MACE}}$ & Density$^{\\mathrm{exp}}$ & Density$^{\\mathrm{pred}}$ & $\\Delta$Density \\\\",
              "P8 header bench")
    fase_mace = {("Hydroxyapatite & $-3.159$ & $-3.176$ & 3.16 & 3.173 & $+0.013$ \\\\", "$-3.176$"): "top6_Ca5P3HO13",
                 ("$\\beta$-TCP & $-3.285$ & $-3.214$ & 3.07 & 3.219 & $+0.149$ \\\\", "$-3.214$"): "top26_Ca3(PO4)2",
                 ("$\\alpha$-TCP & $-3.289$ & $-3.214$ & 2.86 & 3.219 & $+0.359$ \\\\", "$-3.214$"): "alphaTCP_Ca3(PO4)2",
                 ("TTCP & $-3.297$ & $-3.248$ & 3.05 & 3.110 & $+0.060$ \\\\", "$-3.248$"): "TTCP_Ca4P2O9",
                 ("Monetite (DCPA) & $-2.686$ & $-2.635$ & 2.92 & 2.919 & $-0.001$ \\\\", "$-2.635$"): "DCPA_CaPHO4",
                 ("Brushite (DCPD) & $-1.717$ & $-2.020$ & 2.31 & 2.412 & $+0.102$ \\\\", "$-2.020$"): "DCPD_CaPH5O6"}
    for (lama, pred), tag in fase_mace.items():
        eform = float(baris[tag][3])
        assert float(baris[tag][5]) == float(baris[tag][5]), f"{tag}: selisih NaN (fase dilewati)"
        # sisipkan kolom MACE tepat setelah kolom prediksi pada baris tersebut
        baru = lama.replace(pred, pred + f" & ${eform:+.3f}$", 1)
        assert baru != lama, f"{tag}: kolom MACE gagal disisipkan"
        s = ganti(s, lama, baru, f"P8 baris {tag}")
    s = ganti(s, "MAE & & 0.094 & & & 0.114 \\\\",
              "MAE & & 0.094 & " + fm + " & & & 0.114 \\\\", "P8 MAE")
    s = ganti(s,
              "Composition-only descriptors; models trained exclusively on database entries.",
              "Composition-only descriptors; models trained exclusively on database entries; E$_f^{\\mathrm{MACE}}$ is the pretrained MACE-MP-0 (float64) baseline on the same six phases.",
              "P8 caption bench")

    # P9. Koreksi jujur: ukuran model MACE + sitasi
    s = ganti(s, "MACE-MP-0 (medium, float64):", "MACE-MP-0 (float64)~\\cite{batatia2022}:", "P9 medium->float64")

    # P10. Discussion: trade-off terkuantifikasi
    s = ganti(s,
              "We present this trade-off explicitly rather than folding solubility into the MCDM, because a defensible solubility criterion requires values for the \\emph{whole} candidate pool, which do not exist.",
              "We present this trade-off explicitly rather than folding solubility into the MCDM, because a defensible solubility criterion requires values for the \\emph{whole} candidate pool, which do not exist. The resorbability-weighted re-ranking (Table~\\ref{tab:resorb_rank}) makes the trade-off quantitative: with resorbability as a criterion, $\\beta$-TCP, tetracalcium phosphate, and monetite occupy the top three slots while the apatites fall to the bottom---consistent with the clinical role of $\\beta$-TCP and monetite/TTCP-based cements as resorbable materials.",
              "P10 diskusi trade-off")

    # P11. Discussion Accuracy: MACE + Magpie (wording kondisional)
    if mae < 0.094:
        kal11 = ("our pretrained MACE-MP-0 baseline on the six benchmark phases (MAE " + fm
                 + " eV/atom, Table~\\ref{tab:bench}) confirms that the accuracy gain of "
                 "structure-aware surrogates is real")
    else:
        kal11 = ("our pretrained MACE-MP-0 baseline on the six benchmark phases (MAE " + fm
                 + " eV/atom, Table~\\ref{tab:bench}) shows that a pretrained universal force "
                 "field does not beat the database-trained composition surrogate on this narrow "
                 "same-family benchmark---its advantage is generality across material space")
    s = ganti(s,
              "upgrading the surrogate to a GNN or a universal MLFF is a straightforward next step that we leave to future work.",
              "upgrading the surrogate to a GNN or a universal MLFF is a straightforward next step that we leave to future work; "
              + kal11 + ". Elaborating the composition features with 40 Magpie descriptor statistics leaves formation energy essentially unchanged ($R^2 \\approx 0$) but lifts the density model to $R^2 = 0.27$--$0.31$, indicating that structure-governed properties benefit from descriptor statistics even where energy does not.",
              "P11 akurasi MACE+Magpie")

    # P12. Abstrak: baseline MACE + Magpie
    s = ganti(s,
              "The models nevertheless reproduce experimental standard formation enthalpies and densities of six phosphate phases with MAEs of 0.09 eV/atom and 0.11 g/cm$^3$, respectively.",
              "The models nevertheless reproduce experimental standard formation enthalpies and densities of six phosphate phases with MAEs of 0.09 eV/atom and 0.11 g/cm$^3$, respectively. A pretrained universal force-field baseline (MACE-MP-0) attains "
              + fm + " eV/atom on the same six phases, and 40 Magpie descriptor statistics leave formation-energy prediction unchanged ($R^2 \\approx 0$) while lifting density prediction to $R^2 = 0.27$.",
              "P12 abstrak baseline")

    # P13. Abstrak: resorbabilitas kuantitatif
    s = ganti(s,
              "and the stability--resorbability trade-off is made explicit.",
              "and the stability--resorbability trade-off is made explicit and quantitative via a resorbability-weighted re-ranking of the shortlist.",
              "P13 abstrak resorb")

    # P14. Kesimpulan: MACE (wording kondisional)
    if mae < 0.094:
        kal14 = ("A pretrained MACE-MP-0 baseline on the six benchmark phases (MAE " + fm
                 + " eV/atom) quantifies the accuracy headroom of structure-aware surrogates.")
    else:
        kal14 = ("A pretrained MACE-MP-0 baseline on the same six phases (MAE " + fm
                 + " eV/atom) situates the composition surrogate against modern structure-aware force fields.")
    s = ganti(s,
              "MLFF structural pre-validation confirms the stability of the top candidates and yields a porosity design target of 70--78\\% for cortical-bone stiffness; definitive DFT validation inputs are prepared.",
              "MLFF structural pre-validation confirms the stability of the top candidates and yields a porosity design target of 70--78\\% for cortical-bone stiffness; definitive DFT validation inputs are prepared. "
              + kal14,
              "P14 kesimpulan MACE")

    # P15. Bibitem MACE
    s = ganti(s,
              "\\bibitem{schmidt2019} Schmidt J, Marques MRG, Botti S, Marques MAL. Recent advances and applications of machine learning in solid-state materials science. \\textit{npj Comput Mater}. 2019;5:83.\n",
              "\\bibitem{schmidt2019} Schmidt J, Marques MRG, Botti S, Marques MAL. Recent advances and applications of machine learning in solid-state materials science. \\textit{npj Comput Mater}. 2019;5:83.\n"
              "\\bibitem{batatia2022} Batatia I, Kovacs DP, Simm G, Ortner C, Cs\\'anyi G. MACE: higher order equivariant message passing neural networks for fast and accurate force fields. \\textit{Adv Neural Inf Process Syst}. 2022;35:11423--11436.\n",
              "P15 bibitem MACE")

    (MS / nama_file).write_text(s, encoding="utf-8")
    return s


def main():
    baris, mae = muat_mace()
    print(f"MACE MAE = {mae:.3f} eV/atom (6 fase)")
    for nama in ["manuscript.tex", "manuscript_elsarticle.tex"]:
        t = patch((MS / nama).read_text(encoding="utf-8"), nama, baris, mae)
        sisa = [p for p in ["(medium, float64)", "batatia2022"] if p in t]
        masalah = [p for p in sisa if p == "(medium, float64)"]
        print(f"{nama}: sisa '(medium, float64)' -> {'MASIH ADA!' if masalah else 'bersih'}; batatia2022 -> {'ada' if 'batatia2022' in t else 'HILANG!'}")


if __name__ == "__main__":
    main()
