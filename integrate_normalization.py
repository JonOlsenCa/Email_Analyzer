#!/usr/bin/env python3
"""
Integrate Normalization

This script modifies the email processing files to integrate the normalization system
at the point of data extraction and HTML generation.
"""

import os
import re
import shutil
import sys

# Files to modify
FILES_TO_MODIFY = [
    'monitor_new_emails.py',
    'analyze_outlook_emails.py'
]

def backup_file(file_path):
    """Create a backup of a file before modifying it."""
    backup_path = f"{file_path}.bak"
    try:
        shutil.copy2(file_path, backup_path)
        print(f"Created backup: {backup_path}")
        return True
    except Exception as e:
        print(f"Error creating backup of {file_path}: {str(e)}")
        return False

def add_normalizer_import(content):
    """Add import statements for the normalizers."""
    import_statement = """
# Import normalizers
from data_normalizer import CompanyNormalizer, CategoryNormalizer, TemplateNormalizer

# Initialize normalizers
company_normalizer = CompanyNormalizer()
category_normalizer = CategoryNormalizer()
template_normalizer = TemplateNormalizer()
"""

    # Find a good place to add the import
    # Look for other imports first
    import_match = re.search(r'import.*\n\n', content)
    if import_match:
        # Add after the last import block
        pos = import_match.end()
        return content[:pos] + import_statement + content[pos:]

    # If no clear import section, add after the module docstring
    docstring_match = re.search(r'"""[\s\S]*?"""\n\n', content)
    if docstring_match:
        pos = docstring_match.end()
        return content[:pos] + import_statement + content[pos:]

    # If all else fails, add at the beginning
    return import_statement + content

def modify_create_html_index(content):
    """
    Modify the create_html_index function to normalize data before writing to HTML.
    """
    # Find the create_html_index function
    func_pattern = r'def create_html_index\([^)]*\):[\s\S]*?return index_path'
    func_match = re.search(func_pattern, content)

    if not func_match:
        print("Could not find create_html_index function")
        return content

    func_content = func_match.group(0)

    # Find where company name, subject template, and support category are extracted
    # This will vary between files, so we'll look for common patterns

    # Pattern for company name extraction
    company_pattern = r'(company_name\s*=\s*[^=\n]+)'
    company_match = re.search(company_pattern, func_content)

    if company_match:
        # Add normalization after company name extraction
        normalized_company = company_match.group(1) + "\n            # Normalize company name\n            company_name = company_normalizer.normalize(company_name) if company_name else 'Unknown Company'"
        func_content = func_content.replace(company_match.group(1), normalized_company)

    # Pattern for subject template extraction
    template_pattern = r'(subject_template\s*=\s*[^=\n]+)'
    template_match = re.search(template_pattern, func_content)

    if template_match:
        # Add normalization after subject template extraction
        normalized_template = template_match.group(1) + "\n            # Normalize subject template\n            subject_template = template_normalizer.normalize(subject_template) if subject_template else 'Other'"
        func_content = func_content.replace(template_match.group(1), normalized_template)

    # Pattern for support category extraction (if it exists)
    category_pattern = r'(support_category\s*=\s*[^=\n]+)'
    category_match = re.search(category_pattern, func_content)

    if category_match:
        # Add normalization after support category extraction
        normalized_category = category_match.group(1) + "\n            # Normalize support category\n            support_category = category_normalizer.normalize(support_category) if support_category else 'Other'"
        func_content = func_content.replace(category_match.group(1), normalized_category)
    else:
        # If support category isn't found, look for a place to add it
        # This might be after subject template or before writing to the file
        if template_match:
            # Add after subject template
            add_category = "\n            # Extract and normalize support category\n            support_category = 'Other'  # Default value\n            # Try to determine category from description or other fields\n            if 'description' in locals() and description:\n                # Simple categorization based on keywords\n                if any(kw in description.lower() for kw in ['ai', 'model', 'prediction', 'extraction']):\n                    support_category = 'AI Model Prediction & Extraction Issues'\n                elif any(kw in description.lower() for kw in ['document', 'processing', 'upload']):\n                    support_category = 'Document Processing Failures'\n                elif any(kw in description.lower() for kw in ['system', 'bug', 'integration']):\n                    support_category = 'System Bugs & Integration Issues'\n                else:\n                    support_category = 'Other'"

            normalized_template = template_match.group(1) + add_category
            func_content = func_content.replace(template_match.group(1), normalized_template)

    # Update the function in the original content
    return content.replace(func_match.group(0), func_content)

