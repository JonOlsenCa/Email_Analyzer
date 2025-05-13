#!/usr/bin/env python3
"""
Categorize Emails

This script categorizes support emails into predefined categories based on their descriptions.
"""

import os
import re
import json

# Define categories
CATEGORIES = {
    "AI Model Prediction & Extraction Issues": [
        "wrong vendor", "incorrect vendor", "vendor prediction",
        "wrong job", "job predicted", "job number",
        "tax", "taxes", "sales tax",
        "amount", "total", "cost prediction",
        "invoice number", "missing", "not picking up",
        "date", "discount date", "due date",
        "quantity", "unit cost", "line item",
        "prediction", "predicted", "predict"
    ],

    "Document Processing Failures": [
        "email loaded", "work order loaded", "loaded as invoice",
        "email body", "multiple", "unrelated document",
        "uploaded as", "instead of invoice", "reading the work order",
        "wrong page", "wrong document", "attachment",
        "upload", "document"
    ],

    "System Bugs & Integration Issues": [
        "sql", "permission", "error", "vista", "erp",
        "sync", "integration", "cannot be submitted",
        "system issue", "unexpected", "software error",
        "hard closed", "did not attach", "override",
        "not keep", "changed/override", "popup message",
        "system", "bug", "issue"
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

def update_index_html(file_path):
    """
    Update the index.html file to include the new category column.

    Args:
        file_path (str): Path to the index.html file
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the header row and add the new column header
    header_pattern = r'(<tr>\s*<th>#</th>\s*<th>Subject</th>\s*<th>Subject Template</th>\s*<th>Date</th>\s*<th>Description</th>)'
    header_replacement = r'\1\n                <th>Support Category</th>'
    content = re.sub(header_pattern, header_replacement, content)

    # Find all data rows and add the category
    row_pattern = r'(<tr>\s*<td>\d+</td>.*?<td>(.*?)</td>\s*<td>.*?</td>\s*<td>.*?</td>\s*<td>.*?</td>\s*<td>(.*?)</td>)'

    def add_category(match):
        full_match = match.group(1)
        description = match.group(3)
        category = categorize_description(description)
        return f'{full_match}\n                <td>{category}</td>'

    content = re.sub(row_pattern, add_category, content)

    # Save the updated file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Updated {file_path} with support categories")

def main():
    """Main function."""
    index_path = os.path.join('analyzed_emails', 'index.html')
    update_index_html(index_path)

if __name__ == "__main__":
    main()
