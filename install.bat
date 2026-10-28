@echo off
setlocal
cd /d "%~dp0"
title Instalador - THEYTHINK AI
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"
if errorlevel 1 (
    echo.
    echo No se pudo completar la instalacion. Revisa el error anterior y vuelve a ejecutar install.bat.
    pause
    exit /b 1
)
call "%~dp0iniciar.bat"
exit /b %errorlevel%
