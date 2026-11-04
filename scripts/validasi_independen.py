"""Benchmark VALIDASI INDEPENDEN: prediksi ML vs nilai eksperimen literatur.

Kritik yang diperbaiki: validasi sebelumnya membandingkan nilai DATABASE vs literatur
(= QC sumber data), bukan prediksi MODEL. Di sini prediksi SVR-Eform dan RF-densitas
(dilatih MP+AFLOW) diuji pada data eksperimen murni (entalpi pembentukan standar
Wagman/NBS; parameter kisi & densitas dari literatur kristalografi).

Fitur benchmark seluruhnya dari eksperimen: komposisi -> ca_p_ratio/EN_avg/MW/frac;
volume sel & densitas dari literatur.
"""
import time

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR

from common import PROC, REPORTS

FEATURES = ["ca_p_ratio", "EN_avg", "berat_molekul", "volume_A3", "densitas_final_gcm3",
            "frac_Ca", "frac_P", "frac_O", "frac_H", "frac_F"]

ELEM = {"H": (2.20, 1.008, 1), "O": (3.44, 15.999, 6), "F": (3.98, 18.998, 7),
        "P": (2.19, 30.974, 5), "Ca": (1.00, 40.078, 2)}

# Benchmark eksperimen: (nama, Ca, P, O, H, densitas_exp, volume_sel_A3, DHf kJ/mol)
# Sumber: Wagman et al. NBS Tables 1982; parameter kisi: ICDD PDF / literatur standar.
BENCH = [
    ("Hidroksiapatit Ca10(PO4)6(OH)2", 10, 6, 26, 2, 3.16, 528.8, -13409.0, 44),
    ("b-TCP Ca3(PO4)2",                3, 2, 8, 0, 3.07, 3527.0, -4121.0, 13),
    ("a-TCP Ca3(PO4)2",                3, 2, 8, 0, 2.86, 4320.0, -4125.0, 13),
    ("TTCP Ca4(PO4)2O",                4, 2, 9, 0, 3.05, 797.0, -4771.0, 15),
    ("DCPA (monetit) CaHPO4",          1, 1, 4, 1, 2.92, 316.0, -1814.0, 7),
    ("DCPD (brushit) CaHPO4.2H2O",     1, 1, 6, 5, 2.31, 492.0, -2154.0, 13),
]


def deskriptor_bench(ca, p, o, h, dens, vol):
    n = {"Ca": ca, "P": p, "O": o, "H": h}
    tot = sum(n.values())
    en = sum(ELEM[e][0] * c for e, c in n.items()) / tot
    mw = sum(ELEM[e][1] * c for e, c in n.items())
    return {"ca_p_ratio": ca / p, "EN_avg": en, "berat_molekul": mw,
            "volume_A3": vol, "densitas_final_gcm3": dens,
            "frac_Ca": ca / tot, "frac_P": p / tot, "frac_O": o / tot,
            "frac_H": h / tot, "frac_F": 0.0}


def main():
    df = pd.read_csv(PROC / "dataset_deskriptor.csv")
    tr = df[df["sumber"].isin(["MaterialsProject", "AFLOW"])].copy()
    tot = tr[["Ca", "P", "O", "H", "F"]].fillna(0).sum(axis=1)
    for el in ["Ca", "P", "O", "H", "F"]:
        tr[f"frac_{el}"] = tr[el].fillna(0) / tot
    tr = tr.dropna(subset=FEATURES + ["Eform_eV_atom", "densitas_final_gcm3"])

    # model final (sama dengan manuskrip)
    sc_e = StandardScaler().fit(tr[FEATURES])
    svr = SVR(C=50, gamma=0.05, epsilon=0.05).fit(sc_e.transform(tr[FEATURES]), tr["Eform_eV_atom"])
    rf_d = RandomForestRegressor(n_estimators=400, random_state=0, n_jobs=-1).fit(
        tr[FEATURES], tr["densitas_final_gcm3"])

    baris = []
    for nama, ca, p, o, h, dens, vol, dhf, natom in BENCH:
        f = deskriptor_bench(ca, p, o, h, dens, vol)
        X = pd.DataFrame([f])[FEATURES]
        e_pred = float(svr.predict(sc_e.transform(X))[0])
        d_pred = float(rf_d.predict(X)[0])
        e_exp = dhf / natom / 96.485  # kJ/mol -> eV/atom
        baris.append({"fase": nama, "Eform_exp_eV_atom": round(e_exp, 3),
                      "Eform_pred_eV_atom": round(e_pred, 3),
                      "selisih_eV_atom": round(e_pred - e_exp, 3),
                      "densitas_exp": dens, "densitas_pred": round(d_pred, 3),
                      "selisih_densitas": round(d_pred - dens, 3)})

    t = pd.DataFrame(baris)
    mae_e = (t["Eform_exp_eV_atom"] - t["Eform_pred_eV_atom"]).abs().mean()
    mae_d = (t["densitas_exp"] - t["densitas_pred"]).abs().mean()
    t.to_csv(PROC / "benchmark_eksperimen.csv", index=False)

    laporan = f"""# Laporan Validasi Independen: Prediksi ML vs Eksperimen

**Tanggal:** {time.strftime('%Y-%m-%d %H:%M:%S')}
**Konteks koreksi:** validasi sebelumnya membandingkan nilai database vs literatur (QC sumber data);
laporan ini menguji PREDIKSI MODEL (SVR Eform C=50 gamma=0.05; RF densitas) pada data eksperimen
murni yang TIDAK dipakai pelatihan (entalpi pembentukan standar Wagman/NBS; densitas literatur).

## Hasil

{t.round(3).to_markdown(index=False)}

- **MAE Eform = {mae_e:.3f} eV/atom** (dari nilai eksperimen) — bandingkan dengan RMSE CV 0.395.
- **MAE densitas = {mae_d:.3f} g/cm3** — bandingkan dengan RMSE CV 0.096.

## Interpretasi
- Prediksi Eform kini tervalidasi terhadap termokimia EKSPERIMEN (bukan database lain):
  {'KUAT (MAE <= 0.3 eV/atom)' if mae_e <= 0.3 else 'sedang (MAE > 0.3 eV/atom) — catat keterbatasan'}.
- Densitas eksperimen 6 fase Ca-P diprediksi dengan MAE {mae_d:.3f} g/cm3.

## Sumber
- Entalpi pembentukan: Wagman et al., NBS Tables of Chemical Thermodynamic Properties (1982);
  konsisten dengan kompilasi Dorozhkin (2012).
- Parameter kisi & densitas: kartu ICDD/PDF standar (HAp 09-432; b-TCP 09-169; a-TCP 09-348;
  TTCP 25-1137; monetit 09-0080; brushit 09-0077).
"""
    (REPORTS / "laporan_validasi_independen.md").write_text(laporan, encoding="utf-8")
    print(laporan.encode("ascii", "replace").decode("ascii"))


if __name__ == "__main__":
    main()
