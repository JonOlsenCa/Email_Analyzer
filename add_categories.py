#!/usr/bin/env python3
"""
Add Support Categories to index.html

This script adds support categories to the index.html file based on email descriptions.
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

def add_categories_to_html(file_path):
    """
    Add support categories to the HTML file.
    
    Args:
        file_path (str): Path to the HTML file
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the header row index
    header_index = -1
    for i, line in enumerate(lines):
        if '<th>#</th>' in line and '<th>Subject</th>' in line:
            header_index = i
            break
    
    if header_index == -1:
        print("Header row not found")
        return
    
    # Check if Support Category column already exists
    if any('Support Category' in line for line in lines):
        print("Support Category column already exists")
    else:
        # Add Support Category header after Description
        header_line = lines[header_index]
        description_index = header_line.find('<th>Description</th>')
        if description_index != -1:
            end_index = description_index + len('<th>Description</th>')
            new_header = header_line[:end_index] + '\n                <th>Support Category</th>' + header_line[end_index:]
            lines[header_index] = new_header
    
    # Find all rows with descriptions and add categories
    i = header_index + 1
    while i < len(lines):
        if '<td>' in lines[i] and '</td>' in lines[i]:
            # Check if this is a data row
            if '<td>' in lines[i] and '</tr>' not in lines[i]:
                # Find the description in the next few lines
                description = ""
                j = i
                while j < min(i + 10, len(lines)):
                    if '<td>' in lines[j] and '</td>' in lines[j] and j >= i + 4:  # Description is typically the 5th column
                        # Extract description
                        match = re.search(r'<td>(.*?)</td>', lines[j])
                        if match:
                            description = match.group(1)
                            # Remove HTML tags
                            description = re.sub(r'<[^>]*>', '', description)
                            break
                    j += 1
                
                # Categorize the description
                category = categorize_description(description)
                
                # Find where to insert the category
                j = i
                while j < min(i + 15, len(lines)):
                    if '<td>' in lines[j] and '</td>' in lines[j] and j >= i + 4:  # After description
                        # Check if category already exists
                        if 'Support Category' in lines[j+1]:
                            break
                        
                        # Insert category after this line
                        lines.insert(j + 1, f'                <td>{category}</td>\n')
                        break
                    j += 1
            
            # Move to the next row
            i = j + 2
        else:
            i += 1
    
    # Write the updated content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"Added support categories to {file_path}")

def main():
    """Main function."""
    index_path = os.path.join('analyzed_emails', 'index.html')
    add_categories_to_html(index_path)

if __name__ == "__main__":
    main()
