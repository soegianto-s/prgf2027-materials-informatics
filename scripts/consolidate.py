"""Konsolidasi dataset 5 sumber -> inventory terpadu + laporan audit akuisisi."""
import ast
import json
import re
import time
from pathlib import Path

import pandas as pd

from common import RAW, PROC, REPORTS

PAIRS = re.compile(r"([A-Z][a-z]?)(\d*\.?\d*)")


def parse_formula(f):
    """Kembalikan dict elemen->jumlah dari string formula."""
    if not isinstance(f, str):
        return {}
    counts = {}
    for el, n in PAIRS.findall(f.replace(" ", "")):
        if not el:
            continue
        counts[el] = counts.get(el, 0) + (float(n) if n else 1.0)
    return counts


def ca_p(c):
    p = c.get("P", 0)
    return round(c.get("Ca", 0) / p, 3) if p else None


def main():
    rows = []

    # --- Materials Project ---
    mp = pd.read_csv(RAW / "mp" / "mp_summary_cap.csv")
    mp_el = pd.read_csv(RAW / "mp" / "mp_elastic_cap.csv")
    mp = mp.merge(mp_el, on="material_id", how="left", suffixes=("", "_el"))
    for _, r in mp.iterrows():
        el = parse_formula(r["formula_pretty"])
        rows.append({
            "sumber": "MaterialsProject", "id": r["material_id"],
            "formula": r["formula_pretty"], "chemsys": r.get("chemsys"),
            "Ca": el.get("Ca"), "P": el.get("P"), "O": el.get("O"),
            "H": el.get("H"), "F": el.get("F"), "ca_p_ratio": ca_p(el),
            "nsites": r.get("nsites"), "volume_A3": r.get("volume"),
            "Z": None,
            "densitas_gcm3": r.get("density"), "bandgap_eV": r.get("band_gap"),
            "Eform_eV_atom": r.get("formation_energy_per_atom"),
            "E_hull_eV_atom": r.get("energy_above_hull"),
            "stabil": r.get("is_stable"),
            "kristal_sistem": r.get("crystal_system"),
            "spacegroup": r.get("spacegroup_symbol"),
            "bulk_K_GPa": r.get("bulk_modulus"),
            "shear_G_GPa": r.get("shear_modulus"),
            "young_E_GPa": None, "poisson": r.get("homogeneous_poisson"),
            "prototipe": None, "icsd": None, "doi": None, "tahun": None,
        })

    # --- AFLOW ---
    af = pd.read_csv(RAW / "aflow" / "aflow_cap.csv")
    for _, r in af.iterrows():
        el = parse_formula(r.get("compound"))
        g = r.get("geometry")
        if isinstance(g, str):
            try:
                g = ast.literal_eval(g)
            except Exception:
                g = None
        rows.append({
            "sumber": "AFLOW", "id": r.get("auid"),
            "formula": r.get("compound"), "chemsys": None,
            "Ca": el.get("Ca"), "P": el.get("P"), "O": el.get("O"),
            "H": el.get("H"), "F": el.get("F"), "ca_p_ratio": ca_p(el),
            "nsites": None, "volume_A3": r.get("volume_cell"),
            "Z": None,
            "densitas_gcm3": r.get("density"), "bandgap_eV": r.get("Egap"),
            "Eform_eV_atom": r.get("enthalpy_formation_atom"),
            "E_hull_eV_atom": None,
            "stabil": None,
            "kristal_sistem": r.get("lattice_system_relax"),
            "spacegroup": r.get("spacegroup_relax"),
            "bulk_K_GPa": r.get("ael_bulk_modulus_vrh"),
            "shear_G_GPa": r.get("ael_shear_modulus_vrh"),
            "young_E_GPa": r.get("ael_youngs_modulus_vrh"),
            "poisson": None,
            "prototipe": r.get("prototype"), "icsd": None,
            "doi": None, "tahun": None,
        })

    # --- COD ---
    cod = pd.read_csv(RAW / "cod" / "cod_cap.csv")
    for _, r in cod.iterrows():
        fcod = r.get("calcformula") or r.get("formula")
        if fcod is None or (isinstance(fcod, float) and pd.isna(fcod)):
            fcod = ""
        fcod = str(fcod).replace("-", "").strip()
        el = parse_formula(fcod)
        rows.append({
            "sumber": "COD", "id": r.get("file"),
            "formula": fcod,
            "chemsys": None,
            "Ca": el.get("Ca"), "P": el.get("P"), "O": el.get("O"),
            "H": el.get("H"), "F": el.get("F"), "ca_p_ratio": ca_p(el),
            "nsites": None, "volume_A3": pd.to_numeric(r.get("vol"), errors="coerce"),
            "Z": pd.to_numeric(r.get("Z"), errors="coerce"),
            "densitas_gcm3": None, "bandgap_eV": None,
            "Eform_eV_atom": None, "E_hull_eV_atom": None, "stabil": None,
            "kristal_sistem": None, "spacegroup": r.get("sg"),
            "bulk_K_GPa": None, "shear_G_GPa": None, "young_E_GPa": None,
            "poisson": None,
            "prototipe": None, "icsd": None,
            "doi": r.get("doi"), "tahun": pd.to_numeric(r.get("year"), errors="coerce"),
        })

    # --- OQMD (bila akuisisi sudah menghasilkan data) ---
    oq_path = RAW / "oqmd" / "formationenergy.json"
    if oq_path.exists():
        try:
            oq = json.loads(oq_path.read_text(encoding="utf-8"))
            for comp, entri in oq.items():
                for e in entri:
                    el = parse_formula(e.get("composition", comp))
                    n_atom_fu = sum(el.values())
                    natoms = e.get("natoms")
                    # Z = jumlah atom sel / jumlah atom per formula unit (volume OQMD = volume sel penuh)
                    z = natoms / n_atom_fu if (natoms and n_atom_fu) else None
                    rows.append({
                        "sumber": "OQMD", "id": f"oqmd-{e.get('entry_id', comp)}",
                        "formula": (e.get("composition") or comp).replace(" ", ""),
                        "chemsys": None,
                        "Ca": el.get("Ca"), "P": el.get("P"), "O": el.get("O"),
                        "H": el.get("H"), "F": el.get("F"), "ca_p_ratio": ca_p(el),
                        "nsites": natoms, "volume_A3": e.get("volume"), "Z": z,
                        "densitas_gcm3": None, "bandgap_eV": None,
                        "Eform_eV_atom": e.get("delta_e"),
                        "E_hull_eV_atom": None, "stabil": None,
                        "kristal_sistem": None, "spacegroup": e.get("spacegroup"),
                        "bulk_K_GPa": None, "shear_G_GPa": None, "young_E_GPa": None,
                        "poisson": None, "prototipe": e.get("prototype"),
                        "icsd": e.get("icsd_id"),
                        "doi": None, "tahun": None,
                    })
        except Exception as ex:
            print("  OQMD: skip integrasi:", ex)

    # --- PubChem (metadata kimia) ---
    pc_path = RAW / "pubchem" / "pubchem_cap.csv"
    if pc_path.exists():
        pc = pd.read_csv(pc_path)
        for _, r in pc.iterrows():
            el = parse_formula(r.get("MolecularFormula"))
            rows.append({
                "sumber": "PubChem", "id": f"CID{r.get('CID')}",
                "formula": r.get("MolecularFormula"), "chemsys": None,
                "Ca": el.get("Ca"), "P": el.get("P"), "O": el.get("O"),
                "H": el.get("H"), "F": el.get("F"), "ca_p_ratio": ca_p(el),
                "nsites": None, "volume_A3": None, "Z": None, "densitas_gcm3": None,
                "bandgap_eV": None, "Eform_eV_atom": None, "E_hull_eV_atom": None,
                "stabil": None, "kristal_sistem": None, "spacegroup": None,
                "bulk_K_GPa": None, "shear_G_GPa": None, "young_E_GPa": None,
                "poisson": None, "prototipe": None, "icsd": None,
                "doi": None, "tahun": None,
            })

    inv = pd.DataFrame(rows)
    inv.to_csv(PROC / "inventory_dataset.csv", index=False)

    # --- statistik audit ---
    n_total = len(inv)
    comp_key = inv.apply(lambda r: frozenset(parse_formula(r["formula"]).items()), axis=1)
    n_komposisi_unik = comp_key.nunique()
    komplit = inv.notna().mean() * 100
    per_sumber = inv.groupby("sumber").agg(
        jumlah=("id", "count"),
        komposisi_unik=("formula", "nunique"),
        ada_energi=("Eform_eV_atom", lambda s: s.notna().sum()),
        ada_densitas=("densitas_gcm3", lambda s: s.notna().sum()),
        ada_volume=("volume_A3", lambda s: s.notna().sum()),
        ada_elastik=("bulk_K_GPa", lambda s: s.notna().sum()),
        ada_bandgap=("bandgap_eV", lambda s: s.notna().sum()),
    ).reset_index()

    # --- material rujukan ---
    def cari(ref_ca, ref_p, ref_o=None, ref_h=None):
        hit = inv[
            (inv["Ca"].fillna(0).round(1) == ref_ca)
            & (inv["P"].fillna(0).round(1) == ref_p)
            & (abs(inv["O"].fillna(0) - (ref_o or 0)) < 0.6)
            & (abs(inv["H"].fillna(0) - (ref_h or 0)) < 0.6)
        ]
        return hit

    hap = cari(5, 3, 13, 1)
    tcp = cari(3, 2, 8, 0)
    hap_dict = hap.groupby("sumber")["id"].count().to_dict() if len(hap) else {}
    tcp_dict = tcp.groupby("sumber")["id"].count().to_dict() if len(tcp) else {}

    laporan = f"""# Laporan Audit Akuisisi Dataset Biomaterial Kalsium Fosfat
**Tanggal audit:** {time.strftime('%Y-%m-%d %H:%M:%S')}
**Tahapan:** Bagian 2–3 panduan utama (akuisisi + audit dataset)

## Ringkasan
- **Total baris/entri:** {n_total}
- **Komposisi kimia unik:** {n_komposisi_unik}
- **Indikator target:** >= 500 senyawa tervalidasi → {'TERPENUHI' if n_komposisi_unik >= 500 else 'BELUM (menunggu OQMD/sumber lain)'}
- **Sumber & lisensi:**
  - Materials Project (API, CC-BY 4.0) — diakses {time.strftime('%Y-%m-%d')}
  - AFLOW (AFLUX REST, sitasi Curtarolo et al.) — diakses {time.strftime('%Y-%m-%d')}
  - COD (HTTP, CC0 public domain) — diakses {time.strftime('%Y-%m-%d')}
  - PubChem (PUG REST, public domain NCBI) — diakses {time.strftime('%Y-%m-%d')}
  - OQMD (oqmdapi, sitasi Kirklin et al.) — proses berjalan (server flaky)

## Jumlah per Sumber & Kelengkapan Deskriptor
{per_sumber.to_markdown(index=False)}

## Kelengkapan Kolom Utama (%)
{komplit[['formula','densitas_gcm3','Eform_eV_atom','bandgap_eV','bulk_K_GPa','volume_A3','spacegroup']].round(1).to_markdown()}

## Pemeriksaan Material Rujukan (kontrol positif)
- **Hidroksiapatit (Ca5P3O13H):** {len(hap)} entri dari {hap_dict}
- **Trikalsium fosfat (Ca3P2O8):** {len(tcp)} entri dari {tcp_dict}

## Catatan Kualitas
- Data COD: eksperimental (parameter kisi + spacegroup), tanpa energi/sifat mekanik.
- Data MP/AFLOW: komputasional (energi, bandgap, modulus elastik VRH untuk AFLOW).
- Perbandingan antar basis data untuk komposisi sama dilakukan pada tahap eksplorasi (Bagian 5.4 panduan).
"""
    (REPORTS / "laporan_akuisisi.md").write_text(laporan, encoding="utf-8")
    print(laporan.encode("ascii", "replace").decode("ascii"))
    print("inventory tersimpan:", PROC / "inventory_dataset.csv")


if __name__ == "__main__":
    main()
