@echo off
REM Email Analyzer for Outlook
REM This batch file makes it easier to analyze emails from Outlook

echo Email Analyzer for Outlook
echo ========================
echo.

REM Set default values
set EMAIL_ACCOUNT=jon@olsenconsulting.ca
set FOLDER_PATH=Inbox/APWizard_Tickets
set LIMIT=100
set FORMAT=html
set OUTPUT_DIR=analyzed_emails
set SAVE_EML=

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :run
if /i "%~1"=="--email-account" (
    set EMAIL_ACCOUNT=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--folder-path" (
    set FOLDER_PATH=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--limit" (
    set LIMIT=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--format" (
    set FORMAT=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--output-dir" (
    set OUTPUT_DIR=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--save-eml" (
    set SAVE_EML=--save-eml
    shift
    goto :parse_args
)
if /i "%~1"=="--verbose" (
    set VERBOSE=--verbose
    shift
    goto :parse_args
)
if /i "%~1"=="--help" (
    goto :show_help
)
shift
goto :parse_args

:show_help
echo Usage: analyze_outlook.bat [options]
echo.
echo Options:
echo   --email-account EMAIL   Email account to use (default: jon@olsenconsulting.ca)
echo   --folder-path PATH      Path to the Outlook folder (default: Inbox/APWizard_Tickets)
echo   --limit NUMBER          Maximum number of emails to retrieve (default: 100)
echo   --format FORMAT         Output format (text, json, html) (default: html)
echo   --output-dir DIR        Directory to save analysis reports (default: analyzed_emails)
echo   --save-eml              Save emails as EML files
echo   --verbose               Enable verbose output
echo   --help                  Show this help message
goto :eof

:run
echo Analyzing emails from %FOLDER_PATH% in account %EMAIL_ACCOUNT%
echo Retrieving up to %LIMIT% emails
echo Output format: %FORMAT%
echo Output directory: %OUTPUT_DIR%
echo.

python analyze_outlook_emails.py --email-account "%EMAIL_ACCOUNT%" --folder-path "%FOLDER_PATH%" --limit %LIMIT% --format %FORMAT% --output-dir "%OUTPUT_DIR%" %SAVE_EML% %VERBOSE%

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error analyzing emails. Check the logs for details.
    pause
    exit /b 1
)

echo.
echo Analysis complete. Reports saved to: %OUTPUT_DIR%
echo Opening index file...

start "" "%OUTPUT_DIR%\index.html"

echo.
pause
