"""Konversi pKsp literatur -> kelarutan setimbang stoikiometrik S (mol/L) (ronde 7/Q1).

pKsp mentah tidak sebanding antar fase (jumlah ion per formula beda). Di sini tiap fase
ditulis reaksi disolusinya eksplisit, lalu S dihitung dari persamaan kesetimbangan
umum A_(nu+) B_(nu-) -> nu+ A + nu- B:  S = (Ksp/(nu+^nu+ * nu-^nu-))^(1/(nu++nu-)).

Asumsi (dicatat di laporan): aktivitas ~ konsentrasi, tanpa efek ion senama, tanpa
hidrolisis PO4 selain yang eksplisit; OCP memakai Ksp kondisional pada pH tetap
(Ksp' = Ksp/[H+]^2; [H+] = 10^-pH). pH 7,4 dipakai untuk varian kondisional.
"""
import time

import numpy as np
import pandas as pd

from common import PROC, REPORTS

# (label, reaksi, nu_plus, nu_minus, anion_ekstra(=1 utk OH/F), pKsp, kelas, catatan)
FASE = [
    ("Brushite (DCPD)", "CaHPO4.2H2O -> Ca2+ + HPO4(2-) + 2H2O", 1, 1, 0, 6.59, "fast", "pKsp utk CaHPO4.2H2O"),
    ("Monetite (DCPA)", "CaHPO4 -> Ca2+ + HPO4(2-)", 1, 1, 0, 6.90, "fast", "pKsp utk CaHPO4"),
    ("alpha-TCP", "Ca3(PO4)2 -> 3Ca2+ + 2PO4(3-)", 3, 2, 0, 25.5, "resorbable", "pKsp utk alpha-Ca3(PO4)2"),
    ("beta-TCP", "Ca3(PO4)2 -> 3Ca2+ + 2PO4(3-)", 3, 2, 0, 28.9, "resorbable", "pKsp utk beta-Ca3(PO4)2"),
    ("TTCP", "Ca4(PO4)2O -> 4Ca2+ + 2PO4(3-) + O(2-)", 4, 2, 1, 38.0, "slowly resorbable",
     "konvensi: [O(2-)] = S (anion oksida; terhidrolisis jadi 2OH- di larutan)"),
    ("OCP", "Ca8H2(PO4)6.5H2O -> 8Ca2+ + 2H+ + 6PO4(3-) + 5H2O", 8, 6, 0, 96.6, "fast in vivo",
     "Ksp kondisional memuat [H+]^2 -> Ksp' = Ksp/[H+]^2 pada pH tetap"),
    ("Hydroxyapatite", "Ca5(PO4)3OH -> 5Ca2+ + 3PO4(3-) + OH-", 5, 3, 1, 116.8, "essentially insoluble", ""),
    ("Fluorapatite", "Ca5(PO4)3F -> 5Ca2+ + 3PO4(3-) + F-", 5, 3, 1, 121.0, "essentially insoluble", "pKsp ~121 (Dorozhkin)"),
    ("Oxyapatite", "Ca10(PO4)6O -> 10Ca2+ + 6PO4(3-) + O(2-)", 10, 6, 1, 116.8, "essentially insoluble",
     "data terbatas; dipakai ~HA (Elliott) sebagai batas bawah kelarutan"),
]

PH_SENSITIVITAS = 7.4


def hitung_s(pksp, nu_p, nu_m, anion_ekstra, kondisional_h=False, ph=PH_SENSITIVITAS):
    ksp = 10.0 ** (-pksp)
    if kondisional_h:
        # Ksp terukur memuat [H+]^2 -> bagi dengan [H+]^2 pada pH tetap
        ksp = ksp / (10.0 ** (-2 * ph))
    denom = (nu_p ** nu_p) * (nu_m ** nu_m) * (anion_ekstra if anion_ekstra else 1)
    nu_tot = nu_p + nu_m + (1 if anion_ekstra else 0)
    return (ksp / denom) ** (1.0 / nu_tot)


def main():
    baris = []
    for label, reaksi, nu_p, nu_m, an_ex, pksp, kelas, catatan in FASE:
        s = hitung_s(pksp, nu_p, nu_m, an_ex, kondisional_h=(label == "OCP"))
        baris.append({
            "fase": label, "reaksi": reaksi, "nu_plus": nu_p, "nu_minus": nu_m,
            "anion_ekstra": an_ex, "pKsp": pksp, "S_mol_L": s, "log10_S": np.log10(s),
            "S_mmol_L": s * 1e3, "S_mg_L": s * 1e3 * 310.18,  # ~HA per formula sebagai skala kasar
            "kelas": kelas, "catatan": catatan})
    df = pd.DataFrame(baris).sort_values("log10_S", ascending=False)
    df.to_csv(PROC / "kelarutan_ksp.csv", index=False)

    t = df.to_markdown(index=False, floatfmt=".3g")
    urutan = df.sort_values("log10_S", ascending=False)["fase"].str.replace(r" \(.*", "", regex=True).tolist()
    laporan = [f"# Kelarutan Setimbang Stoikiometrik (S, mol/L) dari pKsp Literatur\n"
               f"**Tanggal:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
               f"- S = (Ksp/(nu+^nu+ * nu-^nu-))^(1/(nu++nu-)); asumsi: aktivitas ~ konsentrasi, "
               f"tanpa efek ion senama; OCP kondisional pH {PH_SENSITIVITAS} (Ksp' = Ksp/[H+]^2).",
               f"- S_mg_L hanyalah skala kasar (berat formula ~HA 310 g/mol) — jangan dipakai untuk klaim presisi.\n",
               t,
               f"\n## Temuan",
               f"- Urutan kelarutan: {urutan}",
               f"- Rentang S: {df['S_mol_L'].max():.3g} s.d. {df['S_mol_L'].min():.3g} mol/L — "
               f"rentang {int(df['log10_S'].max() - df['log10_S'].min())} orde besaran.",
               f"- S sebanding antar fase (ternormalisasi stoikiometri); tetap overlay post-hoc, "
               f"bukan kriteria atas seluruh kolam (pKsp hanya ada untuk fase dikenal)."]
    (REPORTS / "laporan_kelarutan.md").write_text("\n".join(laporan), encoding="utf-8")
    print("\n".join(laporan).encode("ascii", "replace").decode("ascii"))


if __name__ == "__main__":
    main()
