#!/usr/bin/env python3
"""
Update Dashboard

This script updates the dashboard.html file with normalized data from the data_normalizer module.
It removes hard-coded constants and injects dynamic data.
"""

import os
import re
import json
from datetime import datetime
from data_normalizer import CompanyNormalizer, CategoryNormalizer, TemplateNormalizer

# Paths
DASHBOARD_TEMPLATE = os.path.join('templates', 'dashboard_template.html')
DASHBOARD_OUTPUT = os.path.join('analyzed_emails', 'dashboard.html')
INDEX_HTML = os.path.join('analyzed_emails', 'index.html')

def ensure_directory_exists(path):
    """Ensure the directory for a file exists."""
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def create_dashboard_template():
    """
    Create a dashboard template from the current dashboard.html file.
    This is a one-time operation to prepare for dynamic updates.
    """
    if not os.path.exists(DASHBOARD_OUTPUT):
        print(f"Dashboard file not found: {DASHBOARD_OUTPUT}")
        return False

    # Create templates directory if it doesn't exist
    ensure_directory_exists(DASHBOARD_TEMPLATE)

    # Read the current dashboard.html
    with open(DASHBOARD_OUTPUT, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace hard-coded company list with a placeholder
    company_pattern = r'const companyNameMap = \{[\s\S]*?\};'
    content = re.sub(company_pattern, '// COMPANY_MAPPINGS_PLACEHOLDER', content)

    # Replace hard-coded required companies list with a placeholder
    companies_pattern = r'const requiredCompanies = \[[\s\S]*?\];'
    content = re.sub(companies_pattern, '// REQUIRED_COMPANIES_PLACEHOLDER', content)

    # Replace hard-coded support categories with a placeholder
    categories_pattern = r'(let |const )supportCategories = \[[\s\S]*?\];'
    content = re.sub(categories_pattern, r'\1supportCategories = // SUPPORT_CATEGORIES_PLACEHOLDER', content)

    # Replace hard-coded subject templates with a placeholder
    templates_pattern = r'(let |const )subjectTemplates = \[[\s\S]*?\];'
    content = re.sub(templates_pattern, r'\1subjectTemplates = // SUBJECT_TEMPLATES_PLACEHOLDER', content)

    # Write the template file
    with open(DASHBOARD_TEMPLATE, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Created dashboard template: {DASHBOARD_TEMPLATE}")
    return True

def update_dashboard():
    """Update the dashboard.html file with normalized data."""
    # Initialize normalizers
    company_normalizer = CompanyNormalizer()
    category_normalizer = CategoryNormalizer()
    template_normalizer = TemplateNormalizer()

    # Check if template exists, create it if not
    if not os.path.exists(DASHBOARD_TEMPLATE):
        if not create_dashboard_template():
            print("Failed to create dashboard template. Using the original dashboard file.")
            # If we can't create a template, use the original file
            with open(DASHBOARD_OUTPUT, 'r', encoding='utf-8') as f:
                template_content = f.read()
        else:
            with open(DASHBOARD_TEMPLATE, 'r', encoding='utf-8') as f:
                template_content = f.read()
    else:
        with open(DASHBOARD_TEMPLATE, 'r', encoding='utf-8') as f:
            template_content = f.read()

    # Get normalized data
    company_mappings = company_normalizer.get_mappings_for_js()
    standardized_companies = company_normalizer.get_all_standardized()
    standardized_categories = category_normalizer.get_all_standardized()
    standardized_templates = template_normalizer.get_all_standardized()

    # Format company mappings for JavaScript
    company_mappings_js = "const companyNameMap = {\n"
    for variant, standard in sorted(company_mappings.items()):
        company_mappings_js += f"    '{variant}': '{standard}',\n"
    company_mappings_js += "};"

    # Format required companies for JavaScript
    companies_js = "const requiredCompanies = [\n"
    for company in sorted(standardized_companies):
        companies_js += f"    \"{company}\",\n"
    companies_js += "];"

    # Format support categories for JavaScript
    categories_js = "[\n"
    for category in sorted(standardized_categories):
        categories_js += f"    \"{category}\",\n"
    categories_js += "]"

    # Format subject templates for JavaScript
    templates_js = "[\n"
    for template in sorted(standardized_templates):
        templates_js += f"    \"{template}\",\n"
    templates_js += "]"

    # Replace placeholders in the template
    content = template_content
    content = content.replace('// COMPANY_MAPPINGS_PLACEHOLDER', company_mappings_js)
    content = content.replace('// REQUIRED_COMPANIES_PLACEHOLDER', companies_js)
    content = content.replace('// SUPPORT_CATEGORIES_PLACEHOLDER', categories_js)
    content = content.replace('// SUBJECT_TEMPLATES_PLACEHOLDER', templates_js)

    # Write the updated dashboard file
    with open(DASHBOARD_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Updated dashboard with normalized data: {DASHBOARD_OUTPUT}")
    return True

def extract_entities_from_index():
    """
    Extract entities from the index.html file and normalize them.
    This helps build up the normalization mappings.
    """
    if not os.path.exists(INDEX_HTML):
        print(f"Index file not found: {INDEX_HTML}")
        return

    # Initialize normalizers
    company_normalizer = CompanyNormalizer()
    category_normalizer = CategoryNormalizer()
    template_normalizer = TemplateNormalizer()

    # Read the index.html file
    with open(INDEX_HTML, 'r', encoding='utf-8') as f:
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
        print(f"Found table headers: {headers}")

        # Find the correct column indices
        for i, header in enumerate(headers):
            if header and "Subject Template" in header:
                subject_template_col = i
                print(f"Subject Template column is {subject_template_col+1}")
            elif header and "Company" in header:
                company_col = i
                print(f"Company column is {company_col+1}")
            elif header and "Category" in header:
                category_col = i
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

    for match in matches:
        if len(match) >= max(subject_template_col, company_col) + 1:
            # Extract company name
            if company_col >= 0 and match[company_col] and match[company_col] != 'N/A':
                company = match[company_col].strip()

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
    for company in companies:
        company_normalizer.normalize(company)

    for category in categories:
        category_normalizer.normalize(category)

    for template in templates:
        template_normalizer.normalize(template)

    # Save the updated mappings
    company_normalizer.save_mappings()
    category_normalizer.save_mappings()
    template_normalizer.save_mappings()

    print(f"Extracted and normalized entities from {INDEX_HTML}")
    print(f"Companies: {len(companies)}")
    print(f"Categories: {len(categories)}")
    print(f"Templates: {len(templates)}")

def main():
    """Main function."""
    # Extract entities from index.html to build up mappings
    extract_entities_from_index()

    # Update the dashboard with normalized data
    update_dashboard()

if __name__ == "__main__":
    main()
