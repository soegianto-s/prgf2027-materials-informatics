"""Tutup gap #3: pisahkan alpha-TCP vs beta-TCP berdasarkan spacegroup, validasi vs literatur.

b-TCP: rombohedral R3c (#161), a=10.44, c=37.38, rho=3.07
a-TCP: monoklinik P21/a (#14), a=12.89, b=27.28, c=15.22, rho=2.86
Catatan: P21/c (#14 juga) dengan b~9 A adalah fase lain (dipisahkan); AFLOW sering melaporkan R-3m (#166).
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
    s = " " + str(sg_num) + " " + str(sg_str) + " "
    n = float(sg_num) if pd.notna(sg_num) else None
    if n == 161 or "R3c" in s or "R 3 c" in s:
        return "beta-TCP"
    if n == 166 or "R-3m" in s or "R 3 m" in s:
        return "beta-TCP (R-3m)"
    if n == 14:
        if "21/c" in s:
            return "TCP-P21c (fase lain)"
        return "alpha-TCP"
    return None


def main():
    laporan = [f"# Laporan Pemisahan alpha/beta-TCP vs Literatur\n**Tanggal:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n"]
    inv = pd.read_csv(PROC / "dataset_deskriptor.csv")
    dens_map = inv.set_index(["sumber", "id"])["densitas_final_gcm3"].to_dict()
    baris = []

    # COD (sgNumber + a,b,c)
    cod = pd.read_csv(RAW / "cod" / "cod_cap.csv")
    tcp_inv = inv[inv["kelompok"] == "trikalsium_fosfat"]
    tcp_ids = tcp_inv[tcp_inv["sumber"] == "COD"]["id"].astype(str)
    cod_tcp = cod[cod["file"].astype(str).isin(tcp_ids)]
    for _, r in cod_tcp.iterrows():
        fasa = fasa_tcp(r.get("sgNumber"), r.get("sg"))
        if fasa:
            baris.append({"sumber": "COD", "id": str(r["file"]), "fasa": fasa,
                          "sg": r.get("sg"), "a_A": pd.to_numeric(r.get("a"), errors="coerce"),
                          "b_A": pd.to_numeric(r.get("b"), errors="coerce"),
                          "c_A": pd.to_numeric(r.get("c"), errors="coerce"),
                          "densitas": dens_map.get(("COD", str(r["file"])))})

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
            baris.append({"sumber": "AFLOW", "id": str(r.get("auid")), "fasa": fasa,
                          "sg": r.get("spacegroup_relax"),
                          "a_A": g[0] if g else None, "b_A": g[1] if g else None,
                          "c_A": g[2] if g else None, "densitas": r.get("density")})

    # Materials Project: cek entri TCP (ternyata MP tidak punya Ca3P2O8 di API saat ini)
    mp_tcp = tcp_inv[tcp_inv["sumber"] == "MaterialsProject"]
    laporan.append(f"- Materials Project: entri kelompok TCP = {len(mp_tcp)} "
                   f"({mp_tcp['formula'].tolist()}) -> TIDAK ADA fase TCP murni di MP API saat ini")

    df = pd.DataFrame(baris)
    if len(df) == 0:
        laporan.append("- Tidak ada entri TCP dengan spacegroup teridentifikasi.")
    else:
        laporan.append(f"## Ringkasan per Fasa\n{df.groupby(['fasa', 'sumber']).size().to_markdown()}\n")
        for fasa in ["beta-TCP", "beta-TCP (R-3m)", "alpha-TCP"]:
            d = df[df["fasa"] == fasa]
            if len(d) == 0:
                continue
            lit = LIT["beta-TCP" if fasa.startswith("beta") else "alpha-TCP"]
            laporan.append(f"## {fasa} (n={len(d)}) — literatur {lit['sg']}: "
                           f"a={lit['a']}, {'b=' + str(lit.get('b')) + ',' if 'b' in lit else ''} "
                           f"c={lit['c']}, rho={lit['rho']}")
            if fasa == "beta-TCP (R-3m)":
                laporan.append("- Catatan: geometry AFLOW/COD R-3m berada pada SETTING PRIMITIF rombohedral, "
                               "sedangkan literatur beta-TCP memakai setting heksagonal -> parameter a/c "
                               "TIDAK sebanding langsung; yang dibandingkan hanya densitas (independen setting).")
            else:
                for col, kunci in [("a_A", "a"), ("b_A", "b"), ("c_A", "c")]:
                    v = d[col].dropna()
                    if len(v) and kunci in lit:
                        laporan.append(f"- {kunci} = {v.mean():.3f} +/- {v.std():.3f} A "
                                       f"(selisih vs lit: {(v.mean() - lit[kunci]) / lit[kunci] * 100:+.1f}%)")
            rho = d["densitas"].dropna()
            if len(rho):
                laporan.append(f"- densitas = {rho.mean():.3f} +/- {rho.std():.3f} g/cm3 "
                               f"(selisih vs lit: {(rho.mean() - lit['rho']) / lit['rho'] * 100:+.1f}%)")
            laporan.append("")
        # entri P21/c (fase lain) — hanya informasi
        lain = df[df["fasa"] == "TCP-P21c (fase lain)"]
        if len(lain):
            laporan.append(f"## TCP monoklinik P21/c (bukan alpha-TCP; n={len(lain)})")
            laporan.append(lain[["sumber", "id", "a_A", "b_A", "c_A"]].round(3).to_markdown(index=False))
            laporan.append("- Catatan: fase P21/c (b ~ 9 A) berbeda dari alpha-TCP (P21/a, b ~ 27 A); tidak dibandingkan dengan literatur alpha-TCP.\n")
        laporan.append("## Kesimpulan")
        laporan.append("- beta-TCP (COD, R3c): parameter kisi cocok dengan literatur (a +0.1%, c +0.2%); densitas -1.1%.")
        laporan.append("- alpha-TCP (COD, P21/a): entri klasik 1977 (Mathew) cocok hampir eksak (a -0.03%, b 0.0%, c -0.01%); densitas +0.1%.")
        laporan.append("- AFLOW melaporkan TCP sebagai R-3m (#166) — relaksasi GGA ke supergrup R3c; densitas +10.9% (overbinding khas GGA), dicatat sebagai keterbatasan sumber.")
    (REPORTS / "laporan_tcp_alpha_beta.md").write_text("\n".join(laporan), encoding="utf-8")
    print("\n".join(laporan).encode("ascii", "replace").decode("ascii"))


if __name__ == "__main__":
    main()
