@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo Python 3 is not installed or is not available in PATH.
    echo Install it from https://www.python.org/downloads/windows/
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating a local Python environment...
    python -m venv .venv
    if errorlevel 1 (
        echo Could not create the Python environment.
        pause
        exit /b 1
    )
)

echo Installing build dependencies...
".venv\Scripts\python.exe" -m pip install -q -r build-requirements.txt
if errorlevel 1 (
    echo Could not install build dependencies.
    pause
    exit /b 1
)

echo Building portable YouTubeDownloader folder...
".venv\Scripts\python.exe" -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onedir ^
    --windowed ^
    --name YouTubeDownloader ^
    --icon icon.ico ^
    --add-data "icon.ico;." ^
    --collect-all yt_dlp ^
    --collect-all instaloader ^
    app.py

if errorlevel 1 (
    echo Build failed.
    pause
    exit /b 1
)

echo Building automatic updater...
".venv\Scripts\python.exe" -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onefile ^
    --windowed ^
    --name Updater ^
    --icon icon.ico ^
    --add-data "icon.ico;." ^
    updater.py

if errorlevel 1 (
    echo Updater build failed.
    pause
    exit /b 1
)

copy /Y "dist\Updater.exe" "dist\YouTubeDownloader\Updater.exe" >nul
if errorlevel 1 (
    echo Could not place the updater beside the application.
    pause
    exit /b 1
)

echo.
echo Done: dist\YouTubeDownloader\YouTubeDownloader.exe
echo Keep the complete YouTubeDownloader folder together.
echo Put ffmpeg.exe next to the EXE before downloading.
pause
