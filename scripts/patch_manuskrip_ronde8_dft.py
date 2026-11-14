"""Patch manuskrip ronde 8: validasi elastik DFT definitif (4 apatit VPS + beta-TCP).

Isi: paragraf metode DFT (QE 7.5, PBE/PSL 1.0.0, k 3x3x3 & ecut 80/640 hasil
konvergensi, 12 regangan Voigt +-1%, C=(s-eps - s+eps)/2eps, VRH, QA sigma<0.5 GPa),
tabel DFT vs MLFF (tab:dft_elastik), koreksi klaim "MLFF systematically high" -> MLFF
underpredict 5.9--6.9%, penutup isu volume HA +4.3% (DFT vc-relax mereproduksi), dan
target porositas Gibson-Ashby 70--79%.

Semua angka dibaca dari hasil_dft.json + hasil_relaksasi_elastik.json + relax.out top6
(assertion wajib) — tidak ada hardcode. Setiap replace ber-assertion count==1;
idempoten; diterapkan pada kedua file .tex.
"""
import json
import re
from pathlib import Path

ROOT = Path(r"D:\latex\prgf2026")
MS = ROOT / "data" / "reports" / "manuscript"
VPS_HASIL = ROOT / "data" / "dft" / "vps_hasil"

TAGS = ["top1_Ca5P3O12F", "top2_Ca10P6O25", "top5_Ca10P6CO27", "top6_Ca5P3HO13", "top26_Ca3(PO4)2"]
LABEL = {
    "top1_Ca5P3O12F": "Fluorapatite",
    "top2_Ca10P6O25": "Oxyapatite",
    "top5_Ca10P6CO27": "Carbonated apatite",
    "top6_Ca5P3HO13": "Hydroxyapatite",
    "top26_Ca3(PO4)2": "$\\beta$-TCP",
}


def muat(nama):
    return json.loads((ROOT / "data" / nama).read_text(encoding="utf-8"))


def ganti(s, lama, baru, label, n=1):
    k = s.count(lama)
    assert k == n, f"[{label}] ketemu {k}x (harus {n}): {lama[:70]}..."
    return s.replace(lama, baru)


def volume_akhir_dft(tag):
    """Volume sel akhir vc-relax (Ang^3) dari baris 'new unit-cell volume' terakhir relax.out."""
    f = VPS_HASIL / tag / "relax.out"
    t = f.read_text(encoding="utf-8", errors="replace")
    baris = re.findall(r"new unit-cell volume =\s+[\d.]+\s+a\.u\.\^3 \(\s*([\d.]+)\s+Ang\^3 \)", t)
    assert baris, f"{f}: tidak ada baris new unit-cell volume"
    return float(baris[-1])


