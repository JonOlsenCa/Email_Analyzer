# Email Analyzer for Outlook

This extension to the Email Analyzer allows you to analyze emails directly from your Microsoft Outlook folders.

## Features

- Connect to Microsoft Outlook using the Windows COM interface
- Retrieve emails from any folder in your Outlook account
- Analyze emails for security risks and content insights
- Generate analysis reports in multiple formats (text, JSON, HTML)
- Create an index of all analyzed emails
- Optionally save emails as EML files for further analysis

## Requirements

- Windows operating system
- Microsoft Outlook installed
- Python 3.6 or higher
- pywin32 library (`pip install pywin32`)

## Usage

### Command Line

```bash
python analyze_outlook_emails.py [options]
```

Options:
- `--email-account EMAIL`: Email account to use (default: jon@olsenconsulting.ca)
- `--folder-path PATH`: Path to the Outlook folder (default: Inbox/APWizard_Tickets)
- `--limit NUMBER`: Maximum number of emails to retrieve (default: 100)
- `--format FORMAT`: Output format (text, json, html) (default: html)
- `--output-dir DIR`: Directory to save analysis reports (default: analyzed_emails)
- `--save-eml`: Save emails as EML files
- `--verbose`: Enable verbose output

Example:
```bash
python analyze_outlook_emails.py --email-account "jon@olsenconsulting.ca" --folder-path "Inbox/APWizard_Tickets" --limit 20 --format html
```

### Batch File (Windows)

For convenience, you can use the provided batch file:

```
analyze_outlook.bat [options]
```

The batch file accepts the same options as the command line script and will automatically open the index.html file after analysis is complete.

## Folder Path Format

The folder path should be specified in the format `Folder/Subfolder/SubSubfolder`. For example:
- `Inbox` - The main Inbox folder
- `Inbox/APWizard_Tickets` - A subfolder named "APWizard_Tickets" in the Inbox
- `Archive/2023/Important` - A nested folder structure

## Output

The script generates the following output:
- Analysis reports for each email in the specified format
- An index.html file that lists all analyzed emails with links to their reports
- Optionally, EML files of the emails (if --save-eml is specified)

All output is saved to the specified output directory (default: analyzed_emails).

## Troubleshooting

### Common Issues

1. **Cannot connect to Outlook**
   - Make sure Outlook is installed and properly configured
   - Try running the script with administrator privileges
   - Ensure Outlook is not in "Protected Mode"

2. **Cannot find folder**
   - Check the folder path format
   - Verify that the folder exists in your Outlook account
   - Try using a simpler path (e.g., just "Inbox") first

3. **Error saving EML files**
   - This may be due to Outlook security settings or permissions
   - Try running without the --save-eml option

### Logs

The script creates detailed logs in the `logs` directory. Check these logs for more information about any errors that occur.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
