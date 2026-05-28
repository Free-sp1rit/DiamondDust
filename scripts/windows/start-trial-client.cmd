@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "REPO_ROOT=%~dp0..\.."
for %%I in ("%REPO_ROOT%") do set "REPO_ROOT=%%~fI"
cd /d "%REPO_ROOT%" || goto fail_cd

set "RUNTIME_DIR=%REPO_ROOT%\.diamonddust-trial"
set "LOG_DIR=%RUNTIME_DIR%\logs"
set "SECRETS_DIR=%RUNTIME_DIR%\secrets"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%SECRETS_DIR%" mkdir "%SECRETS_DIR%"
set "LOG_FILE=%LOG_DIR%\trial-client-launch.log"
set "SECRETS_ENV_FILE=%SECRETS_DIR%\provider-secrets.env"

echo.>> "%LOG_FILE%"
echo ==== DiamondDust trial client launch ====>> "%LOG_FILE%"
echo Repo root: %REPO_ROOT%>> "%LOG_FILE%"

set "PYTHONPATH=%REPO_ROOT%\src"
set "PYTHON_EXE=%REPO_ROOT%\.venv\Scripts\python.exe"

if exist "%PYTHON_EXE%" (
    "%PYTHON_EXE%" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >> "%LOG_FILE%" 2>&1
    if errorlevel 1 goto invalid_venv_python
) else (
    call :select_python
    if errorlevel 1 goto no_python

    echo Creating local Python environment in "%REPO_ROOT%\.venv" ...
    echo Creating local Python environment with !SYSTEM_PYTHON!...>> "%LOG_FILE%"
    call !SYSTEM_PYTHON! -m venv "%REPO_ROOT%\.venv" >> "%LOG_FILE%" 2>&1
    if errorlevel 1 goto setup_failed

    set "PYTHON_EXE=%REPO_ROOT%\.venv\Scripts\python.exe"
    echo Installing DiamondDust trial dependencies ...
    echo Installing DiamondDust trial dependencies...>> "%LOG_FILE%"
    "%PYTHON_EXE%" -m pip install -e "%REPO_ROOT%" >> "%LOG_FILE%" 2>&1
    if errorlevel 1 goto setup_failed
)

call :select_port
if errorlevel 1 goto port_failed

set "FRONTEND_DIST=%REPO_ROOT%\frontend\trial-client\dist"
set "WORKSPACE_DIR=%~1"

echo DiamondDust trial client: http://127.0.0.1:%PORT%/
echo If the browser opens before the page is ready, wait a moment and refresh.
echo Launch log: %LOG_FILE%
echo API key file: %SECRETS_ENV_FILE%
start "" "http://127.0.0.1:%PORT%/"

if "%WORKSPACE_DIR%"=="" (
    if exist "%FRONTEND_DIST%\index.html" (
        "%PYTHON_EXE%" -m diamonddust trial-client --root "%REPO_ROOT%" --port %PORT% --secrets-env-file "%SECRETS_ENV_FILE%" --frontend-dist "%FRONTEND_DIST%"
    ) else (
        "%PYTHON_EXE%" -m diamonddust trial-client --root "%REPO_ROOT%" --port %PORT% --secrets-env-file "%SECRETS_ENV_FILE%"
    )
) else (
    if not exist "%WORKSPACE_DIR%" mkdir "%WORKSPACE_DIR%"
    if exist "%FRONTEND_DIST%\index.html" (
        "%PYTHON_EXE%" -m diamonddust trial-client --root "%REPO_ROOT%" --port %PORT% --secrets-env-file "%SECRETS_ENV_FILE%" --input-dir "%WORKSPACE_DIR%\input-notes" --vault-root "%WORKSPACE_DIR%\knowledge-vault" --feedback-dir "%WORKSPACE_DIR%\feedback" --frontend-dist "%FRONTEND_DIST%"
    ) else (
        "%PYTHON_EXE%" -m diamonddust trial-client --root "%REPO_ROOT%" --port %PORT% --secrets-env-file "%SECRETS_ENV_FILE%" --input-dir "%WORKSPACE_DIR%\input-notes" --vault-root "%WORKSPACE_DIR%\knowledge-vault" --feedback-dir "%WORKSPACE_DIR%\feedback"
    )
)
if errorlevel 1 goto server_failed

endlocal
exit /b 0

:select_python
set "SYSTEM_PYTHON="
call :try_python py -3.13
if defined SYSTEM_PYTHON exit /b 0
call :try_python py -3.12
if defined SYSTEM_PYTHON exit /b 0
call :try_python py -3.11
if defined SYSTEM_PYTHON exit /b 0
call :try_python py -3
if defined SYSTEM_PYTHON exit /b 0
call :try_python python
if defined SYSTEM_PYTHON exit /b 0
exit /b 1

:try_python
%* -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >> "%LOG_FILE%" 2>&1
if not errorlevel 1 (
    set "SYSTEM_PYTHON=%*"
    echo Selected Python: %*>> "%LOG_FILE%"
)
exit /b 0

:select_port
if not "%DIAMONDDUST_TRIAL_PORT%"=="" (
    set "PORT=%DIAMONDDUST_TRIAL_PORT%"
    echo Selected port from DIAMONDDUST_TRIAL_PORT: !PORT!>> "%LOG_FILE%"
    exit /b 0
)
set "PORT="
for %%P in (8765 8766 8767 8768 8769 8770 8771 8772 8773 8774 8775) do (
    if not defined PORT (
        netstat -ano | findstr /R /C:":%%P .*LISTENING" >nul 2>&1
        if errorlevel 1 set "PORT=%%P"
    )
)
if defined PORT (
    echo Selected port: %PORT%>> "%LOG_FILE%"
    exit /b 0
)
exit /b 1

:fail_cd
echo Could not enter the DiamondDust package directory.
pause
exit /b 1

:no_python
echo DiamondDust trial client requires Python 3.11 or newer.
echo Python 3.13 is supported, but the launcher could not find it through py or python.
echo Run: py -0p
echo Launch log: %LOG_FILE%
pause
exit /b 1

:invalid_venv_python
echo Existing .venv does not use Python 3.11 or newer.
echo Delete "%REPO_ROOT%\.venv" and run this launcher again.
echo Launch log: %LOG_FILE%
pause
exit /b 1

:setup_failed
echo DiamondDust trial client setup failed.
echo See launch log: %LOG_FILE%
pause
exit /b 1

:port_failed
echo Could not find an available port from 8765 through 8775.
echo Set DIAMONDDUST_TRIAL_PORT to a free port and run again.
echo Launch log: %LOG_FILE%
pause
exit /b 1

:server_failed
echo DiamondDust trial client stopped with an error.
echo See the console output above and launch log: %LOG_FILE%
pause
exit /b 1