def add_support_category_to_table(content):
    """
    Add support category column to the HTML table if it doesn't exist.
    """
    # Check if the table header already includes support category
    if 'Support Category' in content or 'support_category' in content:
        return content

    # Find the table header row
    header_pattern = r'<tr>\s*<th>#</th>\s*<th>Subject</th>[\s\S]*?</tr>'
    header_match = re.search(header_pattern, content)

    if not header_match:
        print("Could not find table header row")
        return content

    header_row = header_match.group(0)

    # Add support category column after subject template or before company name
    if '<th>Subject Template</th>' in header_row:
        new_header = header_row.replace('<th>Subject Template</th>', '<th>Subject Template</th>\n                <th>Support Category</th>')
    elif '<th>Company Name</th>' in header_row:
        new_header = header_row.replace('<th>Company Name</th>', '<th>Support Category</th>\n                <th>Company Name</th>')
    else:
        # If neither found, add after date
        new_header = header_row.replace('<th>Date</th>', '<th>Date</th>\n                <th>Support Category</th>')

    content = content.replace(header_row, new_header)

    # Also update the table row template to include support category
    row_pattern = r'<tr>\s*<td>{[^}]*}</td>[\s\S]*?</tr>'
    row_match = re.search(row_pattern, content)

    if row_match:
        row_template = row_match.group(0)

        # Add support category cell in the same position as in the header
        if '<td>{format_cell(subject_template)}</td>' in row_template:
            new_row = row_template.replace('<td>{format_cell(subject_template)}</td>', '<td>{format_cell(subject_template)}</td>\n                <td>{format_cell(support_category)}</td>')
        elif '<td>{format_cell(company_name)}</td>' in row_template:
            new_row = row_template.replace('<td>{format_cell(company_name)}</td>', '<td>{format_cell(support_category)}</td>\n                <td>{format_cell(company_name)}</td>')
        else:
            new_row = row_template.replace('<td>{format_cell(date_str)}</td>', '<td>{format_cell(date_str)}</td>\n                <td>{format_cell(support_category)}</td>')

        content = content.replace(row_template, new_row)

    return content

def add_refresh_normalization_call(content):
    """
    Add a call to refresh_normalization.py after creating the index.html file.
    """
    # Find where index.html is created
    index_pattern = r'create_html_index\([^)]*\)'
    index_matches = list(re.finditer(index_pattern, content))

    if not index_matches:
        print("Could not find calls to create_html_index")
        return content

    # For each call to create_html_index, add a call to refresh_normalization
    for match in reversed(index_matches):  # Process in reverse to avoid messing up positions
        pos = match.end()
        update_call = "\n            # Run refresh normalization to update mappings and dashboard\n            try:\n                import subprocess\n                subprocess.run(['python', 'refresh_normalization.py'], check=True)\n                logger.info(\"Ran refresh_normalization.py to update mappings and dashboard\")\n            except Exception as e:\n                logger.warning(f\"Error running refresh_normalization.py: {str(e)}\")"

        # Check if we're inside a try block
        try_match = re.search(r'try:[\s\S]*?' + re.escape(match.group(0)), content)
        if try_match:
            # We're inside a try block, so add before the except
            except_pos = content.find('except', pos)
            if except_pos > 0:
                content = content[:except_pos] + update_call + content[except_pos:]
            else:
                # No except found, add after the match
                content = content[:pos] + update_call + content[pos:]
        else:
            # Not in a try block, add after the match
            content = content[:pos] + update_call + content[pos:]

    return content

def modify_file(file_path):
    """Modify a file to integrate normalization."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False

    # Create a backup
    if not backup_file(file_path):
        return False

    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Make modifications
        content = add_normalizer_import(content)
        content = modify_create_html_index(content)
        content = add_support_category_to_table(content)
        content = add_refresh_normalization_call(content)

        # Write the modified content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Successfully modified {file_path}")
        return True

    except Exception as e:
        print(f"Error modifying {file_path}: {str(e)}")
        # Restore from backup
        backup_path = f"{file_path}.bak"
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, file_path)
            print(f"Restored {file_path} from backup")
        return False

def main():
    """Main function."""
    print("Integrating normalization into email processing files...")

    success_count = 0
    for file_path in FILES_TO_MODIFY:
        if modify_file(file_path):
            success_count += 1

    print(f"Modified {success_count} of {len(FILES_TO_MODIFY)} files")

    if success_count == len(FILES_TO_MODIFY):
        print("\nNormalization integration complete!")
        print("The system will now normalize data before writing to index.html")
    else:
        print("\nSome files could not be modified. Please check the error messages above.")

if __name__ == "__main__":
    main()
