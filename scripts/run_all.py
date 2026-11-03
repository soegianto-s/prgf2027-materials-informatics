"""Orkestrator pipeline Materials Informatics AMREC.

Jalankan dari folder proyek:  python scripts/run_all.py [--from <tahap>] [--skip-oqmd]
Tahap yang sudah menghasilkan data tidak diulang kecuali diminta (--force <tahap>).
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"

TAHAPAN = {
    "akuisi_mp": ("acquire_mp.py", "Akuisisi Materials Project"),
    "akuisi_aflow": ("acquire_aflow.py", "Akuisisi AFLOW"),
    "akuisi_cod": ("acquire_cod.py", "Akuisisi COD"),
    "akuisi_pubchem": ("acquire_pubchem.py", "Akuisisi PubChem"),
    "akuisi_oqmd": ("acquire_oqmd.py", "Akuisisi OQMD (lama bila server flaky)"),
    "konsolidasi": ("consolidate.py", "Konsolidasi dataset + audit"),
    "prapemrosesan": ("preprocess_descriptors.py", "Prapemrosesan + deskriptor"),
    "eda": ("eda.py", "Eksplorasi ruang desain (EDA)"),
    "pemodelan": ("modeling.py", "Pemodelan ML + evaluasi"),
    "mcdm": ("mcdm.py", "MCDM TOPSIS+VIKOR"),
    "xai": ("xai.py", "Interpretasi SHAP"),
    "laporan": ("laporan_final.py", "Laporan final + Top 15"),
    "versi": ("versi_dataset.py", "Snapshot versi dataset"),
}

# bukti bahwa tahap sudah pernah dijalankan
BUKTI = {
    "akuisi_mp": ROOT / "data" / "raw" / "mp" / "mp_summary_cap.csv",
    "akuisi_aflow": ROOT / "data" / "raw" / "aflow" / "aflow_cap.csv",
    "akuisi_cod": ROOT / "data" / "raw" / "cod" / "cod_cap.csv",
    "akuisi_pubchem": ROOT / "data" / "raw" / "pubchem" / "pubchem_cap.csv",
    "akuisi_oqmd": ROOT / "data" / "raw" / "oqmd" / "formationenergy.json",
    "konsolidasi": ROOT / "data" / "processed" / "inventory_dataset.csv",
    "prapemrosesan": ROOT / "data" / "processed" / "dataset_deskriptor.csv",
    "eda": ROOT / "data" / "reports" / "laporan_eda.md",
    "pemodelan": ROOT / "data" / "processed" / "kandidat_scaffold.csv",
    "mcdm": ROOT / "data" / "processed" / "kandidat_ranking.csv",
    "xai": ROOT / "data" / "reports" / "laporan_xai.md",
    "laporan": ROOT / "data" / "reports" / "LAPORAN_FINAL.md",
    "versi": ROOT / "data" / "versions",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="mulai", choices=list(TAHAPAN), default=None,
                    help="mulai dari tahap ini (termasuk)")
    ap.add_argument("--force", action="append", default=[],
                    help="paksa jalankan ulang tahap tertentu (bisa diulang)")
    ap.add_argument("--skip-oqmd", action="store_true", help="lewati OQMD (server flaky)")
    ap.add_argument("--dry-run", action="store_true", help="cetak rencana tanpa eksekusi")
    args = ap.parse_args()

    urutan = list(TAHAPAN)
    if args.mulai:
        urutan = urutan[urutan.index(args.mulai):]

    gagal = []
    for nama in urutan:
        skrip, label = TAHAPAN[nama]
        if nama == "akuisi_oqmd" and args.skip_oqmd:
            print(f"[LEWAT] {label} (--skip-oqmd)")
            continue
        bukti = BUKTI[nama]
        sudah = bukti.exists() and nama not in args.force
        if sudah:
            print(f"[SUDAH] {label} ({bukti.relative_to(ROOT)})")
            continue
        print(f"[JALAN] {label} ...")
        if args.dry_run:
            continue
        t0 = time.time()
        r = subprocess.run([sys.executable, str(SCRIPTS / skrip)], cwd=str(SCRIPTS))
        if r.returncode != 0:
            print(f"[GAGAL] {label} (exit {r.returncode})")
            gagal.append(nama)
            if nama in ("konsolidasi", "prapemrosesan", "eda", "pemodelan", "mcdm", "xai", "laporan"):
                print("  -> berhenti karena tahap hilir bergantung pada tahap ini")
                break
        else:
            print(f"[OK] {label} ({time.time() - t0:.0f} detik)")

    print()
    if gagal:
        print(f"Tahap gagal: {gagal}. Periksa log di atas.")
        sys.exit(1)
    print("Pipeline selesai. Lihat data/reports/LAPORAN_FINAL.md")


if __name__ == "__main__":
    main()
