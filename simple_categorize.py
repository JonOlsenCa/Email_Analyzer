#!/usr/bin/env python3
"""
Simple script to categorize email descriptions and print the results.
"""

import os
import re
from collections import Counter

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

def extract_descriptions_from_html(file_path):
    """
    Extract descriptions from the HTML file.
    
    Args:
        file_path (str): Path to the HTML file
        
    Returns:
        list: List of descriptions
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all description cells
    description_pattern = r'<td>(.*?)</td>\s*<td>.*?</td>\s*<td>.*?</td>\s*<td>.*?</td>\s*<td>(.*?)</td>'
    matches = re.findall(description_pattern, content)
    
    descriptions = []
    for match in matches:
        if len(match) >= 2:
            descriptions.append(match[1])
    
    return descriptions

def main():
    """Main function."""
    index_path = os.path.join('analyzed_emails', 'index.html')
    
    # Extract descriptions
    descriptions = extract_descriptions_from_html(index_path)
    
    # Categorize descriptions
    categories = [categorize_description(desc) for desc in descriptions]
    
    # Print results
    for i, (desc, category) in enumerate(zip(descriptions, categories), 1):
        print(f"{i}. Description: {desc[:50]}... => Category: {category}")
    
    # Print summary
    counter = Counter(categories)
    print("\nSummary:")
    for category, count in counter.items():
        print(f"{category}: {count}")

if __name__ == "__main__":
    main()
