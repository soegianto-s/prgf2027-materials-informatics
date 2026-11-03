"""Prapemrosesan (QC + pencilan) & ekstraksi deskriptor fisikokimia.

Output: data/processed/dataset_deskriptor.csv + data/reports/laporan_prapemrosesan.md
"""
import time
from pathlib import Path

import numpy as np
import pandas as pd

from common import PROC, REPORTS

# --- data unsur: EN Pauling, berat atom, elektron valensi ---
ELEM = {
    "H": (2.20, 1.008, 1), "Li": (0.98, 6.94, 1), "B": (2.04, 10.81, 3),
    "C": (2.55, 12.011, 4), "N": (3.04, 14.007, 5), "O": (3.44, 15.999, 6),
    "F": (3.98, 18.998, 7), "Na": (0.93, 22.990, 1), "Mg": (1.31, 24.305, 2),
    "Al": (1.61, 26.982, 3), "Si": (1.90, 28.086, 4), "P": (2.19, 30.974, 5),
    "S": (2.58, 32.06, 6), "Cl": (3.16, 35.45, 7), "K": (0.82, 39.098, 1),
    "Ca": (1.00, 40.078, 2), "Ti": (1.54, 47.867, 4), "V": (1.63, 50.942, 5),
    "Cr": (1.66, 51.996, 6), "Mn": (1.55, 54.938, 7), "Fe": (1.83, 55.845, 8),
    "Co": (1.88, 58.933, 9), "Ni": (1.91, 58.693, 10), "Cu": (1.90, 63.546, 11),
    "Zn": (1.65, 65.38, 12), "As": (2.18, 74.922, 5), "Br": (2.96, 79.904, 7),
    "Sr": (0.95, 87.62, 2), "Y": (1.22, 88.906, 3), "Zr": (1.33, 91.224, 4),
    "Mo": (2.16, 95.95, 6), "Ag": (1.93, 107.87, 11), "Cd": (1.69, 112.41, 12),
    "Sn": (1.96, 118.71, 4), "I": (2.66, 126.90, 7), "Ba": (0.89, 137.33, 2),
    "La": (1.10, 138.91, 3), "Ce": (1.12, 140.12, 4), "W": (2.36, 183.84, 6),
    "Pb": (2.33, 207.2, 4),
}


def komposisi_deskriptor(row):
    """Dari kolom Ca/P/O/H/F + jumlah atom lain -> EN avg/diff, VEC, berat molekul."""
    n = {}
    for el in ["Ca", "P", "O", "H", "F"]:
        v = row.get(el)
        if pd.notna(v) and v > 0:
            n[el] = float(v)
    total = sum(n.values())
    if total == 0:
        return pd.Series([np.nan] * 4, index=["EN_avg", "EN_diff", "VEC", "berat_molekul"])
    en_avg = sum(ELEM[el][0] * c for el, c in n.items()) / total
    ens = [ELEM[el][0] for el in n]
    en_diff = max(ens) - min(ens)
    vec = sum(ELEM[el][2] * c for el, c in n.items()) / total
    mw = sum(ELEM[el][1] * c for el, c in n.items())
    return pd.Series([en_avg, en_diff, vec, mw],
                     index=["EN_avg", "EN_diff", "VEC", "berat_molekul"])


def kelompok_material(row):
    """Klasifikasi keluarga senyawa berdasarkan komposisi."""
    ca, p, o, h, f = (row.get(k) or 0 for k in ["Ca", "P", "O", "H", "F"])
    if ca and p and h and abs(ca / p - 5 / 3) < 0.05 and abs(o - (13 * ca / 5)) / max(o, 1) < 0.1:
        return "apatit_hidroksi"
    if ca and p and f and abs(ca / p - 5 / 3) < 0.05:
        return "apatit_fluor"
    if ca and p and abs(ca / p - 3 / 2) < 0.05 and o:
        return "trikalsium_fosfat"
    if ca and p and abs(ca / p - 4 / 2) < 0.05 and o:
        return "tetrakalsium_fosfat"
    if ca and p and h and abs(ca / p - 1.0) < 0.05 and o:
        return "dikalsium_fosfat"
    if ca and p and abs(ca / p - 2 / 2) < 0.05 and o and not h:
        return "pirofosfat"
    if ca and p and abs(ca / p - 4 / 3) < 0.05 and o and h:
        return "oktakalsium_fosfat"
    if ca and p and abs(ca / p - 1 / 2) < 0.05 and o:
        return "monokalsium_fosfat"
    if ca and p and o:
        return "fosfat_lain"
    if ca and p:
        return "fosfida_CaP"
    return "lain"


