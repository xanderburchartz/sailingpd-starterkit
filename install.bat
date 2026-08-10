@echo off
REM ─────────────────────────────────────────────────────────────
REM  SailingPD Starter Kit - installer  (Windows)
REM  Plaats de map 'sailingpd-starterkit' IN je SailingPD-map
REM  en dubbelklik dit bestand.
REM ─────────────────────────────────────────────────────────────
setlocal
set "HERE=%~dp0"
for %%I in ("%HERE%..") do set "SPD_DIR=%%~fI"

echo SailingPD-map: %SPD_DIR%
if not exist "%SPD_DIR%\web_root" goto notfound
if not exist "%SPD_DIR%\sailingPD.exe" if not exist "%SPD_DIR%\sailingPD" goto notfound

echo -^> Config-wizard installeren...
if exist "%SPD_DIR%\config-wizard" rmdir /s /q "%SPD_DIR%\config-wizard"
xcopy /e /i /q "%HERE%config-wizard" "%SPD_DIR%\config-wizard" >nul

echo -^> Web-menu (startpagina) installeren...
set "WR=%SPD_DIR%\web_root"
if not exist "%WR%\index.html.orig-spa" if exist "%WR%\index.html" copy /y "%WR%\index.html" "%WR%\index.html.orig-spa" >nul
if exist "%WR%\index.html.orig-spa" copy /y "%WR%\index.html.orig-spa" "%WR%\dials.html" >nul
copy /y "%HERE%web-menu\index.html" "%WR%\index.html" >nul
if not exist "%WR%\thumbs" mkdir "%WR%\thumbs"
copy /y "%HERE%web-menu\thumbs\*.jpg" "%WR%\thumbs\" >nul

echo.
echo Klaar!  Volgende stappen:
echo   1) Start de wizard: dubbelklik  config-wizard\start.bat   (open http://localhost:5001)
echo   2) Doorloop de wizard en klik aan het eind op 'SailingPD starten'.
echo   3) Open het dashboard-menu:  http://localhost:9090/
echo.
echo (De oude standaard-webpagina blijft op  http://localhost:9090/dials.html )
echo.
pause
exit /b 0

:notfound
echo.
echo FOUT: dit lijkt niet je SailingPD-installatiemap (geen web_root of sailingPD gevonden).
echo Plaats de map 'sailingpd-starterkit' IN je SailingPD-map en probeer opnieuw.
pause
exit /b 1
