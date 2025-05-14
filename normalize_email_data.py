#!/usr/bin/env python3
"""
Normalize Email Data

This script normalizes company names, support categories, and subject templates
in the email data. It can be integrated with the email processing workflow.
"""

import os
import re
import json
from data_normalizer import CompanyNormalizer, CategoryNormalizer, TemplateNormalizer

# Initialize normalizers
company_normalizer = CompanyNormalizer()
category_normalizer = CategoryNormalizer()
template_normalizer = TemplateNormalizer()

def normalize_email_data(email_data):
    """
    Normalize company name, support category, and subject template in email data.
    
    Args:
        email_data: Dictionary containing email data
        
    Returns:
        Updated email data with normalized fields
    """
    # Make a copy to avoid modifying the original
    normalized_data = email_data.copy()
    
    # Normalize company name
    if 'company_name' in normalized_data and normalized_data['company_name']:
        normalized_data['company_name'] = company_normalizer.normalize(normalized_data['company_name'])
    
    # Normalize support category
    if 'support_category' in normalized_data and normalized_data['support_category']:
        normalized_data['support_category'] = category_normalizer.normalize(normalized_data['support_category'])
    
    # Normalize subject template
    if 'subject_template' in normalized_data and normalized_data['subject_template']:
        normalized_data['subject_template'] = template_normalizer.normalize(normalized_data['subject_template'])
    
    return normalized_data

def normalize_html_file(html_file):
    """
    Normalize company names, categories, and templates in an HTML file.
    
    Args:
        html_file: Path to the HTML file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find and normalize company names
        company_pattern = r'<td>(.*?)</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>'
        matches = re.findall(company_pattern, content)
        
        for match in matches:
            if len(match) >= 5:
                # Company name (adjust column index as needed)
                if match[4] and match[4] != 'N/A':
                    company = match[4].strip()
                    normalized_company = company_normalizer.normalize(company)
                    content = content.replace(f'<td>{company}</td>', f'<td>{normalized_company}</td>')
                
                # Subject template (adjust column index as needed)
                if match[2] and match[2] != 'N/A':
                    template = match[2].strip()
                    normalized_template = template_normalizer.normalize(template)
                    content = content.replace(f'<td>{template}</td>', f'<td>{normalized_template}</td>')
                
                # Support category (this is a simplification - adjust as needed)
                for i, cell in enumerate(match):
                    if any(category in cell for category in ["AI Model", "Document Processing", "System Bugs", "Integration"]):
                        category = cell.strip()
                        normalized_category = category_normalizer.normalize(category)
                        content = content.replace(f'<td>{category}</td>', f'<td>{normalized_category}</td>')
        
        # Write the updated content
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Normalized entities in {html_file}")
        return True
    
    except Exception as e:
        print(f"Error normalizing HTML file {html_file}: {str(e)}")
        return False

def normalize_json_file(json_file):
    """
    Normalize company names, categories, and templates in a JSON file.
    
    Args:
        json_file: Path to the JSON file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Normalize data based on structure
        if isinstance(data, list):
            # List of records
            for item in data:
                if isinstance(item, dict):
                    # Normalize company name
                    if 'company_name' in item and item['company_name']:
                        item['company_name'] = company_normalizer.normalize(item['company_name'])
                    
                    # Normalize support category
                    if 'support_category' in item and item['support_category']:
                        item['support_category'] = category_normalizer.normalize(item['support_category'])
                    
                    # Normalize subject template
                    if 'subject_template' in item and item['subject_template']:
                        item['subject_template'] = template_normalizer.normalize(item['subject_template'])
        
        elif isinstance(data, dict):
            # Single record or nested structure
            if 'company_name' in data and data['company_name']:
                data['company_name'] = company_normalizer.normalize(data['company_name'])
            
            if 'support_category' in data and data['support_category']:
                data['support_category'] = category_normalizer.normalize(data['support_category'])
            
            if 'subject_template' in data and data['subject_template']:
                data['subject_template'] = template_normalizer.normalize(data['subject_template'])
            
            # Check for nested records
            for key, value in data.items():
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            if 'company_name' in item and item['company_name']:
                                item['company_name'] = company_normalizer.normalize(item['company_name'])
                            
                            if 'support_category' in item and item['support_category']:
                                item['support_category'] = category_normalizer.normalize(item['support_category'])
                            
                            if 'subject_template' in item and item['subject_template']:
                                item['subject_template'] = template_normalizer.normalize(item['subject_template'])
        
        # Write the updated data
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"Normalized entities in {json_file}")
        return True
    
    except Exception as e:
        print(f"Error normalizing JSON file {json_file}: {str(e)}")
        return False

def normalize_directory(directory, file_types=None):
    """
    Normalize all supported files in a directory.
    
    Args:
        directory: Directory path
        file_types: List of file extensions to process (default: ['.html', '.json'])
        
    Returns:
        Number of files processed
    """
    if file_types is None:
        file_types = ['.html', '.json']
    
    count = 0
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            
            if ext in file_types:
                if ext == '.html':
                    if normalize_html_file(file_path):
                        count += 1
                elif ext == '.json':
                    if normalize_json_file(file_path):
                        count += 1
    
    return count

def main():
    """Main function."""
    # Normalize files in the analyzed_emails directory
    count = normalize_directory('analyzed_emails')
    print(f"Normalized {count} files")
    
    # Save the updated mappings
    company_normalizer.save_mappings()
    category_normalizer.save_mappings()
    template_normalizer.save_mappings()
    
    # Update the dashboard with the normalized data
    try:
        from update_dashboard import update_dashboard
        update_dashboard()
    except ImportError:
        print("Could not import update_dashboard module. Please run update_dashboard.py separately.")

if __name__ == "__main__":
    main()
