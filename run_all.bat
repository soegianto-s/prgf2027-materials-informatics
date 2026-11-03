@echo off
rem Orkestrator pipeline Materials Informatics AMREC (Windows)
rem Penggunaan: run_all.bat [--from eda] [--skip-oqmd] [--dry-run]
cd /d "%~dp0"
python scripts\run_all.py %*
pause
