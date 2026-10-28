@echo off
setlocal
cd /d "%~dp0"
title THEYTHINK AI
if not exist "venv\Scripts\python.exe" (
    call "%~dp0install.bat"
    exit /b
)
"venv\Scripts\python.exe" configurar.py
if errorlevel 1 goto error
"venv\Scripts\python.exe" ejecutar.py
if errorlevel 1 goto error
exit /b 0
:error
echo No se pudo iniciar la aplicacion. Revisa el error anterior.
pause
exit /b 1
