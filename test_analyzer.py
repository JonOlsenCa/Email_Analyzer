#!/usr/bin/env python3
"""
Test script for the Email Analyzer.

This script demonstrates how to use the Email Analyzer to analyze an email file.
"""

import sys
import os
from email_parser import EmailParser
from analyzer import Analyzer
from utils import setup_logging

def main():
    """Main function to test the Email Analyzer."""
    # Setup logging
    logger = setup_logging()
    
    # Check if a test email file was provided
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
    else:
        # Use the default test email if none was provided
        test_file = "test_email.eml"
    
    # Check if the test file exists
    if not os.path.exists(test_file):
        print(f"Error: Test file '{test_file}' not found.")
        sys.exit(1)
    
    try:
        # Parse the email
        print(f"Parsing email file: {test_file}")
        parser = EmailParser()
        email_data = parser.parse_file(test_file)
        
        # Print basic email information
        print("\nBasic Email Information:")
        print(f"From: {email_data.from_address}")
        print(f"To: {', '.join(email_data.to_addresses)}")
        print(f"Subject: {email_data.subject}")
        print(f"Date: {email_data.date}")
        
        # Analyze the email
        print("\nAnalyzing email...")
        analyzer = Analyzer()
        analysis_results = analyzer.analyze(email_data)
        
        # Print the analysis results in different formats
        print("\n=== TEXT FORMAT ===")
        print(analysis_results.to_format("text"))
        
        print("\n=== JSON FORMAT ===")
        print(analysis_results.to_format("json"))
        
        # Save HTML report to a file
        html_report = analysis_results.to_format("html")
        report_file = "email_analysis_report.html"
        with open(report_file, "w") as f:
            f.write(html_report)
        print(f"\nHTML report saved to: {report_file}")
        
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
