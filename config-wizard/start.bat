@echo off
REM SailingPD Config Wizard - Windows startscript
REM Dubbelklik dit bestand om de wizard te starten.
setlocal
cd /d "%~dp0"

REM Kies de Python-starter: 'py' (Python launcher) indien aanwezig, anders 'python'
set "PY=python"
where py >nul 2>nul && set "PY=py"

REM Eerste keer: virtuele omgeving aanmaken en packages installeren
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
  ".venv\Scripts\python.exe" -m pip install --quiet -r requirements.txt
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