def main():
    inv = pd.read_csv(PROC / "inventory_dataset.csv")
    log = []

    # ===== QC nilai tak fisik =====
    mask_dens = inv["densitas_gcm3"].notna() & ((inv["densitas_gcm3"] <= 0) | (inv["densitas_gcm3"] > 25))
    mask_vol = inv["volume_A3"].notna() & ((inv["volume_A3"] <= 0) | (inv["volume_A3"] > 20000))
    inv.loc[mask_dens, "densitas_gcm3"] = np.nan
    inv.loc[mask_vol, "volume_A3"] = np.nan
    log.append(f"- Densitas tak fisik dihapus (di-null-kan): {mask_dens.sum()} baris")
    log.append(f"- Volume sel tak fisik dihapus (di-null-kan): {mask_vol.sum()} baris")

    # ===== deskriptor komposisi =====
    desk = inv.apply(komposisi_deskriptor, axis=1)
    inv = pd.concat([inv, desk], axis=1)
    inv["kelompok"] = inv.apply(kelompok_material, axis=1)

    # ===== densitas teoritis dari volume sel (untuk COD dsb) =====
    # rho = M*Z / (NA * V_cell) ; COD punya Z (unit formula per sel)
    inv["densitas_teoritis_gcm3"] = np.nan
    m = inv["volume_A3"].notna() & inv["berat_molekul"].notna()
    z = inv["Z"].fillna(1)
    inv.loc[m, "densitas_teoritis_gcm3"] = (
        inv.loc[m, "berat_molekul"] * z.loc[m] / (inv.loc[m, "volume_A3"] * 0.602214085)
    )
    # isi densitas kosong dengan teoritis
    inv["densitas_final_gcm3"] = inv["densitas_gcm3"].fillna(inv["densitas_teoritis_gcm3"])

    # ===== deteksi pencilan (IQR + z-score) untuk deskriptor numerik inti =====
    numerik = ["densitas_final_gcm3", "Eform_eV_atom", "bandgap_eV",
               "bulk_K_GPa", "shear_G_GPa", "young_E_GPa", "volume_A3"]
    pencilan_log = []
    for col in numerik:
        s = inv[col].dropna()
        if len(s) < 10:
            continue
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        lo, hi = q1 - 3 * iqr, q3 + 3 * iqr
        z = (s - s.mean()) / s.std()
        out = s[(s < lo) | (s > hi) | (z.abs() > 4)]
        if len(out):
            # keputusan: dipertahankan (fisika valid) kecuali densitas/volume tak fisik (sudah di-null)
            pencilan_log.append(f"- {col}: {len(out)} pencilan (batas [{lo:.2f}, {hi:.2f}]) -> "
                                f"DIPERTAHANKAN, ditandai di kolom pencilan_{col}")
            inv[f"pencilan_{col}"] = inv[col].isin(out)

    inv.to_csv(PROC / "dataset_deskriptor.csv", index=False)

    laporan = f"""# Laporan Prapemrosesan & Ekstraksi Deskriptor
**Tanggal:** {time.strftime('%Y-%m-%d %H:%M:%S')}
**Tahapan:** Bagian 3–4 panduan utama

## Keputusan Prapemrosesan
{chr(10).join(log)}

## Pencilan (IQR*3 / z>4) — prinsip: jangan hapus otomatis
{chr(10).join(pencilan_log) if pencilan_log else '- Tidak ada pencilan di luar batas'}

## Missing Values — keputusan eksplisit
- Energi/bandgap/modulus hanya ada di sumber komputasional (MP, AFLOW, OQMD) -> subset pemodelan = MP+AFLOW(+OQMD), TERCATAT sebagai keputusan desain.
- Densitas COD diisi dari densitas teoritis (volume sel + berat molekul).
- Deskriptor dengan missing > 30% pada subset pemodelan akan disisihkan pada seleksi fitur.

## Statistik Deskriptor Utama
{inv[numerik].describe().T.round(3).to_markdown()}

## Distribusi Kelompok Material
{inv['kelompok'].value_counts().to_markdown()}
"""
    (REPORTS / "laporan_prapemrosesan.md").write_text(laporan, encoding="utf-8")
    print(laporan.encode("ascii", "replace").decode("ascii"))
    print("tersimpan:", PROC / "dataset_deskriptor.csv")


if __name__ == "__main__":
    main()
