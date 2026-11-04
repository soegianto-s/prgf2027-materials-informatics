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
    "eda_lanjutan": ("eda_lanjutan.py", "EDA lanjutan: UMAP/HDBSCAN/hierarkis + validasi literatur"),
    "tcp_alpha_beta": ("tcp_alpha_beta.py", "Pemisahan alpha/beta-TCP vs literatur (gap #3)"),
    "pemodelan": ("modeling.py", "Pemodelan ML + evaluasi"),
    "tuning_eform": ("tuning_eform.py", "Tuning Eform ke R2 >= 0.85 (gap #2)"),
    "mcdm": ("mcdm.py", "MCDM TOPSIS+VIKOR"),
    "mcdm_entropi": ("mcdm_entropi.py", "Sensitivitas MCDM: pembobotan entropi"),
    "mcdm_montecarlo": ("mcdm_montecarlo.py", "Monte Carlo MCDM: propagasi ketidakpastian bobot + prediksi"),
    "siapkan_dft": ("siapkan_dft.py", "Input DFT/QE untuk Top 5 kandidat"),
    "xai": ("xai.py", "Interpretasi SHAP"),
    "laporan": ("laporan_final.py", "Laporan final + Top 15"),
    "versi": ("versi_dataset.py", "Snapshot versi dataset"),
    # --- ronde 7 / Q1 (urutan wajib) ---
    "cod_cif": ("acquire_cod_cif.py", "Unduh CIF COD unik (resumable, QC koordinat)"),
    "mace_cod": ("screening_mace_cod.py", "Screening MACE-MP-0 single-point struktur COD"),
    "kalibrasi_hull": ("kalibrasi_hull_mace.py", "Kalibrasi offset MACE->MP GGA + E_hull COD"),
    "fitur_struktur": ("ekstrak_fitur_struktur.py", "Fitur struktural: Q^n, CN Ca, SOAP"),
    "model_struktur": ("modeling_struktur.py", "Model structure-informed (screening, bukan discovery)"),
    "substitusi": ("perluasan_kandidat_mp.py", "Perluasan kandidat substitusi Sr/Mg/Zn/Si (MP)"),
    "kelarutan": ("konversi_ksp.py", "Konversi pKsp -> kelarutan stoikiometrik S"),
    "mcdm_q1": ("mcdm_q1.py", "MCDM Q1: C1 = -E_hull (phase-level)"),
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
    "eda_lanjutan": ROOT / "data" / "reports" / "laporan_eda_lanjutan.md",
    "tcp_alpha_beta": ROOT / "data" / "reports" / "laporan_tcp_alpha_beta.md",
    "pemodelan": ROOT / "data" / "processed" / "kandidat_scaffold.csv",
    "tuning_eform": ROOT / "data" / "reports" / "laporan_tuning_eform.md",
    "mcdm": ROOT / "data" / "processed" / "kandidat_ranking.csv",
    "mcdm_entropi": ROOT / "data" / "reports" / "laporan_sensitivitas.md",
    "mcdm_montecarlo": ROOT / "data" / "reports" / "laporan_montecarlo.md",
    "siapkan_dft": ROOT / "data" / "dft" / "LOG_DFT.md",
    "xai": ROOT / "data" / "reports" / "laporan_xai.md",
    "laporan": ROOT / "data" / "reports" / "LAPORAN_FINAL.md",
    "versi": ROOT / "data" / "versions",
    "cod_cif": ROOT / "data" / "raw" / "cod" / "_manifest_unduhan.json",
    "mace_cod": ROOT / "data" / "processed" / "mace_screening_cod_ringkasan.json",
    "kalibrasi_hull": ROOT / "data" / "processed" / "kalibrasi_mace_ringkasan.json",
    "fitur_struktur": ROOT / "data" / "processed" / "fitur_struktur_ringkasan.json",
    "model_struktur": ROOT / "data" / "processed" / "model_struktur_ringkasan.json",
    "substitusi": ROOT / "data" / "raw" / "mp" / "substitusi" / "substitusi_ringkasan.json",
    "kelarutan": ROOT / "data" / "processed" / "kelarutan_ksp.csv",
    "mcdm_q1": ROOT / "data" / "processed" / "mcdm_q1_ringkasan.json",
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
            if nama in ("konsolidasi", "prapemrosesan", "eda", "pemodelan", "mcdm", "xai", "laporan",
                        "mace_cod", "kalibrasi_hull", "fitur_struktur", "mcdm_q1"):
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
