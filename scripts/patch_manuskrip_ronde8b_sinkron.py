"""Patch manuskrip ronde 8b: sinkronisasi menyeluruh pasca-ronde-8 (DFT definitif).

Menyelaraskan sisa bagian yang belum mencerminkan data DFT baru: keywords,
kontribusi (v) intro, wording metode, pita modulus DFT di paragraf hasil,
kelengkapan dataset (n=9 elastik), dan data availability. Judul sengaja tidak
diubah (tetap akurat: "Systematic Screening and Design").

Syarat: patch_manuskrip_ronde8_dft.py SUDAH dijalankan (marker tab:dft_elastik wajib ada).
Idempoten (guard: keyword "density functional theory"); assertion count==1; kedua .tex.
"""
import json
from pathlib import Path

MS = Path(r"D:\latex\prgf2026\data\reports\manuscript")


def muat(nama):
    return json.loads((Path(r"D:\latex\prgf2026\data") / nama).read_text(encoding="utf-8"))


def ganti(s, lama, baru, label, n=1):
    k = s.count(lama)
    assert k == n, f"[{label}] ketemu {k}x (harus {n}): {lama[:70]}..."
    return s.replace(lama, baru)


def patch(s, nama_file):
    if "density functional theory" in s:
        print(f"{nama_file}: sudah ter-sinkron ronde 8b, dilewati")
        return s
    assert "tab:dft_elastik" in s, f"{nama_file}: jalankan patch_manuskrip_ronde8_dft.py dulu"

    dft = muat("validasi_dft/hasil_dft.json")
    tags = ["top1_Ca5P3O12F", "top2_Ca10P6O25", "top5_Ca10P6CO27", "top6_Ca5P3HO13", "top26_Ca3(PO4)2"]
    e = [dft[t]["E_GPa"] for t in tags]; k = [dft[t]["K_GPa"] for t in tags]
    assert round(min(e), 1) == 216.6 and round(max(e), 1) == 235.8, "pita E DFT berubah"
    assert round(min(k), 1) == 134.7 and round(max(k), 1) == 143.7, "pita K DFT berubah"

    # S1. Keywords (+ DFT + elastik) — sintaks berbeda per format
    if "elsarticle" in nama_file:
        s = ganti(s, "multi-criteria decision making \\sep SHAP",
                  "multi-criteria decision making \\sep SHAP \\sep density functional theory \\sep elastic constants",
                  "S1 keywords elsarticle")
    else:
        s = ganti(s, "multi-criteria decision making; SHAP",
                  "multi-criteria decision making; SHAP; density functional theory; elastic constants",
                  "S1 keywords imrad")

    # S2. Intro: kontribusi (v) ikut menyebut validasi DFT
    s = ganti(s,
              "(v) independent validation of the models against experimental thermochemistry and crystallographic densities.",
              "(v) independent validation of the models against experimental thermochemistry and crystallographic densities, and definitive DFT elastic validation of the top candidates.",
              "S2 kontribusi (v)")

    # S3. Methods: wording "subsequent" -> definitif (validasi sudah dikerjakan)
    s = ganti(s,
              "were prepared for subsequent DFT validation.",
              "were prepared for the definitive DFT elastic validation.",
              "S3 wording metode")
    s = ganti(s,
              "Definitive DFT elastic validation was completed for all five top candidates",
              "The validation was completed for all five top candidates",
              "S3 kalimat kedua metode")

    # S4. Results: pita modulus DFT disebut eksplisit (bukan hanya di tabel)
    s = ganti(s,
              "$\\nu \\approx 0.23$--0.24), consistent with dense apatitic ceramics",
              f"$\\nu \\approx 0.23$--0.24; PBE-DFT: $E = {min(e):.1f}$--${max(e):.1f}$ GPa, $K = {min(k):.1f}$--${max(k):.1f}$ GPa, Table~\\ref{{tab:dft_elastik}}), consistent with dense apatitic ceramics",
              "S4 pita DFT hasil")
    s = ganti(s,
              "the definitive PBE-DFT comparison, Table~\\ref{tab:dft_elastik}, shows MACE-MP-0 underpredicting every modulus consistently",
              "MACE-MP-0 underpredicts every modulus consistently",
              "S4 tanpa referensi tabel dobel")

    # S5. Results dataset: kelengkapan n=9 disilang ke validasi DFT
    s = ganti(s,
              "elastic moduli for 0.3\\% ($n=9$).",
              "elastic moduli for 0.3\\% ($n=9$; DFT-computed for the five top candidates, Table~\\ref{tab:dft_elastik}).",
              "S5 dataset n=9")

    # S6. Data availability: sebut data DFT elastik
    s = ganti(s,
              "the versioned snapshot with SHA-256 checksums, and the complete pipeline source code are available",
              "the versioned snapshot with SHA-256 checksums, the DFT elastic-validation inputs and outputs (Quantum ESPRESSO input decks, stress tensors, and elastic constants of the five top candidates), and the complete pipeline source code are available",
              "S6 data availability")

    (MS / nama_file).write_text(s, encoding="utf-8")
    return s


def main():
    for nama in ["manuscript.tex", "manuscript_elsarticle.tex"]:
        t = patch((MS / nama).read_text(encoding="utf-8"), nama)
        sisa = [p for p in ["were prepared for subsequent DFT validation",
                            "Definitive DFT elastic validation was completed",
                            "independent validation of the models against experimental thermochemistry and crystallographic densities."]
                if p in t]
        print(f"{nama}: sisa pola lama -> {sisa if sisa else 'bersih'}")
        print(f"  marker baru: keywords DFT={'density functional theory' in t}, "
              f"pita hasil={'PBE-DFT: $E = 216.6$--$235.8$' in t}, "
              f"data avail={'elastic-validation inputs' in t}")


if __name__ == "__main__":
    main()
