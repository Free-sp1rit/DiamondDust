@echo off
setlocal EnableExtensions

set "REPO_ROOT=%~dp0..\.."
for %%I in ("%REPO_ROOT%") do set "REPO_ROOT=%%~fI"
cd /d "%REPO_ROOT%" || goto fail_cd

set "LOG_DIR=%REPO_ROOT%\.diamonddust-trial\logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
set "LOG_FILE=%LOG_DIR%\trial-client-launch.log"

echo.>> "%LOG_FILE%"
echo ==== DiamondDust trial client launch ====>> "%LOG_FILE%"
echo Repo root: %REPO_ROOT%>> "%LOG_FILE%"

set "PYTHONPATH=%REPO_ROOT%\src"
set "PYTHON_EXE=%REPO_ROOT%\.venv\Scripts\python.exe"

if exist "%PYTHON_EXE%" (
    "%PYTHON_EXE%" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >> "%LOG_FILE%" 2>&1
    if errorlevel 1 goto invalid_venv_python
) else (
    call :find_python
    if errorlevel 1 goto no_python

    echo Creating local Python environment in "%REPO_ROOT%\.venv" ...
    echo Creating local Python environment...>> "%LOG_FILE%"
    %SYSTEM_PYTHON% -m venv "%REPO_ROOT%\.venv" >> "%LOG_FILE%" 2>&1
    if errorlevel 1 goto setup_failed

    set "PYTHON_EXE=%REPO_ROOT%\.venv\Scripts\python.exe"
    echo Installing DiamondDust trial dependencies ...
    echo Installing DiamondDust trial dependencies...>> "%LOG_FILE%"
    "%PYTHON_EXE%" -m pip install -e "%REPO_ROOT%" >> "%LOG_FILE%" 2>&1
    if errorlevel 1 goto setup_failed
)

set "FRONTEND_DIST=%REPO_ROOT%\frontend\trial-client\dist"
set "WORKSPACE_DIR=%~1"

echo DiamondDust trial client: http://127.0.0.1:8765/
echo If the browser opens before the page is ready, wait a moment and refresh.
echo Launch log: %LOG_FILE%
start "" "http://127.0.0.1:8765/"

if "%WORKSPACE_DIR%"=="" (
    if exist "%FRONTEND_DIST%\index.html" (
        "%PYTHON_EXE%" -m diamonddust trial-client --root "%REPO_ROOT%" --port 8765 --frontend-dist "%FRONTEND_DIST%"
    ) else (
        "%PYTHON_EXE%" -m diamonddust trial-client --root "%REPO_ROOT%" --port 8765
    )
) else (
    if not exist "%WORKSPACE_DIR%" mkdir "%WORKSPACE_DIR%"
    if exist "%FRONTEND_DIST%\index.html" (
        "%PYTHON_EXE%" -m diamonddust trial-client --root "%REPO_ROOT%" --port 8765 --input-dir "%WORKSPACE_DIR%\input-notes" --vault-root "%WORKSPACE_DIR%\knowledge-vault" --feedback-dir "%WORKSPACE_DIR%\feedback" --frontend-dist "%FRONTEND_DIST%"
    ) else (
        "%PYTHON_EXE%" -m diamonddust trial-client --root "%REPO_ROOT%" --port 8765 --input-dir "%WORKSPACE_DIR%\input-notes" --vault-root "%WORKSPACE_DIR%\knowledge-vault" --feedback-dir "%WORKSPACE_DIR%\feedback"
    )
)
if errorlevel 1 goto server_failed

endlocal
exit /b 0

:find_python
py -3.11 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >> "%LOG_FILE%" 2>&1
if not errorlevel 1 (
    set "SYSTEM_PYTHON=py -3.11"
    exit /b 0
)
py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >> "%LOG_FILE%" 2>&1
if not errorlevel 1 (
    set "SYSTEM_PYTHON=py -3"
    exit /b 0
)
python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >> "%LOG_FILE%" 2>&1
if not errorlevel 1 (
    set "SYSTEM_PYTHON=python"
    exit /b 0
)
exit /b 1

:fail_cd
echo Could not enter the DiamondDust package directory.
pause
exit /b 1

:no_python
echo DiamondDust trial client requires Python 3.11 or newer.
echo Install Python from https://www.python.org/downloads/windows/ and enable "Add python.exe to PATH".
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

:server_failed
echo DiamondDust trial client stopped with an error.
echo See the console output above and launch log: %LOG_FILE%
pause
exit /b 1
