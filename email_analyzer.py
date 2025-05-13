#!/usr/bin/env python3
"""
Email Analyzer - A tool for analyzing email content and metadata.

This tool can parse email files, extract metadata, analyze content,
and generate reports about the emails.
"""

import argparse
import sys
from email_parser import EmailParser
from analyzer import Analyzer
from utils import setup_logging, get_version

# Setup logging
logger = setup_logging()

VERSION = "0.1.0"

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Email Analyzer - A tool for analyzing email content and metadata."
    )
    
    parser.add_argument(
        "email_file", 
        nargs="?", 
        help="Path to the email file to analyze"
    )
    
    parser.add_argument(
        "-o", 
        "--output", 
        help="Output file for the analysis report"
    )
    
    parser.add_argument(
        "-f", 
        "--format", 
        choices=["text", "json", "html"], 
        default="text",
        help="Output format for the analysis report"
    )
    
    parser.add_argument(
        "-v", 
        "--verbose", 
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"Email Analyzer {VERSION}",
        help="Show the version and exit"
    )
    
    return parser.parse_args()

def main():
    """Main entry point for the application."""
    args = parse_arguments()
    
    if not args.email_file:
        print("Error: No email file specified.")
        print("Use --help for more information.")
        sys.exit(1)
    
    try:
        # Parse the email
        parser = EmailParser()
        email_data = parser.parse_file(args.email_file)
        
        # Analyze the email
        analyzer = Analyzer()
        analysis_results = analyzer.analyze(email_data)
        
        # Generate and output the report
        if args.output:
            with open(args.output, 'w') as f:
                f.write(analysis_results.to_format(args.format))
            print(f"Analysis report saved to {args.output}")
        else:
            print(analysis_results.to_format(args.format))
            
    except Exception as e:
        logger.error(f"Error analyzing email: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
