"""Model structure-informed (ronde 7/Q1) — BUKAN discovery, label eksplisit.

Fitur bertingkat pada subset MP+AFLOW (label DFT basis data saja; MACE/COD TIDAK
dipakai sebagai label latih):
  F0 = 4 DOF komposisi (ca_p_ratio, frac_P, frac_H, frac_F)
  F1 = F0 + volume + densitas (varian screening lama, pembanding)
  F2 = F0 + spesiasi Q^n + koordinasi Ca (fitur struktural kimiawi)
  F3 = F2 + SOAP-PCA(30) (fingerprint; PCA/scaler di-DALAM-fold, bukan global)

CV: GroupKFold(10) atas formula tereduksi; SVR nested CV (inner 5-fold) utk Eform;
RF untuned utk densitas. Label jujur: membutuhkan struktur yang SUDAH dikenal ->
hanya untuk menyaring entri basis data, bukan memprediksi material baru.
"""
import json
import time

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold, ParameterGrid
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR

from common import PROC, REPORTS
from modeling import FS_KOMPOSISI, GRID_SVR, siapkan_data

FITUR_Q = ["q0_frac", "q1_frac", "q2_frac", "q3_frac", "q_mean"]
FITUR_CN = ["cn_Ca_mean", "cn_Ca_std", "cn6_frac", "cn7_frac", "cn8_frac", "cn9_frac"]
N_PCA = 30


def muat_gabungan():
    sub = siapkan_data()
    fit = pd.read_csv(PROC / "fitur_struktur.csv")
    fit["id"] = fit["id"].astype(str)
    sub["id"] = sub["id"].astype(str)
    g = sub.merge(fit[fit["status"] == "ok"].drop(columns=["status", "alasan"]),
                  on=["sumber", "id"], how="left")
    # SOAP via NPZ
    soap, keys = None, None
    if (PROC / "soap_fingerprint.npz").exists():
        z = np.load(PROC / "soap_fingerprint.npz", allow_pickle=True)
        soap, keys = z["X"], z["keys"].astype(str)
    return g, soap, keys


def nested_cv_svr_pca(X, y, groups, grid, n_pca):
    """Seperti modeling.nested_cv_svr + PCA di dalam setiap fold latih (tidak bocor)."""
    if n_pca <= 0:
        from modeling import nested_cv_svr
        return nested_cv_svr(X, y, groups, grid)[:3]
    outer = GroupKFold(n_splits=10)
    r2s, rmses, maes = [], [], []
    for tr, te in outer.split(X, y, groups):
        Xtr, Xte = X[tr], X[te]
        inner = GroupKFold(n_splits=5)
        best = None
        for p in ParameterGrid(grid):
            skor = []
            for tr2, va in inner.split(Xtr, y[tr], groups[tr]):
                sc = StandardScaler().fit(Xtr[tr2])
                pc = PCA(n_components=min(n_pca, len(Xtr[tr2]))).fit(sc.transform(Xtr[tr2]))
                Z = pc.transform(sc.transform(Xtr[tr2]))
                m = SVR(**p).fit(Z, y[tr][tr2])
                skor.append(r2_score(y[tr][va], m.predict(pc.transform(sc.transform(Xtr[va])))))
            r2_in = float(np.mean(skor))
            if best is None or r2_in > best[0]:
                best = (r2_in, p)
        sc = StandardScaler().fit(Xtr)
        pc = PCA(n_components=min(n_pca, len(Xtr))).fit(sc.transform(Xtr))
        m = SVR(**best[1]).fit(pc.transform(sc.transform(Xtr)), y[tr])
        pred = m.predict(pc.transform(sc.transform(Xte)))
        r2s.append(r2_score(y[te], pred))
        rmses.append(np.sqrt(mean_squared_error(y[te], pred)))
        maes.append(mean_absolute_error(y[te], pred))
    return float(np.mean(r2s)), float(np.mean(rmses)), float(np.mean(maes))


def cv_group_rf(X, y, groups):
    from modeling import cv_group
    return cv_group(X, y, groups,
                    RandomForestRegressor(n_estimators=400, random_state=0, n_jobs=-1), scaler=True)


