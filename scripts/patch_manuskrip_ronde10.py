"""Patch manuskrip ronde 10: konsistensi internal atas umpan balik reviewer.

(1) tab:top DIBANGUN ULANG dari ranking Monte Carlo (sumber kebenaran; tabel lama
bertentangan: karbonat rank 3 padahal top-5 hanya 16,6%); (2) re-ranking
resorbabilitas kini memakai S stoikiometrik (bukan -pKsp lintas stoikiometri) —
hasil dari mcdm_resorb_S.py; (3) tab:resorb memakai kolom S + footnote oksiapatit;
(4) tab:top_q1 diramping (kolom rho/Ca-P dihapus — sumber ketidakkonsistenan) +
narasi beta-TCP jujur; (5) klaim HA "+4,3% input tegang" dikoreksi -> overexpansion
PBE & MACE bersama (rho relax 3,05 vs 3,16 eksperimen); (6) rujukan seksi jadi
\ref+label; (7) tab:kalibrasi dipindah ke Methods (urutan tabel); (8) sitasi diurut
per kemunculan pertama (Elsevier); (9) Zenodo DIHAPUS + seksi Data availability
ganda di elsarticle digabung jadi satu; (10) teks diskusi/kesimpulan disesuaikan.

Syarat: ronde 9 sudah dijalankan; ranking_mc_ringkasan.json + resorb_S_ringkasan.json
sudah dibuat. Idempoten (guard: "ranking_mc_ringkasan" tidak ada di teks — guard
pakai marker baru "median rank (3{,}000"). Assertion count==1.
"""
import json
import re
from pathlib import Path

MS = Path(r"D:\latex\prgf2026\data\reports\manuscript")
PROC = Path(r"D:\latex\prgf2026\data\processed")

F_LATEX = {
    "Ca5P3O12F": "Ca$_5$P$_3$O$_{12}$F",
    "Ca10P6O25": "Ca$_{10}$P$_6$O$_{25}$",
    "Ca5P3HO13": "Ca$_5$P$_3$HO$_{13}$",
    "Ca3(PO4)2": "Ca$_3$(PO$_4$)$_2$",
    "Ca4P2O9": "Ca$_4$P$_2$O$_9$",
    "Ca2P2O7": "Ca$_2$P$_2$O$_7$",
    "Ca10P6CO27": "Ca$_{10}$P$_6$CO$_{27}$",
    "CaPHO4": "CaPHO$_4$",
    "Ca2P2H4O9": "Ca$_2$P$_2$H$_4$O$_9$",
    "Ca4P6O19": "Ca$_4$P$_6$O$_{19}$",
    "Ca(PO3)2": "Ca(PO$_3$)$_2$",
    "Ca8P6H12O29": "Ca$_8$P$_6$H$_{12}$O$_{29}$",
    "CaPH5O6": "CaPH$_5$O$_6$",
    "CaP2H2O7": "CaP$_2$H$_2$O$_7$",
    "CaP4O11": "CaP$_4$O$_{11}$",
}


def sci(x):
    """1.02e-14 -> $1.0\\times10^{-14}$ (2 angka penting)."""
    s = f"{x:.1e}"
    m, e = s.split("e")
    return f"${m}\\times10^{{{int(e)}}}$"


def ganti(s, lama, baru, label, n=1):
    k = s.count(lama)
    assert k == n, f"[{label}] ketemu {k}x (harus {n}): {lama[:70]}..."
    return s.replace(lama, baru)


def ambil_blok(s, marker, label):
    """Potong blok tabel mulai \begin{table} sebelum marker s/d \end{table} berikutnya."""
    mulai_marker = s.index(marker)
    assert s.count(marker) == 1, f"[{label}] marker tidak unik"
    mulai = s.rindex("\\begin{table}", 0, mulai_marker)
    akhir = s.index("\n\\end{table}\n", mulai_marker) + len("\n\\end{table}\n")
    blok = s[mulai:akhir]
    return s[:mulai] + s[akhir:], blok


