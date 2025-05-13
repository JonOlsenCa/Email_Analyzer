@echo off
echo Stopping Refresh Emails server...

:: Find the process ID using port 8001
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001') do (
    set PID=%%a
    goto :found
)

:found
if defined PID (
    echo Found server process with PID: %PID%
    taskkill /F /PID %PID%
    if %errorlevel% equ 0 (
        echo Refresh Emails server stopped successfully.
    ) else (
        echo Failed to stop the Refresh Emails server.
    )
) else (
    echo Refresh Emails server is not running.
)

pause
