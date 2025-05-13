@echo off
REM Email Analyzer Monitor
REM This batch file runs the email monitoring script

echo Email Analyzer Monitor
echo =====================
echo.

cd /d "%~dp0"
python monitor_new_emails.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error monitoring emails. Check the logs for details.
    exit /b 1
)

echo.
echo Monitoring complete.
