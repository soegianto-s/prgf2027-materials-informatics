"""Unduh CIF COD unik (ronde 7/Q1) — resumable + QC koordinat.

Sumber: data/raw/cod/{cap_biner,capo_terner,capoh_kuaterner}.json (metadata query COD)
-> dedupe per `file` (938 unik) -> unduh https://www.crystallography.net/cod/<file>.cif
dengan jeda sopan 1.2 s. Resume: CIF yang sudah ada & lolos QC koordinat dilewati.
QC: file non-kosong, bukan HTML, dan memiliki loop _atom_site_fract_* bernilai numerik
(bukan '?' — contoh COD 6000036/6000037 hanya metadata tanpa koordinat).

Keluaran:
  data/raw/cod/cif/<file>.cif
  data/raw/cod/_manifest_unduhan.json  (per file: status, sha256, ukuran, url, waktu)
  data/raw/cod/_daftar_struktur.csv    (file, formula, calcformula, flags, sg, status)
"""
import hashlib
import json
import re
import time
from pathlib import Path

import pandas as pd

from common import RAW, REPORTS, UA

CIFDIR = RAW / "cod" / "cif"
CIFDIR.mkdir(parents=True, exist_ok=True)
SUMBER = ["cap_biner.json", "capo_terner.json", "capoh_kuaterner.json"]
URL = "https://www.crystallography.net/cod/{f}.cif"
JEDA = 1.2
RETRY_PAUSE = 4


def muat_metadata():
    baris = {}
    for nama in SUMBER:
        d = json.loads((RAW / "cod" / nama).read_text(encoding="utf-8"))
        for x in d:
            f = x.get("file")
            if not f:
                continue
            if f not in baris:
                baris[f] = x
            else:
                # lengkapi field kosong dari entri lain
                for k, v in x.items():
                    if (k not in baris[f]) or baris[f][k] in (None, ""):
                        baris[f][k] = v
    return baris


TOKEN_NUM = re.compile(r"[-+0-9.]+\(?\d*\)?")


def qc_koordinat(teks):
    """True bila CIF punya minimal satu baris data atom dengan >=3 nilai numerik.

    Baris data COD khas: `Ca1 Ca2+ 2 a 0.2331(3) 0. 0.1970(5) 1. 0 d`
    (label, tipe, multiplisitas, Wyckoff, fract x/y/z, occupancy...).
    Nilai '?' (tanpa koordinat) TIDAK cocok dengan pola -> tertolak benar.
    """
    if not teks or teks.strip().startswith(("<", "{")):
        return False
    if "_atom_site_fract_x" not in teks:
        return False
    for line in teks.splitlines():
        c = line.strip()
        if not c or c[0] in "_#;'l" or c.startswith("data_"):
            continue
        if len(TOKEN_NUM.findall(c)) >= 3:
            return True
    return False


def unduh(f, sesi):
    teks = sesi.get(URL.format(f=f), headers=UA, timeout=90)
    if teks is None:
        return None
    if teks.status_code != 200:
        return None
    return teks.text


def main():
    import requests
    meta = muat_metadata()
    sesi = requests.Session()
    sesi.headers.update(UA)
    urut = sorted(meta)
    manifest, daftar = {}, []

    n_total = n_baru = n_resume = n_gagal = 0
    for i, f in enumerate(urut, 1):
        x = meta[f]
        n_total += 1
        target = CIFDIR / f"{f}.cif"
        status = "sukses"
        if target.exists() and target.stat().st_size > 0:
            teks = target.read_text(encoding="utf-8", errors="replace")
            if qc_koordinat(teks):
                n_resume += 1
                status = "resume"
        if status == "sukses":
            teks = None
            for coba in range(4):
                try:
                    r = sesi.get(URL.format(f=f), timeout=90)
                    if r.status_code == 200 and qc_koordinat(r.text):
                        teks = r.text
                        break
                    teks = None
                except Exception:
                    teks = None
                time.sleep(RETRY_PAUSE * (coba + 1))
            if teks is None:
                status = "gagal"
                n_gagal += 1
            else:
                tmp = target.with_suffix(".part")
                tmp.write_text(teks, encoding="utf-8")
                tmp.replace(target)
                n_baru += 1
        sha = hashlib.sha256(target.read_bytes()).hexdigest() if target.exists() else ""
        manifest[f] = {"status": status, "url": URL.format(f=f), "size": target.stat().st_size if target.exists() else 0,
                       "sha256": sha, "waktu": time.strftime("%Y-%m-%d %H:%M:%S"),
                       "formula": x.get("formula", ""), "flags": x.get("flags", ""),
                       "sg": x.get("sg", ""), "year": x.get("year", "")}
        daftar.append({"file": f, "formula": x.get("formula", ""), "calcformula": x.get("calcformula", ""),
                       "flags": x.get("flags", ""), "sg": x.get("sg", ""), "year": x.get("year", ""),
                       "status": status})
        if i % 50 == 0 or i == len(urut):
            (RAW / "cod" / "_manifest_unduhan.json").write_text(
                json.dumps({"total": n_total, "baru": n_baru, "resume": n_resume, "gagal": n_gagal,
                            "manifest": manifest}, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"{i}/{len(urut)}  baru={n_baru} resume={n_resume} gagal={n_gagal}", flush=True)
        time.sleep(JEDA)

    pd.DataFrame(daftar).to_csv(RAW / "cod" / "_daftar_struktur.csv", index=False)
    print(f"SELESAI: total={n_total} baru={n_baru} resume={n_resume} gagal={n_gagal}")


if __name__ == "__main__":
    main()
