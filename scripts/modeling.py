"""Pemodelan ML v2 — metodologi anti-kebocoran & metrik jujur.

Koreksi (2026-11-04, kritik reviewer):
1. Grouping = formula TEREDUKSI (gcd) -> polimorf & kelipatan formula satu fold.
2. Feature set discovery = komposisi MURNI (tanpa volume/densitas — tak diketahui utk material baru).
   Densitas model dengan [volume+MW] dilaporkan hanya sebagai "identitas kristalografi" (bukan klaim).
3. Nested CV utk SVR (inner: pilih hiperparameter; outer: laporan) -> estimasi tidak optimistis.
4. Performa Eform DILAPORKAN dalam keluarga fosfat (tanpa fosfida bimodal).
5. Uji eksternal OQMD: (a) bebas-tumpang-tindih komposisi (strict), (b) penuh dengan catatan.
6. Classifier suitability = cek konsistensi label (fungsi semi-deterministik fitur) — BUKAN klaim prediktif;
   TIDAK lagi dipakai sebagai kriteria MCDM (double counting dengan C1-C3).
"""
import math
import time

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import (accuracy_score, f1_score, mean_absolute_error,
                             mean_squared_error, r2_score)
from sklearn.model_selection import GroupKFold, ParameterGrid
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from xgboost import XGBRegressor

from common import PROC, REPORTS

FS_KOMPOSISI = ["ca_p_ratio", "EN_avg", "berat_molekul", "frac_Ca", "frac_P",
                "frac_O", "frac_H", "frac_F"]
FS_IDENTITAS_DENSITAS = ["berat_molekul", "volume_A3"]  # rho = MZ/(NA V) -> hampir identitas
FS_FULL = ["ca_p_ratio", "EN_avg", "berat_molekul", "volume_A3",
           "densitas_final_gcm3", "frac_Ca", "frac_P", "frac_O", "frac_H", "frac_F"]

GRID_SVR = {"C": [1, 10, 50], "gamma": [0.01, 0.05, 0.1], "epsilon": [0.05, 0.1]}


