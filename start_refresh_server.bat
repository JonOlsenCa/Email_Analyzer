@echo off
echo Checking if Refresh Emails server is already running...

:: Check if the server is already running on port 8001
netstat -ano | findstr :8001 > nul
if %errorlevel% equ 0 (
    echo Refresh Emails server is already running on port 8001.

    :: Test if the server is responding
    python test_refresh_server.py > nul
    if %errorlevel% equ 0 (
        echo Server is responding correctly.
    ) else (
        echo WARNING: Server is running but not responding correctly.
        echo Stopping the current server and starting a new one...

        :: Find and kill the process using port 8001
        for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001') do (
            taskkill /F /PID %%a > nul 2>&1
        )

        :: Start a new server
        goto :start_server
    )
) else (
    :start_server
    echo Starting Refresh Emails server...
    start "Refresh Emails Server" cmd /c "python refresh_emails.py && pause"

    :: Wait a moment for the server to start
    timeout /t 3 > nul

    :: Verify the server started successfully
    netstat -ano | findstr :8001 > nul
    if %errorlevel% equ 0 (
        echo Refresh Emails server started successfully.

        :: Test if the server is responding
        python test_refresh_server.py > nul
        if %errorlevel% equ 0 (
            echo Server is responding correctly.
        ) else (
            echo WARNING: Server started but is not responding correctly.
            echo The Refresh button may not work properly.
        )
    ) else (
        echo WARNING: Refresh Emails server may not have started correctly.
        echo The Refresh button may not work properly.
    )
)
