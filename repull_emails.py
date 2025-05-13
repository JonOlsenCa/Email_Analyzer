#!/usr/bin/env python3
"""
Re-pull Emails from Outlook

This script deletes all existing email reports and re-pulls emails from Outlook.
"""

import os
import shutil
import logging
import sys
from analyze_outlook_emails import main as analyze_main

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def repull_emails():
    """Delete existing reports and re-pull emails from Outlook."""
    logger = setup_logging()
    
    # Output directory for email reports
    output_dir = "analyzed_emails"
    
    # Check if the directory exists
    if os.path.exists(output_dir):
        logger.info(f"Deleting existing reports in {output_dir}...")
        
        # Delete all files in the directory except index.html
        for filename in os.listdir(output_dir):
            file_path = os.path.join(output_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                logger.error(f"Error deleting {file_path}: {e}")
    else:
        # Create the directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Created output directory: {output_dir}")
    
    # Re-pull emails from Outlook
    logger.info("Re-pulling emails from Outlook...")
    analyze_main()
    
    logger.info("Email re-pull complete. All reports have been regenerated.")

if __name__ == "__main__":
    repull_emails()