def main():
    g, soap, keys = muat_gabungan()
    laporan = [f"# Laporan Model Structure-Informed (ronde 7/Q1)\n**Tanggal:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
               f"- Label: HANYA DFT basis data (MP+AFLOW). MACE/COD tidak dipakai sebagai label latih.",
               f"- Fitur struktural membutuhkan struktur dikenal -> varian SCREENING, bukan discovery.",
               f"- SOAP: PCA {N_PCA} komponen di-dalam-fold (tidak bocor).\n"]
    tabel = []

    # Eform MP+AFLOW (skenario screening basis data)
    d = g[g["sumber"].isin(["MaterialsProject", "AFLOW"])].dropna(
        subset=FS_KOMPOSISI + ["Eform_eV_atom"]).reset_index(drop=True)
    grp = d["komposisi_reduksi"].values
    laporan.append(f"## Eform — MP+AFLOW (n={len(d)}), semua fitur dihitung di dalam CV")

    X0 = d[FS_KOMPOSISI].values
    r2, rmse, mae = nested_cv_svr_pca(X0, d["Eform_eV_atom"].values, grp, GRID_SVR, n_pca=0)
    tabel.append({"fitur": "F0 komposisi (4-DOF)", "target": "Eform", "R2": round(r2, 3),
                  "RMSE": round(rmse, 3), "MAE": round(mae, 3)})

    F1 = FS_KOMPOSISI + ["volume_A3", "densitas_final_gcm3"]
    r2, rmse, mae = nested_cv_svr_pca(d[F1].values, d["Eform_eV_atom"].values, grp, GRID_SVR, n_pca=0)
    tabel.append({"fitur": "F1 + volume + densitas (screening lama)", "target": "Eform",
                  "R2": round(r2, 3), "RMSE": round(rmse, 3), "MAE": round(mae, 3)})

    d2 = d.dropna(subset=FITUR_Q + FITUR_CN).reset_index(drop=True)
    grp2 = d2["komposisi_reduksi"].values
    F2 = FS_KOMPOSISI + FITUR_Q + FITUR_CN
    r2, rmse, mae = nested_cv_svr_pca(d2[F2].values, d2["Eform_eV_atom"].values, grp2, GRID_SVR, n_pca=0)
    tabel.append({"fitur": f"F2 + Q^n + CN Ca (n={len(d2)})", "target": "Eform",
                  "R2": round(r2, 3), "RMSE": round(rmse, 3), "MAE": round(mae, 3)})

    # F3 = F2 + SOAP-PCA
    if soap is not None:
        idx_map = dict(zip(keys, range(len(keys))))
        ik = [idx_map.get(f"{r['sumber']}|{r['id']}") for _, r in d2.iterrows()]
        ada = [i is not None for i in ik]
        d3 = d2[ada].reset_index(drop=True)
        ik = [idx_map[f"{r['sumber']}|{r['id']}"] for _, r in d3.iterrows()]
        Xs = np.hstack([d3[F2].values, soap[ik]])
        r2, rmse, mae = nested_cv_svr_pca(Xs, d3["Eform_eV_atom"].values,
                                          d3["komposisi_reduksi"].values, GRID_SVR, n_pca=N_PCA)
        tabel.append({"fitur": f"F3 + SOAP-PCA({N_PCA}) (n={len(d3)})", "target": "Eform",
                      "R2": round(r2, 3), "RMSE": round(rmse, 3), "MAE": round(mae, 3)})

    # Densitas MP+AFLOW (RF untuned, protokol sama dengan model densitas utama)
    dd = g[g["sumber"].isin(["MaterialsProject", "AFLOW"])].dropna(
        subset=FS_KOMPOSISI + ["densitas_final_gcm3"]).reset_index(drop=True)
    grpd = dd["komposisi_reduksi"].values
    r2, rmse, mae = cv_group_rf(dd[FS_KOMPOSISI].values, dd["densitas_final_gcm3"].values, grpd)
    tabel.append({"fitur": f"F0 komposisi (n={len(dd)})", "target": "Densitas",
                  "R2": round(r2, 3), "RMSE": round(rmse, 3), "MAE": round(mae, 3)})
    dd2 = dd.dropna(subset=FITUR_Q + FITUR_CN).reset_index(drop=True)
    r2, rmse, mae = cv_group_rf(dd2[FS_KOMPOSISI + FITUR_Q + FITUR_CN].values,
                                dd2["densitas_final_gcm3"].values,
                                dd2["komposisi_reduksi"].values)
    tabel.append({"fitur": f"F2 + Q^n + CN Ca (n={len(dd2)})", "target": "Densitas",
                  "R2": round(r2, 3), "RMSE": round(rmse, 3), "MAE": round(mae, 3)})

    t = pd.DataFrame(tabel)
    t.to_csv(PROC / "hasil_model_struktur.csv", index=False)
    ringkas = {"tanggal": time.strftime("%Y-%m-%d %H:%M:%S"),
               "n_eform": int(len(d)), "n_densitas": int(len(dd)),
               "n_eform_fitur_struktur": int(len(d2)), "n_pca": N_PCA,
               "hasil": t.to_dict("records"),
               "catatan": "label DFT saja; PCA/scaler dalam fold; struktur dikenal -> screening bukan discovery"}
    (PROC / "model_struktur_ringkasan.json").write_text(json.dumps(ringkas, indent=2, ensure_ascii=False), encoding="utf-8")
    laporan.append(t.to_markdown(index=False))
    laporan.append(f"\n- Gain R2 Eform F2 vs F0 = {t.iloc[2]['R2'] - t.iloc[0]['R2']:+.3f} "
                   f"(dibandingkan F1 vs F0 = {t.iloc[1]['R2'] - t.iloc[0]['R2']:+.3f})")
    (REPORTS / "laporan_model_struktur.md").write_text("\n".join(laporan), encoding="utf-8")
    print("\n".join(laporan).encode("ascii", "replace").decode("ascii"))


if __name__ == "__main__":
    main()
