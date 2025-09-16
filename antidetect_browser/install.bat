@echo off
echo ========================================
echo Custom Anti-Detect Browser Installer
echo ========================================
echo.

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Creating directories...
if not exist "profiles" mkdir profiles

echo.
echo Installation complete!
echo.
echo To run the browser:
echo python main.py
echo.
pause 