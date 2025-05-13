@echo off
echo Installing Email Analyzer dependencies...

:: Check if pip is available
where pip > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip not found. Please make sure Python is installed correctly.
    pause
    exit /b 1
)

:: Install dependencies from requirements.txt
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo Dependencies installed successfully.
) else (
    echo ERROR: Failed to install dependencies.
)

pause
