@echo off
setlocal

set "REPO_ROOT=%~dp0..\.."
for %%I in ("%REPO_ROOT%") do set "REPO_ROOT=%%~fI"

set "PYTHONPATH=%REPO_ROOT%\src"
set "PYTHON_EXE=%REPO_ROOT%\.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"

echo DiamondDust trial client: http://127.0.0.1:8765/
"%PYTHON_EXE%" -m diamonddust trial-client --root "%REPO_ROOT%" --port 8765

endlocal
