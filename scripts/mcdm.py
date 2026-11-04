"""Analisis multiobjektif: TOPSIS + VIKOR, 3 set bobot (sensitivitas), pemeringkatan kandidat.

Kriteria (revisi ronde 4 — panduan utama Bagian 8.1):
  C1 stabilitas termodinamika (Eform makin negatif makin baik)
  C2 densitas dalam pita klinis [1.0, 3.2] g/cm3 (nol penalti di dalam pita)
  C3 Ca/P mendekati 1.67 (mineral tulang)

Keputusan revisi (reviewer ronde 4, tercatat):
  - C4 modulus Young DITARIK: hanya n=9 punya K&G -> imputasi median untuk 98% entri
    menjadikan kriteria praktis konstanta/noise. Modulus adalah sifat LEVEL SCAFFOLD
    (arsitektur + porositas, Gibson-Ashby) dan ditangani di tahap desain hilir
    (Bagian validasi komputasional), bukan kriteria material.
  - C5 bandgap DITARIK: tidak ada fungsi elektronik pada scaffold tulang; entri
    metalik sudah terseleksi oleh kriteria komposisi dan kerapatan.
  - C6 skor kelayakan ML (classifier) DIHAPUS sejak 2026-11-04 — double counting C1-C3.
  - FILTER KENETRALAN MUATAN (baru): pemeriksaan stoikiometri — formula dengan muatan
    formal != 0 (oksidasi standar Ca+2, P+5, O-2, H+1, F-1, C+4) dikeluarkan dari
    kolam kandidat (contoh: Ca5P3O13, Ca5(PO4)3).
  - Propagasi ketidakpastian ML ke peringkat: lihat mcdm_montecarlo.py
    (bobot Dirichlet + noise Gaussian sebesar MAE CV model).
"""
import time

import numpy as np
import pandas as pd

from common import PROC, REPORTS
from consolidate import parse_formula

KRITERIA = ["C_stabilitas", "C_densitas", "C_cap"]
BENEFIT = np.array([True, True, True])  # semua sudah diarahkan "makin besar makin baik"

WEIGHTS = {
    "W1_berimbang": np.array([0.40, 0.30, 0.30]),
    "W2_stabilitas": np.array([0.60, 0.20, 0.20]),
    "W3_komposisi": np.array([0.30, 0.30, 0.40]),
}

# Oksidasi standar untuk pemeriksaan kenetralan muatan (sistem Ca-P-O-H-F-C)
OXID = {"Ca": 2.0, "P": 5.0, "O": -2.0, "H": 1.0, "F": -1.0, "C": 4.0}


def muatan_formula(f):
    """Muatan formal bersih formula (None bila ada unsur di luar sistem).

    Bilangan oksidasi P bergantung konteks: +5 bila ada O (fosfat), -3 tanpa O (fosfida).
    """
    cnt = parse_formula(f)
    if set(cnt) - set(OXID):
        return None
    p_ox = 5.0 if "O" in cnt else -3.0
    return sum(n * (p_ox if e == "P" else OXID[e]) for e, n in cnt.items())


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
    for c in ["Eform_eV_atom", "densitas_final_gcm3", "ca_p_ratio"]:
        k[c] = pd.to_numeric(k[c], errors="coerce")

    # Filter kenetralan muatan (pemeriksaan stoikiometri, reviewer ronde 4)
    # + syarat mengandung O: kolam kandidat = kalsium FOSFAT (fosfida seperti Ca3P2
    # netral secara muatan tetapi di luar kelas material scaffold & reaktif thd air).
    q = k["formula"].map(muatan_formula)
    tak_dikenal = q.isna()
    tak_netral = q.notna() & (q.abs() > 1e-6)
    tanpa_o = ~k["ada_O"].fillna(False).astype(bool)
    n_unsur = int(tak_dikenal.sum())
    n_muatan = int(tak_netral.sum())
    n_fosfida = int(tanpa_o.sum())
    contoh_muatan = k.loc[tak_netral, "formula"].head(8).tolist()
    k = k[~(tak_dikenal | tak_netral | tanpa_o)].copy()

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

    A = k[KRITERIA].values
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
               f"**Tahapan:** Bagian 8 panduan utama (revisi ronde 4)\n",
               f"## Kriteria & Arah\n- C1 stabilitas (max), C2 densitas pita [1.0, 3.2] g/cm3 (max), "
               f"C3 Ca/P->1.67 (max)",
               f"- C4 modulus & C5 bandgap DITARIK (reviewer ronde 4): C4 imputasi median utk 98% entri "
               f"(n=9) = praktis konstanta + salah level (sifat scaffold, bukan material); C5 tanpa "
               f"fungsi elektronik pada scaffold tulang. C6 (kelayakan ML) sudah ditarik sebelumnya.",
               f"- Filter kenetralan muatan (stoikiometri): {n_muatan} entri muatan != 0 dibuang "
               f"(contoh: {', '.join(contoh_muatan) if contoh_muatan else '-'}); {n_unsur} entri "
               f"berunsur di luar sistem dan {n_fosfida} fosfida (tanpa O, di luar kelas material "
               f"kalsium fosfat) dibuang. Kolam akhir: {len(k)} entri.",
               f"- Bobot: {WEIGHTS}",
               f"## Posisi Material Rujukan (peringkat rerata dari 6 skenario)\n- HAp: {cek('Ca5P3HO13|Ca10H2O26P6')}",
               f"- TCP: {cek('Ca3O8P2|Ca3P2O8')}",
               f"- Fluorapatit: {cek('Ca5P3O12F|Ca10F2O24P6')}",
               f"## Top 15 Kandidat (peringkat rerata TOPSIS+VIKOR x 3 bobot)\n"]
    top = k.head(15)
    laporan.append(top[[
        "formula", "sumber", "kelompok", "peringkat_rerata", "kali_top10",
        "Eform_eV_atom", "densitas_final_gcm3", "ca_p_ratio", "layak"]].round(3).to_markdown(index=False))

    top.to_csv(PROC / "kandidat_top15.csv", index=False)
    k.to_csv(PROC / "kandidat_ranking.csv", index=False)
    (REPORTS / "laporan_mcdm.md").write_text("\n".join(laporan), encoding="utf-8")
    print("\n".join(laporan).encode("ascii", "replace").decode("ascii"))


if __name__ == "__main__":
    main()
