"""Ekstraksi fitur struktural (ronde 7/Q1): spesiasi Q^n fosfat, koordinasi Ca, SOAP.

Sumber struktur:
- MP: fetch live via siapkan_dft.ambil_struktur_mp (cache ke data/raw/struktur/mp/<id>.json)
- AFLOW: CONTCAR.relax.vasp via siapkan_dft.ambil_poscar_aflow (cache POSCAR)
- COD: data/raw/cod/cif/<file>.cif (hasil acquire_cod_cif.py)

Fitur:
- Q^n (n=0..3): tiap P -> jumlah O tetangga (<=1.85 A) yang menjembatani >=2 P;
  agregasi fraksi q0..q3 + q_mean.
- CN Ca: CrystalNN (fallback cutoff 3.2 A hitung O) -> cn_Ca_mean, cn_Ca_std, fraksi CN 6/7/8/9.
- SOAP (dscribe): species tetap [Ca,P,O,H,F,C], rcut 5.0, nmax 4, lmax 4, periodic;
  disimpan NPZ (fitur_struktur.npz) + parameter dicatat di ringkasan.

Checkpoint JSONL per (sumber,id) -> resumable. Label jujur: fitur ini butuh struktur dikenal
-> hanya untuk varian screening, BUKAN discovery.
"""
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from common import PROC, RAW, REPORTS, ROOT

STRDIR = RAW / "struktur"
STRDIR.mkdir(parents=True, exist_ok=True)
CKPT = STRDIR / "fitur_checkpoint.jsonl"
SOAP_NPZ = PROC / "soap_fingerprint.npz"
SPESIES_SOAP = ["Ca", "P", "O", "H", "F", "C"]
RCUT, NMAX, LMAX = 5.0, 4, 4


def ke_struktur_pmg(atoms):
    from pymatgen.io.ase import AseAtomsAdaptor
    return AseAtomsAdaptor.get_structure(atoms)


def simbol(s):
    """Simbol unsur dominan situs — aman untuk situs disorder (pymatgen 2025: .specie hilang)."""
    try:
        return s.specie.symbol
    except AttributeError:
        return max(s.species.items(), key=lambda kv: kv[1])[0].symbol


def hitung_q(struktur):
    """Fraksi Q^0..Q^3 + q_mean dari struktur pymatgen (P-O <= 1.85 A)."""
    from pymatgen.core import Structure
    p_idx = [i for i, s in enumerate(struktur) if simbol(s) == "P"]
    if not p_idx:
        return {"q0_frac": np.nan, "q1_frac": np.nan, "q2_frac": np.nan, "q3_frac": np.nan, "q_mean": np.nan}
    all_nbrs = struktur.get_all_neighbors(1.85, include_index=True)
    # o_bridge: O yang bertetangga dengan >=2 P
    o_bridge = set()
    for i, nbrs in enumerate(all_nbrs):
        if simbol(struktur[i]) == "O":
            p_ikut = sum(1 for n in nbrs if simbol(n) == "P")
            if p_ikut >= 2:
                o_bridge.add(i)
    q = []
    for i in p_idx:
        o_terikat = [n for n in all_nbrs[i] if simbol(n) == "O"]
        jembatan = sum(1 for n in o_terikat if n.index in o_bridge)
        q.append(min(jembatan, 3))
    q = np.array(q)
    return {"q0_frac": float((q == 0).mean()), "q1_frac": float((q == 1).mean()),
            "q2_frac": float((q == 2).mean()), "q3_frac": float((q == 3).mean()),
            "q_mean": float(q.mean())}


