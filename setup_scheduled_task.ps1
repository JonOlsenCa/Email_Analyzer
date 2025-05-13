# PowerShell script to create a scheduled task for Email Analyzer
# This script must be run with administrator privileges

# Get the current directory
$currentDir = Get-Location

# Create the task action - run the batch file
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c $currentDir\monitor_emails.bat" -WorkingDirectory "$currentDir"

# Create the trigger - run every 15 minutes
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 15) -RepetitionDuration ([TimeSpan]::MaxValue)

# Set the principal (run with highest privileges)
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType S4U -RunLevel Highest

# Create the settings
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

# Register the task
Register-ScheduledTask -TaskName "Email Analyzer Monitor" -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Monitors Outlook for new emails in the APWizard_Tickets folder and analyzes them"

Write-Host "Scheduled task 'Email Analyzer Monitor' created successfully."
Write-Host "The task will run every 15 minutes to check for new emails."
Write-Host "You can modify the schedule in Task Scheduler if needed."
