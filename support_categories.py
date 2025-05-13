#!/usr/bin/env python3
"""
Support Categories Module

This module defines the support ticket categories and provides functions to categorize email descriptions.
"""

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
        "ACA", "picking up", "should be vendor",
        "format recognition", "data misclassification",
        "field", "number", "incorrect format"
    ],
    
    "Document Processing Failures": [
        "email loaded", "work order loaded", "loaded as invoice", 
        "email body", "multiple", "unrelated document", 
        "uploaded as", "instead of invoice", "reading the work order", 
        "wrong page", "wrong document", "attachment",
        "upload", "document", "WIZARD IS READING",
        "email vs invoice", "confusion", "mixup",
        "attachment recognition"
    ],
    
    "System Bugs & Integration Issues": [
        "sql", "permission", "error", "vista", "erp", 
        "sync", "integration", "cannot be submitted", 
        "system issue", "unexpected", "software error", 
        "hard closed", "did not attach", "override", 
        "not keep", "changed/override", "popup message",
        "system", "bug", "issue", "GRANT SELECT", "mismatch",
        "settings not saving", "submission error", "breakdown"
    ],
    
    "Other": [
        "feature request", "training", "question", "process", 
        "UI", "UX", "feedback", "inquiry"
    ]
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
