@echo off
setlocal EnableDelayedExpansion
title Instalador - THEYTHINK AI

:: Cambiar al directorio del script
cd /d "%~dp0"

echo ======================================================================
echo             THEYTHINK AI -- INSTALADOR AUTOMATIZADO
echo ======================================================================
echo.

:: 1. Comprobar que Python está instalado
echo [1/5] Comprobando instalacion de Python...
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] No se ha encontrado Python en el sistema o no esta en el PATH.
    echo.
    echo Por favor instala Python 3.10 o superior desde https://www.python.org/
    echo IMPORTANTE: Durante la instalacion marca la casilla "Add python.exe to PATH".
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set "PY_VER=%%i"
echo   - OK: %PY_VER% detectado.
echo.

:: 2. Crear entorno virtual si no existe
echo [2/5] Configurando el entorno virtual (venv)...
if not exist "venv\Scripts\activate.bat" (
    echo   - Creando nuevo entorno virtual 'venv'...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Fallo al crear el entorno virtual.
        pause
        exit /b 1
    )
    echo   - Entorno virtual creado exitosamente.
) else (
    echo   - El entorno virtual 'venv' ya existe.
)
echo.

:: 3. Activar e instalar dependencias
echo [3/5] Instalando / actualizando librerias de requirements.txt...
call venv\Scripts\activate.bat

python -m pip install --upgrade pip --quiet
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Ocurrio un error al instalar las dependencias con pip.
    pause
    exit /b 1
)
echo   - Dependencias instaladas correctamente.
echo.

:: 4. Configurar archivo .env
echo [4/5] Configurando variables de entorno (.env)...
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo   - Se creo el archivo .env a partir de .env.example
    ) else (
        echo DEEPSEEK_API_KEY=> .env
        echo   - Se creo el archivo .env base.
    )

    echo.
    echo Deseas ingresar tu clave de DeepSeek API ahora?
    set /p "USER_API_KEY=Ingresa tu API Key (o presiona ENTER para omitir): "
    if defined USER_API_KEY (
        if not "!USER_API_KEY!"=="" (
            echo DEEPSEEK_API_KEY=!USER_API_KEY!> .env
            echo   - Clave de DeepSeek guardada en .env
        )
    )
) else (
    echo   - El archivo .env ya existe. (Se conservo la configuracion actual).
)
echo.

:: 5. Inicializar / Poblar la base de datos
echo [5/5] Inicializando base de datos SQLite y agentes iniciales...
python seed.py --force
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ADVERTENCIA] Hubo un aviso al ejecutar seed.py, pero la instalacion continuo.
) else (
    echo   - Base de datos inicializada correctamente.
)
echo.

echo ======================================================================
echo             INSTALACION COMPLETADA CON EXITO!
echo ======================================================================
echo.
echo Ahora puedes iniciar la plataforma ejecutando 'iniciar.bat' o 'python app.py'.
echo.

set /p "START_NOW=Deseas iniciar la aplicacion ahora mismo? (S/N): "
if /i "%START_NOW%"=="S" (
    echo.
    echo Iniciando THEYTHINK AI en http://127.0.0.1:5000 ...
    echo Puedes cerrar esta ventana o presionar CTRL+C para detener el servidor.
    echo.
    start http://127.0.0.1:5000
    python app.py
)

pause
exit /b 0
