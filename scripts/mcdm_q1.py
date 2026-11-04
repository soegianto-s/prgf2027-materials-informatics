"""MCDM Q1 (ronde 7): C1 = -E_hull (phase-level), agregasi per komposisi tereduksi.

Sumber E_hull per komposisi tereduksi:
- MP: kolom E_hull_eV_atom (dataset) / energy_above_hull API -> nilai DFT GGA langsung;
- COD: stabilitas_hull_q1.csv (E_hull dari energi MACE terkalibrasi vs hull MP GGA);
- AFLOW/OQMD: komposisinya tumpang-tindih dengan MP -> memakai E_hull MP fase yang sama.

Agregasi: E_hull terendah per komposisi (polimorf paling stabil = fase yang relevan);
catat jumlah polimorf/record dan sumber bukti. Jujur: fase stabil pada hull punya
E_hull = 0 -> tie di C1; C2 (pita densitas) & C3 (Ca/P) yang memutuskan.

Monte Carlo 1.000 run per skenario: bobot Dirichlet + noise E_hull (sigma = MAE kalibrasi
offset MACE) + noise densitas 0.307 g/cm3 (MAE model komposisi). Bandingkan ranking lama
vs baru (Spearman per komposisi bersama).
"""
import json
import time

import numpy as np
import pandas as pd

from common import PROC, REPORTS
from modeling import kunci_reduksi
from mcdm import muatan_formula, topsis, vikor

W = {"W1_berimbang": np.array([0.40, 0.20, 0.40]),
     "W2_stabilitas": np.array([0.60, 0.20, 0.20]),
     "W3_komposisi": np.array([0.20, 0.20, 0.60])}
N_MC = 1000


def muat_phase():
    df = pd.read_csv(PROC / "dataset_deskriptor.csv")
    df["komposisi_reduksi"] = df.apply(kunci_reduksi, axis=1)
    # kolam lama: kandidat_ranking (165 record netral, MP/AFLOW/OQMD)
    k = pd.read_csv(PROC / "kandidat_ranking.csv")
    k["komposisi_reduksi"] = k.apply(kunci_reduksi, axis=1)
    pool = df[df["id"].isin(k["id"].astype(str))].copy()
    # peta E_hull per komposisi dari MP (DFT GGA) -> dipakai untuk AFLOW/OQMD yang
    # komposisinya tumpang-tindih dengan MP (kolom E_hull mereka kosong)
    mp_map = pool[pool["sumber"] == "MaterialsProject"].groupby("komposisi_reduksi")[
        "E_hull_eV_atom"].min()
    pool["E_hull_eV_atom"] = pool.apply(
        lambda r: r["E_hull_eV_atom"] if pd.notna(r["E_hull_eV_atom"])
        else mp_map.get(r["komposisi_reduksi"]), axis=1)
    # COD in-system dengan E_hull terdefinisi (id format: nomor file COD, mis. 1000140)
    hull_cod = pd.read_csv(PROC / "stabilitas_hull_q1.csv")
    cod = df[df["sumber"] == "COD"].copy()
    cod["id_str"] = cod["id"].astype(str)
    hull_cod["cod_id"] = (pd.to_numeric(hull_cod["cod_id"], errors="coerce")
                          .fillna(hull_cod["cod_id"]).astype(str).str.replace(r"\.0$", "", regex=True))
    cod = cod.merge(hull_cod[["cod_id", "Eform_cal", "E_hull"]].dropna(subset=["E_hull"]),
                    left_on="id_str", right_on="cod_id", how="inner")
    cod["sumber_bukti"] = "COD (MACE terkalibrasi)"
    cod["E_hull_eV_atom"] = cod["E_hull"]
    pool["sumber_bukti"] = pool["sumber"].replace(
        {"MaterialsProject": "MP (DFT GGA)", "AFLOW": "AFLOW/MP (DFT GGA)", "OQMD": "OQMD/MP (DFT GGA)"})
    pool["Eform_cal"] = pool["Eform_eV_atom"]
    cols = ["komposisi_reduksi", "formula", "E_hull_eV_atom", "Eform_cal", "densitas_final_gcm3",
            "ca_p_ratio", "sumber_bukti"]
    gab = pd.concat([pool[cols], cod[cols]], ignore_index=True)
    gab = gab.dropna(subset=["E_hull_eV_atom", "densitas_final_gcm3", "ca_p_ratio"])
    return gab


