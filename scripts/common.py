"""Utilitas bersama akuisisi data Materials Informatics (AMREC, Universitas Airlangga)."""
import json
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(r"D:\latex\prgf2026")
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
REPORTS = ROOT / "data" / "reports"
for d in (RAW, PROC, REPORTS):
    d.mkdir(parents=True, exist_ok=True)

UA = {
    "User-Agent": "AMREC-MaterialsInformatics/1.0 (Universitas Airlangga; kontak: soegianto@fst.unair.ac.id)"
}


def mp_key():
    """Ambil kunci Materials Project dari env MP_API_KEY/PMG_MAPI_KEY atau ~/.pmgrc.yaml."""
    env = os.environ.get("MP_API_KEY") or os.environ.get("PMG_MAPI_KEY")
    if env:
        return env
    p = Path.home() / ".pmgrc.yaml"
    if p.exists():
        m = re.search(r"PMG_MAPI_KEY:\s*(\S+)", p.read_text(encoding="utf-8"))
        if m:
            return m.group(1)
    sys.exit("ERROR: kunci Materials Project tidak ditemukan (env MP_API_KEY atau ~/.pmgrc.yaml)")


def save_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    print(f"  saved {path.name} ({len(str(obj)) // 1024} KB)")


def get(url, *, headers=None, tries=4, pause=8, timeout=90, **kw):
    """GET dengan retry eksponensial. Kembalikan Response atau None."""
    import requests

    h = dict(UA)
    if headers:
        h.update(headers)
    for i in range(tries):
        try:
            r = requests.get(url, headers=h, timeout=timeout, **kw)
            if r.status_code == 200:
                return r
            print(f"  HTTP {r.status_code} {url[:110]} (coba {i + 1}/{tries})")
        except Exception as e:
            print(f"  error {type(e).__name__}: {e} (coba {i + 1}/{tries})")
        time.sleep(pause * (i + 1))
    return None
