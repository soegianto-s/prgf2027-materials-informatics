"""Patch manuskrip ronde 9: revisi menyeluruh berdasarkan umpan balik reviewer.

Isi: (1) abstrak ditulis ulang <=250 kata, (2) jejak riwayat revisi dihapus (naskah
menceritakan studi final), (3) seksi substitusi + Tabel 9 dipotong (keputusan user),
(4) sitasi diri soelistiono2026 + bibitem dorozhkin dihapus, (5) sitasi yang tadinya
tidak dikutip kini dikutip (jain2013, curtarolo2012, kirklin2015, grazulis2009,
mathew1977, lundberg2017), (6) perbaikan: 0.493->0.226, ref tab:top rusak, urutan
tabel (tab:val dipindah sebelum tab:bench), duplikat "950 unique compositions",
klaim clustering vs 43% noise, angka figur (n=2829, 91.4%), (7) data availability
dengan URL GitHub publik.

Syarat: patch ronde 8 + 8b sudah dijalankan. Idempoten (guard URL GitHub).
Assertion count==1; diterapkan pada kedua file .tex.
"""
import re
from pathlib import Path

MS = Path(r"D:\latex\prgf2026\data\reports\manuscript")

ABSTRAK_BARU = (
    "Bone defects from trauma, disease, and congenital conditions remain a major clinical challenge. "
    "Calcium phosphate biomaterials are attractive scaffold candidates owing to their biocompatibility and "
    "osteoconductivity, yet systematic candidate selection is time- and cost-intensive. We present an "
    "end-to-end Materials Informatics framework that integrates five open databases (2{,}885 curated "
    "entries, 950 unique compositions), leakage-resistant machine learning, and multi-objective ranking "
    "to screen calcium phosphate compositions for bone scaffolds. Under composition-grouped "
    "cross-validation, the composition-only formation-energy model attains $R^2 = 0.11$ with no "
    "within-family predictive power, yet reproduces experimental formation enthalpies and densities of six "
    "benchmark phases with MAEs of 0.09 eV/atom and 0.11 g/cm$^3$. Multi-objective ranking (TOPSIS/VIKOR "
    "over stability, a clinically processable density band, and Ca/P ratio, with charge-neutrality "
    "filtering and Monte Carlo uncertainty propagation) places fluorapatite, oxyapatite, hydroxyapatite, "
    "and $\\beta$-TCP at the top with high rank stability, and a literature resorbability overlay makes "
    "the stability--resorbability trade-off explicit. Definitive PBE-DFT elastic validation places the "
    "top candidates' dense-material Young's moduli at 216.6--235.8 GPa and reproduces the MACE-MP-0 "
    "force-field pre-validation within $\\approx$6\\%, confirming its reliability for this material "
    "class; Gibson--Ashby scaling then yields a 70--79\\% porosity design target for cortical-bone "
    "stiffness. The framework systematically screens and orders known composition space without claiming "
    "accelerated discovery, and is fully replicable (versioned dataset, open code)."
)


def hitung_kata(ab):
    t = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^}]*\})?", " ", ab)
    t = t.replace("{,}", ",").replace("--", " ").replace("~", " ")
    return len([w for w in re.split(r"\s+", t) if re.search(r"[A-Za-z0-9]", w)])


def ganti(s, lama, baru, label, n=1):
    k = s.count(lama)
    assert k == n, f"[{label}] ketemu {k}x (harus {n}): {lama[:70]}..."
    return s.replace(lama, baru)


def hapus_blok_tabel(s, marker_kapsi, label):
    """Hapus blok tabel (mulai \begin{table} sampai \end{table} pertama setelah marker)."""
    mulai = s.index(marker_kapsi)
    mulai_tabel = s.rindex("\\begin{table}", 0, mulai)
    akhir = s.index("\n\\end{table}\n", mulai) + len("\n\\end{table}\n")
    assert s.count(marker_kapsi) == 1, f"[{label}] marker kapsi tidak unik"
    return s[:mulai_tabel] + s[akhir:], s[mulai_tabel:akhir]