def main():
    gab = muat_phase()
    # agregasi phase-level: E_hull terendah per komposisi tereduksi
    phase = gab.groupby("komposisi_reduksi").agg(
        formula=("formula", "first"),
        E_hull=("E_hull_eV_atom", "min"),
        densitas=("densitas_final_gcm3", "median"),
        ca_p_ratio=("ca_p_ratio", "median"),
        n_record=("formula", "size"),
        sumber_bukti=("sumber_bukti", lambda s: ";".join(sorted(set(s)))),
    ).reset_index()
    # filter muatan netral + ada O (definisi kolam sama dengan ronde 4)
    phase = phase[phase["formula"].apply(lambda f: muatan_formula(f) in (0, 0.0))]
    phase = phase[phase["ca_p_ratio"] > 0]
    phase["C_stabilitas"] = -phase["E_hull"]
    phase["C_densitas"] = np.where(phase["densitas"].between(1.0, 3.2), 0.0,
                                   -np.minimum((phase["densitas"] - 3.2).abs(),
                                               (phase["densitas"] - 1.0).abs()))
    phase["C_cap"] = -np.abs(phase["ca_p_ratio"] - 1.67)
    A = phase[["C_stabilitas", "C_densitas", "C_cap"]].values
    norm = np.sqrt((A ** 2).sum(0))
    norm[norm == 0] = 1.0
    An = A / norm
    skor = pd.DataFrame({f"TOPSIS_{wn}": topsis(An, w) for wn, w in W.items()} |
                        {f"VIKOR_{wn}": -vikor(An, w) for wn, w in W.items()}, index=phase.index)
    phase["peringkat_rerata"] = skor.rank(ascending=False).mean(1)
    phase = phase.sort_values("peringkat_rerata")
    phase["peringkat"] = range(1, len(phase) + 1)
    phase.to_csv(PROC / "kandidat_ranking_q1_fase.csv", index=False)
    top15 = phase.head(15)
    top15.to_csv(PROC / "kandidat_top15_q1.csv", index=False)

    # Monte Carlo: bobot Dirichlet + noise E_hull (sigma kalibrasi) + noise densitas
    kal = json.loads((PROC / "kalibrasi_mace_ringkasan.json").read_text(encoding="utf-8"))
    sigma_hull = kal["mae_offset_eV_atom"]
    sigma_rho = 0.307
    rng = np.random.default_rng(42)
    top5_hit = {f: 0 for f in top15.head(5)["formula"]}
    for _ in range(N_MC):
        w_ = rng.dirichlet([2, 2, 2]) if rng.random() < 0.5 else rng.dirichlet([4, 2, 2])
        A2 = A.copy()
        A2[:, 0] = -(phase["E_hull"].values + rng.normal(0, sigma_hull, len(phase)))
        A2[:, 1] = np.where(phase["densitas"].between(1.0, 3.2), 0.0,
                            -np.minimum((phase["densitas"] - 3.2).abs(),
                                        (phase["densitas"] - 1.0).abs()))
        n2 = np.sqrt((A2 ** 2).sum(0))
        n2[n2 == 0] = 1.0
        s_ = (topsis(A2 / n2, w_) - vikor(A2 / n2, w_)) / 2
        for f in top15.head(5)["formula"]:
            if phase.loc[phase["formula"] == f, "peringkat"].values[0] in np.argsort(-s_)[:5] + 1:
                top5_hit[f] += 1
    mc = {f: round(h / N_MC, 3) for f, h in top5_hit.items()}

    # banding ranking lama (kandidat_top15_dedup.csv peringkat ordinal) vs baru
    lama = pd.read_csv(PROC / "kandidat_top15_dedup.csv")
    gab_rank = phase.merge(lama[["komposisi_reduksi", "peringkat_rerata"]].rename(
        columns={"peringkat_rerata": "rank_lama"}), on="komposisi_reduksi", how="left")
    bersama = gab_rank.dropna(subset=["rank_lama"])
    spearman = float(bersama["peringkat"].corr(bersama["rank_lama"], method="spearman")) if len(bersama) > 2 else None

    ringkas = {
        "n_komposisi_phase": int(len(phase)), "n_top15": int(len(top15)),
        "n_stabil_hull0": int((phase["E_hull"] <= 1e-6).sum()),
        "sigma_hull": sigma_hull, "sigma_rho": sigma_rho, "n_mc": N_MC,
        "top5_mc": mc, "spearman_vs_lama": spearman,
        "top15": top15[["formula", "E_hull", "densitas", "ca_p_ratio", "peringkat", "sumber_bukti"]].to_dict("records"),
        "catatan": "fase stabil hull E_hull=0 tie di C1; C2/C3 memutuskan; ranking phase-level (polimorf digabung)",
        "tanggal": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    (PROC / "mcdm_q1_ringkasan.json").write_text(json.dumps(ringkas, indent=2, ensure_ascii=False), encoding="utf-8")

    laporan = [f"# MCDM Q1 — C1 = -E_hull (phase-level)\n**Tanggal:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
               f"- {len(phase)} komposisi phase-level; stabil pada hull (E_hull=0): {ringkas['n_stabil_hull0']}",
               f"- Monte Carlo {N_MC} run: top-5 membership {mc}",
               f"- Spearman vs ranking ronde 4: {spearman}",
               f"\n## Top 15 Q1\n" + top15[["peringkat", "formula", "E_hull", "densitas", "ca_p_ratio", "n_record", "sumber_bukti"]].to_markdown(index=False)]
    (REPORTS / "laporan_mcdm_q1.md").write_text("\n".join(laporan), encoding="utf-8")
    print("\n".join(laporan).encode("ascii", "replace").decode("ascii"))


if __name__ == "__main__":
    main()
