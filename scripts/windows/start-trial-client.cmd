@echo off
setlocal

set "REPO_ROOT=%~dp0..\.."
for %%I in ("%REPO_ROOT%") do set "REPO_ROOT=%%~fI"

set "PYTHONPATH=%REPO_ROOT%\src"
set "PYTHON_EXE=%REPO_ROOT%\.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
    echo Creating local Python environment in "%REPO_ROOT%\.venv" ...
    python -m venv "%REPO_ROOT%\.venv"
    if errorlevel 1 exit /b 1
    set "PYTHON_EXE=%REPO_ROOT%\.venv\Scripts\python.exe"
    echo Installing DiamondDust trial dependencies ...
    "%PYTHON_EXE%" -m pip install -e "%REPO_ROOT%"
    if errorlevel 1 exit /b 1
)
set "FRONTEND_DIST=%REPO_ROOT%\frontend\trial-client\dist"
set "WORKSPACE_DIR=%~1"

echo DiamondDust trial client: http://127.0.0.1:8765/
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

endlocal
