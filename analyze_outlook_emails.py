#!/usr/bin/env python3
"""
Analyze Outlook Emails

This script retrieves emails from a specified Outlook folder and analyzes them
using the Email Analyzer.
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from outlook_connector import OutlookConnector
from analyzer import Analyzer
from utils import setup_logging

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Retrieve and analyze emails from an Outlook folder."
    )

    parser.add_argument(
        "--email-account",
        default="jon@olsenconsulting.ca",
        help="Email account to use (default: jon@olsenconsulting.ca)"
    )

    parser.add_argument(
        "--folder-path",
        default="Inbox/APWizard_Tickets",
        help="Path to the Outlook folder (default: Inbox/APWizard_Tickets)"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Maximum number of emails to retrieve (default: 100)"
    )

    parser.add_argument(
        "--output-dir",
        default="analyzed_emails",
        help="Directory to save analysis reports (default: analyzed_emails)"
    )

    parser.add_argument(
        "--format",
        choices=["text", "json", "html"],
        default="html",
        help="Output format for analysis reports (default: html)"
    )

    parser.add_argument(
        "--save-eml",
        action="store_true",
        help="Save emails as EML files"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    return parser.parse_args()

def main():
    """Main function."""
    args = parse_arguments()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logging(log_level)

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    try:
        # Connect to Outlook
        connector = OutlookConnector()
        if not connector.connect():
            logger.error("Failed to connect to Outlook. Exiting.")
            sys.exit(1)

        # Get the specified folder
        folder = connector.get_folder_by_path(args.email_account, args.folder_path)
        if not folder:
            logger.error(f"Could not find folder: {args.folder_path}. Exiting.")
            sys.exit(1)

        # Create EML directory if saving emails
        eml_dir = os.path.join(args.output_dir, "eml_files")
        if args.save_eml:
            os.makedirs(eml_dir, exist_ok=True)

        # Get emails from the folder
        logger.info(f"Retrieving up to {args.limit} emails from {args.folder_path}...")
        emails = connector.get_emails_from_folder(
            folder,
            limit=args.limit,
            save_to_eml=args.save_eml,
            output_dir=eml_dir if args.save_eml else None
        )

        if not emails:
            logger.warning("No emails found in the specified folder.")
            sys.exit(0)

        logger.info(f"Retrieved {len(emails)} emails. Analyzing...")

        # Create analyzer
        analyzer = Analyzer()

        # Analyze each email
        for i, email_data in enumerate(emails):
            logger.info(f"Analyzing email {i+1}/{len(emails)}: {email_data.subject}")

            # Analyze the email
            analysis_results = analyzer.analyze(email_data)

            # Generate a filename for the report
            safe_subject = "".join([c if c.isalnum() or c in " -_" else "_" for c in email_data.subject])
            safe_subject = safe_subject[:50]  # Limit length
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"{safe_subject}_{timestamp}.{args.format}"
            report_path = os.path.join(args.output_dir, report_filename)

            # Save the report
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(analysis_results.to_format(args.format))

            logger.info(f"Saved analysis report to: {report_path}")

            # Print summary for text format
            if args.format == "text":
                print(f"\nEmail {i+1}: {email_data.subject}")
                print(f"From: {email_data.from_address}")
                print(f"Date: {email_data.date}")
                print(f"Security Risk: {analysis_results.summary.get('Overall Security Risk', 'Unknown')}")
                print(f"Report: {report_path}")
                print("-" * 50)

        # Create an index.html file if using HTML format
        if args.format == "html":
            create_html_index(args.output_dir, emails, args.folder_path)

        logger.info(f"Analysis complete. Reports saved to: {args.output_dir}")

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

def create_html_index(output_dir, emails, folder_path):
    """
    Create an HTML index file for the analysis reports.

    Args:
        output_dir (str): Directory containing the reports
        emails (list): List of analyzed emails
        folder_path (str): Path to the Outlook folder
    """
    index_path = os.path.join(output_dir, "index.html")

    # Use a dictionary to store unique reports based on email content
    # This will ensure we don't have duplicates
    unique_reports = {}

    # First, create a mapping of emails by their unique identifiers
    # We'll use a combination of subject, date, and from_address as a unique key
    for email in emails:
        # Create a unique key for each email
        if hasattr(email, 'date') and email.date:
            date_str = str(email.date)
        else:
            date_str = ""

        unique_key = f"{email.subject}|{date_str}|{email.from_address}"

        # Store the most recent report for each unique email
        if unique_key not in unique_reports:
            # Create a safe subject for filename matching
            safe_subject = "".join([c if c.isalnum() or c in " -_" else "_" for c in email.subject])
            safe_subject = safe_subject[:50]  # Limit length

            # Find the most recent report file for this email
            latest_report = None
            latest_timestamp = None

            for filename in os.listdir(output_dir):
                if filename.endswith(".html") and filename != "index.html" and safe_subject in filename:
                    # Extract timestamp from filename
                    try:
                        timestamp_part = filename.rsplit("_", 1)[1].split(".")[0]
                        if not latest_timestamp or timestamp_part > latest_timestamp:
                            latest_timestamp = timestamp_part
                            latest_report = filename
                    except:
                        # If we can't parse the timestamp, just use this file if we don't have one yet
                        if not latest_report:
                            latest_report = filename

            if latest_report:
                unique_reports[unique_key] = (email.subject, latest_report, email)

    # Convert the dictionary to a list
    reports = list(unique_reports.values())

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
        .dropdown-content {{
            display: none;
            position: absolute;
            background-color: #f9f9f9;
            min-width: 160px;
            box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
            z-index: 1;
            padding: 12px 16px;
        }}
        .dropdown {{ position: relative; display: inline-block; }}
        .btn {{
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            cursor: pointer;
            margin-bottom: 10px;
        }}
        .checkbox-item {{ margin: 5px 0; }}
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
        .refresh-btn {{
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 15px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 14px;
            margin: 10px 0;
            cursor: pointer;
            border-radius: 3px;
        }}
        .refresh-btn:hover {{
            background-color: #45a049;
        }}
        .refresh-btn:disabled {{
            background-color: #cccccc;
            color: #666666;
            cursor: not-allowed;
        }}
    </style>
    <script>
        // Global variables to track current sort state
        let currentSortColumn = 3; // Default sort by Date column (0-based index)
        let currentSortDirection = 'desc'; // Default sort direction is descending
        let activeFilters = {{}}; // Store active filters for each column
        let allTableData = []; // Store all table data for filtering

        function toggleColumns() {{
            const dropdown = document.getElementById('columnDropdown');
            dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
        }}

        function toggleColumn(colIndex, checked) {{
            const table = document.getElementById('emailTable');
            const rows = table.getElementsByTagName('tr');

            // Skip header row (index 0)
            for (let i = 0; i < rows.length; i++) {{
                const cells = rows[i].getElementsByTagName(i === 0 ? 'th' : 'td');
                if (cells.length > colIndex) {{
                    cells[colIndex].style.display = checked ? '' : 'none';
                }}
            }}
        }}

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

        // Function to refresh emails
        function refreshEmails() {{
            // Get the latest email date from the table
            const table = document.getElementById('emailTable');
            const rows = Array.from(table.rows).slice(1); // Skip header row
            let latestDate = null;

            // Find the latest date in the table
            rows.forEach(row => {{
                const dateCell = row.cells[3]; // Date is in column 3 (0-based index)
                if (dateCell) {{
                    const dateStr = dateCell.textContent.trim();
                    if (dateStr && dateStr !== 'N/A') {{
                        const date = new Date(dateStr);
                        if (!isNaN(date) && (!latestDate || date > latestDate)) {{
                            latestDate = date;
                        }}
                    }}
                }}
            }});

            // Format the date for the API request
            const latestDateStr = latestDate ?
                latestDate.getFullYear() + '-' +
                String(latestDate.getMonth() + 1).padStart(2, '0') + '-' +
                String(latestDate.getDate()).padStart(2, '0') + ' ' +
                String(latestDate.getHours()).padStart(2, '0') + ':' +
                String(latestDate.getMinutes()).padStart(2, '0') + ':' +
                String(latestDate.getSeconds()).padStart(2, '0') : '';

            // Disable the refresh button and show loading state
            const refreshBtn = document.getElementById('refreshButton');
            const originalText = refreshBtn.textContent;
            refreshBtn.textContent = 'Refreshing...';
            refreshBtn.disabled = true;

            // Make API request to get new emails
            fetch('http://localhost:8001/refresh?latest_email_date=' + encodeURIComponent(latestDateStr))
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        const newEmails = data.new_emails;
                        if (newEmails && newEmails.length > 0) {{
                            // Add new emails to the table
                            addNewEmailsToTable(newEmails);
                            alert('Added ' + newEmails.length + ' new email(s)');
                        }} else {{
                            alert('No new emails found');
                        }}
                    }} else {{
                        alert('Failed to refresh emails: ' + (data.error || 'Unknown error'));
                    }}
                    refreshBtn.textContent = originalText;
                    refreshBtn.disabled = false;
                }})
                .catch(error => {{
                    console.error('Error refreshing emails:', error);
                    alert('An error occurred while refreshing emails. Please try again.');
                    refreshBtn.textContent = originalText;
                    refreshBtn.disabled = false;
                }});
        }}

        // Function to add new emails to the table
        function addNewEmailsToTable(newEmails) {{
            const table = document.getElementById('emailTable');
            const tbody = table.tBodies[0] || table;

            // Add each new email to the table
            newEmails.forEach(email => {{
                const row = document.createElement('tr');

                // Add row number (will be updated later)
                const cellNum = document.createElement('td');
                cellNum.textContent = '0';
                row.appendChild(cellNum);

                // Add subject
                const cellSubject = document.createElement('td');
                cellSubject.textContent = email.subject;
                row.appendChild(cellSubject);

                // Add subject template
                const cellSubjectTemplate = document.createElement('td');
                if (email.subject_template) {{
                    cellSubjectTemplate.textContent = email.subject_template;
                }} else {{
                    cellSubjectTemplate.innerHTML = '<span class="empty-cell">N/A</span>';
                }}
                row.appendChild(cellSubjectTemplate);

                // Add date
                const cellDate = document.createElement('td');
                if (email.date) {{
                    cellDate.textContent = email.date;
                }} else {{
                    cellDate.innerHTML = '<span class="empty-cell">N/A</span>';
                }}
                row.appendChild(cellDate);

                // Add description
                const cellDescription = document.createElement('td');
                if (email.description) {{
                    cellDescription.textContent = email.description;
                }} else {{
                    cellDescription.innerHTML = '<span class="empty-cell">N/A</span>';
                }}
                row.appendChild(cellDescription);

                // Add company name
                const cellCompanyName = document.createElement('td');
                if (email.company_name) {{
                    cellCompanyName.textContent = email.company_name;
                }} else {{
                    cellCompanyName.innerHTML = '<span class="empty-cell">N/A</span>';
                }}
                row.appendChild(cellCompanyName);

                // Add company ID
                const cellCompanyId = document.createElement('td');
                if (email.company_id) {{
                    cellCompanyId.textContent = email.company_id;
                }} else {{
                    cellCompanyId.innerHTML = '<span class="empty-cell">N/A</span>';
                }}
                row.appendChild(cellCompanyId);

                // Add invoice ID
                const cellInvoiceId = document.createElement('td');
                if (email.invoice_id) {{
                    cellInvoiceId.innerHTML = '<a href="https://platform.apwizard.ai/ap-task/' + email.invoice_id + '" target="_blank">' + email.invoice_id + '</a>';
                }} else {{
                    cellInvoiceId.innerHTML = '<span class="empty-cell">N/A</span>';
                }}
                row.appendChild(cellInvoiceId);

                // Add invoice number
                const cellInvoiceNumber = document.createElement('td');
                if (email.invoice_number) {{
                    cellInvoiceNumber.textContent = email.invoice_number;
                }} else {{
                    cellInvoiceNumber.innerHTML = '<span class="empty-cell">N/A</span>';
                }}
                row.appendChild(cellInvoiceNumber);

                // Add client name
                const cellClientName = document.createElement('td');
                if (email.client_name) {{
                    cellClientName.textContent = email.client_name;
                }} else {{
                    cellClientName.innerHTML = '<span class="empty-cell">N/A</span>';
                }}
                row.appendChild(cellClientName);

                // Add client ID
                const cellClientId = document.createElement('td');
                if (email.client_id) {{
                    cellClientId.textContent = email.client_id;
                }} else {{
                    cellClientId.innerHTML = '<span class="empty-cell">N/A</span>';
                }}
                row.appendChild(cellClientId);

                // Add user email
                const cellUserEmail = document.createElement('td');
                if (email.user_email) {{
                    cellUserEmail.textContent = email.user_email;
                }} else {{
                    cellUserEmail.innerHTML = '<span class="empty-cell">N/A</span>';
                }}
                row.appendChild(cellUserEmail);

                // Add user name
                const cellUserName = document.createElement('td');
                if (email.user_name) {{
                    cellUserName.textContent = email.user_name;
                }} else {{
                    cellUserName.innerHTML = '<span class="empty-cell">N/A</span>';
                }}
                row.appendChild(cellUserName);

                // Add user ID
                const cellUserId = document.createElement('td');
                if (email.user_id) {{
                    cellUserId.textContent = email.user_id;
                }} else {{
                    cellUserId.innerHTML = '<span class="empty-cell">N/A</span>';
                }}
                row.appendChild(cellUserId);

                // Add report link (placeholder since we don't have a report file for new emails)
                const cellReport = document.createElement('td');
                cellReport.innerHTML = '<span class="empty-cell">N/A</span>';
                row.appendChild(cellReport);

                // Add the row to the table
                tbody.insertBefore(row, tbody.firstChild);
            }});

            // Update row numbers
            const allRows = Array.from(table.rows).slice(1); // Skip header row
            allRows.forEach((row, index) => {{
                row.cells[0].textContent = index + 1;
            }});

            // Update the email count
            const emailCount = document.getElementById('emailCount');
            emailCount.textContent = allRows.length;

            // Apply current column visibility settings
            for (let i = 1; i < 15; i++) {{
                const checkbox = document.getElementById('col' + i);
                if (checkbox && !checkbox.checked) {{
                    toggleColumn(i, false);
                }}
            }}

            // Re-sort the table using the current sort settings
            sortTable(currentSortColumn, currentSortColumn === 3 ? 'date' : 'string');

            // Re-apply filters
            applyFilters();
        }}

        // Initialize column visibility, sorting, and filters on page load
        window.onload = function() {{
            // Only show these columns by default: Subject, Subject Template, Date, Description,
            // Company Name, Invoice ID, Invoice Number, User Email, and Report

            // Hide Company ID
            toggleColumn(6, false);
            // Invoice ID is now visible by default
            // Hide Client Name
            toggleColumn(9, false);
            // Hide Client ID
            toggleColumn(10, false);
            // Hide User Name
            toggleColumn(12, false);
            // Hide User ID
            toggleColumn(13, false);

            // Update checkboxes to match initial state
            document.getElementById('col6').checked = false;
            document.getElementById('col7').checked = true; // Invoice ID is checked
            document.getElementById('col9').checked = false;
            document.getElementById('col10').checked = false;
            document.getElementById('col12').checked = false;
            document.getElementById('col13').checked = false;

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
    <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>Total emails analyzed: <span id="emailCount">{len(reports)}</span></p>
    <button id="refreshButton" class="refresh-btn" onclick="refreshEmails()">Refresh</button>

    <div class="dropdown">
        <button class="btn" onclick="toggleColumns()">Show Columns</button>
        <div class="dropdown-content" id="columnDropdown">
            <div class="checkbox-item"><input type="checkbox" id="col1" checked onchange="toggleColumn(1, this.checked)"> <label for="col1">Subject</label></div>
            <div class="checkbox-item"><input type="checkbox" id="col2" checked onchange="toggleColumn(2, this.checked)"> <label for="col2">Subject Template</label></div>
            <div class="checkbox-item"><input type="checkbox" id="col3" checked onchange="toggleColumn(3, this.checked)"> <label for="col3">Date</label></div>
            <div class="checkbox-item"><input type="checkbox" id="col4" checked onchange="toggleColumn(4, this.checked)"> <label for="col4">Description</label></div>
            <div class="checkbox-item"><input type="checkbox" id="col5" checked onchange="toggleColumn(5, this.checked)"> <label for="col5">Company Name</label></div>
            <div class="checkbox-item"><input type="checkbox" id="col6" onchange="toggleColumn(6, this.checked)"> <label for="col6">Company ID</label></div>
            <div class="checkbox-item"><input type="checkbox" id="col7" checked onchange="toggleColumn(7, this.checked)"> <label for="col7">Invoice ID</label></div>
            <div class="checkbox-item"><input type="checkbox" id="col8" checked onchange="toggleColumn(8, this.checked)"> <label for="col8">Invoice Number</label></div>
            <div class="checkbox-item"><input type="checkbox" id="col9" onchange="toggleColumn(9, this.checked)"> <label for="col9">Client Name</label></div>
            <div class="checkbox-item"><input type="checkbox" id="col10" onchange="toggleColumn(10, this.checked)"> <label for="col10">Client ID</label></div>
            <div class="checkbox-item"><input type="checkbox" id="col11" checked onchange="toggleColumn(11, this.checked)"> <label for="col11">User Email</label></div>
            <div class="checkbox-item"><input type="checkbox" id="col12" onchange="toggleColumn(12, this.checked)"> <label for="col12">User Name</label></div>
            <div class="checkbox-item"><input type="checkbox" id="col13" onchange="toggleColumn(13, this.checked)"> <label for="col13">User ID</label></div>
            <div class="checkbox-item"><input type="checkbox" id="col14" checked onchange="toggleColumn(14, this.checked)"> <label for="col14">Report</label></div>
        </div>
    </div>

    <div class="container">
        <table id="emailTable">
            <tr>
                <th>#</th>
                <th>Subject</th>
                <th>Subject Template</th>
                <th>Date</th>
                <th>Description</th>
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
            description = ""
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
                # Force extraction of structured data if not already done
                # This ensures we have the latest data
                from outlook_connector import OutlookConnector
                connector = OutlookConnector()
                connector._extract_structured_data(email_data)

                subject_template = email_data.subject_template
                description = email_data.description if hasattr(email_data, 'description') else ""
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
                <td>{format_cell(description)}</td>
                <td>{format_cell(company_name)}</td>
                <td>{format_cell(company_id)}</td>
                <td>{format_cell(f'<a href="{email_data.invoice_id_url if hasattr(email_data, "invoice_id_url") and email_data.invoice_id_url else f"https://platform.apwizard.ai/ap-task/{invoice_id}"}" target="_blank">{invoice_id}</a>') if invoice_id else '<span class="empty-cell">N/A</span>'}</td>
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

if __name__ == "__main__":
    main()
