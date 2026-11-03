"""Snapshot versi dataset final + manifest checksum (SHA-256).

Output: data/versions/dataset_v1.0_YYYYMMDD/ (file kunci) + VERSION.md
"""
import hashlib
import json
import shutil
import time
from pathlib import Path

from common import PROC, ROOT

FILE_KUNCI = [
    "inventory_dataset.csv",
    "dataset_deskriptor.csv",
    "kandidat_ranking.csv",
    "kandidat_top15_dedup.csv",
    "hasil_cv_regresi.csv",
]

LAPORAN_KUNCI = [
    "LAPORAN_FINAL.md",
    "laporan_akuisisi.md",
    "laporan_prapemrosesan.md",
    "laporan_eda.md",
    "laporan_pemodelan.md",
    "laporan_mcdm.md",
    "laporan_xai.md",
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blok in iter(lambda: f.read(1 << 20), b""):
            h.update(blok)
    return h.hexdigest()


def main():
    tgl = time.strftime("%Y%m%d")
    nama = f"dataset_v1.0_{tgl}"
    dst = ROOT / "data" / "versions" / nama
    dst.mkdir(parents=True, exist_ok=True)
    manifest = {"nama": nama, "tanggal": time.strftime("%Y-%m-%d %H:%M:%S"),
                "sumber": "data/processed + data/reports", "file": {}}
    for f in FILE_KUNCI:
        src = PROC / f
        if src.exists():
            shutil.copy2(src, dst / f)
            manifest["file"][f] = sha256(dst / f)
    # salinan laporan + figures
    rep = dst / "reports"
    rep.mkdir(exist_ok=True)
    for f in LAPORAN_KUNCI:
        src = ROOT / "data" / "reports" / f
        if src.exists():
            shutil.copy2(src, rep / f)
            manifest["file"][f"reports/{f}"] = sha256(rep / f)
    fig = ROOT / "data" / "reports" / "figures"
    if fig.exists():
        shutil.copytree(fig, rep / "figures", dirs_exist_ok=True)
        manifest["file"]["reports/figures/"] = "disalin utuh"
    (dst / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False),
                                      encoding="utf-8")
    # VERSION.md ringkas
    (ROOT / "VERSION.md").write_text(
        f"# Versi Dataset\n\n- **{nama}** — {manifest['tanggal']}\n"
        f"- Entri: 2.605 / komposisi unik: 903 (lihat `data/reports/laporan_akuisisi.md`)\n"
        f"- Checksum: `data/versions/{nama}/manifest.json`\n",
        encoding="utf-8")
    print(f"Versi tersimpan: {dst}")
    for k, v in manifest["file"].items():
        print(f"  {k}: {v[:16] if len(v) > 20 else v}")


if __name__ == "__main__":
    main()
