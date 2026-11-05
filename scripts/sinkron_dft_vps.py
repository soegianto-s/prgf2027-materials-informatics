"""Sinkronisasi pipeline DFT VPS Badung <-> folder lokal data/dft.

VPS menjalankan QE 24/7 (tmux, lepas sesi lokal); folder ini sumber kebenaran
input. Hasil VPS ditarik ke data/dft/vps_hasil/ (di-gitignore — artefak, bukan sumber).

Pemakaian:
  python scripts/sinkron_dft_vps.py tarik    # unduh hasil VPS -> data/dft/vps_hasil/
  python scripts/sinkron_dft_vps.py dorong   # unggah skrip + input material ke VPS
  python scripts/sinkron_dft_vps.py status   # ekor log VPS + proses berjalan
"""
import argparse
import subprocess
from pathlib import Path

from common import ROOT

VPS = "badung-vps"
VPS_DFT = "/root/prgf_dft"
DFT = ROOT / "data" / "dft"
HASIL = DFT / "vps_hasil"
# kandidat yang dijalankan di VPS (antrean vps_setup.sh)
TAGS = ["top1_Ca5P3O12F", "top2_Ca10P6O25", "top5_Ca10P6CO27", "top6_Ca5P3HO13"]
LOG_FILES = ["run.log", "konvergensi.log", "konvergensi_summary.txt", "PRGF_DFT_STATUS.md"]


def tarik():
    """Unduh snapshot hasil VPS (log + output per material) -> data/dft/vps_hasil/."""
    HASIL.mkdir(parents=True, exist_ok=True)
    snap = HASIL / "vps_snapshot.tar.gz"
    # exclude: pseudo (sudah lokal), out/ & *.save (wavefunction besar)
    remote = (
        f"cd {VPS_DFT} && tar czf - "
        f"--exclude=*/pseudo --exclude=*/out --exclude=*/ktest_out/*.save "
        f"--exclude=*/strain_out/*.save "
        f"{' '.join(LOG_FILES)} {' '.join(TAGS)}"
    )
    with open(snap, "wb") as fh:
        r = subprocess.run(["ssh", VPS, remote], stdout=fh, stderr=subprocess.PIPE)
    if r.returncode != 0:
        print("GAGAL menarik snapshot dari VPS:\n" + r.stderr.decode(errors="replace")[-400:])
        return 1
    subprocess.run(["tar", "xzf", str(snap), "-C", str(HASIL)], check=True)
    print(f"OK: hasil VPS ditarik ke {HASIL} (snapshot: {snap.name})")
    return 0


def dorong():
    """Unggah skrip pipeline + input material lokal ke VPS (merge, tidak hapus hasil VPS)."""
    for nama in ["vps_setup.sh", "konvergensi.sh"]:
        r = subprocess.run(
            ["scp", "-q", str(ROOT / "scripts" / nama), f"{VPS}:{VPS_DFT}/"],
            capture_output=True, text=True)
        print(f"{nama}: {'OK' if r.returncode == 0 else 'GAGAL — ' + r.stderr[-200:]}")
    for tag in TAGS:
        if not (DFT / tag).exists():
            print(f"{tag}: folder lokal tidak ada, lewati")
            continue
        r = subprocess.run(
            ["scp", "-q", "-r", str(DFT / tag), f"{VPS}:{VPS_DFT}/"],
            capture_output=True, text=True)
        print(f"{tag}: {'OK' if r.returncode == 0 else 'GAGAL — ' + r.stderr[-200:]}")
    return 0


def status():
    remote = (
        f"echo === konvergensi.log ===; tail -5 {VPS_DFT}/konvergensi.log; "
        f"echo === run.log ===; tail -5 {VPS_DFT}/run.log; "
        f"echo === tmux ===; tmux ls 2>/dev/null; "
        f"echo === proses ===; ps aux | grep pw.x | grep -v grep | "
        f"awk '{{print $12, $13}}'"
    )
    r = subprocess.run(["ssh", VPS, remote], capture_output=True, text=True, timeout=600)
    print(r.stdout + r.stderr)
    return r.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["tarik", "dorong", "status"])
    args = ap.parse_args()
    return {"tarik": tarik, "dorong": dorong, "status": status}[args.mode]()


if __name__ == "__main__":
    raise SystemExit(main())
