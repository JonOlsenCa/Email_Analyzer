#!/usr/bin/env python3
"""
Monitor New Emails

This script monitors an Outlook folder for new emails and analyzes them.
It keeps track of which emails have already been analyzed to avoid duplicates.
"""

import os
import sys
import json
import logging
import hashlib
from datetime import datetime
from outlook_connector import OutlookConnector
from analyzer import Analyzer
from utils import setup_logging

# Configuration
EMAIL_ACCOUNT = "jon@olsenconsulting.ca"
FOLDER_PATH = "Inbox/APWizard_Tickets"
OUTPUT_DIR = "analyzed_emails"
FORMAT = "html"
TRACKING_FILE = "processed_emails.json"

def get_email_hash(email_data):
    """
    Generate a unique hash for an email to track which emails have been processed.

    Args:
        email_data: EmailData object

    Returns:
        str: Hash string
    """
    # Create a string with key email properties
    hash_string = f"{email_data.subject}|{email_data.from_address}|{email_data.date}|{len(email_data.body_text)}"

    # Generate a hash
    return hashlib.md5(hash_string.encode()).hexdigest()

def load_processed_emails():
    """
    Load the list of already processed emails.

    Returns:
        dict: Dictionary of processed email hashes with timestamps
    """
    if os.path.exists(TRACKING_FILE):
        try:
            with open(TRACKING_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading tracking file: {str(e)}")

    return {}

def save_processed_emails(processed_emails):
    """
    Save the list of processed emails.

    Args:
        processed_emails (dict): Dictionary of processed email hashes with timestamps
    """
    try:
        with open(TRACKING_FILE, 'w') as f:
            json.dump(processed_emails, f, indent=2)
    except Exception as e:
        logging.error(f"Error saving tracking file: {str(e)}")

def create_html_index(output_dir, emails, folder_path):
    """
    Create an HTML index file for the analysis reports.

    Args:
        output_dir (str): Directory containing the reports
        emails (list): List of analyzed emails
        folder_path (str): Path to the Outlook folder
    """
    index_path = os.path.join(output_dir, "index.html")

    # Get all HTML reports and match with emails
    reports = []
    email_map = {email.subject: email for email in emails}

    for filename in os.listdir(output_dir):
        if filename.endswith(".html") and filename != "index.html":
            # Extract email subject from filename
            subject = filename.rsplit("_", 1)[0]

            # Find the corresponding email data
            email_data = None
            for email_subject, email in email_map.items():
                if subject in email_subject or email_subject in subject:
                    email_data = email
                    break

            reports.append((subject, filename, email_data))

    # Sort reports by filename (which includes the timestamp)
    reports.sort(key=lambda x: x[1], reverse=True)

    # Create the HTML index
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>Email Analysis Reports - {folder_path}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333366; }}
        table {{ border-collapse: collapse; width: 100%; overflow-x: auto; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{
            background-color: #f2f2f2;
            position: sticky;
            top: 0;
            cursor: pointer;
            user-select: none;
        }}
        th:hover {{ background-color: #ddd; }}
        th.sorted-asc::after {{ content: " ▲"; }}
        th.sorted-desc::after {{ content: " ▼"; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        tr:hover {{ background-color: #f2f2f2; }}
        .timestamp {{ color: #666; font-size: 0.8em; }}
        .container {{ overflow-x: auto; }}
        .empty-cell {{ color: #999; font-style: italic; }}
        .filter-container {{
            display: none;
            position: absolute;
            background-color: white;
            border: 1px solid #ddd;
            padding: 10px;
            z-index: 100;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            max-height: 300px;
            overflow-y: auto;
            min-width: 200px;
        }}
        .filter-option {{ margin: 5px 0; }}
        .filter-search {{
            width: 100%;
            padding: 5px;
            margin-bottom: 10px;
            box-sizing: border-box;
        }}
        .filter-buttons {{
            display: flex;
            justify-content: space-between;
            margin-top: 10px;
        }}
        .filter-buttons button {{
            padding: 5px 10px;
            cursor: pointer;
        }}
    </style>
    <script>
        // Global variables to track current sort state
        let currentSortColumn = 3; // Default sort by Date column (0-based index)
        let currentSortDirection = 'desc'; // Default sort direction is descending
        let activeFilters = {{}}; // Store active filters for each column
        let allTableData = []; // Store all table data for filtering

        // Function to get cell text content, handling special cases
        function getCellValue(row, index) {{
            const cell = row.cells[index];
            if (!cell) return '';

            // If cell contains an anchor tag, get the text from that
            const anchor = cell.querySelector('a');
            if (anchor) return anchor.textContent.trim();

            // If cell contains a span with class 'empty-cell', treat as empty
            const emptyCell = cell.querySelector('.empty-cell');
            if (emptyCell) return '';

            // Otherwise, get the text content
            return cell.textContent.trim();
        }}

        // Function to compare values for sorting
        function compareValues(a, b, type, direction) {{
            // Handle empty values
            if (a === '' && b === '') return 0;
            if (a === '') return direction === 'asc' ? 1 : -1;
            if (b === '') return direction === 'asc' ? -1 : 1;

            // Compare based on data type
            if (type === 'date') {{
                // Parse dates and compare
                const dateA = new Date(a);
                const dateB = new Date(b);
                return direction === 'asc'
                    ? dateA - dateB
                    : dateB - dateA;
            }} else if (type === 'number') {{
                // Parse numbers and compare
                const numA = parseFloat(a.replace(/[^0-9.-]+/g, ''));
                const numB = parseFloat(b.replace(/[^0-9.-]+/g, ''));
                return direction === 'asc'
                    ? numA - numB
                    : numB - numA;
            }} else {{
                // Default string comparison
                return direction === 'asc'
                    ? a.localeCompare(b)
                    : b.localeCompare(a);
            }}
        }}

        // Function to sort the table by a specific column
        function sortTable(columnIndex, dataType = 'string') {{
            const table = document.getElementById('emailTable');
            const headers = table.querySelectorAll('th');
            const rows = Array.from(table.rows).slice(1); // Skip header row

            // Determine sort direction
            let direction = 'asc';
            if (columnIndex === currentSortColumn) {{
                // If already sorting by this column, toggle direction
                direction = currentSortDirection === 'asc' ? 'desc' : 'asc';
            }}

            // Update sort indicators in headers
            headers.forEach(header => {{
                header.classList.remove('sorted-asc', 'sorted-desc');
            }});
            headers[columnIndex].classList.add(direction === 'asc' ? 'sorted-asc' : 'sorted-desc');

            // Sort the rows
            rows.sort((rowA, rowB) => {{
                const valueA = getCellValue(rowA, columnIndex);
                const valueB = getCellValue(rowB, columnIndex);
                return compareValues(valueA, valueB, dataType, direction);
            }});

            // Reorder the rows in the table
            const tbody = table.tBodies[0] || table;
            rows.forEach(row => tbody.appendChild(row));

            // Update row numbers
            rows.forEach((row, index) => {{
                row.cells[0].textContent = index + 1;
            }});

            // Update current sort state
            currentSortColumn = columnIndex;
            currentSortDirection = direction;
        }}

        // Function to create and show filter dropdown for a column
        function showFilter(columnIndex, event) {{
            // Don't sort when clicking on filter
            event.stopPropagation();

            // Remove any existing filter containers
            const existingContainers = document.querySelectorAll('.filter-container');
            existingContainers.forEach(container => container.remove());

            // Get unique values for this column
            const table = document.getElementById('emailTable');
            const rows = Array.from(table.rows).slice(1); // Skip header row
            const values = new Set();

            rows.forEach(row => {{
                const value = getCellValue(row, columnIndex);
                if (value) values.add(value);
            }});

            // Create filter container
            const header = table.rows[0].cells[columnIndex];
            const container = document.createElement('div');
            container.className = 'filter-container';
            container.style.top = (header.offsetHeight) + 'px';
            container.style.left = '0';

            // Add search input
            const search = document.createElement('input');
            search.type = 'text';
            search.className = 'filter-search';
            search.placeholder = 'Search...';
            search.addEventListener('input', function() {{
                const searchText = this.value.toLowerCase();
                const options = container.querySelectorAll('.filter-option');
                options.forEach(option => {{
                    const text = option.textContent.toLowerCase();
                    option.style.display = text.includes(searchText) ? '' : 'none';
                }});
            }});
            container.appendChild(search);

            // Add "Select All" option
            const allOption = document.createElement('div');
            allOption.className = 'filter-option';
            const allCheckbox = document.createElement('input');
            allCheckbox.type = 'checkbox';
            allCheckbox.checked = !activeFilters[columnIndex];
            allCheckbox.addEventListener('change', function() {{
                const options = container.querySelectorAll('.filter-option input[type="checkbox"]');
                options.forEach(option => {{
                    option.checked = this.checked;
                }});
            }});
            allOption.appendChild(allCheckbox);
            allOption.appendChild(document.createTextNode(' Select All'));
            container.appendChild(allOption);

            // Add options for each unique value
            const sortedValues = Array.from(values).sort();
            sortedValues.forEach(value => {{
                const option = document.createElement('div');
                option.className = 'filter-option';

                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.value = value;
                checkbox.checked = !activeFilters[columnIndex] ||
                                  (activeFilters[columnIndex] &&
                                   activeFilters[columnIndex].includes(value));

                option.appendChild(checkbox);
                option.appendChild(document.createTextNode(' ' + value));
                container.appendChild(option);
            }});

            // Add filter buttons
            const buttonContainer = document.createElement('div');
            buttonContainer.className = 'filter-buttons';

            const applyButton = document.createElement('button');
            applyButton.textContent = 'Apply Filter';
            applyButton.addEventListener('click', function() {{
                const selectedValues = [];
                const options = container.querySelectorAll('.filter-option:not(:first-child) input:checked');
                options.forEach(option => {{
                    selectedValues.push(option.value);
                }});

                if (selectedValues.length === 0 || selectedValues.length === sortedValues.length) {{
                    // If none or all selected, remove filter
                    delete activeFilters[columnIndex];
                }} else {{
                    // Otherwise, set filter
                    activeFilters[columnIndex] = selectedValues;
                }}

                applyFilters();
                container.remove();
            }});

            const clearButton = document.createElement('button');
            clearButton.textContent = 'Clear';
            clearButton.addEventListener('click', function() {{
                delete activeFilters[columnIndex];
                applyFilters();
                container.remove();
            }});

            buttonContainer.appendChild(clearButton);
            buttonContainer.appendChild(applyButton);
            container.appendChild(buttonContainer);

            // Position and show the container
            header.appendChild(container);
            container.style.display = 'block';

            // Close when clicking outside
            document.addEventListener('click', function closeFilter(e) {{
                if (!container.contains(e.target) && e.target !== header) {{
                    container.remove();
                    document.removeEventListener('click', closeFilter);
                }}
            }});
        }}

        // Function to apply all active filters
        function applyFilters() {{
            const table = document.getElementById('emailTable');
            const rows = Array.from(table.rows).slice(1); // Skip header row

            // Show all rows first
            rows.forEach(row => {{
                row.style.display = '';
            }});

            // Apply each active filter
            Object.keys(activeFilters).forEach(columnIndex => {{
                const allowedValues = activeFilters[columnIndex];
                if (!allowedValues || allowedValues.length === 0) return;

                rows.forEach(row => {{
                    // Skip already hidden rows
                    if (row.style.display === 'none') return;

                    const value = getCellValue(row, parseInt(columnIndex));
                    if (!allowedValues.includes(value)) {{
                        row.style.display = 'none';
                    }}
                }});
            }});

            // Update row numbers for visible rows
            let visibleIndex = 1;
            rows.forEach(row => {{
                if (row.style.display !== 'none') {{
                    row.cells[0].textContent = visibleIndex++;
                }}
            }});
        }}

        // Function to add filter buttons to headers
        function setupColumnFilters() {{
            const table = document.getElementById('emailTable');
            const headers = table.querySelectorAll('th');

            // Skip the first column (#)
            for (let i = 1; i < headers.length; i++) {{
                const header = headers[i];

                // Make header clickable for sorting
                header.addEventListener('click', function() {{
                    // Determine data type for this column
                    let dataType = 'string';
                    if (i === 3) dataType = 'date'; // Date column
                    if (i === 8) dataType = 'number'; // Invoice Number column

                    sortTable(i, dataType);
                }});

                // Add filter button
                const filterBtn = document.createElement('span');
                filterBtn.innerHTML = ' 🔍';
                filterBtn.style.cursor = 'pointer';
                filterBtn.style.fontSize = '12px';
                filterBtn.title = 'Filter';
                filterBtn.addEventListener('click', function(event) {{
                    showFilter(i, event);
                }});

                header.appendChild(filterBtn);
            }}
        }}

        // Initialize sorting and filters on page load
        window.onload = function() {{
            // Setup column filters
            setupColumnFilters();

            // Sort the table by date in descending order by default
            sortTable(3, 'date'); // Date is column index 3 (0-based)

            // Add a class to indicate that sorting and filtering are initialized
            document.body.classList.add('sorting-initialized');
        }};
    </script>
    <script src="table-sorter.js"></script>
</head>
<body>
    <h1>Email Analysis Reports - {folder_path}</h1>
    <p>Last updated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>Total emails analyzed: {len(reports)}</p>

    <div class="container">
        <table id="emailTable">
            <tr>
                <th>#</th>
                <th>Subject</th>
                <th>Subject Template</th>
                <th>Date</th>
                <th>Company Name</th>
                <th>Company ID</th>
                <th>Invoice ID</th>
                <th>Invoice Number</th>
                <th>Client Name</th>
                <th>Client ID</th>
                <th>User Email</th>
                <th>User Name</th>
                <th>User ID</th>
                <th>Report</th>
            </tr>
""")

        for i, (subject, filename, email_data) in enumerate(reports):
            # Format date if available
            date_str = ""
            if email_data and email_data.date:
                try:
                    date_str = email_data.date.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    date_str = str(email_data.date)

            # Get structured data if available
            subject_template = ""
            company_name = ""
            company_id = ""
            invoice_id = ""
            invoice_number = ""
            client_name = ""
            client_id = ""
            user_email = ""
            user_name = ""
            user_id = ""

            if email_data:
                subject_template = email_data.subject_template
                company_name = email_data.company_name
                company_id = email_data.company_id
                invoice_id = email_data.invoice_id
                invoice_number = email_data.invoice_number
                client_name = email_data.client_name
                client_id = email_data.client_id
                user_email = email_data.user_email
                user_name = email_data.user_name
                user_id = email_data.user_id

            # Helper function to format cell content
            def format_cell(value):
                if value:
                    return value
                return '<span class="empty-cell">N/A</span>'

            f.write(f"""
            <tr>
                <td>{i+1}</td>
                <td>{subject}</td>
                <td>{format_cell(subject_template)}</td>
                <td>{format_cell(date_str)}</td>
                <td>{format_cell(company_name)}</td>
                <td>{format_cell(company_id)}</td>
                <td>{format_cell(invoice_id)}</td>
                <td>{format_cell(invoice_number)}</td>
                <td>{format_cell(client_name)}</td>
                <td>{format_cell(client_id)}</td>
                <td>{format_cell(user_email)}</td>
                <td>{format_cell(user_name)}</td>
                <td>{format_cell(user_id)}</td>
                <td><a href="{filename}" target="_blank">View Report</a></td>
            </tr>
""")

        f.write("""
        </table>
    </div>
</body>
</html>
""")

    return index_path

def main():
    """Main function."""
    # Setup logging
    logger = setup_logging()
    logger.info("Starting email monitoring")

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load list of already processed emails
    processed_emails = load_processed_emails()
    logger.info(f"Loaded {len(processed_emails)} previously processed emails")

    try:
        # Connect to Outlook
        connector = OutlookConnector()
        if not connector.connect():
            logger.error("Failed to connect to Outlook. Exiting.")
            sys.exit(1)

        # Get the specified folder
        folder = connector.get_folder_by_path(EMAIL_ACCOUNT, FOLDER_PATH)
        if not folder:
            logger.error(f"Could not find folder: {FOLDER_PATH}. Exiting.")
            sys.exit(1)

        # Get all emails from the folder
        logger.info(f"Retrieving emails from {FOLDER_PATH}...")
        emails = connector.get_emails_from_folder(folder)

        if not emails:
            logger.warning("No emails found in the specified folder.")
            sys.exit(0)

        logger.info(f"Retrieved {len(emails)} emails. Checking for new emails...")

        # Filter out already processed emails
        new_emails = []
        for email in emails:
            email_hash = get_email_hash(email)
            if email_hash not in processed_emails:
                new_emails.append((email, email_hash))

        if not new_emails:
            logger.info("No new emails to process.")
            sys.exit(0)

        logger.info(f"Found {len(new_emails)} new emails. Analyzing...")

        # Create analyzer
        analyzer = Analyzer()

        # Analyze each new email
        for i, (email_data, email_hash) in enumerate(new_emails):
            logger.info(f"Analyzing new email {i+1}/{len(new_emails)}: {email_data.subject}")

            # Analyze the email
            analysis_results = analyzer.analyze(email_data)

            # Generate a filename for the report
            safe_subject = "".join([c if c.isalnum() or c in " -_" else "_" for c in email_data.subject])
            safe_subject = safe_subject[:50]  # Limit length
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"{safe_subject}_{timestamp}.{FORMAT}"
            report_path = os.path.join(OUTPUT_DIR, report_filename)

            # Save the report
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(analysis_results.to_format(FORMAT))

            logger.info(f"Saved analysis report to: {report_path}")

            # Mark email as processed
            processed_emails[email_hash] = {
                "subject": email_data.subject,
                "from": email_data.from_address,
                "date": str(email_data.date),
                "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        # Save the updated list of processed emails
        save_processed_emails(processed_emails)
        logger.info(f"Updated processed emails list. Total: {len(processed_emails)}")

        # Create an index.html file
        if FORMAT == "html":
            create_html_index(OUTPUT_DIR, emails, FOLDER_PATH)
            logger.info(f"Updated index file: {os.path.join(OUTPUT_DIR, 'index.html')}")

        logger.info(f"Analysis complete. {len(new_emails)} new emails processed.")

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
