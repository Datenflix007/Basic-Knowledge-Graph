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
echo   [2]  Eigene Exzerpte hinzufuegen (Dateidialog, beliebig viele)
echo.
set /p CHOICE="Auswahl (1 oder 2): "

set /a INPUT_COUNT=0
set "INPUT_LIST=%TEMP%\kgexzerpt_inputs_%RANDOM%_%RANDOM%.txt"
if exist "!INPUT_LIST!" del "!INPUT_LIST!" >nul 2>&1

if not "%CHOICE%"=="2" goto after_excerpts

:add_excerpts
echo.
echo Oeffne Dateidialog. Du kannst eine oder mehrere Dateien auswaehlen.
for /f "usebackq delims=" %%F in (`powershell -NoProfile -Command "Add-Type -AssemblyName System.Windows.Forms; $d = New-Object System.Windows.Forms.OpenFileDialog; $d.Title = 'Exzerpte auswaehlen'; $d.Filter = 'Markdown/PDF (*.md;*.pdf)|*.md;*.pdf|Markdown (*.md)|*.md|PDF (*.pdf)|*.pdf|Alle Dateien (*.*)|*.*'; $d.InitialDirectory = '%~dp0'; $d.Multiselect = $true; if ($d.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) { $d.FileNames | ForEach-Object { Write-Output $_ } }"`) do (
    set /a INPUT_COUNT+=1
    >> "!INPUT_LIST!" echo(%%F
    echo   [+] %%F
)

if !INPUT_COUNT! EQU 0 (
    echo Keine Exzerpte ausgewaehlt.
    set /p RETRY="Nochmal auswaehlen? (j/n): "
    if /I "!RETRY!"=="j" goto add_excerpts
) else (
    echo.
    echo Aktuell ausgewaehlte Exzerpte: !INPUT_COUNT!
    set /p MORE="Weitere Exzerpte hinzufuegen? (j = weitere, sonst Graph bauen): "
    if /I "!MORE!"=="j" goto add_excerpts
)

:after_excerpts
if !INPUT_COUNT! EQU 0 (
    set "EXAMPLE_FILE=%~dp0example.md"
    > "!INPUT_LIST!" echo(!EXAMPLE_FILE!
    echo Erstelle Standardbeispiel...
    (
        echo ^| Seite ^| Inhalt ^| Anmerkung ^|
        echo ^|-------^|--------^|-----------^|
        echo ^| 1 ^| Dies ist ein Beispieltext. ^| Wichtige Information ^|
    ) > "!EXAMPLE_FILE!"
)

echo.
echo Eingabedateien:
type "!INPUT_LIST!"
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
set "KG_INPUT_LIST=!INPUT_LIST!"
set "KG_PYTHON=%PYTHON%"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$inputs = Get-Content -LiteralPath $env:KG_INPUT_LIST; & $env:KG_PYTHON -m kgexzerpt.cli build @inputs --out graph.json --format svelte; exit $LASTEXITCODE"
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
call npm install
if errorlevel 1 (
    echo Fehler beim Installieren der Node-Abhaengigkeiten.
    popd
    pause
    exit /b 1
)

echo Starte Vite-Entwicklungsserver und oeffne den Wissensgraphen im Browser...
echo Falls der Browser nicht automatisch startet, oeffne die im Terminal angezeigte Local-URL.
call npm run dev -- --host 127.0.0.1 --open

popd
if exist "!INPUT_LIST!" del "!INPUT_LIST!" >nul 2>&1
endlocal
