# Email Analyzer Refresh Functionality

This document explains how to use the Refresh functionality in the Email Analyzer.

## Overview

The Refresh button allows you to fetch new emails that have arrived in your Outlook folder since the last time you ran the Email Analyzer, without having to restart the entire application.

## How It Works

1. When you click the Refresh button, the Email Analyzer:
   - Finds the latest email date in your current table
   - Makes an API request to fetch only new emails that arrived after that date
   - Adds any new emails to the table
   - Updates the email count
   - Maintains your current sorting and filtering

## Requirements

The Refresh functionality requires the Refresh Emails server to be running. This server handles the API requests to fetch new emails from Outlook.

## Starting the Server

The Refresh Emails server is automatically started when you run the Email Analyzer using the `run_email_analyzer.bat` script. You'll see a separate command window titled "Refresh Emails Server" that should remain open while you're using the Email Analyzer.

If you need to start the server manually:
1. Open Command Prompt
2. Navigate to the Email_Analyzer directory
3. Run: `start_refresh_server.bat`

## Stopping the Server

When you're done using the Email Analyzer, you can stop the Refresh Emails server:
1. Close the "Refresh Emails Server" command window, or
2. Run: `stop_refresh_server.bat`

## Troubleshooting

If the Refresh button shows an error:
1. Make sure the Refresh Emails server is running
2. Check that the server window is open and hasn't encountered any errors
3. If the server is not running, start it using `start_refresh_server.bat`
4. Try refreshing again

If you continue to have issues, restart the Email Analyzer using `run_email_analyzer.bat`.
