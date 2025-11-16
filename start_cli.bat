@echo off
setlocal

set BASE_DIR=%~dp0
set ENV_DIR=%BASE_DIR%env
set SENTINEL=%ENV_DIR%\deps.ok

if not exist "%ENV_DIR%" (
    call "%BASE_DIR%setup_env.bat" --silent
    if errorlevel 1 (
        echo [FEHLER] Die Umgebung konnte nicht vorbereitet werden.
        exit /b 1
    )
) else if not exist "%SENTINEL%" (
    call "%BASE_DIR%setup_env.bat" --silent
    if errorlevel 1 (
        echo [FEHLER] Die Umgebung konnte nicht vorbereitet werden.
        exit /b 1
    )
)

call "%ENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo [FEHLER] Aktivierung der virtuellen Umgebung ist fehlgeschlagen.
    exit /b 1
)

python "%BASE_DIR%cli.py"
set EXITCODE=%ERRORLEVEL%

if %EXITCODE% neq 0 (
    echo [FEHLER] CLI wurde mit Fehlercode %EXITCODE% beendet.
) else (
    echo [OK] CLI beendet.
)

exit /b %EXITCODE%