def urutkan_bib(s, label):
    """Urutkan \bibitem menurut kemunculan pertama \cite di teks (sebelum bibliografi)."""
    mulai = s.index("\\begin{thebibliography}")
    akhir = s.index("\\end{thebibliography}") + len("\\end{thebibliography}")
    blok = s[mulai:akhir]
    arg = re.search(r"\\begin\{thebibliography\}\{(\d+)\}", blok).group(1)
    item = re.findall(r"\\bibitem\{([^}]+)\}(.*?)(?=\n\\bibitem|\n\\end\{thebibliography\})", blok, re.S)
    bibit = {k: f"\\bibitem{{{k}}}{v}" for k, v in item}
    urutan = []
    for m in re.finditer(r"\\cite\{([^}]+)\}", s[:mulai]):
        for k in m.group(1).split(","):
            k = k.strip()
            if k not in urutan:
                urutan.append(k)
    assert set(urutan) == set(bibit), f"[{label}] cite vs bibitem tidak setara: " \
        f"tanpa bibitem={set(urutan)-set(bibit)}, tak dikutip={set(bibit)-set(urutan)}"
    baru = f"\\begin{{thebibliography}}{{{arg}}}\n" + "\n".join(bibit[k] for k in urutan) + "\n\\end{thebibliography}"
    return s[:mulai] + baru + s[akhir:]


