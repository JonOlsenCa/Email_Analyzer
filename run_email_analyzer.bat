@echo off
echo Starting Email Analyzer...

:: Start the Refresh Emails server if it's not already running
call start_refresh_server.bat

echo Running Email Analyzer...
python analyze_outlook_emails.py

echo Opening index.html in browser...
start analyzed_emails\index.html

echo Email Analyzer is now running.
echo The Refresh button will work as long as the Refresh Emails Server is running.
