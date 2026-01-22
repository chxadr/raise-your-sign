@echo off
cd /d "%~dp0..\main" && pyinstaller main.spec && pause
