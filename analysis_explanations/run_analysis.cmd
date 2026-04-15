@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "REPO_ROOT=%%~fI"
set "PYTHON_EXE=%REPO_ROOT%\.venv\Scripts\python.exe"
set "ANALYSIS_SCRIPT=%SCRIPT_DIR%run_explanation_analysis.py"

if not exist "%PYTHON_EXE%" (
    echo Python executable not found at "%PYTHON_EXE%"
    exit /b 1
)

if not exist "%ANALYSIS_SCRIPT%" (
    echo Analysis script not found at "%ANALYSIS_SCRIPT%"
    exit /b 1
)

pushd "%REPO_ROOT%"
"%PYTHON_EXE%" "%ANALYSIS_SCRIPT%" %*
set "EXIT_CODE=%ERRORLEVEL%"
popd

exit /b %EXIT_CODE%