def hitung_cn_ca(struktur):
    """CN Ca via CrystalNN (hanya tetangga O); fallback cutoff 3.2 A."""
    ca_idx = [i for i, s in enumerate(struktur) if simbol(s) == "Ca"]
    if not ca_idx:
        return {"cn_Ca_mean": np.nan, "cn_Ca_std": np.nan,
                "cn6_frac": np.nan, "cn7_frac": np.nan, "cn8_frac": np.nan, "cn9_frac": np.nan}
    try:
        from pymatgen.analysis.local_env import CrystalNN
        cnn = CrystalNN(distance_cutoffs=None, x_diff_weight=3.0, porous_adjustment=False)
        cn = []
        for i in ca_idx:
            try:
                cn.append(sum(1 for n in cnn.get_nn_info(struktur, i)
                              if simbol(n["site"]) == "O"))
            except Exception:
                cn.append(np.nan)
        cn = np.array([c for c in cn if c == c], dtype=float)
    except Exception:
        cn = np.array([])
    if len(cn) < 3:  # CrystalNN gagal -> fallback cutoff
        all_nbrs = struktur.get_all_neighbors(3.2, include_index=False)
        cn = np.array([sum(1 for n in all_nbrs[i] if simbol(n) == "O") for i in ca_idx])
    return {"cn_Ca_mean": float(cn.mean()), "cn_Ca_std": float(cn.std()),
            "cn6_frac": float((cn == 6).mean()), "cn7_frac": float((cn == 7).mean()),
            "cn8_frac": float((cn == 8).mean()), "cn9_frac": float((cn == 9).mean())}


def hitung_soap(struktur):
    """Vektor SOAP (n_species^2 * nmax^2 * (lmax+1) = 36*16*5 = 2880).

    dscribe 2.x membutuhkan ASE Atoms — pymatgen Structure dikonversi dulu.
    """
    from dscribe.descriptors import SOAP
    from pymatgen.io.ase import AseAtomsAdaptor
    if not set(struktur.symbol_set) <= set(SPESIES_SOAP):
        raise ValueError(f"unsur di luar set SOAP {SPESIES_SOAP}: {struktur.symbol_set}")
    atoms = AseAtomsAdaptor.get_atoms(struktur)
    soap = SOAP(species=SPESIES_SOAP, periodic=True, r_cut=RCUT, n_max=NMAX, l_max=LMAX, sparse=False)
    v = soap.create(atoms)
    return np.asarray(v, dtype=np.float64)


def ambil_struktur(sumber, rid, meta):
    """Kembalikan pymatgen Structure atau None + alasan."""
    from pymatgen.core import Structure
    if sumber == "COD":
        f = rid
        path = RAW / "cod" / "cif" / f"{f}.cif"
        if not path.exists():
            return None, "cif_tidak_ada"
        try:
            from pymatgen.io.cif import CifParser
            return CifParser(str(path)).parse_structures(primitive=False)[0], None
        except Exception as e:
            try:
                from ase.io import read
                return ke_struktur_pmg(read(str(path))), "parser_ase"
            except Exception as e2:
                return None, f"parse_gagal_{type(e).__name__}"
    if sumber == "MaterialsProject":
        cache = STRDIR / "mp" / f"{rid}.json"
        if cache.exists():
            return Structure.from_dict(json.loads(cache.read_text(encoding="utf-8"))), None
        from siapkan_dft import ambil_struktur_mp
        d = ambil_struktur_mp(rid)
        if not d:
            return None, "api_gagal"
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(d["structure"], ensure_ascii=False), encoding="utf-8")
        return Structure.from_dict(d["structure"]), None
    if sumber == "AFLOW":
        cache = STRDIR / "aflow" / f"{rid}.vasp"
        if cache.exists():
            poscar = cache.read_text(encoding="utf-8")
        else:
            from siapkan_dft import ambil_poscar_aflow
            poscar = ambil_poscar_aflow(meta.get("aurl", ""))
            if not poscar:
                return None, "aflow_unduh_gagal"
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text(poscar, encoding="utf-8")
        st = parse_aflow_concar(poscar)
        if st is None:
            return None, "aflow_parse_gagal"
        return st, None
    return None, f"sumber_tak_dikenal_{sumber}"


def parse_aflow_concar(teks):
    """Parser CONTCAR.relax.vasp AFLOW: simbol unsur di ujung baris koordinat.

    Format AFLOW: baris 2 = skala; 3-5 = vektor kisi; 6 = jumlah per jenis;
    7 = 'Direct(5) [A3B2]'; lalu baris atom 'x y z Simbol'. Tidak kompatibel ASE.
    """
    from pymatgen.core import Structure, Lattice
    garis = [g for g in teks.splitlines() if g.strip()]
    if len(garis) < 9:
        return None
    try:
        skala = float(garis[1].split()[0])
        lat = np.array([[float(x) for x in garis[i].split()[:3]] for i in range(2, 5)]) * skala
        jumlah = [int(x) for x in garis[5].split()]
        atom = []
        for g in garis[8:8 + sum(jumlah)]:
            p = g.split()
            atom.append((p[-1], float(p[0]), float(p[1]), float(p[2])))
        species, coords = [a[0] for a in atom], [[a[1], a[2], a[3]] for a in atom]
        return Structure(Lattice(lat), species, coords, coords_are_cartesian=False)
    except Exception:
        return None


