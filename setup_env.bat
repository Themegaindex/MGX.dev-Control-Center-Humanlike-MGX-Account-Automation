@echo off
setlocal

set SILENT=0
if /I "%~1"=="--silent" set SILENT=1

set ENV_DIR=env
set REQ_FILE=requirements.txt
set LOG_FILE=%TEMP%\setup_env.log
set SENTINEL=%ENV_DIR%\deps.ok
set FINAL_MSG=
set EXITCODE=0

echo [INFO] Prüfe Python-Installation ...
python --version >nul 2>&1
if errorlevel 1 (
    set FINAL_MSG=[FEHLER] Python wurde nicht gefunden. Bitte installiere Python 3.11+ und füge es zur PATH-Variable hinzu.
    set EXITCODE=1
    goto :finish
)

if not exist "%ENV_DIR%" (
    echo [INFO] Virtuelle Umgebung wird erstellt ...
    python -m venv "%ENV_DIR%"
    if errorlevel 1 (
        set FINAL_MSG=[FEHLER] Erstellung der virtuellen Umgebung ist fehlgeschlagen.
        set EXITCODE=1
        goto :finish
    )
) else (
    echo [INFO] Virtuelle Umgebung '%ENV_DIR%' gefunden.
)

if not exist "%REQ_FILE%" (
    set FINAL_MSG=[FEHLER] %REQ_FILE% fehlt. Bitte lege die Datei an und starte das Skript erneut.
    set EXITCODE=1
    goto :finish
)

call "%ENV_DIR%\Scripts\activate.bat" >nul 2>&1
if errorlevel 1 (
    set FINAL_MSG=[FEHLER] Aktivierung der virtuellen Umgebung ist fehlgeschlagen.
    set EXITCODE=1
    goto :finish
)

echo [INFO] Prüfe/aktualisiere Python-Pakete ...
del "%LOG_FILE%" >nul 2>&1
pip install --disable-pip-version-check -r "%REQ_FILE%" >"%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo [FEHLER] Installation der Abhängigkeiten ist fehlgeschlagen. Details:
    type "%LOG_FILE%"
    set FINAL_MSG=[FEHLER] Paketinstallation fehlgeschlagen.
    set EXITCODE=1
    goto :finish
)

echo Bereit > "%SENTINEL%"
set FINAL_MSG=[OK] Umgebung OK – alles bereit.

:finish
if defined FINAL_MSG echo %FINAL_MSG%
if "%SILENT%"=="0" pause
exit /b %EXITCODE%
