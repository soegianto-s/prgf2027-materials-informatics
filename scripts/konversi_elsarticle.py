"""Konversi manuscript.tex (article) -> manuscript_elsarticle.tex (elsarticle, jurnal Elsevier).

Idempotent: setiap kali manuscript.tex diperbarui, jalankan skrip ini lalu kompilasi ulang.
"""
from pathlib import Path

SRC = Path(r"D:\latex\prgf2026\data\reports\manuscript\manuscript.tex")
DST = Path(r"D:\latex\prgf2026\data\reports\manuscript\manuscript_elsarticle.tex")

HEADER = r"""\documentclass[review,11pt,a4paper]{elsarticle}
\usepackage[margin=2.4cm]{geometry}
\usepackage{booktabs}
\usepackage{caption}
\usepackage[hidelinks]{hyperref}

\captionsetup{font=small,labelfont=bf,skip=4pt}
\graphicspath{{../figures/}}
\setlength{\parskip}{3pt}

\journal{Computational Materials Science}

\begin{document}

\begin{frontmatter}

\title{An Artificial-Intelligence-Based Materials Informatics Framework for the Accelerated Discovery of Calcium Phosphate Biomaterials as Candidate Scaffolds for Bone Tissue Engineering}

\author[unair]{Soegianto Soelistiono\corref{cor1}}
\ead{soegianto@fst.unair.ac.id}
\author[unair]{Herri Trilaksana}
\author[unair]{Yhosep Gita Yhun Yhuwana}
\author[aru]{Bernardi Pranggono}

\affiliation[unair]{organization={Department of Physics, Faculty of Science and Technology, Universitas Airlangga}, city={Surabaya}, postcode={60115}, country={Indonesia}}
\affiliation[aru]{organization={School of Computing and Information Science, Anglia Ruskin University}, city={Cambridge}, country={United Kingdom}}
\cortext[cor1]{Corresponding author}

"""

KEYWORD = r"""\begin{keyword}
materials informatics \sep machine learning \sep calcium phosphate \sep bone tissue engineering \sep scaffold \sep multi-criteria decision making \sep SHAP
\end{keyword}
\end{frontmatter}
"""


def main():
    lines = SRC.read_text(encoding="utf-8").splitlines(keepends=True)
    i_doc = next(i for i, l in enumerate(lines) if l.startswith(r"\documentclass"))
    i_mt = next(i for i, l in enumerate(lines) if r"\maketitle" in l)
    badan = lines[i_mt + 1:]
    baru = []
    lewati_end_abstract = False
    for l in badan:
        if "\\textbf{Keywords:}" in l:
            # baris keywords menggantikan \end{abstract} (keywords ada DI DALAM abstract)
            baru.append("\\end{abstract}\n\n" + KEYWORD)
            lewati_end_abstract = True
        elif lewati_end_abstract and l.strip() == "\\end{abstract}":
            lewati_end_abstract = False  # sudah ditutup di atas
        else:
            baru.append(l)
    DST.write_text(HEADER + "".join(baru), encoding="utf-8", newline="")
    print("elsarticle ditulis:", DST)


if __name__ == "__main__":
    main()
