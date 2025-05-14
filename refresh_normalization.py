#!/usr/bin/env python3
"""
Refresh Normalization

This script is designed to be run each time emails are refreshed.
It normalizes new data while preserving established entities.
"""

import os
import sys
import re
import json
import argparse
from data_normalizer import CompanyNormalizer, CategoryNormalizer, TemplateNormalizer

def setup_arg_parser():
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(description='Refresh normalization for email data')
    parser.add_argument('--review', action='store_true', help='Review pending mappings')
    parser.add_argument('--force', action='store_true', help='Force update of dashboard even if no changes')
    parser.add_argument('--verbose', action='store_true', help='Show verbose output')
    return parser

def extract_entities_from_index(index_file, verbose=False):
    """
    Extract entities from the index.html file and normalize them.
    This helps build up the normalization mappings.
    """
    if not os.path.exists(index_file):
        print(f"Index file not found: {index_file}")
        return False
    
    # Initialize normalizers
    company_normalizer = CompanyNormalizer()
    category_normalizer = CategoryNormalizer()
    template_normalizer = TemplateNormalizer()
    
    # Read the index.html file
    with open(index_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # First, find the table headers to identify the correct columns
    header_pattern = r'<tr>\s*<th>#</th>\s*<th>(.*?)</th>\s*<th>(.*?)</th>\s*<th>(.*?)</th>\s*<th>(.*?)</th>\s*<th>(.*?)</th>\s*<th>(.*?)</th>'
    header_match = re.search(header_pattern, content)
    
    # Initialize column indices
    subject_template_col = 2  # Default assumption (3rd column, 0-based index would be 2)
    company_col = 4  # Default assumption (5th column, 0-based index would be 4)
    category_col = -1  # Will try to find this
    
    # If we found headers, determine the correct columns
    if header_match:
        headers = list(header_match.groups())
        if verbose:
            print(f"Found table headers: {headers}")
        
        # Find the correct column indices
        for i, header in enumerate(headers):
            if header and "Subject Template" in header:
                subject_template_col = i
                if verbose:
                    print(f"Subject Template column is {subject_template_col+1}")
            elif header and "Company" in header:
                company_col = i
                if verbose:
                    print(f"Company column is {company_col+1}")
            elif header and "Category" in header:
                category_col = i
                if verbose:
                    print(f"Category column is {category_col+1}")
    
    # Extract data from table rows
    row_pattern = r'<tr>\s*<td>.*?</td>\s*' + r'<td>(.*?)</td>\s*' * 10  # Match up to 10 columns
    matches = re.findall(row_pattern, content)
    
    companies = set()
    categories = set()
    templates = set()
    
    # Known valid subject templates (for validation)
    valid_templates = {
        "Incorrect Vendor Prediction",
        "System Performance Issues",
        "Error Uploading Documents",
        "Integration Issue with ERP/Accounting System",
        "Unable to Submit Invoice",
        "Unexpected Error",
        "Other"
    }
    
    # Known valid categories (for validation)
    valid_categories = {
        "AI Model Prediction & Extraction Issues",
        "Document Processing Failures",
        "System Bugs & Integration Issues",
        "Other"
    }
    
    # Known valid company names
    known_companies = [
        "Beacon Communications, LLC",
        "Ben Hur Construction Co.",
        "BluSky Restoration Contractors, LLC",
        "Concrete & Materials Placement",
        "Doggett Concrete Construction",
        "GBI",
        "Gulf Stream Construction Co., Inc.",
        "H&M Mechanical Constructors, Inc.",
        "Haskell Lemon",
        "NP Mechanical, Inc.",
        "S.M. Hentges",
        "TSU One, Inc.",
        "TaftElectric",
        "Moisture Loc",
        "Comtel Systems Technology",
        "Great Basin Industrial",
        "Doggett Residential"
    ]
    
    # Patterns to exclude
    exclude_patterns = [
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',  # UUID
        r'^[0-9]+$',  # Numeric ID
        r'^[0-9.-]+$',  # Numeric ID with dots or dashes
        r'^<',  # HTML tags
        r'error|issue|warning|incorrect|wrong|missing|invoice|wizard|system|prediction|vendor|document',  # Error messages
        r'^The\s',  # Sentences starting with "The"
        r'^There\s',  # Sentences starting with "There"
        r'^Is\s',  # Sentences starting with "Is"
        r'^We\s',  # Sentences starting with "We"
        r'^Not\s',  # Sentences starting with "Not"
        r'^This\s',  # Sentences starting with "This"
        r'^All\s',  # Sentences starting with "All"
        r'^Due\s',  # Sentences starting with "Due"
        r'^Changed\s',  # Sentences starting with "Changed"
        r'^Data\s',  # Sentences starting with "Data"
        r'^PO\s',  # Sentences starting with "PO"
        r'^SQL\s',  # Sentences starting with "SQL"
        r'^SHOULD\s',  # Sentences starting with "SHOULD"
        r'^WIZARD\s',  # Sentences starting with "WIZARD"
        r'^GRANT\s',  # Sentences starting with "GRANT"
        r'^email\s',  # Sentences starting with "email"
        r'^invoice\s',  # Sentences starting with "invoice"
        r'^sales\s',  # Sentences starting with "sales"
        r'^the\s',  # Sentences starting with "the"
        r'^this\s'  # Sentences starting with "this"
    ]
    
    for match in matches:
        if len(match) >= max(subject_template_col, company_col) + 1:
            # Extract company name
            if company_col >= 0 and match[company_col] and match[company_col] != 'N/A':
                company = match[company_col].strip()
                
                # Check if it's a valid company name
                is_valid = True
                
                # Check against exclude patterns
                for pattern in exclude_patterns:
                    if re.search(pattern, company, re.IGNORECASE):
                        is_valid = False
                        break
                
                # If it's a known company, it's valid regardless of patterns
                if company in known_companies:
                    is_valid = True
                
                # Check if it's too long to be a company name (likely an error message)
                if len(company) > 50:
                    is_valid = False
                
                # Check if it contains too many words to be a company name
                words = company.split()
                if len(words) > 8:
                    is_valid = False
                
                if is_valid:
                    companies.add(company)
            
            # Extract subject template
            if subject_template_col >= 0 and match[subject_template_col] and match[subject_template_col] != 'N/A':
                template = match[subject_template_col].strip()
                # Validate that it's a known template or looks like one
                if template in valid_templates or \
                   any(keyword in template for keyword in ["Vendor", "System", "Error", "Upload", "Integration", "Invoice", "Unexpected"]):
                    templates.add(template)
            
            # Extract support category
            if category_col >= 0 and match[category_col] and match[category_col] != 'N/A':
                category = match[category_col].strip()
                # Validate that it's a known category or looks like one
                if category in valid_categories or \
                   any(keyword in category for keyword in ["AI Model", "Document Processing", "System Bugs", "Integration"]):
                    categories.add(category)
            elif category_col < 0:
                # If we couldn't find the category column, try to infer from other columns
                for cell in match:
                    if cell and any(keyword in cell for keyword in ["AI Model", "Document Processing", "System Bugs", "Integration"]):
                        categories.add(cell.strip())
    
    # Normalize and save each entity
    changes_made = False
    
    # Process companies
    company_count = len(company_normalizer.mappings)
    for company in companies:
        company_normalizer.normalize(company)
    if len(company_normalizer.mappings) > company_count:
        changes_made = True
        if verbose:
            print(f"Added {len(company_normalizer.mappings) - company_count} new company mappings")
    
    # Process categories
    category_count = len(category_normalizer.mappings)
    for category in categories:
        category_normalizer.normalize(category)
    if len(category_normalizer.mappings) > category_count:
        changes_made = True
        if verbose:
            print(f"Added {len(category_normalizer.mappings) - category_count} new category mappings")
    
    # Process templates
    template_count = len(template_normalizer.mappings)
    for template in templates:
        template_normalizer.normalize(template)
    if len(template_normalizer.mappings) > template_count:
        changes_made = True
        if verbose:
            print(f"Added {len(template_normalizer.mappings) - template_count} new template mappings")
    
    # Save the updated mappings
    company_normalizer.save_mappings()
    category_normalizer.save_mappings()
    template_normalizer.save_mappings()
    
    if verbose:
        print(f"Extracted and normalized entities from {index_file}")
        print(f"Companies: {len(companies)}")
        print(f"Categories: {len(categories)}")
        print(f"Templates: {len(templates)}")
    
    return changes_made

def review_pending_mappings():
    """Review pending mappings for all normalizers."""
    from review_mappings import review_normalizer
    
    # Initialize normalizers
    company_normalizer = CompanyNormalizer()
    category_normalizer = CategoryNormalizer()
    template_normalizer = TemplateNormalizer()
    
    # Review pending mappings
    review_normalizer(company_normalizer, "company name")
    review_normalizer(category_normalizer, "support category")
    review_normalizer(template_normalizer, "subject template")

def update_dashboard(force=False, verbose=False):
    """Update the dashboard with normalized data."""
    from update_dashboard import update_dashboard as update_dash
    
    if verbose:
        print("Updating dashboard with normalized data...")
    
    # Update the dashboard
    update_dash()
    
    if verbose:
        print("Dashboard updated successfully")

def main():
    """Main function."""
    # Parse command line arguments
    parser = setup_arg_parser()
    args = parser.parse_args()
    
    # Extract entities from index.html
    index_file = os.path.join('analyzed_emails', 'index.html')
    changes_made = extract_entities_from_index(index_file, args.verbose)
    
    # Review pending mappings if requested
    if args.review:
        review_pending_mappings()
        changes_made = True  # Force update after review
    
    # Update dashboard if changes were made or forced
    if changes_made or args.force:
        update_dashboard(args.force, args.verbose)
    elif args.verbose:
        print("No changes made, dashboard not updated")

if __name__ == "__main__":
    main()
