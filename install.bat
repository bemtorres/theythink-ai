@echo off
setlocal
cd /d "%~dp0"
title Instalador - THEYTHINK AI
echo Instalacion completa de THEYTHINK AI
echo Incluye 31 personas con imagen y los 4 proyectos de Music Pro.
echo.
if not exist "%~dp0setup.ps1" (
    echo ERROR: Falta setup.ps1. Descarga o copia la carpeta completa del proyecto.
    pause
    exit /b 1
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"
if errorlevel 1 (
    echo.
    echo No se pudo completar la instalacion. Revisa el error anterior y vuelve a ejecutar install.bat.
    pause
    exit /b 1
)
call "%~dp0iniciar.bat"
exit /b %errorlevel%
