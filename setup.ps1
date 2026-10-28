$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

function Invoke-PythonStep {
    param([string]$Executable, [string[]]$Arguments)
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Fallo al ejecutar Python ($($Arguments -join ' '))." }
}

try {
    Write-Host '[1/6] Buscando Python 3.10 o superior...'
    $python = $null
    $candidates = @((Join-Path $PSScriptRoot 'venv\Scripts\python.exe'))
    foreach ($name in @('python.exe', 'py.exe')) {
        $command = Get-Command $name -ErrorAction SilentlyContinue
        if ($command -and $command.Source -notlike '*\WindowsApps\*') { $candidates += $command.Source }
    }
    $candidates += Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe'
    foreach ($candidate in $candidates) {
        if (-not (Test-Path -LiteralPath $candidate)) { continue }
        $detected = & $candidate -c 'import sys; print(sys.executable) if sys.version_info >= (3,10) else sys.exit(1)' 2>$null
        if ($LASTEXITCODE -eq 0 -and $detected) { $python = ($detected | Select-Object -Last 1); break }
    }
    if (-not $python) {
        Write-Host 'Descargando e instalando Python para el usuario actual...'
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        $arch = if ([Environment]::Is64BitOperatingSystem) { 'amd64' } else { 'win32' }
        $suffix = if ($arch -eq 'amd64') { '-amd64' } else { '' }
        $installer = Join-Path ([IO.Path]::GetTempPath()) ('tai-python-' + [guid]::NewGuid().ToString() + '.exe')
        try {
            Invoke-WebRequest -UseBasicParsing -Uri "https://www.python.org/ftp/python/3.12.10/python-3.12.10$suffix.exe" -OutFile $installer
            $signature = Get-AuthenticodeSignature -LiteralPath $installer
            if ($signature.Status -ne 'Valid' -or $signature.SignerCertificate.Subject -notmatch 'Python Software Foundation') {
                throw 'La firma del instalador de Python no es valida.'
            }
            $process = Start-Process -FilePath $installer -ArgumentList '/quiet InstallAllUsers=0 PrependPath=0 Include_launcher=0 Include_test=0' -WindowStyle Hidden -Wait -PassThru
            if ($process.ExitCode -notin @(0, 3010)) { throw "El instalador de Python fallo: $($process.ExitCode)" }
        } finally {
            if (Test-Path -LiteralPath $installer) { Remove-Item -LiteralPath $installer }
        }
        $python = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe'
        if (-not (Test-Path -LiteralPath $python)) { throw 'No se encontro Python despues de instalarlo.' }
    }

    Write-Host '[2/6] Preparando el entorno virtual...'
    $venvPython = Join-Path $PSScriptRoot 'venv\Scripts\python.exe'
    if ($python -ne $venvPython) {
        Invoke-PythonStep -Executable $python -Arguments @('-m', 'venv', 'venv')
    }
    Write-Host '[3/6] Instalando dependencias...'
    Invoke-PythonStep -Executable $venvPython -Arguments @('-m', 'pip', 'install', '--upgrade', 'pip')
    Invoke-PythonStep -Executable $venvPython -Arguments @('-m', 'pip', 'install', '-r', 'requirements.txt')
    Write-Host '[4/6] Verificando personas e imagenes incluidas en el proyecto...'
    $catalogCheck = @'
from pathlib import Path
from personas import PERSONAS, PERFILES_EMPRESA

faltantes = [
    p['nombre'] for p in PERSONAS
    if not p.get('avatar_url', '').startswith('/static/')
    or not Path(p['avatar_url'].lstrip('/')).is_file()
]
if faltantes:
    raise FileNotFoundError('Faltan avatares locales: ' + ', '.join(faltantes)
                            + '. Descarga o copia el proyecto completo, incluida static/img/personas/.')
print(f'Catalogo verificado: {len(PERSONAS)} personas con imagen; '
      f'{len(PERFILES_EMPRESA)} perfiles de Music Pro.')
'@
    Invoke-PythonStep -Executable $venvPython -Arguments @('-c', $catalogCheck)
    Write-Host '[5/6] Configurando la credencial de DeepSeek...'
    Invoke-PythonStep -Executable $venvPython -Arguments @('configurar.py')
    Write-Host '[6/6] Cargando personas, conocimientos, conversaciones y avatares...'
    Invoke-PythonStep -Executable $venvPython -Arguments @('seed.py')
    Write-Host 'Instalacion completada. Abriendo THEYTHINK AI...'
} catch {
    Write-Host ('ERROR: ' + $_.Exception.Message) -ForegroundColor Red
    exit 1
}
exit 0
