"""Hitung konstanta elastik DFT dari output VPS (data/dft/vps_hasil/<tag>/strain_out/).

Dijalankan SETELAH produksi VPS selesai (run.log: 4 material "12/12 strain +
referensi OK"). Format hasil identik dengan jalankan_dft.py
(data/validasi_dft/<tag>_elastik.json); hasil_dft.json digabung dengan entri
top26_Ca3(PO4)2 yang sudah ada — tidak ditimpa.

Pemakaian:
  python scripts/hitung_elastik_vps.py
"""
import json
from pathlib import Path

import numpy as np

from common import ROOT
from validasi_mlff import vrh

HASIL_VPS = ROOT / "data" / "dft" / "vps_hasil"
OUT = ROOT / "data" / "validasi_dft"
AMP = 0.01
RY_BOHR3_KE_GPA = 14710.5  # 1 Ry/bohr^3
TAGS = ["top1_Ca5P3O12F", "top2_Ca10P6O25", "top5_Ca10P6CO27", "top6_Ca5P3HO13"]
# tegangan referensi (tanpa regangan) wajib kecil — konsistensi titik setimbang
BATAS_SIGMA_REF_GPA = 0.5


def baca_stress(tag, nama):
    """Tensor tegangan 6 komponen Voigt (GPa) dari <nama>.out."""
    f = HASIL_VPS / tag / "strain_out" / f"{nama}.out"
    t = f.read_text(encoding="utf-8", errors="replace")
    assert "total   stress" in t, f"{f}: blok total stress tidak ditemukan"
    blok = t.split("total   stress")[1].splitlines()[1:4]
    s = np.array([[float(x) for x in g.split()[:3]] for g in blok]) * RY_BOHR3_KE_GPA
    return np.array([s[0, 0], s[1, 1], s[2, 2], s[1, 2], s[0, 2], s[0, 1]])


def elastik(tag):
    c = np.zeros((6, 6))
    for i in range(6):
        sp = baca_stress(tag, f"scf_elastik_{i + 1}+.in")
        sm = baca_stress(tag, f"scf_elastik_{i + 1}-.in")
        # konvensi QE: tegangan positif = kompresi -> C = (sigma(-eps) - sigma(+eps)) / 2eps
        c[:, i] = (sm - sp) / (2 * AMP)
    c = (c + c.T) / 2
    # QA fisis
    assert np.allclose(c, c.T), "tensor tidak simetris"
    assert np.all(np.diag(c) > 0), "C_ii tidak positif (hasil tak fisis)"
    s0 = baca_stress(tag, "scf_referensi.in")
    maks = float(np.max(np.abs(s0)))
    assert maks < BATAS_SIGMA_REF_GPA, (
        f"tegangan referensi {maks:.2f} GPa > {BATAS_SIGMA_REF_GPA} GPa — "
        f"titik setimbang tidak konsisten")
    return c, vrh(c)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    agregat = OUT / "hasil_dft.json"
    # pertahankan entri yang sudah ada (top26) — jangan ditimpa
    if agregat.exists():
        hasil = json.loads(agregat.read_text(encoding="utf-8"))
    else:
        hasil = {}
    for tag in TAGS:
        try:
            c, (k, g, e, nu) = elastik(tag)
        except (AssertionError, FileNotFoundError) as ex:
            print(f"{tag}: GAGAL — {ex}")
            continue
        rec = {"tag": tag, "C_ij": np.round(c, 2).tolist(), "K_GPa": round(k, 1),
               "G_GPa": round(g, 1), "E_GPa": round(e, 1), "nu": round(nu, 3)}
        (OUT / f"{tag}_elastik.json").write_text(
            json.dumps(rec, indent=2), encoding="utf-8")
        hasil[tag] = rec
        print(f"{tag}: K={k:.1f} G={g:.1f} E={e:.1f} nu={nu:.3f} GPa")
    agregat.write_text(json.dumps(hasil, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"agregat: {agregat}")


if __name__ == "__main__":
    main()
