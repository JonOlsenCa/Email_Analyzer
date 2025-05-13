# Email Analyzer Setup Instructions

This document provides instructions for setting up the Email Analyzer to automatically monitor and analyze emails from your Outlook folder.

## Initial Setup

1. Make sure you have Python 3.6 or higher installed on your system.
2. Install the required Python packages by running the `install_dependencies.bat` file or using the following command:
   ```
   pip install -r requirements.txt
   ```
3. Make sure Microsoft Outlook is installed and configured with your email account.

## Running the Email Analyzer

The easiest way to run the Email Analyzer is to use the provided batch file:

1. Open Command Prompt
2. Navigate to the Email_Analyzer directory
3. Run the following command:
   ```
   run_email_analyzer.bat
   ```

This will:
1. Start the Refresh Emails server (if it's not already running)
2. Analyze all emails in the "APWizard_Tickets" folder in your Outlook inbox
3. Open the results in your web browser

You can also run the analyzer directly with:
```
python analyze_outlook_emails.py
```

## Setting Up Automatic Monitoring

To set up automatic monitoring of new emails:

### Option 1: Using the PowerShell Script (Recommended)

1. Right-click on `setup_scheduled_task.ps1` and select "Run with PowerShell as Administrator"
2. If prompted, confirm that you want to run the script
3. The script will create a scheduled task that runs every 15 minutes to check for new emails

### Option 2: Manual Setup in Task Scheduler

1. Open Task Scheduler (search for "Task Scheduler" in the Start menu)
2. Click on "Create Basic Task..."
3. Enter a name (e.g., "Email Analyzer Monitor") and description, then click Next
4. Select "Daily" as the trigger, then click Next
5. Set the start time to the current time, then click Next
6. Select "Start a program" as the action, then click Next
7. Browse to the location of `monitor_emails.bat` in your Email_Analyzer directory
8. Set the "Start in" field to your Email_Analyzer directory
9. Click Next, then Finish
10. Right-click on the newly created task and select "Properties"
11. Go to the "Triggers" tab, select the trigger, and click "Edit"
12. Check "Repeat task every" and set it to 15 minutes
13. Set "for a duration of" to "Indefinitely"
14. Click OK, then OK again to save the changes

## Viewing the Results

The analysis results are saved in the "analyzed_emails" directory. To view the results:

1. Open the "analyzed_emails" directory
2. Open "index.html" in your web browser
3. This page shows a list of all analyzed emails with links to their detailed reports
4. Click on any email in the list to view its detailed analysis report

The index page is automatically updated whenever new emails are analyzed.

### Using the Refresh Button

The Email Analyzer includes a Refresh button that allows you to fetch new emails without restarting the application:

1. Click the "Refresh" button in the top-left corner of the index page
2. The analyzer will fetch any new emails that have arrived since the last analysis
3. New emails will be added to the table automatically

For the Refresh button to work, the Refresh Emails server must be running. This server is automatically started when you run `run_email_analyzer.bat`.

For more information about the Refresh functionality, see the `REFRESH_INSTRUCTIONS.md` file.

## Customizing the Configuration

If you want to change the configuration (e.g., monitor a different folder or email account), you can edit the `monitor_new_emails.py` file:

1. Open `monitor_new_emails.py` in a text editor
2. Modify the configuration variables at the top of the file:
   - `EMAIL_ACCOUNT`: The email account to monitor
   - `FOLDER_PATH`: The path to the Outlook folder to monitor
   - `OUTPUT_DIR`: The directory to save analysis reports
   - `FORMAT`: The output format (text, json, html)
3. Save the file

## Troubleshooting

If you encounter any issues:

1. Check the log files in the "logs" directory for error messages
2. Make sure Outlook is running and properly configured
3. Make sure the specified folder exists in your Outlook account
4. Try running the script manually to see if there are any errors

### Refresh Button Issues

If the Refresh button shows an error:

1. Make sure the Refresh Emails server is running
   - Look for a command window titled "Refresh Emails Server"
   - If it's not running, run `start_refresh_server.bat`
2. If the server is running but the button still doesn't work:
   - Try stopping the server with `stop_refresh_server.bat`
   - Then start it again with `start_refresh_server.bat`
3. Make sure you have the required dependencies installed
   - Run `install_dependencies.bat` to install them

For more detailed information, refer to the README.md, OUTLOOK_README.md, and REFRESH_INSTRUCTIONS.md files.
