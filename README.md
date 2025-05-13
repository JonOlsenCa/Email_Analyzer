# Email Analyzer

A Python tool for analyzing email content and metadata to extract insights and identify potential security risks.

## Features

- Parse email files in various formats (EML, MSG, TXT)
- Extract email metadata (headers, sender, recipients, date, etc.)
- Analyze email content for security risks
- Identify potential phishing attempts
- Extract URLs, IP addresses, and other indicators
- Generate analysis reports in multiple formats (text, JSON, HTML)

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/Email_Analyzer.git
cd Email_Analyzer
```

No additional dependencies are required for basic functionality. The tool uses Python's standard library.

## Usage

### Command Line Interface

```bash
python email_analyzer.py [email_file] [options]
```

Options:
- `-o, --output`: Output file for the analysis report
- `-f, --format`: Output format (text, json, html)
- `-v, --verbose`: Enable verbose output
- `--version`: Show the version and exit

Example:
```bash
python email_analyzer.py sample_email.eml -f json -o analysis_report.json
```

### As a Module

```python
from email_parser import EmailParser
from analyzer import Analyzer

# Parse the email
parser = EmailParser()
email_data = parser.parse_file("sample_email.eml")

# Analyze the email
analyzer = Analyzer()
analysis_results = analyzer.analyze(email_data)

# Get the results in different formats
text_report = analysis_results.to_format("text")
json_report = analysis_results.to_format("json")
html_report = analysis_results.to_format("html")

# Print or save the reports
print(text_report)
```

## Testing

Run the test script to analyze a sample email:

```bash
python test_analyzer.py [test_email_file]
```

If no test email file is provided, it will use the default `test_email.eml`.

## Project Structure

- `email_analyzer.py`: Main application file with CLI interface
- `email_parser.py`: Module for parsing email files
- `analyzer.py`: Module for analyzing email content and metadata
- `utils.py`: Utility functions
- `test_analyzer.py`: Test script
- `test_email.eml`: Sample email for testing

## Security Analysis Features

The Email Analyzer performs the following security checks:

- Authentication verification (SPF, DKIM, DMARC)
- URL extraction and analysis
- IP address identification
- Attachment risk assessment
- Phishing indicators detection
- Sender domain verification

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Future Enhancements

- Support for more email formats
- Integration with threat intelligence platforms
- Machine learning-based phishing detection
- Improved content analysis
- GUI interface
