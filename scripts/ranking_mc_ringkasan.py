"""Ringkasan ranking final (Monte Carlo, per komposisi tereduksi) -> JSON.

Alasan: tab:top manuskrip lama berisi ranking deterministik level-rekaman yang
bertentangan dengan narasi Monte Carlo (mis. karbonat apatit rank 3 vs top-5 hanya
16,6% di MC). Skrip ini membangun SATU sumber kebenaran: urutan per komposisi
tereduksi menurut median rank MC (3.000 run, laporan_montecarlo.md) + nilai
E_f/rho/Ca-P dari rekaman terbaik tiap komposisi (kandidat_ranking.csv).

Output: data/processed/ranking_mc_ringkasan.json
"""
import json
import re

import pandas as pd

from common import PROC

# formula -> kunci komposisi tereduksi (Ca-P-O-H-F) sesuai kandidat_ranking.csv
FORMULA_KE_KUNCI = {
    "Ca5P3O12F": "5-3-12-0-1",
    "Ca10P6O25": "10-6-25-0-0",
    "Ca5P3HO13": "5-3-13-1-0",
    "Ca3(PO4)2": "3-2-8-0-0",
    "Ca4P2O9": "4-2-9-0-0",
    "Ca2P2O7": "2-2-7-0-0",
    "Ca10P6CO27": "10-6-27-0-0",
    "CaPHO4": "1-1-4-1-0",
    "Ca2P2H4O9": "2-2-9-4-0",
    "Ca4P6O19": "4-6-19-0-0",
    "Ca(PO3)2": "1-2-6-0-0",
    "Ca8P6H12O29": "8-6-29-12-0",
    "CaPH5O6": "1-1-6-5-0",
    "CaP2H2O7": "1-2-7-2-0",
    "CaP4O11": "1-4-11-0-0",
}
KELUARGA = {
    "Ca5P3O12F": "fluorapatite",
    "Ca10P6O25": "oxyapatite",
    "Ca5P3HO13": "hydroxyapatite",
    "Ca3(PO4)2": "$\\beta$-TCP",
    "Ca4P2O9": "TTCP",
    "Ca2P2O7": "Ca-pyrophosphate",
    "Ca10P6CO27": "carbonated apatite",
    "CaPHO4": "monetite (DCPA)",
    "Ca2P2H4O9": "DCP-related hydrate",
    "Ca4P6O19": "calcium polyphosphate",
    "Ca(PO3)2": "calcium metaphosphate",
    "Ca8P6H12O29": "OCP",
    "CaPH5O6": "brushite (DCPD)",
    "CaP2H2O7": "calcium dihydrogen pyrophosphate",
    "CaP4O11": "calcium ultraphosphate",
}


def parse_mc():
    """Baca tabel Monte Carlo dari laporan_montecarlo.md -> dict formula -> angka."""
    teks = (PROC.parent / "reports" / "laporan_montecarlo.md").read_text(encoding="utf-8")
    baris = [l for l in teks.splitlines() if l.startswith("|") and "formula" not in l and "---" not in l]
    hasil = {}
    for l in baris:
        sel = [c.strip() for c in l.strip("|").split("|")]
        if len(sel) < 8:
            continue
        f, med, p5, p95, t5, t10 = sel[0], float(sel[3]), float(sel[4]), float(sel[5]), float(sel[6]), float(sel[7])
        hasil[f] = {"median_rank": med, "p5_rank": p5, "p95_rank": p95,
                    "pct_top5": t5, "pct_top10": t10}
    return hasil


def main():
    mc = parse_mc()
    assert len(mc) >= 15, f"baris MC hanya {len(mc)}"
    k = pd.read_csv(PROC / "kandidat_ranking.csv")
    k["kunci"] = k["formula"].map({f: FORMULA_KE_KUNCI[f] for f in FORMULA_KE_KUNCI})

    terurut = sorted(mc.items(), key=lambda kv: kv[1]["median_rank"])
    ringkas = []
    for i, (formula, m) in enumerate(terurut, 1):
        kunci = FORMULA_KE_KUNCI[formula]
        grp = k[k["kunci"] == kunci]
        assert len(grp) >= 1, f"{formula} ({kunci}) tidak ada di kandidat_ranking.csv"
        terbaik = grp.sort_values("peringkat_rerata").iloc[0]
        ringkas.append({
            "order": i,
            "formula": formula,
            "keluarga": KELUARGA[formula],
            "sumber": terbaik["sumber"],
            "median_rank": m["median_rank"],
            "p5_rank": m["p5_rank"],
            "p95_rank": m["p95_rank"],
            "pct_top5": m["pct_top5"],
            "pct_top10": m["pct_top10"],
            "E_f": round(float(terbaik["Eform_eV_atom"]), 2),
            "rho": round(float(terbaik["densitas_final_gcm3"]), 2),
            "ca_p": round(float(terbaik["ca_p_ratio"]), 2),
        })
    assert len(ringkas) == 15, f"jumlah ringkas {len(ringkas)} != 15"
    # sanity: 4 besar = FAp, oksiapatit, HAp, beta-TCP (sesuai narasi manuskrip)
    assert [r["formula"] for r in ringkas[:4]] == ["Ca5P3O12F", "Ca10P6O25", "Ca5P3HO13", "Ca3(PO4)2"]
    # klaim teks: slot ke-5 diperebutkan TTCP 17% / karbonat 17% / pirofosfat 16%
    assert abs(ringkas[4]["pct_top5"] - 17.4) < 0.5 and abs(ringkas[6]["pct_top5"] - 16.6) < 0.5 \
        and abs(ringkas[5]["pct_top5"] - 15.7) < 0.5, "pct_top5 slot-5 berubah"
    out = PROC / "ranking_mc_ringkasan.json"
    out.write_text(json.dumps({"top15": ringkas}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"OK: {len(ringkas)} komposisi -> {out}")
    for r in ringkas[:6]:
        print(f"  {r['order']}. {r['formula']:12s} median {r['median_rank']:5.1f} "
              f"[{r['p5_rank']:3.0f}-{r['p95_rank']:3.0f}] top5 {r['pct_top5']:4.1f}%  "
              f"Ef {r['E_f']:+.2f}  rho {r['rho']:.2f}  Ca/P {r['ca_p']:.2f}")


if __name__ == "__main__":
    main()
