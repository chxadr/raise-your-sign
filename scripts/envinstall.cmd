@echo off
setlocal enabledelayedexpansion

set VENV_DIR=.venv
set PY_VERSION=3.13

color 0A
echo Checking Python %PY_VERSION% version requirements ...

:: Check Python version
py -V:%PY_VERSION% --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    color 0A
    echo Python %PY_VERSION% not found.
    echo Attempting to install Python %PY_VERSION% ...
    py install %PY_VERSION%   
    if %ERRORLEVEL% neq 0 (
       color 0C
       echo Failed to install Python %PY_VERSION%. Please install it manually
       exit /b 1
    )
    color 0A
    echo Python %PY_VERSION% installed successfully
)
:: Create the virtual environment
color 0A
echo Creating Python virtual environment ...
echo     Python version: %PY_VERSION%
echo     Location: %VENV_DIR%
py -V:%PY_VERSION% -m venv %VENV_DIR%
if %ERRORLEVEL% neq 0 (
    color 0C
    echo Failed to create Python virtual environment
    if exist "%VENV_DIR%" (
        rmdir /s /q "%VENV_DIR%"
    )
    exit /b 1
)
color 0A
echo Python virtual environment created at %VENV_DIR%

:: Install requirements
%VENV_DIR%\Scripts\pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    color 0C
    echo Failed to install requirements
    echo Consider a manual installation of all dependencies
    echo     run: %VENV_DIR%\Scripts\activate
    echo     run: pip install ^<PACKAGE_NAME^>==^<VERSION^>
    echo Or delete %VENV_DIR% with rmdir /s /q %VENV_DIR%
    exit /b 1
)
color 0A
echo Python virtual environment is ready to be used
echo To activate, run: %VENV_DIR%\Scripts\activate
exit /b 0