def patch(s, nama_file):
    if "prgf2027-materials-informatics" in s:
        print(f"{nama_file}: sudah ter-patch ronde 9, dilewati")
        return s
    assert "tab:dft_elastik" in s, f"{nama_file}: jalankan patch ronde 8/8b dulu"

    # R1. Abstrak baru (<=250 kata) — penggantian programatik, tanpa transkripsi teks lama
    n_kata = hitung_kata(ABSTRAK_BARU)
    assert n_kata <= 250, f"abstrak baru {n_kata} kata > 250"
    mulai = s.index("Bone defects arising from trauma")
    akhir = s.index("AI-assisted biomaterial screening platform.") + len("AI-assisted biomaterial screening platform.")
    s = s[:mulai] + ABSTRAK_BARU + s[akhir:]

    # R2. Intro: hapus kalimat studi awal + sitasi diri
    s = ganti(s,
              "As a preliminary step, our group developed a data-driven discovery workflow for calcium phosphate scaffolds using materials informatics and machine learning clustering, screening hundreds of compounds based on thermodynamic stability, crystal structure, density, and electronic properties~\\cite{soelistiono2026}. That study demonstrated that multi-objective descriptor balancing yields more representative material rankings than single dominant parameters, but it did not yet constitute a systematic, replicable framework. The present work advances beyond it in five specific ways:",
              "The present work contributes in five specific ways:",
              "R2 hapus sitasi diri")

    # R3. MCDM: kriteria "withdrawn on scrutiny" -> pilihan desain
    s = ganti(s, "Two earlier criteria were withdrawn on internal and reviewer scrutiny:",
              "Two further candidate criteria were excluded by design:", "R3 kriteria MCDM")

    # R4. Sitasi yang selama ini tidak dikutip
    s = ganti(s, "the Materials Project REST API (CC-BY 4.0)",
              "the Materials Project REST API~\\cite{jain2013} (CC-BY 4.0)", "R4 jain2013")
    s = ganti(s, "the Crystallography Open Database (COD, CC0, queried over HTTP)",
              "the Crystallography Open Database~\\cite{grazulis2009} (COD, CC0, queried over HTTP)", "R4 grazulis2009")
    s = ganti(s, "cite Curtarolo et al.", "\\cite{curtarolo2012}", "R4 curtarolo2012")
    s = ganti(s, "cite Kirklin et al.", "\\cite{kirklin2015}", "R4 kirklin2015")
    s = ganti(s, "SHAP (TreeExplainer) values", "SHAP (TreeExplainer)~\\cite{lundberg2017} values", "R4 lundberg2017")
    s = ganti(s, "reproduced to $\\leq 0.03\\%$ because COD stores",
              "reproduced to $\\leq 0.03\\%$~\\cite{mathew1977} because COD stores", "R4 mathew1977")

    # R5. Dataset: duplikat 950 + n figur + clustering jujur + n=9 tanpa forward-ref tabel
    s = ganti(s,
              "The consolidated dataset contains 2{,}885 entries and 950 unique compositions (950 unique compositions, exceeding the curation target of 500).",
              "The consolidated dataset contains 2{,}885 entries and 950 unique compositions, exceeding the curation target of 500 (2{,}829 entries carry the complete five-descriptor set used in the figures).",
              "R5 duplikat 950")
    s = ganti(s,
              "elastic moduli for 0.3\\% ($n=9$; DFT-computed for the five top candidates, Table~\\ref{tab:dft_elastik}).",
              "elastic moduli for 0.3\\% ($n=9$; dense-material elastic constants for the five top candidates are DFT-computed and reported below).",
              "R5 n=9 tanpa forward-ref")
    s = ganti(s,
              "Clustering is robust: K-means ($k=5$, silhouette 0.502) is consistent with hierarchical Ward clustering (ARI = 0.884), and HDBSCAN identifies 17 dense clusters with 1{,}246 noise points (Supplementary).",
              "K-means ($k=5$, silhouette 0.502) and hierarchical Ward clustering agree closely (ARI = 0.884); HDBSCAN instead assigns 1{,}246 of 2{,}885 entries (43\\%) to noise while finding 17 dense clusters (Supplementary), indicating that the design space forms continuous families rather than well-separated clusters.",
              "R5 clustering jujur")

    # R6. Figur: angka dari regenerasi dataset penuh
    s = ganti(s, "shows that 88\\% of the five nearest neighbors of an entry come from the same database",
              "shows that 91.4\\% of the five nearest neighbors of an entry come from the same database",
              "R6 fraksi tetangga")
    s = ganti(s, "The dataset is source-biased (88\\% same-source nearest neighbors)",
              "The dataset is source-biased (91.4\\% same-source nearest neighbors)",
              "R6 diskusi bias sumber")
    s = ganti(s,
              "Design space of calcium phosphates mapped by PCA over five non-collinear descriptors, colored by material family.",
              "Design space of calcium phosphates ($n=2{,}829$ entries with the complete five-descriptor set) mapped by PCA over five non-collinear descriptors, colored by material family (legend counts are family memberships).",
              "R6 kapsi Fig 1")
    s = ganti(s,
              "t-SNE embedding colored by data source, revealing source-driven separation (88\\% same-source nearest neighbors) that motivates the computational-only modeling subset.",
              "t-SNE embedding of the $2{,}829$ entries with the complete five-descriptor set, colored by data source (legend counts per database); 91.4\\% of the five nearest neighbors share an entry's source, revealing source-driven separation that motivates the computational-only modeling subset.",
              "R6 kapsi Fig 3")

    # R7. Hasil ML: klausa headline scores + angka density salah + recorded decision
    s = ganti(s,
              "within the phosphate family alone: composition alone carries essentially no within-family predictive power, and earlier headline scores reflected the trivial phosphide--phosphate separation and structure features.",
              "within the phosphate family alone: composition alone carries essentially no within-family predictive power.",
              "R7 hapus headline scores")
    s = ganti(s,
              "for density they add a modest gain ($R^2$ 0.493 $\\rightarrow$ 0.293)",
              "for density the structure features yield a modest gain on the same subset ($R^2$ 0.226 $\\rightarrow$ 0.293)",
              "R7 angka density")
    s = ganti(s,
              "imputation was therefore abandoned (recorded decision).",
              "imputation is therefore not used.",
              "R7 recorded decision")

    # R8. Ranking: "earlier one" -> "record-level"
    s = ganti(s, "the ranking correlates with the earlier one (Spearman 0.75)",
              "the ranking correlates with the record-level ranking (Spearman 0.75)", "R8 teks ranking")
    s = ganti(s, "Spearman vs the earlier record-level ranking: 0.75",
              "Spearman vs the record-level ranking: 0.75", "R8 kapsi ranking")

    # R9. Potong seksi substitusi (keputusan user)
    s = ganti(s, "\\subsection{Solubility and substitution screening}",
              "\\subsection{Solubility screening}", "R9 judul seksi")
    s = ganti(s,
              " in Section 4. The substitution screen (Table~\\ref{tab:substitusi}) extends the design space: Si-substituted Ca$_5$Si(PO$_6$)$_2$ ranks first, Mg-phosphates dominate the endpoints, and every Sr-phosphate is excluded by the clinical density band (all above 3.2 g/cm$^3$)---a constraint the screen makes explicit rather than ignores.",
              " in Section 4.", "R9 paragraf substitusi")
    s, blok_sub = hapus_blok_tabel(s, "\\caption{Substitution screen over Ca--P--O--X", "R9 tabel substitusi")
    assert "tab:substitusi" in blok_sub and len(blok_sub) > 400

    # R10. Pindah tab:val ke setelah paragraf QC (sebelum tab:bench) — urutan pembahasan benar
    mulai_val = s.index("\\begin{table}[ht]\n\\centering\\small\n\\caption{Dataset quality control:")
    akhir_val = s.index("\n\\end{table}\n", mulai_val) + len("\n\\end{table}\n")
    blok_val = s[mulai_val:akhir_val]
    s = s[:mulai_val] + s[akhir_val:]
    s = ganti(s,
              "a typical GGA overbinding artifact recorded as a source-specific limitation.\n\n\\textbf{Independent model validation.}",
              "a typical GGA overbinding artifact recorded as a source-specific limitation.\n\n" + blok_val + "\\textbf{Independent model validation.}",
              "R10 pindah tab:val")

    # R11. Diskusi: hapus riwayat revisi
    s = ganti(s,
              "We therefore make no claim of ``rediscovering'' the clinical hierarchy, and accordingly the phrase ``accelerated discovery'' has been removed from the title and framing of this work: the framework screens and orders known composition space rather than discovering new phases.",
              "We therefore make no claim of ``rediscovering'' the clinical hierarchy: the framework screens and orders known composition space rather than discovering new phases.",
              "R11 frase diperiksa ulang diskusi")
    s = ganti(s, "A project-internal accuracy target ($R^2 \\geq 0.85$) that predated the leakage analysis is withdrawn as arbitrary. ",
              "", "R11 target withdrawn")
    s = ganti(s,
              "Reduced-formula grouping, nested CV, and the four-DOF composition feature set materially lowered reported scores (formation-energy $R^2$ from 0.87 to 0.11 in the discovery setting); a further structural finding is that",
              "Reduced-formula grouping, nested CV, and the four-DOF composition feature set are the leakage controls that define the reported scores; a further structural finding is that",
              "R11 0.87 ke 0.11")
    s = ganti(s,
              "which is why the modulus criterion (C4) was withdrawn rather than median-imputed (Methods)",
              "which is why the modulus criterion (C4) is deliberately omitted rather than median-imputed (Methods)",
              "R11 C4 withdrawn")
    s = ganti(s,
              "and was withdrawn as a predictive claim and as an MCDM criterion.",
              "and is therefore neither reported as a predictive claim nor used as an MCDM criterion.",
              "R11 suitability withdrawn")

    # R12. Header tabel resorb: ref tab:top rusak
    s = ganti(s, "Rank (tab:top)", "Rank (Tab.~\\ref{tab:top})", "R12 ref tab:top")

    # R13. Kesimpulan: buang "says so in its title"
    s = ganti(s,
              "it makes no claim of accelerated discovery of new phases, and it says so in its title.",
              "it makes no claim of accelerated discovery of new phases.",
              "R13 kesimpulan")

    # R14. Data availability: tautan GitHub publik (keputusan user)
    s = ganti(s,
              "and the complete pipeline source code are available in the accompanying research repository, which will be deposited on Zenodo upon acceptance (DOI to be inserted at the proof stage).",
              "and the complete pipeline source code are openly available at \\url{https://github.com/soegianto-s/prgf2027-materials-informatics}; a citable Zenodo archive will be deposited upon acceptance (DOI to be inserted at the proof stage).",
              "R14 tautan GitHub")

    # R15. Hapus bibitem tidak terpakai (sitasi diri + buku dorozhkin duplikat)
    s = ganti(s,
              "\\bibitem{soelistiono2026} Soelistiono S. Data-driven discovery of calcium-phosphate biomaterial scaffolds using materials informatics and machine learning clustering. \\textit{Int J Appl Pharm Life Sci}. 2026.\n",
              "", "R15 bibitem soelistiono")
    s = ganti(s,
              "\\bibitem{dorozhkin} Dorozhkin SV. Calcium orthophosphates: applications in nature, biology, and medicine. \\textit{Pan Stanford Publishing}; 2012.\n",
              "", "R15 bibitem dorozhkin buku")

    (MS / nama_file).write_text(s, encoding="utf-8")
    return s


