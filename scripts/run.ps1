$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$BotProperties = Join-Path $ProjectRoot "BOT.properties"

if (-not (Test-Path $VenvPython)) {
    Write-Error "Ambiente virtuale non trovato. Eseguire prima setup.ps1."
    exit 1
}

if (-not (Test-Path $BotProperties)) {
    Write-Error "BOT.properties non trovato. Eseguire prima setup.ps1."
    exit 1
}

$LogsDirectory = Join-Path $ProjectRoot "logs"

New-Item `
    -ItemType Directory `
    -Force `
    -Path $LogsDirectory `
    | Out-Null

$LogFile = Join-Path `
    $LogsDirectory `
    ("run-{0}.log" -f (Get-Date -Format "yyyy-MM-dd"))

& $VenvPython main.py run *>&1 |
    Tee-Object -FilePath $LogFile

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}