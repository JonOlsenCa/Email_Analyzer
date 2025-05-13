@echo off
REM Email Analyzer Batch File for Windows
REM This batch file makes it easier to run the Email Analyzer on Windows

if "%~1"=="" (
    echo Error: No email file specified.
    echo Usage: analyze_email.bat [email_file] [options]
    echo.
    echo Options:
    echo   -o, --output   Output file for the analysis report
    echo   -f, --format   Output format (text, json, html)
    echo   -v, --verbose  Enable verbose output
    echo   --version      Show the version and exit
    exit /b 1
)

python email_analyzer.py %*
