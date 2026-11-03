"""Tutup gap #2: tuning hyperparameter agar R2 Eform >= 0.85 (GroupKFold komposisi)."""
import time

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold, ParameterGrid
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR

from common import PROC, REPORTS

FEATURES = ["ca_p_ratio", "EN_avg", "berat_molekul", "volume_A3", "densitas_final_gcm3",
            "frac_Ca", "frac_P", "frac_O", "frac_H", "frac_F"]


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


def main():
    df = pd.read_csv(PROC / "dataset_deskriptor.csv")
    sub = df[df["sumber"].isin(["MaterialsProject", "AFLOW", "OQMD"])].copy()
    tot = sub[["Ca", "P", "O", "H", "F"]].fillna(0).sum(axis=1)
    for el in ["Ca", "P", "O", "H", "F"]:
        sub[f"frac_{el}"] = sub[el].fillna(0) / tot
    kunci = sub[["Ca", "P", "O", "H", "F"]].fillna(0).round(1).astype(str).agg("-".join, axis=1)
    d = sub.dropna(subset=FEATURES + ["Eform_eV_atom"]).reset_index(drop=True)
    X, y = d[FEATURES].values, d["Eform_eV_atom"].values
    groups = kunci.loc[d.index].values
    print(f"n = {len(d)} (MP+AFLOW+OQMD), grup komposisi = {len(set(groups))}")

    hasil = []
    # SVR grid
    grid_svr = ParameterGrid({
        "C": [1, 10, 50, 100, 500],
        "gamma": ["scale", 0.01, 0.05, 0.1],
        "epsilon": [0.05, 0.1, 0.2],
    })
    for p in grid_svr:
        r2, rmse, mae = cv_group(X, y, groups, SVR(**p), scaler=True)
        hasil.append(("SVR", str(p), r2, rmse, mae))
    # RF grid
    grid_rf = ParameterGrid({
        "n_estimators": [400, 800],
        "max_depth": [None, 8, 12],
        "min_samples_leaf": [1, 2],
    })
    for p in grid_rf:
        r2, rmse, mae = cv_group(X, y, groups, RandomForestRegressor(
            random_state=0, n_jobs=-1, **p))
        hasil.append(("RF", str(p), r2, rmse, mae))

    t = pd.DataFrame(hasil, columns=["model", "param", "R2", "RMSE", "MAE"])
    t = t.sort_values("R2", ascending=False).reset_index(drop=True)
    t.to_csv(PROC / "hasil_tuning_eform.csv", index=False)
    terbaik = t.iloc[0]
    capai = terbaik["R2"] >= 0.85
    laporan = f"""# Laporan Tuning Eform (gap #2: target R2 >= 0.85)
**Tanggal:** {time.strftime('%Y-%m-%d %H:%M:%S')} | n = {len(d)} | GroupKFold(10) berbasis komposisi

## Terbaik
- {terbaik['model']} {terbaik['param']}: **R2 = {terbaik['R2']:.3f}** (RMSE {terbaik['RMSE']:.3f}, MAE {terbaik['MAE']:.3f})
- Target R2 >= 0.85: **{'TERCAPAI' if capai else 'BELUM — selisih ' + str(round(0.85 - terbaik['R2'], 3))}**

## 5 Teratas
{t.head(5).round(4).to_markdown(index=False)}
"""
    (REPORTS / "laporan_tuning_eform.md").write_text(laporan, encoding="utf-8")
    print(laporan.encode("ascii", "replace").decode("ascii"))


if __name__ == "__main__":
    main()
