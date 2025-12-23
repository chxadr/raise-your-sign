:: NOTE : this script relies on Python install manager.
::        see https://www.python.org/downloads/windows/

@echo off
setlocal enabledelayedexpansion

set "VENV_DIR=.venv"
set "PY_VERSION=3.13"

if exist "%VENV_DIR%" (
   echo %VENV_DIR% already exists
   echo if this is not a mistake, remove the directory first
   exit /b 1
)

echo Checking Python %PY_VERSION% version requirements ...

:: Check Python version
py -V:%PY_VERSION% --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python %PY_VERSION% not found.
    echo Attempting to install Python %PY_VERSION% ...
    py install %PY_VERSION%   
    if %ERRORLEVEL% neq 0 (
        echo Failed to install Python %PY_VERSION%. Please install it manually
        exit /b 1
    )
    echo Python %PY_VERSION% installed successfully
)
:: Create the virtual environment
echo Creating Python virtual environment ...
echo     Python version: %PY_VERSION%
echo     Location: %VENV_DIR%%NC%
py -V:%PY_VERSION% -m venv %VENV_DIR%
if %ERRORLEVEL% neq 0 (
    echo Failed to create Python virtual environment
    if exist "%VENV_DIR%" (
        rmdir /s /q "%VENV_DIR%"
    )
    exit /b 1
)
echo Python virtual environment created at %VENV_DIR%%NC%

:: Install requirements
%VENV_DIR%\Scripts\pip install -e .
if %ERRORLEVEL% neq 0 (
    echo Failed to install requirements
    echo Consider a manual installation of all dependencies
    echo     run: %VENV_DIR%\Scripts\activate
    echo     run: pip install ^<PACKAGE_NAME^>==^<VERSION^>
    echo See pyproject.toml
    echo Or delete %VENV_DIR% with rmdir /s /q %VENV_DIR%
    exit /b 1
)
echo Python virtual environment is ready to be used
echo To activate, run: %VENV_DIR%\Scripts\activate
exit /b 0

