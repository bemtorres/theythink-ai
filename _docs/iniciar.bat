@echo off
setlocal
title Iniciar - THEYTHINK AI (Django)

:: Cambiar al directorio del script
cd /d "%~dp0"

echo ======================================================================
echo                 INICIANDO THEYTHINK AI (DJANGO)
echo ======================================================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] No se encontro el entorno virtual 'venv'.
    echo Por favor ejecuta primero 'install.bat' para instalar la aplicacion.
    echo.
    pause
    exit /b 1
)

:: Activar entorno virtual
call venv\Scripts\activate.bat

:: Abrir navegador y correr servidor Django
echo Servidor iniciado en: http://127.0.0.1:8000
echo Panel Django Admin en: http://127.0.0.1:8000/django-admin/
echo Presiona CTRL+C en esta consola para detener el servidor.
echo.
start http://127.0.0.1:8000
python manage.py runserver 127.0.0.1:8000

pause
