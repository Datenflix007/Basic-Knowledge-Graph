@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ==========================================
echo   Knowledge Graph Visualisierung
echo ==========================================
echo.
echo Welche Eingabedatei soll verwendet werden?
echo   [1]  Standardbeispiel (wird automatisch erstellt)
echo   [2]  Eigenes Exzerpt auswaehlen (Dateidialog)
echo.
set /p CHOICE="Auswahl (1 oder 2): "

set "INPUT_FILE="

if "%CHOICE%"=="2" (
    echo Oeffne Dateidialog...
    for /f "usebackq delims=" %%F in (`powershell -NoProfile -Command "Add-Type -AssemblyName System.Windows.Forms; $d = New-Object System.Windows.Forms.OpenFileDialog; $d.Title = 'Exzerpt auswaehlen'; $d.Filter = 'Markdown (*.md)|*.md|Alle Dateien (*.*)|*.*'; $d.InitialDirectory = '%~dp0'; if ($d.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) { Write-Output $d.FileName }"`) do set "INPUT_FILE=%%F"
    if "!INPUT_FILE!"=="" echo Kein Exzerpt ausgewaehlt, verwende Standardbeispiel.
)

if "!INPUT_FILE!"=="" (
    set "INPUT_FILE=%~dp0example.md"
    echo Erstelle Standardbeispiel...
    (
        echo ^| Seite ^| Inhalt ^| Anmerkung ^|
        echo ^|-------^|--------^|-----------^|
        echo ^| 1 ^| Dies ist ein Beispieltext. ^| Wichtige Information ^|
    ) > "!INPUT_FILE!"
)

echo.
echo Eingabedatei: !INPUT_FILE!
echo.

echo Erstelle virtuelle Umgebung...
if not exist ".venv\Scripts\python.exe" (
    python -m venv .venv
)
if not exist ".venv\Scripts\python.exe" (
    echo Python virtuelle Umgebung konnte nicht erstellt werden.
    pause
    exit /b 1
)
set "PYTHON=.venv\Scripts\python.exe"

echo Installiere Abhaengigkeiten...
"%PYTHON%" -m pip install --upgrade pip -q
"%PYTHON%" -m pip install -r requirements.txt -q
"%PYTHON%" -m pip install -e . -q

echo Lade optionales deutsches spaCy-Modell...
"%PYTHON%" -c "import spacy; spacy.load('de_core_news_lg')" 2>nul
if errorlevel 1 (
    "%PYTHON%" -m spacy download de_core_news_lg
)

echo Baue Wissensgraph...
"%PYTHON%" -m kgexzerpt.cli build "!INPUT_FILE!" --out graph.json --format svelte
if errorlevel 1 (
    echo Fehler beim Erstellen von graph.json
    pause
    exit /b 1
)

echo Kopiere Graphdaten in Svelte-App...
if not exist "svelte-app\public" mkdir "svelte-app\public"
copy /Y graph.json "svelte-app\public\graph.json" >nul

where npm >nul 2>&1
if errorlevel 1 (
    echo npm nicht gefunden. Bitte installiere Node.js von https://nodejs.org
    pause
    exit /b 1
)

pushd "svelte-app"
echo Installiere Node-Abhaengigkeiten...
npm install

echo Starte Vite-Entwicklungsserver (Browser oeffnet sich automatisch)...
npm run dev

popd
endlocal