def main():
    df = pd.read_csv(PROC / "dataset_deskriptor.csv")
    # struktur tersedia: MP (57), AFLOW (234), COD (938 unik) — OQMD/PubChem tanpa struktur
    sub = df[df["sumber"].isin(["MaterialsProject", "AFLOW", "COD"])].copy()
    if "aurl" not in sub.columns:
        sub["aurl"] = None
    aflow_meta = pd.read_csv(RAW / "aflow" / "aflow_cap.csv", dtype=str)
    aurl_map = dict(zip(aflow_meta["auid"].astype(str), aflow_meta["aurl"].astype(str))) \
        if {"auid", "aurl"} <= set(aflow_meta.columns) else {}

    selesai = {}
    if CKPT.exists():
        for line in CKPT.read_text(encoding="utf-8").splitlines():
            if line.strip():
                d = json.loads(line)
                selesai[(d["sumber"], d["id"])] = d

    baris, vektor, keys = [], [], []
    n_ok = n_skip = 0
    total = len(sub)
    for i, (_, r) in enumerate(sub.iterrows(), 1):
        key = (r["sumber"], str(r["id"]))
        if key in selesai:
            continue
        struktur, alasan = ambil_struktur(r["sumber"], str(r["id"]),
                                          {"aurl": aurl_map.get(str(r["id"]), "")})
        if struktur is None:
            d = {"sumber": r["sumber"], "id": str(r["id"]), "status": "skip", "alasan": alasan}
            n_skip += 1
        else:
            try:
                q = hitung_q(struktur)
                cn = hitung_cn_ca(struktur)
                soap = hitung_soap(struktur)
                d = {"sumber": r["sumber"], "id": str(r["id"]), "status": "ok",
                     "formula": str(r["formula"]), "natom": int(len(struktur)),
                     **q, **cn, "alasan": alasan}
                vektor.append(soap)
                keys.append(f"{r['sumber']}|{r['id']}")
                n_ok += 1
            except Exception as e:
                d = {"sumber": r["sumber"], "id": str(r["id"]), "status": "skip",
                     "alasan": f"fitur_gagal_{type(e).__name__}"}
                n_skip += 1
        with CKPT.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(d, ensure_ascii=False) + "\n")
        selesai[key] = d
        if i % 50 == 0 or i == total:
            print(f"{i}/{total}  ok={n_ok} skip={n_skip}", flush=True)
            if vektor:
                np.savez(SOAP_NPZ, X=np.vstack(vektor), keys=np.array(keys, dtype=object))

    # simpan final
    if vektor:
        np.savez(SOAP_NPZ, X=np.vstack(vektor), keys=np.array(keys, dtype=object))
    df_fit = pd.DataFrame([d for d in selesai.values()])
    df_fit.to_csv(PROC / "fitur_struktur.csv", index=False)
    ringkas = {
        "n_total": total, "n_ok": n_ok, "n_skip": n_skip,
        "soap_dimensi": [len(SPESIES_SOAP) ** 2 * NMAX ** 2 * (LMAX + 1)],
        "soap_param": {"species": SPESIES_SOAP, "r_cut": RCUT, "n_max": NMAX, "l_max": LMAX},
        "catatan": "fitur struktural membutuhkan struktur dikenal -> varian screening, bukan discovery",
        "tanggal": time.strftime("%Y-%m-%d %H:%M:%S"),
        "alasan_skip": df_fit[df_fit["status"] == "skip"]["alasan"].value_counts().to_dict() if len(df_fit) else {},
    }
    (PROC / "fitur_struktur_ringkasan.json").write_text(json.dumps(ringkas, indent=2, ensure_ascii=False), encoding="utf-8")
    print("ringkasan:", json.dumps(ringkas, indent=1)[:600])
    print(f"SELESAI: ok={n_ok} skip={n_skip}")


if __name__ == "__main__":
    main()