def patch(s, nama_file):
    if "Median rank [p5--p95]" in s:
        print(f"{nama_file}: sudah ter-patch ronde 10, dilewati")
        return s

    mc = json.loads((PROC / "ranking_mc_ringkasan.json").read_text(encoding="utf-8"))["top15"]
    rs = json.loads((PROC / "resorb_S_ringkasan.json").read_text(encoding="utf-8"))["rows"]
    assert [r["formula"] for r in mc[:4]] == ["Ca5P3O12F", "Ca10P6O25", "Ca5P3HO13", "Ca3(PO4)2"]
    assert [r["formula"] for r in rs[:2]] == ["Ca3(PO4)2", "Ca4P2O9"]
    assert [r["formula"] for r in rs[-2:]] == ["Ca5P3HO13", "Ca5P3O12F"]

    # P1. tab:top DIBANGUN ULANG dari MC
    baris_top = "\n".join(
        f"{F_LATEX[r['formula']]} & {r['keluarga']} & {r['order']} & "
        f"{r['median_rank']:.0f} [{r['p5_rank']:.0f}--{r['p95_rank']:.0f}] & "
        f"{r['E_f']:+.2f} & {r['rho']:.2f} & {r['ca_p']:.2f} \\\\"
        for r in mc)
    tabel_top = (
        "\\begin{table}[ht]\n\\centering\\small\n"
        "\\caption{Top 15 candidate compositions (reduced-formula groups; charge-neutral calcium phosphates) ordered by Monte Carlo median rank (3{,}000 runs; TOPSIS and VIKOR across three weighting scenarios with Dirichlet-sampled weights and ML-prediction noise; lower is better). $E_f$, $\\rho$, and Ca/P are the consolidated-dataset record values of each composition's best-ranked record.}\n"
        "\\label{tab:top}\n"
        "\\begin{tabular}{llclccc}\n\\toprule\n"
        "Formula & Family & Order & Median rank [p5--p95] & $E_f$ (eV/at) & $\\rho$ (g/cm$^3$) & Ca/P \\\\\n\\midrule\n"
        + baris_top + "\n\\bottomrule\n\\end{tabular}\n\\end{table}\n\n")
    s, _ = ambil_blok(s, "\\caption{Top 15 candidate biomaterials", "P1 tab:top lama")
    s = ganti(s, "\\begin{table}[ht]\n\\centering\\small\n\\caption{Q1 phase-level ranking",
              tabel_top + "\\begin{table}[ht]\n\\centering\\small\n\\caption{Q1 phase-level ranking",
              "P1 tab:top baru")

    # P2. tab:top_q1: hapus kolom rho/Ca-P (sumber ketidakkonsistenan) + kapsi baru
    tabel_q1 = (
        "\\begin{table}[ht]\n\\centering\\small\n"
        "\\caption{Q1 phase-level ranking (21 compositions; C1 = $E_\\mathrm{hull}$; the C2 density-band and C3 Ca/P criteria use the phase-aggregated values; top 10 shown). Spearman vs the deterministic record-level ranking: 0.75.}\n"
        "\\label{tab:top_q1}\n"
        "\\begin{tabular}{lcc}\n\\toprule\n"
        "Formula & $E_\\mathrm{hull}$ (eV/at) & Rank \\\\\n\\midrule\n"
        "Ca5P3O12F & 0.000 & 1 \\\\\n"
        "Ca5P3HO13 & 0.000 & 2 \\\\\n"
        "Ca10P6CO27 & 0.000 & 3 \\\\\n"
        "Ca10P6O25 & 0.007 & 4 \\\\\n"
        "Ca4P2O9 & 0.000 & 5 \\\\\n"
        "Ca8P6H12O29 & 0.016 & 6 \\\\\n"
        "CaPHO4 & 0.000 & 7 \\\\\n"
        "Ca2P2O7 & 0.000 & 8 \\\\\n"
        "Ca2P2H4O9 & 0.009 & 9 \\\\\n"
        "CaPH5O6 & 0.016 & 10 \\\\\n"
        "\\bottomrule\n\\end{tabular}\n\\end{table}\n\n")
    s, blok_q1 = ambil_blok(s, "\\caption{Q1 phase-level ranking", "P2 tab:top_q1 lama")
    assert "Ca5P3O12F" in blok_q1
    s = ganti(s, "\\begin{table}[ht]\n\\centering\\small\n\\caption{Resorbability-weighted re-ranking",
              tabel_q1 + "\\begin{table}[ht]\n\\centering\\small\n\\caption{Resorbability-weighted re-ranking",
              "P2 tab:top_q1 baru")

    # P3. tab:resorb_rank dari re-ranking S
    KELAS_RESORB = {
        "Ca3(PO4)2": "resorbable",
        "Ca4P2O9": "slowly resorbable",
        "CaPHO4": "fast",
        "CaPH5O6": "fast",
        "Ca8P6H12O29": "fast in vivo",
        "Ca10P6O25": "apatite",
        "Ca5P3HO13": "apatite",
        "Ca5P3O12F": "apatite",
    }
    baris_rs = "\n".join(
        f"{F_LATEX[r['formula']]} & {KELAS_RESORB[r['formula']]} & {r['order_mc']} & "
        f"{r['order_resorb_S']} & {r['ca_p']:.2f} & {sci(r['S_mol_L'])} \\\\"
        for r in rs)
    tabel_rs = (
        "\\begin{table}[ht]\n\\centering\\small\n"
        "\\caption{Resorbability-weighted re-ranking of the shortlist: three criteria (stability, Ca/P proximity, resorbability = stoichiometric equilibrium solubility $S$; Table~\\ref{tab:kelarutan}) under three weighting scenarios (balanced; stability-dominant; resorbability-dominant). Only compositions with literature solubility products (25\\,$^\\circ$C) are included; the density-band criterion is non-discriminative on this shortlist and is dropped.}\n"
        "\\label{tab:resorb_rank}\n"
        "\\begin{tabular}{llcccc}\n\\toprule\n"
        "Formula & Class & Order (Tab.~\\ref{tab:top}) & Order (+resorb.) & Ca/P & $S$ (mol/L) \\\\\n\\midrule\n"
        + baris_rs + "\n\\bottomrule\n\\end{tabular}\n\\end{table}\n\n")
    s, blok_rs = ambil_blok(s, "\\caption{Resorbability-weighted re-ranking of the shortlist", "P3 tab:resorb_rank lama")
    assert "tab:resorb_rank" in blok_rs
    s = ganti(s, "\\begin{table}[ht]\n\\centering\\small\n\\caption{MACE-to-MP-GGA calibration",
              tabel_rs + "\\begin{table}[ht]\n\\centering\\small\n\\caption{MACE-to-MP-GGA calibration",
              "P3 tab:resorb_rank baru")

    # P4. tab:resorb: kolom pKsp -> S + footnote oksiapatit
    tabel_resorb = (
        "\\begin{table}[ht]\n\\centering\\small\n"
        "\\caption{Literature resorbability overlay for the clinically established shortlist phases (25\\,$^\\circ$C); $S$ = stoichiometric equilibrium solubility (mol/L) converted from literature p$K_\\mathrm{sp}$ (Table~\\ref{tab:kelarutan}); degradation class after \\cite{dorozhkin2009}.}\n"
        "\\label{tab:resorb}\n"
        "\\begin{tabular}{lccll}\n\\toprule\n"
        "Phase & $S$ (mol/L) & Degradation class & Order (Tab.~\\ref{tab:top}) & Scaffold role \\\\\n\\midrule\n"
        "Brushite (DCPD) & $5.1\\times10^{-4}$ & fast & 13 & resorbable cement precursor \\\\\n"
        "Monetite (DCPA) & $3.5\\times10^{-4}$ & fast & 8 & resorbable cement precursor \\\\\n"
        "OCP & $2.0\\times10^{-7}$ & fast in vivo & 12 & HA precursor, resorbable \\\\\n"
        "$\\alpha$-TCP & $3.1\\times10^{-6}$ & resorbable & (same comp. as 4) & cement setting component \\\\\n"
        "$\\beta$-TCP & $6.5\\times10^{-7}$ & resorbable & 4 & resorbable scaffold (clinical) \\\\\n"
        "TTCP & $1.4\\times10^{-6}$ & slowly resorbable & 5 & cement setting component \\\\\n"
        "Hydroxyapatite & $3.0\\times10^{-14}$ & essentially insoluble & 3 & permanent/low-turnover \\\\\n"
        "Fluorapatite & $1.0\\times10^{-14}$ & essentially insoluble & 1 & dental, low-turnover \\\\\n"
        "Oxyapatite$^{a}$ & $1.8\\times10^{-8}$ & essentially insoluble & 2 & high-temperature apatite \\\\\n"
        "\\bottomrule\n\\end{tabular}\n"
        "\\vspace{2pt}\\footnotesize $^{a}$No literature value; p$K_\\mathrm{sp}$ assumed equal to hydroxyapatite (lower bound after \\cite{elliott1994}).\n"
        "\\end{table}\n\n")
    s, blok_resorb = ambil_blok(s, "\\caption{Literature resorbability overlay", "P4 tab:resorb lama")
    assert "Scaffold role" in blok_resorb
    s = ganti(s, "Several limitations are worth noting",
              tabel_resorb + "Several limitations are worth noting", "P4 tab:resorb baru")

    # P5. Narasi MC: slot kelima + q1 + beta-TCP jujur
    s = ganti(s,
              "while carbonated apatite and tetracalcium phosphate contest the fifth slot (17\\% each).",
              "while tetracalcium phosphate (17\\%), carbonated apatite (17\\%), and calcium pyrophosphate (16\\%) contest the fifth slot.",
              "P5 slot kelima")
    s = ganti(s,
              "With the hull-based C1 and phase-level aggregation (Table~\\ref{tab:top_q1}), the same apatitic phases lead, and the ranking correlates with the record-level ranking (Spearman 0.75); the COD screen confirms the pool's coverage rather than overturning it.",
              "With the hull-based C1 and phase-level aggregation (Table~\\ref{tab:top_q1}), the four apatitic phases again lead, and the ranking correlates with the deterministic record-level ranking (Spearman 0.75); $\\beta$-TCP---order 4 under uncertainty propagation---sits outside the phase-level top 10, a difference the correlation quantifies rather than hides.",
              "P5 q1 + beta-TCP")
    s = ganti(s,
              "A resorbability-weighted sensitivity analysis (Table~\\ref{tab:resorb_rank}) re-ranks the eight shortlist compositions with literature $\\mathrm{p}K_\\mathrm{sp}$ on three criteria (stability, Ca/P proximity, resorbability) under three weighting scenarios: $\\beta$-TCP, tetracalcium phosphate, and monetite climb to the top three, while fluorapatite, oxyapatite, and hydroxyapatite drop the most, making the stability--resorbability trade-off quantitatively explicit.",
              "A resorbability-weighted sensitivity analysis (Table~\\ref{tab:resorb_rank}) re-ranks the eight shortlist compositions with literature solubility products converted to stoichiometric equilibrium solubilities $S$ on three criteria (stability, Ca/P proximity, resorbability) under three weighting scenarios: $\\beta$-TCP and tetracalcium phosphate occupy the top two slots, monetite and oxyapatite follow, while hydroxyapatite and fluorapatite fall to the bottom, making the stability--resorbability trade-off quantitatively explicit.",
              "P5 narasi resorb S")

    # P6. Methods MCDM: -pKsp -> S
    s = ganti(s,
              "resorbability ($-\\mathrm{p}K_\\mathrm{sp}$; more soluble is better for a resorbable scaffold)",
              "resorbability (stoichiometric equilibrium solubility $S$, more soluble is better for a resorbable scaffold)",
              "P6 kriteria S")
    s = ganti(s,
              "because $\\mathrm{p}K_\\mathrm{sp}$ values exist for known phases alone and cannot be generalized to the full candidate pool.",
              "because solubility data exist for known phases alone and cannot be generalized to the full candidate pool.",
              "P6 alasan S")

    # P7. Klaim HA "+4,3% input tegang" -> overexpansion PBE & MACE bersama
    s = ganti(s,
              "hydroxyapatite expands by $+4.3\\%$---a genuine relaxation of the strained idealized input structure, reproduced almost exactly by DFT vc-relax (final volumes 547.6 vs.\\ 547.7 \\AA$^3$), not an MLFF artifact",
              "hydroxyapatite expands by $+4.3\\%$---reproduced almost exactly by DFT vc-relax (final volumes 547.6 vs.\\ 547.7 \\AA$^3$; $\\rho = 3.05$ g/cm$^3$ vs.\\ 3.16 experimental), a systematic overexpansion shared by both methods rather than an MLFF artifact (the input structure itself is consistent with experiment, $\\rho = 3.18$ g/cm$^3$)",
              "P7 HA overexpansion")
    s = ganti(s,
              "hydroxyapatite $+4.3\\%$, reproduced by DFT vc-relax to within 0.1\\% of the MLFF final volume)",
              "hydroxyapatite $+4.3\\%$, reproduced by DFT vc-relax---a shared systematic overexpansion of this phase rather than an artifact of either method)",
              "P7 diskusi HA")

    # P8. Diskusi: peringkat baru + kalimat kelarutan + kontes slot-5
    s = ganti(s,
              "tetracalcium phosphate (rank 6) and monetite (rank 9)---the two setting components of the classic calcium phosphate cements---and octacalcium phosphate (rank 8) sit inside the shortlist; the tail (ranks 10--15) consists of acid and condensed calcium phosphates that rank poorly on stability.",
              "tetracalcium phosphate (order 5) and monetite (order 8)---the two setting components of the classic calcium phosphate cements---sit inside the shortlist; octacalcium phosphate (order 12) and the tail (orders 9--15) consist of acid and condensed calcium phosphates that rank poorly on stability.",
              "P8 peringkat diskusi")
    s = ganti(s,
              "the fifth slot is contested (17\\% each for carbonated apatite and tetracalcium phosphate)",
              "the fifth slot is contested (17\\% tetracalcium phosphate, 17\\% carbonated apatite, 16\\% calcium pyrophosphate)",
              "P8 kontes slot-5 diskusi")
    s = ganti(s,
              "Table~\\ref{tab:resorb} overlays literature solubility products (negative decadic logarithm, p$K_\\mathrm{sp}$, 25\\,$^\\circ$C) and degradation class~\\cite{elliott1994,dorozhkin2009,wang2008} onto the clinically established shortlist phases.",
              "Table~\\ref{tab:resorb} overlays stoichiometric equilibrium solubilities $S$ (mol/L at 25\\,$^\\circ$C, converted from literature p$K_\\mathrm{sp}$; Table~\\ref{tab:kelarutan}) and degradation class~\\cite{elliott1994,dorozhkin2009,wang2008} onto the clinically established shortlist phases.",
              "P8 kalimat kelarutan")
    s = ganti(s,
              "The order is instructive: brushite and monetite are orders of magnitude more soluble than octacalcium phosphate, which in turn degrades faster than the TCPs, while the apatites (hydroxyapatite, fluorapatite, oxyapatite) are essentially insoluble under physiological pH.",
              "The order is instructive: brushite and monetite are orders of magnitude more soluble than the TCPs and octacalcium phosphate, while the apatites (hydroxyapatite, fluorapatite, oxyapatite) are essentially insoluble under physiological pH.",
              "P8 urutan kelarutan")
    s = ganti(s,
              "with resorbability as a criterion, $\\beta$-TCP, tetracalcium phosphate, and monetite occupy the top three slots while the apatites fall to the bottom",
              "with resorbability as a criterion, $\\beta$-TCP and tetracalcium phosphate occupy the top two slots while hydroxyapatite and fluorapatite fall to the bottom",
              "P8 hasil re-rank S")

    # P9. Rujukan seksi -> label + ref
    s = ganti(s, "\\subsection{Multi-objective ranking}",
              "\\subsection{Multi-objective ranking}\\label{sec:ranking}", "P9 label ranking")
    s = ganti(s, "\\subsection{Solubility screening}",
              "\\subsection{Solubility screening}\\label{sec:kelarutan}", "P9 label kelarutan")
    s = ganti(s, "\\subsection{Interpretability and experimental validation}",
              "\\subsection{Interpretability and experimental validation}\\label{sec:validasi}", "P9 label validasi")
    s = ganti(s, "\\section{Discussion}", "\\section{Discussion}\\label{sec:diskusi}", "P9 label diskusi")
    s = ganti(s, "handled downstream (Section 3.4)", "handled downstream (Section~\\ref{sec:validasi})", "P9 ref validasi")
    s = ganti(s, "assessed post hoc from literature for the shortlist (Section 3.3)",
              "assessed post hoc from literature for the shortlist (Section~\\ref{sec:kelarutan})", "P9 ref kelarutan")
    s = ganti(s, "trade-off in Section 4.", "trade-off in Section~\\ref{sec:diskusi}.", "P9 ref diskusi")

    # P10. tab:kalibrasi dipindah ke Methods (setelah paragraf ML, sebelum MCDM)
    s, blok_kal = ambil_blok(s, "\\caption{MACE-to-MP-GGA calibration", "P10 tab:kalibrasi lama")
    assert "tab:kalibrasi" in blok_kal
    s = ganti(s, "\\subsection{Multi-criteria decision making (MCDM)}",
              blok_kal + "\\subsection{Multi-criteria decision making (MCDM)}", "P10 tab:kalibrasi ke Methods")

    # P11. Zenodo dihapus + Data availability disatukan (elsarticle punya seksi ganda)
    s = ganti(s,
              "The consolidated dataset (2{,}885 entries, 950 unique compositions), the versioned snapshot with SHA-256 checksums, the DFT elastic-validation inputs and outputs (Quantum ESPRESSO input decks, stress tensors, and elastic constants of the five top candidates), and the complete pipeline source code are openly available at \\url{https://github.com/soegianto-s/prgf2027-materials-informatics}; a citable Zenodo archive will be deposited upon acceptance (DOI to be inserted at the proof stage). The underlying data originate from the Materials Project (CC-BY 4.0), AFLOW, the Crystallography Open Database (CC0), PubChem (public domain), and OQMD, with access dates and licenses recorded per source.",
              "The consolidated dataset (2{,}885 entries, 950 unique compositions), the descriptor table, candidate ranking, per-stage reports, the DFT elastic-validation inputs and outputs (Quantum ESPRESSO input decks, stress tensors, and elastic constants of the five top candidates), and the complete pipeline source code are openly available at \\url{https://github.com/soegianto-s/prgf2027-materials-informatics} (git-tracked; dataset snapshot with SHA-256 checksums). The underlying data originate from the Materials Project (CC-BY 4.0), AFLOW, the Crystallography Open Database (CC0), PubChem (public domain), and OQMD, with access dates and licenses recorded per source; AFLOW and OQMD require citation of their respective references.",
              "P11 data availability terpadu")
    if "Data and code availability" in s:
        i0 = s.index("\\section*{Data and code availability}")
        i1 = s.index("\\begin{thebibliography}")
        assert "project repository" in s[i0:i1], "P11: teks seksi ganda tidak ditemukan"
        s = s[:i0] + s[i1:]

    # P12. Urutkan sitasi per kemunculan pertama
    s = urutkan_bib(s, "P12 urutan sitasi")

    (MS / nama_file).write_text(s, encoding="utf-8")
    return s


def main():
    for nama in ["manuscript.tex", "manuscript_elsarticle.tex"]:
        t = patch((MS / nama).read_text(encoding="utf-8"), nama)
        sisa = [p for p in ["Zenodo", "Data and code availability", "-\\mathrm{p}K_\\mathrm{sp}",
                            "rank 6) and monetite (rank 9)", "strained idealized input",
                            "17\\% each for carbonated apatite", "Section 3.4", "Section 3.3",
                            "3.13 & 1.67", "cited in the project repository"]
                if p in t]
        print(f"{nama}: sisa pola lama -> {sisa if sisa else 'bersih'}")
        print(f"  marker baru: tab:top MC={'Median rank [p5--p95]' in t}, "
              f"resorb S={'resorbability = stoichiometric equilibrium solubility' in t}, "
              f"HA overexpansion={'systematic overexpansion shared by both methods' in t}, "
              f"kalibrasi di Methods={'Multi-criteria decision making (MCDM)' in t and t.index('tab:kalibrasi') < t.index('Multi-criteria decision making')}")


if __name__ == "__main__":
    main()
