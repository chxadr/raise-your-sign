@echo off
echo Cleaning up build artifacts and temporary files...

:: Remove build/ directory
echo Removing build/ ...
rmdir /s /q build

:: Remove dist/ directory
echo Removing dist/ ...
rmdir /s /q dist

:: Remove .egg-info directories inside src/
echo Removing *.egg-info directories inside src/...
for /d /r src %%d in (*.egg-info) do rmdir /s /q "%%d"

:: Remove __pycache__ directories inside src/
echo Removing __pycache__ directories inside src/...
for /d /r src %%d in (__pycache__) do rmdir /s /q "%%d"

:: Remove .pyc files inside src/
echo Removing *.pyc files inside src/...
for /r src %%f in (*.pyc) do del /q "%%f"

echo Clean complete!
pause

