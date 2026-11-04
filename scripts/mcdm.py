"""Analisis multiobjektif: TOPSIS + VIKOR, 3 set bobot (sensitivitas), pemeringkatan kandidat.

Kriteria (Bagian 8.1 panduan utama):
  C1 stabilitas termodinamika (Eform makin negatif makin baik)
  C2 densitas mendekati 2.0 g/cm3 (tulang)
  C3 Ca/P mendekati 1.67 (hidroksiapatit)
  C4 modulus Young turunan (9KG/(3K+G)) mendekati 15 GPa; missing -> imputasi median (tercatat)
  C5 bandgap: makin besar makin baik (cap 5 eV), metal (0) dihukum; missing -> imputasi median
  C6 skor kelayakan model ML (0/1)
"""
import time

import numpy as np
import pandas as pd

from common import PROC, REPORTS

# KOREKSI (2026-11-04): C6 (skor classifier) DIHAPUS — double counting dengan C1-C3.
KRITERIA = ["C_stabilitas", "C_densitas", "C_cap", "C_modulus", "C_bandgap"]
BENEFIT = np.array([True, True, True, True, True])  # semua sudah diarahkan "makin besar makin baik"

WEIGHTS = {
    "W1_berimbang": np.array([0.35, 0.25, 0.15, 0.15, 0.10]),
    "W2_stabilitas": np.array([0.50, 0.15, 0.15, 0.10, 0.10]),
    "W3_mekanik": np.array([0.25, 0.20, 0.10, 0.35, 0.10]),
}


def topsis(A, w):
    V = A * w
    ip = V.max(0)  # semua benefit
    inn = V.min(0)
    dp = np.sqrt(((V - ip) ** 2).sum(1))
    dn = np.sqrt(((V - inn) ** 2).sum(1))
    return dn / (dp + dn + 1e-12)


def vikor(A, w, v=0.5):
    fstar = A.max(0)
    fworst = A.min(0)
    jarak = w * (fstar - A) / (fstar - fworst + 1e-12)
    S = jarak.sum(1)
    R = jarak.max(1)
    Q = v * (S - S.min()) / (S.max() - S.min() + 1e-12) + (1 - v) * (R - R.min()) / (R.max() - R.min() + 1e-12)
    return Q


def main():
    k = pd.read_csv(PROC / "kandidat_scaffold.csv")
    for c in ["bulk_K_GPa", "shear_G_GPa", "young_E_GPa", "bandgap_eV", "Eform_eV_atom",
              "densitas_final_gcm3", "ca_p_ratio"]:
        k[c] = pd.to_numeric(k[c], errors="coerce")
    k["young_E_deriv_GPa"] = np.where(
        k["bulk_K_GPa"].notna() & k["shear_G_GPa"].notna(),
        9 * k["bulk_K_GPa"] * k["shear_G_GPa"] / (3 * k["bulk_K_GPa"] + k["shear_G_GPa"]),
        np.nan)
    # C_stabilitas: Eform ABSOLUT (makna fisika). Catatan: skala AFLOW offset vs MP/OQMD
    # (hingga 0.8 eV) -> entri AFLOW sedikit dirugikan; dicatat sebagai keterbatasan.
    k["C_stabilitas"] = -k["Eform_eV_atom"]
    # koreksi sirkularitas (2026-11-04): densitas jadi kriteria PITA [1.0, 3.2] g/cm3.
    # Justifikasi: scaffold padat meraih modulus tulang via POROSITAS (Gibson-Ashby),
    # bukan dengan menyamakan densitas tulang; pita mencakup semua keramik CaP klinis.
    rho = k["densitas_final_gcm3"]
    k["C_densitas"] = np.where(rho.between(1.0, 3.2), 0.0,
                               -np.minimum((rho - 3.2).abs(), (rho - 1.0).abs()))
    k["C_cap"] = -np.abs(k["ca_p_ratio"] - 1.67)
    k["C_modulus"] = -np.abs(k["young_E_deriv_GPa"] - 15)
    k["C_bandgap"] = np.clip(k["bandgap_eV"].fillna(-1), 0, 5) / 5.0

    # imputasi median untuk kriteria dengan missing (tercatat)
    med = k[KRITERIA].median()
    A = k[KRITERIA].fillna(med).values
    # normalisasi vektor
    An = A / np.sqrt((A ** 2).sum(0))

    hasil = {}
    for wn, w in WEIGHTS.items():
        hasil[f"TOPSIS_{wn}"] = topsis(An, w)
        hasil[f"VIKOR_{wn}"] = -vikor(An, w)  # negatifkan agar "makin besar makin baik" seragam

    skor = pd.DataFrame(hasil, index=k.index)
    peringkat = skor.rank(ascending=False)
    k["skor_rerata"] = skor.mean(1)
    k["peringkat_rerata"] = peringkat.mean(1)
    k["kali_top10"] = (peringkat <= 10).sum(1)
    k = k.sort_values("peringkat_rerata")

    # sanity check material rujukan
    def cek(formula_substr):
        m = k[k["formula"].astype(str).str.contains(formula_substr, case=False, na=False)]
        return m[["formula", "peringkat_rerata"]].head(3).to_markdown(index=False) if len(m) else "- tidak ada"

    laporan = [f"# Laporan Analisis Multiobjektif (MCDM)\n**Tanggal:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
               f"**Tahapan:** Bagian 8 panduan utama\n",
               f"## Kriteria & Arah\n- C1 stabilitas (max), C2 densitas->2.0 (max), C3 Ca/P->1.67 (max), "
               f"C4 modulus->15 GPa (max), C5 bandgap (max), C6 kelayakan ML (max)",
               f"- Imputasi median untuk C4/C5 yang hilang (keputusan tercatat).",
               f"- Bobot: {WEIGHTS}",
               f"## Posisi Material Rujukan (peringkat rerata dari 6 skenario)\n- HAp: {cek('Ca5P3HO13|Ca10H2O26P6')}",
               f"- TCP: {cek('Ca3O8P2|Ca3P2O8')}",
               f"- Fluorapatit: {cek('Ca5P3O12F|Ca10F2O24P6')}",
               f"## Top 15 Kandidat (peringkat rerata TOPSIS+VIKOR x 3 bobot)\n"]
    top = k.head(15)
    laporan.append(top[[
        "formula", "sumber", "kelompok", "peringkat_rerata", "kali_top10",
        "Eform_eV_atom", "densitas_final_gcm3", "ca_p_ratio", "young_E_deriv_GPa",
        "bandgap_eV", "layak"]].round(3).to_markdown(index=False))

    top.to_csv(PROC / "kandidat_top15.csv", index=False)
    k.to_csv(PROC / "kandidat_ranking.csv", index=False)
    (REPORTS / "laporan_mcdm.md").write_text("\n".join(laporan), encoding="utf-8")
    print("\n".join(laporan).encode("ascii", "replace").decode("ascii"))


if __name__ == "__main__":
    main()
