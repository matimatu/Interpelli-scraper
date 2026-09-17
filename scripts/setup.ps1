$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "Cartella progetto: $ProjectRoot"

# Verifica la presenza di Python
$PyCommand = Get-Command py -ErrorAction SilentlyContinue

if (-not $PyCommand) {
    $PyCommand = Get-Command python -ErrorAction SilentlyContinue
}

if (-not $PyCommand) {
    Write-Error @"
Python non è installato oppure non è disponibile nel PATH.
Installare Python e ripetere l'operazione.
"@
    exit 1
}

# Crea l'ambiente virtuale se non esiste
$VenvDirectory = Join-Path $ProjectRoot ".venv"

if (-not (Test-Path $VenvDirectory)) {
    Write-Host "Creazione dell'ambiente virtuale..."

    if ($PyCommand.Name -eq "py.exe") {
        & py -3 -m venv $VenvDirectory
    }
    else {
        & python -m venv $VenvDirectory
    }
}
else {
    Write-Host "Ambiente virtuale già presente."
}

$VenvPython = Join-Path $VenvDirectory "Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Error "Python dell'ambiente virtuale non trovato: $VenvPython"
    exit 1
}

# Aggiorna pip e installa le dipendenze
Write-Host "Aggiornamento di pip..."
& $VenvPython -m pip install --upgrade pip

Write-Host "Installazione delle dipendenze..."
& $VenvPython -m pip install -r (Join-Path $ProjectRoot "requirements.txt")

# Installa Chromium per Playwright
Write-Host "Installazione di Chromium per Playwright..."
& $VenvPython -m playwright install chromium

# Crea BOT.properties dal file di esempio
$BotProperties = Join-Path $ProjectRoot "BOT.properties"
$BotPropertiesExample = Join-Path $ProjectRoot "BOT.properties.example"

if (-not (Test-Path $BotProperties)) {
    if (-not (Test-Path $BotPropertiesExample)) {
        Write-Error @"
File BOT.properties.example non trovato.
Impossibile creare BOT.properties.
"@
        exit 1
    }

    Copy-Item `
        -Path $BotPropertiesExample `
        -Destination $BotProperties

    Write-Host ""
    Write-Host "Creato BOT.properties dal file BOT.properties.example."
    Write-Host "Inserire BOT_TOKEN e CHAT_ID nel file BOT.properties."
}
else {
    Write-Host "BOT.properties già presente: non verrà sovrascritto."
}

# Crea le cartelle locali necessarie
$OutputDirectory = Join-Path $ProjectRoot "output"
$LogsDirectory = Join-Path $ProjectRoot "logs"

New-Item `
    -ItemType Directory `
    -Force `
    -Path $OutputDirectory `
    | Out-Null

New-Item `
    -ItemType Directory `
    -Force `
    -Path $LogsDirectory `
    | Out-Null

Write-Host ""
Write-Host "Setup completato."
Write-Host ""
Write-Host "Passaggi successivi:"
Write-Host "1. Modificare BOT.properties."
Write-Host "2. Verificare BOT_TOKEN e CHAT_ID."
Write-Host "3. Avviare il programma con:"
Write-Host "   powershell -ExecutionPolicy Bypass -File .\scripts\run.ps1"