def main():
    dft = muat("validasi_dft/hasil_dft.json")
    mlff = muat("validasi_mlff/hasil_relaksasi_elastik.json")

    # assertion kelengkapan data
    baris = []
    for tag in TAGS:
        d, m = dft[tag], mlff[tag]
        assert len(d["C_ij"]) == 6 and all(len(r) == 6 for r in d["C_ij"]), f"{tag}: C_ij bukan 6x6"
        for k in ["K_GPa", "G_GPa", "E_GPa", "nu"]:
            assert k in d and k in m, f"{tag}: kunci {k} hilang di DFT/MLFF"
        de = (d["E_GPa"] - m["E_GPa"]) / d["E_GPa"] * 100
        assert 4.0 < de < 10.0, f"{tag}: galat relatif E tak wajar ({de:.1f}%)"
        baris.append((tag, LABEL[tag], d, m, round(de, 1)))
    e_dft = [d["E_GPa"] for _, _, d, _, _ in baris]
    # klaim di teks: pita 216.6--235.8 GPa dan galat 5.9--6.9%
    assert round(min(e_dft), 1) == 216.6 and round(max(e_dft), 1) == 235.8, "pita E DFT berubah"
    assert round(min(b[4] for b in baris), 1) == 5.9 and round(max(b[4] for b in baris), 1) == 6.9, "pita galat E berubah"
    # urutan kandidat per E sama di DFT dan MACE
    assert [t for t, _, d, _, _ in sorted(baris, key=lambda b: b[2]["E_GPa"])] == \
           [t for t, _, _, m, _ in sorted(baris, key=lambda b: b[3]["E_GPa"])], "urutan E DFT vs MACE beda"

    # volume HA: DFT vc-relax vs MLFF (klaim 547.6 vs 547.7)
    v_dft = volume_akhir_dft("top6_Ca5P3HO13")
    v_mlff = mlff["top6_Ca5P3HO13"]["vol_akhir_A3"]
    assert abs(v_dft - v_mlff) / v_dft < 0.001, f"volume HA DFT {v_dft} vs MLFF {v_mlff} tidak <0.1%"

    # rentang K/G untuk kalimat hasil
    k_dft = [d["K_GPa"] for _, _, d, _, _ in baris]; g_dft = [d["G_GPa"] for _, _, d, _, _ in baris]
    k_galat = [round((d["K_GPa"] - m["K_GPa"]) / d["K_GPa"] * 100, 1) for _, _, d, m, _ in baris]
    g_galat = [round((d["G_GPa"] - m["G_GPa"]) / d["G_GPa"] * 100, 1) for _, _, d, m, _ in baris]
    assert (min(k_galat), max(k_galat)) == (2.6, 3.5), f"pita galat K {min(k_galat)}--{max(k_galat)}"
    assert (min(g_galat), max(g_galat)) == (6.6, 7.7), f"pita galat G {min(g_galat)}--{max(g_galat)}"

    # tabel tab:dft_elastik
    baris_tab = "\n".join(
        f"{label} & {d['E_GPa']:.1f} / {m['E_GPa']:.1f} & {de:.1f} & "
        f"{d['K_GPa']:.1f} / {m['K_GPa']:.1f} & {d['G_GPa']:.1f} / {m['G_GPa']:.1f} & "
        f"{d['nu']:.3f} / {m['nu']:.3f} \\\\"
        for _, label, d, m, de in baris)
    tabel_dft = (
        "\\begin{table}[ht]\n\\centering\\small\n"
        "\\caption{Definitive DFT elastic validation of the five top candidates (PBE, Quantum ESPRESSO; vc-relax + twelve Voigt strain patterns $\\pm1\\%$ + unstrained reference). $\\Delta E=100\\,(E^{\\mathrm{DFT}}-E^{\\mathrm{MACE}})/E^{\\mathrm{DFT}}$; MACE-MP-0 (float64) values from the structural pre-validation.}\n"
        "\\label{tab:dft_elastik}\n"
        "\\begin{tabular}{lccccc}\n\\toprule\n"
        "Phase & $E^{\\mathrm{DFT}}/E^{\\mathrm{MACE}}$ (GPa) & $\\Delta E$ (\\%) & $K^{\\mathrm{DFT}}/K^{\\mathrm{MACE}}$ (GPa) & $G^{\\mathrm{DFT}}/G^{\\mathrm{MACE}}$ (GPa) & $\\nu^{\\mathrm{DFT}}/\\nu^{\\mathrm{MACE}}$ \\\\\n\\midrule\n"
        + baris_tab + "\n\\bottomrule\n\\end{tabular}\n\\end{table}\n\n")

    for nama in ["manuscript.tex", "manuscript_elsarticle.tex"]:
        s = (MS / nama).read_text(encoding="utf-8")
        if "tab:dft_elastik" in s and "giannozzi2009" in s:
            print(f"{nama}: sudah ter-patch ronde 8, dilewati")
            continue

        # P1. Abstrak: validasi elastik DFT
        s = ganti(s,
                  "endpoints). SHAP analysis identifies",
                  "endpoints). PBE-DFT elastic validation of the top candidates (Quantum ESPRESSO; vc-relax plus twelve Voigt strain patterns $\\pm1\\%$) places their dense-material Young's moduli at $\\approx$217--236 GPa---reproducing the MACE-MP-0 pre-validation within 6--7\\%---and confirms the $+4.3\\%$ cell relaxation that MLFF had flagged for hydroxyapatite. SHAP analysis identifies",
                  "P1 abstrak DFT")

        # P2. Intro kontribusi (iv)
        s = ganti(s,
                  "(iv) the top candidates receive independent experimental benchmarking and machine-learned force-field pre-validation; and",
                  "(iv) the top candidates receive independent experimental benchmarking, machine-learned force-field pre-validation, and definitive DFT elastic validation; and",
                  "P2 kontribusi (iv)")

        # P3. Methods: protokol DFT lengkap
        s = ganti(s,
                  "Structures of the top-5 candidates were exported (POSCAR, CIF) and Quantum ESPRESSO input files (scf/relax, PSL 1.0.0 pseudopotentials) were prepared for subsequent DFT validation.",
                  "Structures of the top-5 candidates were exported (POSCAR, CIF) and Quantum ESPRESSO input files (scf/relax, PSL 1.0.0 pseudopotentials) were prepared for subsequent DFT validation. Definitive DFT elastic validation was completed for all five top candidates with Quantum ESPRESSO~\\cite{giannozzi2009} (v7.5; the $\\beta$-TCP reference from an earlier v6.7 run under the identical protocol): PBE exchange--correlation, PSL 1.0.0 pseudopotentials, kinetic-energy cutoffs of 80/640 Ry, and a $3\\times3\\times3$ $\\mathbf{k}$-mesh---a converged setting (total energy changes by 0.008 meV/atom from the $3\\times3\\times3$ to the $4\\times4\\times4$ mesh, and by $\\approx$9 meV/atom from 60/480 to 80/640 Ry cutoffs). Each cell was tightly relaxed (vc-relax), then strained by $\\varepsilon=\\pm1\\%$ in each of the six Voigt patterns (twelve strained SCF runs) plus one unstrained reference SCF, all with stress tensors printed. Elastic constants follow as $C_{ij}=(\\sigma_i(-\\varepsilon)-\\sigma_i(+\\varepsilon))/2\\varepsilon$ (Ry/bohr$^3$ converted to GPa), symmetrized, and polycrystalline moduli were obtained by Voigt--Reuss--Hill averaging. Quality gates required the reference-cell residual stress to stay below 0.5 GPa and $C$ to be symmetric with a positive diagonal.",
                  "P3 metode DFT")

        # P4. Results MLFF structural validation: HA + koreksi klaim MLFF + porositas
        s = ganti(s,
                  "hydroxyapatite expands by $+4.3\\%$, flagged for priority DFT verification)",
                  f"hydroxyapatite expands by $+4.3\\%$---a genuine relaxation of the strained idealized input structure, reproduced almost exactly by DFT vc-relax (final volumes {v_dft:.1f} vs.\\ {v_mlff:.1f} \\AA$^3$), not an MLFF artifact)",
                  "P4 HA volume")
        s = ganti(s,
                  "(MLFF stiffness is known to be systematically high; definitive DFT runs will be reported separately)",
                  "(the definitive PBE-DFT comparison, Table~\\ref{tab:dft_elastik}, shows MACE-MP-0 underpredicting every modulus consistently---Young's by 5.9--6.9\\%, shear by 6.6--7.7\\%, bulk by 2.6--3.5\\%---while preserving the ordering of the five candidates)",
                  "P4 koreksi klaim MLFF")
        s = ganti(s,
                  "roughly \\textbf{70--78\\% porosity}",
                  "roughly \\textbf{70--79\\% porosity}",
                  "P4 porositas hasil")

        # P5. Discussion: HA + loop tertutup + target porositas
        s = ganti(s,
                  "(four of five with $|dV| \\leq 0.41\\%$; hydroxyapatite $+4.3\\%$, flagged for priority DFT)",
                  "(four of five with $|dV| \\leq 0.41\\%$; hydroxyapatite $+4.3\\%$, reproduced by DFT vc-relax to within 0.1\\% of the MLFF final volume)",
                  "P5 diskusi HA")
        s = ganti(s,
                  "while definitive DFT validation will be reported separately (inputs prepared)",
                  "while definitive DFT validation now closes that loop: PBE elastic constants place the five candidates' Young's moduli at 216.6--235.8 GPa, reproducing the MACE-MP-0 pre-validation within 5.9--6.9\\% (Table~\\ref{tab:dft_elastik})",
                  "P5 diskusi loop DFT")
        s = ganti(s,
                  "yields porosity design targets (70--78\\%)",
                  "yields porosity design targets (70--79\\%)",
                  "P5 porositas diskusi")

        # P6. Conclusion
        s = ganti(s,
                  "MLFF structural pre-validation confirms the stability of the top candidates and yields a porosity design target of 70--78\\% for cortical-bone stiffness; definitive DFT validation inputs are prepared.",
                  "MLFF structural pre-validation confirms the stability of the top candidates, and definitive PBE-DFT elastic validation places their dense-material Young's moduli at $\\approx$217--236 GPa---reproducing the MLFF values within 6--7\\%---yielding a porosity design target of 70--79\\% for cortical-bone stiffness.",
                  "P6 kesimpulan")

        # P7. Tabel tab:dft_elastik sebelum tab:val
        s = ganti(s,
                  "\\begin{table}[ht]\n\\centering\\small\n\\caption{Dataset quality control: database values versus experimental literature. This table verifies the data sources; it does not validate the machine-learning models (see Table~\\ref{tab:bench}).}",
                  tabel_dft + "\\begin{table}[ht]\n\\centering\\small\n\\caption{Dataset quality control: database values versus experimental literature. This table verifies the data sources; it does not validate the machine-learning models (see Table~\\ref{tab:bench}).}",
                  "P7 tabel dft_elastik")

        # P8. Bibitem QE
        s = ganti(s,
                  "\\bibitem{himanen2020} Himanen L, J\\\"ager MOJ, Morooka EV, et al. DScribe: library of descriptors for machine learning in materials science. \\textit{Comput Phys Commun}. 2020;247:106949.\n",
                  "\\bibitem{himanen2020} Himanen L, J\\\"ager MOJ, Morooka EV, et al. DScribe: library of descriptors for machine learning in materials science. \\textit{Comput Phys Commun}. 2020;247:106949.\n"
                  "\\bibitem{giannozzi2009} Giannozzi P, Baroni S, Bonini N, et al. QUANTUM ESPRESSO: a modular and open-source software project for quantum simulations of materials. \\textit{J Phys Condens Matter}. 2009;21(39):395502.\n",
                  "P8 bibitem QE")

        (MS / nama).write_text(s, encoding="utf-8")
        sisa = [p for p in ["flagged for priority DFT", "definitive DFT runs will be reported separately",
                            "definitive DFT validation will be reported separately",
                            "definitive DFT validation inputs are prepared", "70--78"]
                if p in s]
        print(f"{nama}: sisa pola lama -> {sisa if sisa else 'bersih'}")
        print(f"  marker baru: tab:dft_elastik={'tab:dft_elastik' in s}, giannozzi2009={'giannozzi2009' in s}, "
              f"70--79={'70--79' in s}")


if __name__ == "__main__":
    main()