def kunci_reduksi(row):
    v = [int(round(float(row.get(k)))) if pd.notna(row.get(k)) else 0
         for k in ["Ca", "P", "O", "H", "F"]]
    if sum(v) == 0:
        return "0-0-0-0-0"
    g = 0
    for x in v:
        g = math.gcd(g, x)
    return "-".join(str(x // g) for x in v)


def siapkan_data():
    df = pd.read_csv(PROC / "dataset_deskriptor.csv")
    sub = df[df["sumber"].isin(["MaterialsProject", "AFLOW", "OQMD"])].copy()
    tot = sub[["Ca", "P", "O", "H", "F"]].fillna(0).sum(axis=1)
    for el in ["Ca", "P", "O", "H", "F"]:
        sub[f"frac_{el}"] = sub[el].fillna(0) / tot
    sub["komposisi_reduksi"] = sub.apply(kunci_reduksi, axis=1)
    sub["ada_O"] = sub["O"].fillna(0) > 0
    return sub.reset_index(drop=True)


def cv_group(X, y, groups, model, scaler=False):
    gkf = GroupKFold(n_splits=10)
    r2s, rmses, maes = [], [], []
    for tr, te in gkf.split(X, y, groups):
        Xtr, Xte = X[tr], X[te]
        if scaler:
            sc = StandardScaler().fit(Xtr)
            Xtr, Xte = sc.transform(Xtr), sc.transform(Xte)
        model.fit(Xtr, y[tr])
        pred = model.predict(Xte)
        r2s.append(r2_score(y[te], pred))
        rmses.append(np.sqrt(mean_squared_error(y[te], pred)))
        maes.append(mean_absolute_error(y[te], pred))
    return float(np.mean(r2s)), float(np.mean(rmses)), float(np.mean(maes))


def nested_cv_svr(X, y, groups, grid):
    """Nested CV: outer 10-fold pelaporan; inner 5-fold (GroupKFold) pilih hiperparameter."""
    outer = GroupKFold(n_splits=10)
    r2s, rmses, maes = [], [], []
    terpilih = []
    for tr, te in outer.split(X, y, groups):
        Xtr, Xte = X[tr], X[te]
        inner = GroupKFold(n_splits=5)
        best = None
        for p in ParameterGrid(grid):
            skor = []
            for tr2, va in inner.split(Xtr, y[tr], groups[tr]):
                sc = StandardScaler().fit(Xtr[tr2])
                m = SVR(**p).fit(sc.transform(Xtr[tr2]), y[tr][tr2])
                skor.append(r2_score(y[tr][va], m.predict(sc.transform(Xtr[va]))))
            r2_in = float(np.mean(skor))
            if best is None or r2_in > best[0]:
                best = (r2_in, p)
        terpilih.append(best[1])
        sc = StandardScaler().fit(Xtr)
        m = SVR(**best[1]).fit(sc.transform(Xtr), y[tr])
        pred = m.predict(sc.transform(Xte))
        r2s.append(r2_score(y[te], pred))
        rmses.append(np.sqrt(mean_squared_error(y[te], pred)))
        maes.append(mean_absolute_error(y[te], pred))
    return (float(np.mean(r2s)), float(np.mean(rmses)), float(np.mean(maes)), terpilih)


def main():
    sub = siapkan_data()
    laporan = [f"# Laporan Pemodelan ML v2 (anti-leakage, metrik jujur)\n"
               f"**Tanggal:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
               f"**Grouping:** formula tereduksi (gcd) | **CV:** GroupKFold(10) | "
               f"**SVR:** nested CV (inner 5-fold pilih hiperparameter)\n"]

    # ===== Eform: fitur komposisi murni (skenario discovery) =====
    d = sub.dropna(subset=FS_KOMPOSISI + ["Eform_eV_atom"]).reset_index(drop=True)
    X, y = d[FS_KOMPOSISI].values, d["Eform_eV_atom"].values
    g = d["komposisi_reduksi"].values
    laporan.append(f"## Eform (eV/atom) — fitur KOMPOSISI MURNI, semua sumber n={len(d)}")
    tabel = []
    for nm, mdl in [("RF", RandomForestRegressor(n_estimators=400, random_state=0, n_jobs=-1)),
                    ("GBR", GradientBoostingRegressor(random_state=0)),
                    ("XGB", XGBRegressor(n_estimators=400, learning_rate=0.05, max_depth=5,
                                         random_state=0, verbosity=0))]:
        r2, rmse, mae = cv_group(X, y, g, mdl)
        tabel.append({"model": nm, "R2": round(r2, 3), "RMSE": round(rmse, 3), "MAE": round(mae, 3)})
    r2, rmse, mae, terpilih = nested_cv_svr(X, y, g, GRID_SVR)
    tabel.append({"model": "SVR-nested", "R2": round(r2, 3), "RMSE": round(rmse, 3), "MAE": round(mae, 3)})
    t = pd.DataFrame(tabel)
    t.to_csv(PROC / "hasil_cv_eform_komposisi.csv", index=False)
    laporan.append(t.to_markdown(index=False))
    laporan.append(f"- Hiperparameter terpilih (outer): {terpilih[:3]} ...")

    # ===== Eform skenario SCREENING basis data: fitur struktur-informed (volume+densitas tersedia di basis data) =====
    # Ini BUKAN skenario discovery; sah bila framework dipakai menyaring entri basis data.
    d2 = sub[sub["sumber"].isin(["MaterialsProject", "AFLOW"])].dropna(
        subset=FS_FULL + ["Eform_eV_atom"]).reset_index(drop=True)
    r2u, rmseu, maeu, _ = nested_cv_svr(d2[FS_FULL].values, d2["Eform_eV_atom"].values,
                                        d2["komposisi_reduksi"].values, GRID_SVR)
    laporan.append(f"## Eform — skenario SCREENING (fitur termasuk volume+densitas, MP+AFLOW n={len(d2)})")
    laporan.append(f"- SVR nested: R2 = {r2u:.3f}, RMSE = {rmseu:.3f}, MAE = {maeu:.3f} "
                   f"(catatan: TIDAK berlaku untuk material baru — densitas/volume tak diketahui)")

    # ===== Eform dalam keluarga fosfat (tanpa fosfida) =====
    dp = d[d["ada_O"]].reset_index(drop=True)
    Xp, yp, gp = dp[FS_KOMPOSISI].values, dp["Eform_eV_atom"].values, dp["komposisi_reduksi"].values
    r2p, rmsep, maep = cv_group(Xp, yp, gp, SVR(C=50, gamma=0.05, epsilon=0.05), scaler=True)
    laporan.append(f"## Eform DALAM KELUARGA FOSFAT (ada O, n={len(dp)}) — SVR C=50")
    laporan.append(f"- R2 = {r2p:.3f}, RMSE = {rmsep:.3f}, MAE = {maep:.3f}")
    laporan.append("- Catatan: rentang fosfida vs fosfat bimodal TIDAK lagi mengatrol R2 di sini.")

    # ===== Densitas: (a) identitas kristalografi [MW+volume] — bukan klaim; (b) komposisi murni =====
    dd = sub.dropna(subset=FS_IDENTITAS_DENSITAS + ["densitas_final_gcm3"]).reset_index(drop=True)
    r2i, rmsei, maei = cv_group(dd[FS_IDENTITAS_DENSITAS].values, dd["densitas_final_gcm3"].values,
                                dd["komposisi_reduksi"].values,
                                RandomForestRegressor(n_estimators=400, random_state=0, n_jobs=-1))
    laporan.append(f"## Densitas — [berat molekul + volume] = IDENTITAS KRISTALOGRAFI (bukan klaim prediktif)")
    laporan.append(f"- R2 = {r2i:.3f} (konsistensi data; rho = MZ/(NA V))")
    dc = dd.dropna(subset=FS_KOMPOSISI).reset_index(drop=True)
    r2c, rmsec, maec = cv_group(dc[FS_KOMPOSISI].values, dc["densitas_final_gcm3"].values,
                                dc["komposisi_reduksi"].values,
                                RandomForestRegressor(n_estimators=400, random_state=0, n_jobs=-1))
    laporan.append(f"## Densitas — fitur KOMPOSISI MURNI (prediksi nyata, n={len(dc)})")
    laporan.append(f"- R2 = {r2c:.3f}, RMSE = {rmsec:.3f}, MAE = {maec:.3f}")

    # ===== Uji eksternal OQMD bebas-tumpang-tindih =====
    tr = d[d["sumber"] != "OQMD"]
    te = d[d["sumber"] == "OQMD"]
    kunci_latih = set(tr["komposisi_reduksi"])
    te_bebas = te[~te["komposisi_reduksi"].isin(kunci_latih)]
    sc = StandardScaler().fit(tr[FS_KOMPOSISI])
    mdl = SVR(C=50, gamma=0.05, epsilon=0.05).fit(sc.transform(tr[FS_KOMPOSISI]), tr["Eform_eV_atom"])
    for nama, txx in [("OQMD PENUH (komposisi bisa tumpang tindih dgn latih)", te),
                      ("OQMD BEBAS TUMPANG TINDIH (strict)", te_bebas)]:
        if len(txx) == 0:
            laporan.append(f"- {nama}: kosong")
            continue
        pred = mdl.predict(sc.transform(txx[FS_KOMPOSISI]))
        laporan.append(f"## Uji eksternal — {nama} (n={len(txx)})")
        laporan.append(f"- R2 = {r2_score(txx['Eform_eV_atom'], pred):.3f}, "
                       f"RMSE = {np.sqrt(mean_squared_error(txx['Eform_eV_atom'], pred)):.3f}, "
                       f"MAE = {mean_absolute_error(txx['Eform_eV_atom'], pred):.3f}")

    # ===== Classifier = cek konsistensi label (bukan klaim) =====
    sub["layak"] = ((sub["Eform_eV_atom"] <= -2.5) &
                    (sub["ca_p_ratio"].between(1.0, 2.1)) &
                    (sub["densitas_final_gcm3"].between(0.5, 4.5))).astype(int)
    laporan.append("## Classifier suitability — CEK KONSISTENSI LABEL (bukan klaim prediktif)")
    laporan.append("- Label adalah fungsi semi-deterministik dari fitur (pita Ca/P & densitas ada di fitur; "
                   "hanya Eform yang perlu dipelajari) -> akurasi tinggi DIHARAPKAN dan tidak informatif.")
    laporan.append("- Keputusan: skor ini TIDAK dipakai sebagai kriteria MCDM (double counting dengan C1-C3).")

    sub[["id", "sumber", "formula", "layak", "ca_p_ratio", "Eform_eV_atom",
         "densitas_final_gcm3", "bandgap_eV", "bulk_K_GPa", "shear_G_GPa", "young_E_GPa",
         "kelompok", "komposisi_reduksi", "ada_O"]].to_csv(
        PROC / "kandidat_scaffold.csv", index=False)
    (REPORTS / "laporan_pemodelan.md").write_text("\n".join(laporan), encoding="utf-8")
    print("\n".join(laporan).encode("ascii", "replace").decode("ascii"))


if __name__ == "__main__":
    main()