def main():
    print(f"kata abstrak baru: {hitung_kata(ABSTRAK_BARU)} (batas 250)")
    for nama in ["manuscript.tex", "manuscript_elsarticle.tex"]:
        t = patch((MS / nama).read_text(encoding="utf-8"), nama)
        sisa = [p for p in ["withdrawn on internal and reviewer", "headline scores", "0.87 to 0.11",
                            "has been removed from the title", "withdrawn as arbitrary", "recorded decision",
                            "cite Curtarolo", "cite Kirklin", "soelistiono2026", "tab:substitusi",
                            "Substitution screen", "0.493", "950 unique compositions (950",
                            "Rank (tab:top)", "will be deposited on Zenodo upon acceptance",
                            "88\\% same-source", "88\\% of the five", "and it says so in its title"]
                if p in t]
        print(f"{nama}: sisa pola lama -> {sisa if sisa else 'bersih'}")
        m_url = "prgf2027-materials-informatics" in t
        m_n = "2{,}829" in t
        m_914 = "91.4\\%" in t
        m_jain = "\\cite{jain2013}" in t
        m_val = "Independent model validation." in t
        print(f"  marker baru: URL GitHub={m_url}, n=2829={m_n}, 91.4%={m_914}, jain2013={m_jain}, tab:val urut={m_val}")


if __name__ == "__main__":
    main()
