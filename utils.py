"""
Utility functions for the Email Analyzer application.
"""

import logging
import os
import sys
from datetime import datetime

def setup_logging(log_level=logging.INFO):
    """
    Set up logging for the application.
    
    Args:
        log_level: The logging level to use
        
    Returns:
        logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Set up logging to file
    log_filename = f"logs/email_analyzer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger('email_analyzer')
    logger.info(f"Logging initialized. Log file: {log_filename}")
    
    return logger

def get_version():
    """
    Get the current version of the application.
    
    Returns:
        str: Version string
    """
    return "0.1.0"

def format_file_size(size_in_bytes):
    """
    Format a file size in bytes to a human-readable format.
    
    Args:
        size_in_bytes (int): Size in bytes
        
    Returns:
        str: Formatted file size
    """
    if size_in_bytes < 1024:
        return f"{size_in_bytes} bytes"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.1f} KB"
    elif size_in_bytes < 1024 * 1024 * 1024:
        return f"{size_in_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_in_bytes / (1024 * 1024 * 1024):.1f} GB"

def sanitize_filename(filename):
    """
    Sanitize a filename to ensure it's valid for the current OS.
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Replace invalid characters with underscores
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Ensure the filename isn't too long
    if len(filename) > 255:
        base, ext = os.path.splitext(filename)
        filename = base[:255-len(ext)] + ext
    
    return filename

def extract_domain_from_email(email_address):
    """
    Extract the domain from an email address.
    
    Args:
        email_address (str): Email address
        
    Returns:
        str: Domain name or empty string if not found
    """
    if '@' in email_address:
        return email_address.split('@')[-1]
    return ""
