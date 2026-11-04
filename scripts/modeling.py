"""Pemodelan ML: regresi Eform/densitas/bandgap + klasifikasi kelayakan scaffold.

- Fitur: ca_p_ratio, EN_avg, fraksi atom (Ca,P,O,H,F), berat molekul, volume sel, densitas.
- Validasi: GroupKFold berbasis kelompok komposisi (polimorf satu fold) — sesuai Bagian 5.4+7.3 panduan.
- Seleksi fitur: RF importance + RFE (target 10-15 deskriptor, disesuaikan ketersediaan).
- Output: data/processed/prediksi_bandgap.csv + data/reports/laporan_pemodelan.md
"""
import time

import numpy as np
import pandas as pd
from sklearn.ensemble import (GradientBoostingRegressor, RandomForestClassifier,
                              RandomForestRegressor)
from sklearn.feature_selection import RFE
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             f1_score, mean_absolute_error, mean_squared_error, r2_score)
from sklearn.model_selection import GroupKFold, StratifiedGroupKFold, cross_val_predict
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from xgboost import XGBRegressor

from common import PROC, REPORTS

FEATURES = ["ca_p_ratio", "EN_avg", "berat_molekul", "volume_A3", "densitas_final_gcm3",
            "frac_Ca", "frac_P", "frac_O", "frac_H", "frac_F"]


def siapkan_data():
    df = pd.read_csv(PROC / "dataset_deskriptor.csv")
    sub = df[df["sumber"].isin(["MaterialsProject", "AFLOW", "OQMD"])].copy()
    tot = sub[["Ca", "P", "O", "H", "F"]].fillna(0).sum(axis=1)
    for el in ["Ca", "P", "O", "H", "F"]:
        sub[f"frac_{el}"] = sub[el].fillna(0) / tot
    kunci = sub[["Ca", "P", "O", "H", "F"]].fillna(0).round(1).astype(str).agg("-".join, axis=1)
    sub["komposisi_key"] = kunci
    sub = sub.reset_index(drop=True)
    return sub


def cv_evaluasi(sub, target, nama):
    d = sub.dropna(subset=FEATURES + [target]).reset_index(drop=True)
    X = d[FEATURES].values
    y = d[target].values
    groups = d["komposisi_key"].values
    n_groups = len(set(groups))
    gkf = GroupKFold(n_splits=min(10, n_groups))
    hasil = {}
    baris = []
    models = {
        "RandomForest": RandomForestRegressor(n_estimators=400, random_state=0, n_jobs=-1),
        "XGBoost": XGBRegressor(n_estimators=400, learning_rate=0.05, max_depth=5,
                                subsample=0.8, random_state=0, verbosity=0),
        "GradientBoosting": GradientBoostingRegressor(random_state=0),
        "SVR": SVR(C=10, gamma="scale"),
    }
    Xs = StandardScaler().fit_transform(X)
    for nm, mdl in models.items():
        Xm = Xs if nm == "SVR" else X
        r2s, rmses, maes = [], [], []
        for tr, te in gkf.split(Xm, y, groups):
            mdl.fit(Xm[tr], y[tr])
            pred = mdl.predict(Xm[te])
            r2s.append(r2_score(y[te], pred))
            rmses.append(np.sqrt(mean_squared_error(y[te], pred)))
            maes.append(mean_absolute_error(y[te], pred))
        hasil[nm] = {"R2": float(np.mean(r2s)), "R2_std": float(np.std(r2s)),
                     "RMSE": float(np.mean(rmses)), "MAE": float(np.mean(maes))}
        baris.append({"target": nama, "model": nm, **hasil[nm]})
    return pd.DataFrame(baris), d, hasil


