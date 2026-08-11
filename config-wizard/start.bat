@echo off
REM SailingPD Config Wizard - Windows startscript
REM Dubbelklik dit bestand om de wizard te starten.
setlocal
cd /d "%~dp0"

REM Kies de Python-starter: 'py' (Python launcher) indien aanwezig, anders 'python'
set "PY=python"
where py >nul 2>nul && set "PY=py"

REM Omgeving opzetten zodra de venv ontbreekt OF de pakketten er niet in zitten.
REM Die tweede controle is nodig: een afgebroken pip-installatie laat een venv
REM achter die compleet lijkt, waarna een volgende start strandt op
REM "ModuleNotFoundError: flask".
set "NEED_SETUP=1"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -c "import flask, PIL" >nul 2>nul && set "NEED_SETUP=0"
)

if "%NEED_SETUP%"=="1" (
  if not exist ".venv\Scripts\python.exe" (
    echo Eerste keer: virtuele omgeving aanmaken...
    %PY% -m venv .venv
    if errorlevel 1 (
      echo.
      echo FOUT: Python is niet gevonden. Installeer Python 3.9+ van https://www.python.org/downloads/
      echo Vink bij de installatie "Add Python to PATH" aan.
      echo.
      pause
      exit /b 1
    )
  ) else (
    echo Benodigde pakketten ontbreken - opnieuw installeren...
  )
  ".venv\Scripts\python.exe" -m pip install --quiet -r requirements.txt
  if errorlevel 1 (
    echo.
    echo FOUT: kon Flask/Pillow niet installeren ^(internetverbinding nodig^).
    echo Maak verbinding met internet en start dit bestand opnieuw.
    echo.
    pause
    exit /b 1
  )
  echo Klaar.
)

echo.
echo ===============================================================
echo   SailingPD Config Wizard
echo   Zorg dat deze map in je SailingPD-installatiemap staat
echo   Open in de browser: http://localhost:5001
echo ===============================================================
echo.

REM Open de browser (laadt de pagina nog niet? even verversen zodra de server draait)
start "" http://localhost:5001

REM Start de wizard (dit venster open laten; sluiten stopt de wizard)
".venv\Scripts\python.exe" app.py

pause
endlocal
