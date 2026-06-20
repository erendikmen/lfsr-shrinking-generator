@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo  Shrinking Generator Simulator - Windows EXE Builder
echo ============================================================
echo.

echo [1/3] Checking Python...
python --version
if errorlevel 1 (
    echo Python was not found. Install Python 3 from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo [2/3] Installing / updating PyInstaller...
python -m pip install --upgrade pip pyinstaller
if errorlevel 1 (
    echo PyInstaller installation failed.
    pause
    exit /b 1
)

echo.
echo [3/3] Building single-file Windows executable...
python -m PyInstaller --onefile --windowed --name ShrinkingGeneratorSimulator ShrinkingGeneratorSimulator.pyw
if errorlevel 1 (
    echo Build failed.
    pause
    exit /b 1
)

echo.
echo Done! Your EXE is here:
echo %cd%\dist\ShrinkingGeneratorSimulator.exe
echo.
pause
