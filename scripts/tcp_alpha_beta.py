"""Tutup gap #3: pisahkan alpha-TCP vs beta-TCP berdasarkan spacegroup, validasi vs literatur.

b-TCP: rombohedral R3c (sg #161), a=10.44 A, c=37.38 A, rho=3.07 g/cm3
a-TCP: monoklinik P21/a (sg #14), a=12.89 b=27.28 c=15.22 A, rho=2.86 g/cm3
"""
import ast
import time

import numpy as np
import pandas as pd

from common import PROC, RAW, REPORTS

LIT = {
    "beta-TCP": {"sg": "R3c (161)", "a": 10.44, "c": 37.38, "rho": 3.07},
    "alpha-TCP": {"sg": "P21/a (14)", "a": 12.89, "b": 27.28, "c": 15.22, "rho": 2.86},
}


def fasa_tcp(sg_num, sg_str):
    s = str(sg_num) + " " + str(sg_str)
    if "161" in str(sg_num):
        return "beta-TCP"
    if "14" in str(sg_num) or "P 1 21/a" in s or "P21/a" in s:
        return "alpha-TCP"
    return None


def main():
    laporan = [f"# Laporan Pemisahan alpha/beta-TCP vs Literatur\n**Tanggal:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n"]
    baris = []

    # COD (punya sgNumber + a,b,c)
    cod = pd.read_csv(RAW / "cod" / "cod_cap.csv")
    inv = pd.read_csv(PROC / "dataset_deskriptor.csv")
    tcp_inv = inv[(inv["kelompok"] == "trikalsium_fosfat")].copy()
    cod_tcp = cod[cod["file"].astype(str).isin(tcp_inv[tcp_inv["sumber"] == "COD"]["id"].astype(str))]
    for _, r in cod_tcp.iterrows():
        fasa = fasa_tcp(r.get("sgNumber"), r.get("sg"))
        if fasa:
            baris.append({"sumber": "COD", "id": r["file"], "fasa": fasa,
                          "sg": r.get("sg"), "sgNumber": r.get("sgNumber"),
                          "a_A": pd.to_numeric(r.get("a"), errors="coerce"),
                          "b_A": pd.to_numeric(r.get("b"), errors="coerce"),
                          "c_A": pd.to_numeric(r.get("c"), errors="coerce"),
                          "densitas": None})

    # AFLOW (spacegroup_relax + geometry)
    af = pd.read_csv(RAW / "aflow" / "aflow_cap.csv")
    af_tcp = af[af["compound"].astype(str).isin(["Ca3O8P2", "Ca3P2O8"])]
    for _, r in af_tcp.iterrows():
        fasa = fasa_tcp(r.get("spacegroup_relax"), "")
        g = r.get("geometry")
        if isinstance(g, str):
            try:
                g = ast.literal_eval(g)
            except Exception:
                g = None
        if fasa:
            baris.append({"sumber": "AFLOW", "id": r.get("auid"), "fasa": fasa,
                          "sg": r.get("spacegroup_relax"), "sgNumber": r.get("spacegroup_relax"),
                          "a_A": g[0] if g else None, "b_A": g[1] if g else None,
                          "c_A": g[2] if g else None, "densitas": r.get("density")})

    # Materials Project (spacegroup_symbol/number dari inventory)
    mp_tcp = tcp_inv[tcp_inv["sumber"] == "MaterialsProject"]
    for _, r in mp_tcp.iterrows():
        fasa = fasa_tcp(r.get("spacegroup_number"), r.get("spacegroup_symbol"))
        if fasa:
            baris.append({"sumber": "MaterialsProject", "id": r["id"], "fasa": fasa,
                          "sg": r.get("spacegroup_symbol"), "sgNumber": r.get("spacegroup_number"),
                          "a_A": None, "b_A": None, "c_A": None,
                          "densitas": r.get("densitas_final_gcm3")})

    df = pd.DataFrame(baris)
    if len(df) == 0:
        laporan.append("- Tidak ada entri TCP dengan spacegroup teridentifikasi (R3c/161 atau P21/a/14).")
    else:
        laporan.append(f"## Ringkasan per Fasa\n{df.groupby(['fasa', 'sumber']).size().to_markdown()}")
        for fasa, lit in LIT.items():
            d = df[df["fasa"] == fasa]
            if len(d) == 0:
                laporan.append(f"\n## {fasa}: tidak ada entri teridentifikasi (literatur sg {lit['sg']})")
                continue
            a = d["a_A"].dropna()
            c = d["c_A"].dropna()
            rho = d["densitas"].dropna()
            laporan.append(f"\n## {fasa} (literatur: {lit['sg']}, a={lit['a']}, c={lit['c']}, rho={lit['rho']})")
            laporan.append(f"- jumlah entri: {len(d)}")
            if len(a):
                laporan.append(f"- a = {a.mean():.3f} +/- {a.std():.3f} A (selisih vs lit: {(a.mean() - lit['a']) / lit['a'] * 100:+.1f}%)")
            if len(c):
                laporan.append(f"- c = {c.mean():.3f} +/- {c.std():.3f} A (selisih vs lit: {(c.mean() - lit['c']) / lit['c'] * 100:+.1f}%)")
            if len(rho):
                laporan.append(f"- densitas = {rho.mean():.3f} +/- {rho.std():.3f} g/cm3 (selisih vs lit: {(rho.mean() - lit['rho']) / lit['rho'] * 100:+.1f}%)")
    (REPORTS / "laporan_tcp_alpha_beta.md").write_text("\n".join(laporan), encoding="utf-8")
    print("\n".join(laporan).encode("ascii", "replace").decode("ascii"))


if __name__ == "__main__":
    main()
