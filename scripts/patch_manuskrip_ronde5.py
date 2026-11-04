"""Patch manuskrip ronde 5 (reviewer: literatur/baseline, gaya penulisan, encoding, data availability).

Setiap replace ber-assertion — tidak ada kegagalan diam-diam.
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


def patch(s, nama_file):
    # idempoten: file yang sudah ter-patch ronde 5 dilewati
    if "\\section*{Data availability}" in s and "untuned reference baselines" in s:
        print(f"{nama_file}: sudah ter-patch ronde 5, dilewati")
        return s

    # P1. Preamble: fontenc/inputenc/lmodern (ligatur fi/ff hilang di PDF);
    # titik sisip berbeda: article memakai amsmath, elsarticle memakai hyperref
    if "\\usepackage{amsmath}\n" in s:
        s = ganti(s, "\\usepackage{amsmath}\n",
                  "\\usepackage{amsmath}\n\\usepackage[T1]{fontenc}\n\\usepackage[utf8]{inputenc}\n\\usepackage{lmodern}\n",
                  "P1 fontenc (amsmath)")
    else:
        s = ganti(s, "\\usepackage[hidelinks]{hyperref}\n",
                  "\\usepackage[hidelinks]{hyperref}\n\\usepackage[T1]{fontenc}\n\\usepackage[utf8]{inputenc}\n\\usepackage{lmodern}\n",
                  "P1 fontenc (hyperref)")

    # P2. Intro: literatur ML material anorganik menggantikan ref farmasi/protein
    s = ganti(s,
              "Data-driven approaches have been used to predict material properties, biomolecular stability, and product characteristics using materials databases and machine learning algorithms~\\cite{kang2023,kalejaye2024,hayashi2023}, and AI has transformed pharmaceutical formulation and manufacturing workflows in an analogous manner~\\cite{nizamuddin2025,han2025,vora2023,gholap2024}.",
              "In the inorganic-materials domain, descriptor-based toolkits such as Magpie and Matminer~\\cite{ward2016,ward2018}, graph neural networks such as CGCNN, MEGNet, M3GNet, and CHGNet~\\cite{xie2018,chen2019,chen2022,deng2023}, and the broader materials-informatics methodology~\\cite{ramprasad2017,schmidt2019} are established baselines; machine-learning studies that target calcium phosphate biomaterials specifically, however, remain scarce, which motivates the present framework.",
              "P2 intro literatur")

    # P3. Novelty vs soelistiono2026
    s = ganti(s,
              "That study demonstrated that multi-objective descriptor balancing yields more representative material rankings than single dominant parameters, but it did not yet constitute a systematic, replicable framework.",
              "That study demonstrated that multi-objective descriptor balancing yields more representative material rankings than single dominant parameters, but it did not yet constitute a systematic, replicable framework. The present work advances beyond it in five specific ways: (i) five databases are integrated with a recorded acquisition audit instead of a single source; (ii) predictive models are evaluated under a leakage-resistant protocol (reduced-formula grouping, nested cross-validation, composition-only discovery features) with explicitly quantified limitations; (iii) the multi-criteria ranking is restricted to criteria with pool-wide data coverage, guarded by a charge-neutrality filter, and equipped with Monte Carlo uncertainty propagation; (iv) the top candidates receive independent experimental benchmarking and machine-learned force-field pre-validation; and (v) the entire pipeline is versioned and fully replicable.",
              "P3 novelty")

    # P4. Methods ML: status baseline (hanya SVR yang di-tuning)
    s = ganti(s,
              "Regression targets were formation energy (eV/atom) and density (g/cm$^3$); models included random forest (RF), XGBoost, gradient boosting, and support vector regression (SVR).",
              "Regression targets were formation energy (eV/atom) and density (g/cm$^3$); models included random forest (RF), XGBoost, gradient boosting, and support vector regression (SVR). All four model families were evaluated under identical grouped cross-validation; only the SVR received hyperparameter tuning (nested CV), while the tree-based models served as untuned reference baselines.",
              "P4 baseline methods")

    # P5. Results 3.2: nilai R2 negatif baseline = bukti, bukan kegagalan model
    s = ganti(s,
              "The suitability label, being a semi-deterministic function of its own features, is not reported as a predictive result.",
              "Under the same protocol, the untuned default baselines (random forest, gradient boosting, XGBoost) attain grouped-CV $R^2$ between $-0.55$ and $-1.07$ for formation energy; we report these negative values as evidence for the low information content of the four-DOF composition features rather than as model failures. The suitability label, being a semi-deterministic function of its own features, is not reported as a predictive result.",
              "P5 baseline results")

    # P6. Discussion: sitasi GNN baseline
    s = ganti(s,
              "well behind graph-neural-network state of the art (CGCNN, MEGNet, M3GNet/CHGNet report MAE $\\approx$ 0.03--0.1 eV/atom on benchmark sets)",
              "well behind graph-neural-network state of the art (CGCNN, MEGNet, M3GNet/CHGNet report MAE $\\approx$ 0.03--0.1 eV/atom on benchmark sets~\\cite{xie2018,chen2019,chen2022,deng2023})",
              "P6 sitasi GNN")

    # P7. Gaya proyek -> akademik
    s = ganti(s, "(target $\\geq 500$ met)",
              "(950 unique compositions, exceeding the curation target of 500)", "P7 target met")
    s = ganti(s, "definitive DFT runs await cluster resources",
              "definitive DFT runs will be reported separately", "P7 await 1")
    s = ganti(s, "while definitive DFT validation awaits cluster resources (inputs prepared)",
              "while definitive DFT validation will be reported separately (inputs prepared)", "P7 await 2")
    s = ganti(s, "An earlier internal target ($R^2 \\geq 0.85$) was set without a leakage analysis and is withdrawn as arbitrary.",
              "A project-internal accuracy target ($R^2 \\geq 0.85$) that predated the leakage analysis is withdrawn as arbitrary.",
              "P7 0.85")
    s = ganti(s, "supporting the AMREC roadmap toward an AI-assisted biomaterial screening platform",
              "and points toward an AI-assisted biomaterial screening platform", "P7 AMREC")
    s = ganti(s, "(PRGF Discovery Research, 2027)", "(PRGF Discovery Research)", "P7 grant year")

    # P8. Data availability (sebelum Acknowledgments)
    s = ganti(s, "\\section*{Acknowledgments}",
              "\\section*{Data availability}\n"
              "The consolidated dataset (2{,}885 entries, 950 unique compositions), the versioned snapshot with SHA-256 checksums, and the complete pipeline source code are available in the accompanying research repository, which will be deposited on Zenodo upon acceptance (DOI to be inserted at the proof stage). The underlying data originate from the Materials Project (CC-BY 4.0), AFLOW, the Crystallography Open Database (CC0), PubChem (public domain), and OQMD, with access dates and licenses recorded per source.\n\n"
              "\\section*{Acknowledgments}",
              "P8 data availability")

    # P9. Bibitem: hapus 7 ref farmasi/protein
    ref_hapus = [
        "\\bibitem{kang2023} Kang S, Kim M, Sun J, et al. Prediction of protein aggregation propensity via data-driven approaches. \\textit{ACS Biomater Sci Eng}. 2023;9(11):6451--6463.\n",
        "\\bibitem{kalejaye2024} Kalejaye L, Wu IE, Terry T, et al. DeepSP: deep learning-based spatial properties to predict monoclonal antibody stability. \\textit{Comput Struct Biotechnol J}. 2024;23:2220--2229.\n",
        "\\bibitem{hayashi2023} Hayashi Y, Nakano Y, Marumo Y, et al. A data-driven approach to predicting tablet properties after accelerated test using raw material property database and machine learning. \\textit{Chem Pharm Bull (Tokyo)}. 2023;71(6):406--415.\n",
        "\\bibitem{nizamuddin2025} Nizamuddin SF, Ikramuddin M, Dhore NS. Artificial intelligence in pharmaceutical sciences: transforming drug discovery, formulation, and manufacturing. \\textit{Mediterr J Med Res}. 2025;2(4):269--275.\n",
        "\\bibitem{han2025} Han Y, Kim DH, Pack SP. Nanomaterials in drug delivery: leveraging artificial intelligence and big data for predictive design. \\textit{Int J Mol Sci}. 2025;26(22):11121.\n",
        "\\bibitem{vora2023} Vora LK, Gholap AD, Jetha K, et al. Artificial intelligence in pharmaceutical technology and drug delivery design. \\textit{Pharmaceutics}. 2023;15(7):1916.\n",
        "\\bibitem{gholap2024} Gholap AD, Uddin MJ, Faiyazuddin M, et al. Advances in artificial intelligence for drug delivery and development: a comprehensive review. \\textit{Comput Biol Med}. 2024;178:108702.\n",
    ]
    for r in ref_hapus:
        s = ganti(s, r, "", f"P9 hapus {r[9:r.index('}')]}")

    # P10. Bibitem baru: literatur ML material anorganik
    s = ganti(s,
              "\\bibitem{martelli2025} Martelli A, Bellucci D, Cannillo V. The role of artificial intelligence in biomaterials science: a review. \\textit{Polymers (Basel)}. 2025;17(19):2668.\n",
              "\\bibitem{martelli2025} Martelli A, Bellucci D, Cannillo V. The role of artificial intelligence in biomaterials science: a review. \\textit{Polymers (Basel)}. 2025;17(19):2668.\n"
              "\\bibitem{ward2016} Ward L, Agrawal A, Choudhary A, Wolverton C. A general-purpose machine learning framework for predicting properties of inorganic materials. \\textit{npj Comput Mater}. 2016;2:16028.\n"
              "\\bibitem{ward2018} Ward L, Dunn A, Faghaninia A, et al. Matminer: an open source toolkit for materials data mining. \\textit{Comput Mater Sci}. 2018;152:60--69.\n"
              "\\bibitem{xie2018} Xie T, Grossman JC. Crystal graph convolutional neural networks for an accurate and interpretable prediction of material properties. \\textit{Phys Rev Lett}. 2018;120:145301.\n"
              "\\bibitem{chen2019} Chen C, Ye W, Zuo Y, Zheng C, Ong SP. Graph networks as a universal machine learning framework for molecules and crystals. \\textit{Chem Mater}. 2019;31(9):3564--3572.\n"
              "\\bibitem{chen2022} Chen C, Ong SP. A universal graph deep learning interatomic potential for the periodic table. \\textit{Nat Comput Sci}. 2022;2(11):718--728.\n"
              "\\bibitem{deng2023} Deng B, Zhong P, Jun K, et al. CHGNet as a pretrained universal neural network potential for charge-informed atomistic modelling. \\textit{Nat Mach Intell}. 2023;5(9):1031--1041.\n"
              "\\bibitem{ramprasad2017} Ramprasad R, Batra R, Pilania G, Mannodi-Kanakkithodi A, Kim C. Machine learning in materials informatics: recent applications and prospects. \\textit{npj Comput Mater}. 2017;3:54.\n"
              "\\bibitem{schmidt2019} Schmidt J, Marques MRG, Botti S, Marques MAL. Recent advances and applications of machine learning in solid-state materials science. \\textit{npj Comput Mater}. 2019;5:83.\n",
              "P10 bibitem baru")

    (MS / nama_file).write_text(s, encoding="utf-8")
    return s


for nama in ["manuscript.tex", "manuscript_elsarticle.tex"]:
    t = patch(baca(nama), nama)
    sisa = [p for p in ["kang2023", "kalejaye2024", "hayashi2023", "nizamuddin2025", "han2025",
                        "vora2023", "gholap2024", "AMREC roadmap", "await cluster",
                        "target $\\geq 500$ met", "2027)", "Ruang desain", "berat_molekul"]
            if p in t]
    print(f"{nama}: sisa pola lama -> {sisa if sisa else 'TIDAK ADA (bersih)'}")
