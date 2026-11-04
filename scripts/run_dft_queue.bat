@echo off
rem Antrean DFT PRGF — dijalankan Task Scheduler agar lepas dari sesi interaktif.
cd /d D:\latex\prgf2026
"C:\Users\soegianto\AppData\Local\Programs\Python\Python310\python.exe" scripts\jalankan_dft.py --semua --np 12 >> data\validasi_dft\run_semua.log 2>&1
echo [%date% %time%] antrean DFT selesai >> data\validasi_dft\run_semua.log