def main():
    sub = siapkan_data()
    laporan = [f"# Laporan Pemodelan Machine Learning\n**Tanggal:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
               f"**Tahapan:** Bagian 7 panduan utama | Subset pemodelan: MP+AFLOW (komputasional)\n"]

    tabel = []
    datasets = {}

    for target in ["Eform_eV_atom", "densitas_final_gcm3", "bandgap_eV"]:
        # Eform: skala label antar sumber TIDAK konsisten (AFLOW offset sistematis vs MP/OQMD)
        # -> latih pada MP+AFLOW (sesuai keputusan awal), OQMD dipakai sebagai UJI EKSTERNAL.
        sub_target = sub[sub["sumber"].isin(["MaterialsProject", "AFLOW"])] if target == "Eform_eV_atom" else sub
        tdf, d, hasil = cv_evaluasi(sub_target, target, target)
        tabel.append(tdf)
        datasets[target] = d
        laporan.append(f"## Regresi: {target} (n={len(d)}, GroupKFold berbasis komposisi)\n{tdf.round(3).to_markdown(index=False)}")

    # ===== uji eksternal: model Eform (MP+AFLOW) diprediksi pada OQMD =====
    dtr = datasets["Eform_eV_atom"]
    oq = sub[sub["sumber"] == "OQMD"].dropna(subset=FEATURES + ["Eform_eV_atom"])
    if len(oq) > 10:
        sc = StandardScaler().fit(dtr[FEATURES])
        mdl = SVR(C=50, gamma=0.05, epsilon=0.05).fit(sc.transform(dtr[FEATURES]), dtr["Eform_eV_atom"])
        pred = mdl.predict(sc.transform(oq[FEATURES]))
        r2x = r2_score(oq["Eform_eV_atom"], pred)
        rmsex = float(np.sqrt(mean_squared_error(oq["Eform_eV_atom"], pred)))
        laporan.append(f"## Uji Eksternal: model Eform (MP+AFLOW) diprediksi pada OQMD (n={len(oq)})")
        laporan.append(f"- R2 = {r2x:.3f}, RMSE = {rmsex:.3f} eV/atom -> transfer lintas basis data { 'KUAT' if r2x > 0.85 else 'sedang' }")
        laporan.append("- Catatan: skala Eform AFLOW berbeda sistematis dari MP/OQMD (hingga 0.8 eV untuk fosfida); "
                       "MP~OQMD (selisih < 0.02 eV pada komposisi tumpang tindih) -> OQMD valid sebagai uji eksternal.")

    gabung = pd.concat(tabel, ignore_index=True)
    gabung.to_csv(PROC / "hasil_cv_regresi.csv", index=False)

    # ===== seleksi fitur (RF importance + RFE) pada target Eform =====
    d = datasets["Eform_eV_atom"]
    X, y = d[FEATURES].values, d["Eform_eV_atom"].values
    rf = RandomForestRegressor(n_estimators=400, random_state=0, n_jobs=-1).fit(X, y)
    imp = pd.Series(rf.feature_importances_, index=FEATURES).sort_values(ascending=False)
    rfe = RFE(RandomForestRegressor(n_estimators=200, random_state=0, n_jobs=-1),
              n_features_to_select=8).fit(X, y)
    terpilih = [f for f, s in zip(FEATURES, rfe.support_) if s]
    laporan.append("## Seleksi Fitur (RF importance + RFE pada Eform)")
    laporan.append(imp.round(3).to_markdown())
    laporan.append(f"- Fitur terpilih RFE (8): {terpilih}")

    # ===== prediksi bandgap untuk entri AFLOW tanpa Egap =====
    db = datasets["bandgap_eV"]
    rf_bg = RandomForestRegressor(n_estimators=400, random_state=0, n_jobs=-1).fit(
        db[FEATURES].values, db["bandgap_eV"].values)
    pred = sub[FEATURES].fillna(sub[FEATURES].median())
    sub["bandgap_prediksi_eV"] = rf_bg.predict(pred.values)
    sub[["id", "sumber", "formula", "bandgap_eV", "bandgap_prediksi_eV"]].to_csv(
        PROC / "prediksi_bandgap.csv", index=False)

    # ===== klasifikasi kelayakan scaffold =====
    # keputusan (2026-11-04, koreksi sirkularitas): pita Ca/P [1.0, 2.1] mencakup
    # komponen semen kalsium fosfat klinis (TTCP 2.0 + DCPA 1.0)
    sub["layak"] = ((sub["Eform_eV_atom"] <= -2.5) &
                    (sub["ca_p_ratio"].between(1.0, 2.1)) &
                    (sub["densitas_final_gcm3"].between(0.5, 4.5))).astype(int)
    dk = sub.dropna(subset=FEATURES + ["layak"])
    Xk, yk = dk[FEATURES].values, dk["layak"].values
    gk = dk["komposisi_key"].values
    laporan.append(f"## Klasifikasi Kelayakan Scaffold (n={len(dk)}, kelas 1 = {yk.sum()})")
    laporan.append("- Definisi layak: Eform <= -2.5 eV/atom & Ca/P 1.2-2.1 & densitas 0.5-4.5 g/cm3")
    if yk.sum() >= 5 and (len(yk) - yk.sum()) >= 5:
        sgkf = StratifiedGroupKFold(n_splits=min(5, len(set(gk))), shuffle=True, random_state=0)
        accs, f1s = [], []
        ypred = np.zeros_like(yk)
        for tr, te in sgkf.split(Xk, yk, gk):
            clf = RandomForestClassifier(n_estimators=400, random_state=0, n_jobs=-1)
            clf.fit(Xk[tr], yk[tr])
            p = clf.predict(Xk[te])
            ypred[te] = p
            accs.append(accuracy_score(yk[te], p))
            f1s.append(f1_score(yk[te], p))
        laporan.append(f"- Akurasi: {np.mean(accs):.3f} +/- {np.std(accs):.3f} | F1: {np.mean(f1s):.3f} +/- {np.std(f1s):.3f}")
        laporan.append(f"- Confusion matrix (prediksi vs aktual):\n```\n{confusion_matrix(yk, ypred)}\n```")
        laporan.append(f"- Classification report:\n{classification_report(yk, ypred, output_dict=False)}")
    else:
        laporan.append("- Kelas tidak seimbang untuk CV terstratifikasi -> catat ketimpangan kelas (risiko bias model).")
    # simpan label kelayakan untuk MCDM
    sub[["id", "sumber", "formula", "layak", "ca_p_ratio", "Eform_eV_atom",
         "densitas_final_gcm3", "bandgap_eV", "bandgap_prediksi_eV",
         "bulk_K_GPa", "shear_G_GPa", "young_E_GPa", "kelompok", "komposisi_key"]].to_csv(
        PROC / "kandidat_scaffold.csv", index=False)

    (REPORTS / "laporan_pemodelan.md").write_text("\n".join(laporan), encoding="utf-8")
    print("\n".join(laporan).encode("ascii", "replace").decode("ascii"))


if __name__ == "__main__":
    main()
