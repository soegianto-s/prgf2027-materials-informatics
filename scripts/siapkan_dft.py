"""Siapkan input DFT/Quantum ESPRESSO untuk Top 5 kandidat.

Struktur diunduh dari Materials Project API (fallback: POSCAR statis AFLOWLIB).
Keluaran per kandidat: POSCAR (VASP), struktur.cif, scf.in, relax.in, README_DFT.md
"""
import math
import time
from pathlib import Path

import pandas as pd
import requests

from common import PROC, ROOT, mp_key, save_json

DFT = ROOT / "data" / "dft"
KEY = mp_key()
HDR = {"x-api-key": KEY}

# PSL 1.0.0 PBE (pseudo-dojo.org)
PSEUDO = {
    "Ca": "Ca.pbe-spn-kjpaw_psl.1.0.0.UPF",
    "P": "P.pbe-n-rrkjus_psl.1.0.0.UPF",
    "O": "O.pbe-n-rrkjus_psl.1.0.0.UPF",
    "H": "H.pbe-rrkjus_psl.1.0.0.UPF",
    "F": "F.pbe-n-rrkjus_psl.1.0.0.UPF",
    "C": "C.pbe-n-rrkjus_psl.1.0.0.UPF",
}


def reduksi(baris):
    """Kunci komposisi ternormalisasi (gcd) dari komposisi_key/komposisi_reduksi 'Ca-P-O-H-F'."""
    key = baris.get("komposisi_key", "")
    if not key or str(key) == "nan":
        key = baris.get("komposisi_reduksi", "")
    try:
        vals = [int(round(float(x))) for x in str(key).split("-")]
    except Exception:
        return "0-0-0-0-0"
    if len(vals) < 5 or sum(vals) == 0:
        return "0-0-0-0-0"
    v = vals[:5]
    g = 0
    for x in v:
        g = math.gcd(g, x)
    return "-".join(str(x // g) for x in v)


def ambil_struktur_mp(material_id):
    r = requests.get(
        "https://api.materialsproject.org/materials/summary/",
        params={"material_ids": material_id,
                "_fields": "material_id,formula_pretty,structure"},
        headers=HDR, timeout=120)
    if r.status_code != 200:
        return None
    d = r.json().get("data", [])
    return d[0] if d else None


def ambil_poscar_aflow(aurl):
    """aurl: 'aflowlib.duke.edu:AFLOWDATA/LIB2_WEB/Ca_svP/259' -> POSCAR statis."""
    if not aurl or ":" not in str(aurl):
        return None
    host, path = str(aurl).split(":", 1)
    url = f"https://{host}/{path}/CONTCAR.relax.vasp"
    try:
        rr = requests.get(url, timeout=90)
        return rr.text if rr.status_code == 200 else None
    except Exception:
        return None


def matriks_to_lattice(m):
    a = math.sqrt(sum(x * x for x in m[0]))
    b = math.sqrt(sum(x * x for x in m[1]))
    c = math.sqrt(sum(x * x for x in m[2]))
    dot = lambda u, v: sum(x * y for x, y in zip(u, v))
    al = math.degrees(math.acos(max(-1, min(1, dot(m[1], m[2]) / (b * c)))))
    be = math.degrees(math.acos(max(-1, min(1, dot(m[0], m[2]) / (a * c)))))
    ga = math.degrees(math.acos(max(-1, min(1, dot(m[0], m[1]) / (a * b)))))
    return a, b, c, al, be, ga


def tulis_input(nama_dir, formula, struktur):
    d = DFT / nama_dir
    d.mkdir(parents=True, exist_ok=True)
    lat = struktur["lattice"]["matrix"]
    situs = struktur["sites"]
    spesies = sorted({s["species"][0]["element"] for s in situs})
    a, b, c, al, be, ga = matriks_to_lattice(lat)

    # POSCAR
    elemen = []
    hitung = {}
    for s in situs:
        el = s["species"][0]["element"]
        hitung[el] = hitung.get(el, 0) + 1
    for el in spesies:
        elemen.append(el)
    pos = []
    for el in spesies:
        for s in situs:
            if s["species"][0]["element"] == el:
                xyz = s["abc"]
                pos.append(f"  {xyz[0]:.9f}  {xyz[1]:.9f}  {xyz[2]:.9f}")
    baris_poscar = [formula, "1.0"]
    baris_poscar.append("\n".join(f"    {lat[i][0]:.10f}  {lat[i][1]:.10f}  {lat[i][2]:.10f}" for i in range(3)))
    baris_poscar.append("  ".join(elemen))
    baris_poscar.append("  ".join(str(hitung[e]) for e in elemen))
    baris_poscar.append("Direct")
    baris_poscar.extend(pos)
    (d / "POSCAR").write_text("\n".join(baris_poscar) + "\n", encoding="utf-8")

    # CIF
    cif = [f"data_{nama_dir}",
           "_chemical_formula_structural  '" + formula + "'",
           f"_cell_length_a  {a:.5f}", f"_cell_length_b  {b:.5f}", f"_cell_length_c  {c:.5f}",
           f"_cell_angle_alpha  {al:.4f}", f"_cell_angle_beta  {be:.4f}", f"_cell_angle_gamma  {ga:.4f}",
           "_symmetry_space_group_name_H-M  'P 1'", "_symmetry_Int_Tables_number  1",
           "loop_", "_atom_site_type_symbol", "_atom_site_fract_x", "_atom_site_fract_y",
           "_atom_site_fract_z"]
    for s in situs:
        el = s["species"][0]["element"]
        x, y, z = s["abc"]
        cif.append(f"  {el}  {x:.6f}  {y:.6f}  {z:.6f}")
    (d / "struktur.cif").write_text("\n".join(cif) + "\n", encoding="utf-8")

    # QE input
    nat = len(situs)
    ntyp = len(spesies)
    header = f"""&CONTROL
  calculation = 'scf'
  prefix = '{nama_dir}'
  pseudo_dir = './pseudo/'
  outdir = './out/'
  verbosity = 'high'
/
&SYSTEM
  ibrav = 0
  nat = {nat}
  ntyp = {ntyp}
  ecutwfc = 60.0
  ecutrho = 480.0
  occupations = 'smearing'
  smearing = 'gaussian'
  degauss = 0.01
/
&ELECTRONS
  conv_thr = 1.0d-8
  mixing_beta = 0.7
/
"""
    spesies_block = "\n".join(f" {e}  {MASS[e]}  {PSEUDO[e]}" for e in spesies)
    cell_block = "\n".join(f"  {lat[i][0]:.8f}  {lat[i][1]:.8f}  {lat[i][2]:.8f}" for i in range(3))
    atom_block = "\n".join(f" {s['species'][0]['element']}  {s['abc'][0]:.8f}  {s['abc'][1]:.8f}  {s['abc'][2]:.8f}" for s in situs)
    sk = "2 2 2 0 0 0"
    scf = f"""{header}ATOMIC_SPECIES
{spesies_block}
CELL_PARAMETERS angstrom
{cell_block}
ATOMIC_POSITIONS crystal
{atom_block}
K_POINTS automatic
{sk}
"""
    relax = scf.replace("calculation = 'scf'", "calculation = 'vc-relax'").replace(
        "conv_thr = 1.0d-8", "conv_thr = 1.0d-6")
    relax = relax.replace("/\n&ELECTRONS", "  press = 0.0\n  cell_dofree = 'all'\n/\n&CELL\n/\n&ELECTRONS", 1)
    (d / "scf.in").write_text(scf, encoding="utf-8")
    (d / "relax.in").write_text(relax, encoding="utf-8")

    readme = f"""# Validasi DFT — {formula} ({nama_dir})

Struktur: Materials Project (https://materialsproject.org), lisensi CC-BY 4.0.

## Pseudopotensial (wajib diunduh)
PSL 1.0.0 PBE dari http://pseudo-dojo.org -> folder `pseudo/`:
{chr(10).join('- ' + PSEUDO[e] for e in spesies)}

## Cara menjalankan (Quantum ESPRESSO >= 7.0)
    mpirun -np N pw.x -in scf.in > scf.out
    mpirun -np N pw.x -in relax.in > relax.out   # vc-relax: verifikasi stabilitas kisi

## Target verifikasi (dari kerangka MI)
- Stabilitas: energi pembentukan tetap negatif setelah relaksasi ({struktur.get('_Eform', 'lihat laporan')}).
- Densitas pasca-relaksasi dibandingkan dengan prediksi (lihat data/processed/kandidat_top15_dedup.csv).
- Bila tersedia ph.x: modulus elastik untuk validasi kriteria C4 MCDM.
"""
    (d / "README_DFT.md").write_text(readme, encoding="utf-8")
    return spesies


def main():
    rank = pd.read_csv(PROC / "kandidat_ranking.csv")
    for c in ["peringkat_rerata"]:
        rank[c] = pd.to_numeric(rank[c], errors="coerce")
    rank["kunci_reduksi"] = rank.apply(reduksi, axis=1)
    terbaik = rank.sort_values("peringkat_rerata").drop_duplicates(subset="kunci_reduksi")
    top5 = terbaik.head(5).copy()
    aflow = pd.read_csv(ROOT / "data" / "raw" / "aflow" / "aflow_cap.csv")

    hasil = []
    for i, r in top5.iterrows():
        tag = f"top{i + 1}_{r['formula']}"
        struktur = None
        if r["sumber"] == "MaterialsProject":
            struktur = ambil_struktur_mp(r["id"])
            # prefer struktur MP terkecil dengan komposisi sama (hemat komputasi MLFF/DFT;
            # sel kecil/primitif setara secara fisika untuk validasi elastik)
            mp_sama = rank[(rank["sumber"] == "MaterialsProject")
                           & (rank["kunci_reduksi"] == r["kunci_reduksi"])]
            n_min = len(struktur["structure"]["sites"]) if struktur else None
            for _, m in mp_sama.iterrows():
                if m["id"] == r["id"]:
                    continue
                alt = ambil_struktur_mp(m["id"])
                if alt is not None and (n_min is None or len(alt["structure"]["sites"]) < n_min):
                    struktur, n_min = alt, len(alt["structure"]["sites"])
        if struktur is None:
            # cari struktur MP dengan komposisi ternormalisasi sama
            mp_sama = rank[(rank["sumber"] == "MaterialsProject")
                           & (rank["kunci_reduksi"] == r["kunci_reduksi"])]
            if len(mp_sama):
                struktur = ambil_struktur_mp(mp_sama.iloc[0]["id"])
        if struktur is None and r["sumber"] == "AFLOW":
            baris_af = aflow[aflow["compound"] == r["formula"]]
            poscar = ambil_poscar_aflow(baris_af.iloc[0]["aurl"]) if len(baris_af) else None
            if poscar:
                d = DFT / tag
                d.mkdir(parents=True, exist_ok=True)
                (d / "POSCAR_AFLOW").write_text(poscar, encoding="utf-8")
                hasil.append(f"{tag}: POSCAR dari AFLOWLIB (tanpa struktur MP)")
                continue
        if struktur is None:
            hasil.append(f"{tag}: GAGAL ambil struktur")
            continue
        spesies = tulis_input(tag, str(r["formula"]), struktur["structure"])
        save_json(DFT / tag / "_sumber_mp.json", struktur)
        hasil.append(f"{tag}: {len(struktur['structure']['sites'])} atom, elemen {spesies} -> POSCAR+CIF+scf.in+relax.in")

    # log
    (DFT / "LOG_DFT.md").write_text(
        f"# Log Persiapan Validasi DFT\n**Tanggal:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        + "\n".join(f"- {h}" for h in hasil), encoding="utf-8")
    print("\n".join(hasil))


MASS = {"H": 1.008, "C": 12.011, "O": 15.999, "F": 18.998, "P": 30.974, "Ca": 40.078}


if __name__ == "__main__":
    main()
