#!/usr/bin/env python3
"""
Update Support Categories in index.html

This script updates the Support Category column in the index.html file based on email descriptions.
"""

import os
import re

# Define categories and their keywords
CATEGORIES = {
    "AI Model Prediction & Extraction Issues": [
        "wrong vendor", "incorrect vendor", "vendor prediction", 
        "wrong job", "job predicted", "job number", 
        "tax", "taxes", "sales tax", 
        "amount", "total", "cost prediction", 
        "invoice number", "missing", "not picking up", 
        "date", "discount date", "due date",
        "quantity", "unit cost", "line item",
        "prediction", "predicted", "predict",
        "ACA", "picking up", "should be vendor"
    ],
    
    "Document Processing Failures": [
        "email loaded", "work order loaded", "loaded as invoice", 
        "email body", "multiple", "unrelated document", 
        "uploaded as", "instead of invoice", "reading the work order", 
        "wrong page", "wrong document", "attachment",
        "upload", "document", "WIZARD IS READING"
    ],
    
    "System Bugs & Integration Issues": [
        "sql", "permission", "error", "vista", "erp", 
        "sync", "integration", "cannot be submitted", 
        "system issue", "unexpected", "software error", 
        "hard closed", "did not attach", "override", 
        "not keep", "changed/override", "popup message",
        "system", "bug", "issue", "GRANT SELECT", "mismatch"
    ],
    
    "Other": []  # Default category if none of the above match
}

def categorize_description(description):
    """
    Categorize an email description into one of the predefined categories.
    
    Args:
        description (str): The email description
        
    Returns:
        str: The category name
    """
    if not description:
        return "Other"
    
    description = description.lower()
    
    # Check each category's keywords
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword.lower() in description:
                return category
    
    # If no match found, return "Other"
    return "Other"

def update_categories_in_html(file_path):
    """
    Update support categories in the HTML file.
    
    Args:
        file_path (str): Path to the HTML file
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all rows with descriptions
    row_pattern = r'<tr>\s*<td>(\d+)</td>\s*<td>.*?</td>\s*<td>.*?</td>\s*<td>.*?</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>'
    
    def replace_category(match):
        row_num = match.group(1)
        description = match.group(2)
        current_category = match.group(3)
        
        # If the current category is not a real category (e.g., it's a company name), replace it
        if current_category not in CATEGORIES.keys():
            new_category = categorize_description(description)
            return f'<tr>\n                <td>{row_num}</td>\n                <td>.*?</td>\n                <td>.*?</td>\n                <td>.*?</td>\n                <td>{description}</td>\n                <td>{new_category}</td>'
        
        return match.group(0)
    
    updated_content = re.sub(row_pattern, replace_category, content)
    
    # Write the updated content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"Updated support categories in {file_path}")

def main():
    """Main function."""
    index_path = os.path.join('analyzed_emails', 'index.html')
    update_categories_in_html(index_path)

if __name__ == "__main__":
    main()
