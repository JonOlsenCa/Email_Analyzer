// table-sorter.js - Adds sorting and filtering functionality to the email table

// This script is designed to be loaded after the page has loaded
// It will add sorting and filtering functionality to the email table

// Global variables to track current sort state
let currentSortColumn = 3; // Default sort by Date column (0-based index)
let currentSortDirection = 'desc'; // Default sort direction is descending
let activeFilters = {}; // Store active filters for each column

// Function to get cell text content, handling special cases
function getCellValue(row, index) {
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
}

// Function to compare values for sorting
function compareValues(a, b, type, direction) {
    // Handle empty values
    if (a === '' && b === '') return 0;
    if (a === '') return direction === 'asc' ? 1 : -1;
    if (b === '') return direction === 'asc' ? -1 : 1;

    // Compare based on data type
    if (type === 'date') {
        // Parse dates and compare
        const dateA = new Date(a);
        const dateB = new Date(b);
        return direction === 'asc'
            ? dateA - dateB
            : dateB - dateA;
    } else if (type === 'number') {
        // Parse numbers and compare
        const numA = parseFloat(a.replace(/[^0-9.-]+/g, ''));
        const numB = parseFloat(b.replace(/[^0-9.-]+/g, ''));
        return direction === 'asc'
            ? numA - numB
            : numB - numA;
    } else {
        // Default string comparison
        return direction === 'asc'
            ? a.localeCompare(b)
            : b.localeCompare(a);
    }
}

// Function to sort the table by a specific column
function sortTable(columnIndex, dataType = 'string') {
    const table = document.getElementById('emailTable');
    const headers = table.querySelectorAll('th');
    const rows = Array.from(table.rows).slice(1); // Skip header row

    // Determine sort direction
    let direction = 'asc';
    if (columnIndex === currentSortColumn) {
        // If already sorting by this column, toggle direction
        direction = currentSortDirection === 'asc' ? 'desc' : 'asc';
    }

    // Update sort indicators in headers
    headers.forEach(header => {
        header.classList.remove('sorted-asc', 'sorted-desc');
    });
    headers[columnIndex].classList.add(direction === 'asc' ? 'sorted-asc' : 'sorted-desc');

    // Sort the rows
    rows.sort((rowA, rowB) => {
        const valueA = getCellValue(rowA, columnIndex);
        const valueB = getCellValue(rowB, columnIndex);
        return compareValues(valueA, valueB, dataType, direction);
    });

    // Reorder the rows in the table
    const tbody = table.tBodies[0] || table;
    rows.forEach(row => tbody.appendChild(row));

    // Update row numbers
    rows.forEach((row, index) => {
        row.cells[0].textContent = index + 1;
    });

    // Update current sort state
    currentSortColumn = columnIndex;
    currentSortDirection = direction;
}

// Function to create and show filter dropdown for a column
function showFilter(columnIndex, event) {
    // Don't sort when clicking on filter
    event.stopPropagation();

    // Remove any existing filter containers
    const existingContainers = document.querySelectorAll('.filter-container');
    existingContainers.forEach(container => container.remove());

    // Get unique values for this column
    const table = document.getElementById('emailTable');
    const rows = Array.from(table.rows).slice(1); // Skip header row
    const values = new Set();

    rows.forEach(row => {
        const value = getCellValue(row, columnIndex);
        if (value) values.add(value);
    });

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
    search.addEventListener('input', function() {
        const searchText = this.value.toLowerCase();
        const options = container.querySelectorAll('.filter-option');
        options.forEach(option => {
            const text = option.textContent.toLowerCase();
            option.style.display = text.includes(searchText) ? '' : 'none';
        });
    });
    container.appendChild(search);

    // Add "Select All" option
    const allOption = document.createElement('div');
    allOption.className = 'filter-option';
    const allCheckbox = document.createElement('input');
    allCheckbox.type = 'checkbox';
    allCheckbox.checked = !activeFilters[columnIndex];
    allCheckbox.addEventListener('change', function() {
        const options = container.querySelectorAll('.filter-option input[type="checkbox"]');
        options.forEach(option => {
            option.checked = this.checked;
        });
    });
    allOption.appendChild(allCheckbox);
    allOption.appendChild(document.createTextNode(' Select All'));
    container.appendChild(allOption);

    // Add options for each unique value
    const sortedValues = Array.from(values).sort();
    sortedValues.forEach(value => {
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
    });

    // Add filter buttons
    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'filter-buttons';

    const applyButton = document.createElement('button');
    applyButton.textContent = 'Apply Filter';
    applyButton.addEventListener('click', function() {
        const selectedValues = [];
        const options = container.querySelectorAll('.filter-option:not(:first-child) input:checked');
        options.forEach(option => {
            selectedValues.push(option.value);
        });

        if (selectedValues.length === 0 || selectedValues.length === sortedValues.length) {
            // If none or all selected, remove filter
            delete activeFilters[columnIndex];
        } else {
            // Otherwise, set filter
            activeFilters[columnIndex] = selectedValues;
        }

        applyFilters();
        container.remove();
    });

    const clearButton = document.createElement('button');
    clearButton.textContent = 'Clear';
    clearButton.addEventListener('click', function() {
        delete activeFilters[columnIndex];
        applyFilters();
        container.remove();
    });

    buttonContainer.appendChild(clearButton);
    buttonContainer.appendChild(applyButton);
    container.appendChild(buttonContainer);

    // Position and show the container
    header.appendChild(container);
    container.style.display = 'block';

    // Close when clicking outside
    document.addEventListener('click', function closeFilter(e) {
        if (!container.contains(e.target) && e.target !== header) {
            container.remove();
            document.removeEventListener('click', closeFilter);
        }
    });
}

// Function to apply all active filters
function applyFilters() {
    const table = document.getElementById('emailTable');
    const rows = Array.from(table.rows).slice(1); // Skip header row

    // Show all rows first
    rows.forEach(row => {
        row.style.display = '';
    });

    // Apply each active filter
    Object.keys(activeFilters).forEach(columnIndex => {
        const allowedValues = activeFilters[columnIndex];
        if (!allowedValues || allowedValues.length === 0) return;

        rows.forEach(row => {
            // Skip already hidden rows
            if (row.style.display === 'none') return;

            const value = getCellValue(row, parseInt(columnIndex));
            if (!allowedValues.includes(value)) {
                row.style.display = 'none';
            }
        });
    });

    // Update row numbers for visible rows
    let visibleIndex = 1;
    rows.forEach(row => {
        if (row.style.display !== 'none') {
            row.cells[0].textContent = visibleIndex++;
        }
    });
}

// Function to add filter buttons to headers
function setupColumnFilters() {
    const table = document.getElementById('emailTable');
    const headers = table.querySelectorAll('th');

    // Skip the first column (#)
    for (let i = 1; i < headers.length; i++) {
        const header = headers[i];

        // Make header clickable for sorting
        header.addEventListener('click', function() {
            // Determine data type for this column
            let dataType = 'string';
            if (i === 3) dataType = 'date'; // Date column
            if (i === 8) dataType = 'number'; // Invoice Number column

            sortTable(i, dataType);
        });

        // Add filter button
        const filterBtn = document.createElement('span');
        filterBtn.innerHTML = ' 🔍';
        filterBtn.style.cursor = 'pointer';
        filterBtn.style.fontSize = '12px';
        filterBtn.title = 'Filter';
        filterBtn.addEventListener('click', function(event) {
            showFilter(i, event);
        });

        header.appendChild(filterBtn);
    }
}

// Add CSS styles for sorting and filtering
function addStyles() {
    const style = document.createElement('style');
    style.textContent = `
        th {
            cursor: pointer;
            user-select: none;
        }
        th:hover { background-color: #ddd; }
        th.sorted-asc::after { content: " ▲"; }
        th.sorted-desc::after { content: " ▼"; }
        .filter-container {
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
        }
        .filter-option { margin: 5px 0; }
        .filter-search {
            width: 100%;
            padding: 5px;
            margin-bottom: 10px;
            box-sizing: border-box;
        }
        .filter-buttons {
            display: flex;
            justify-content: space-between;
            margin-top: 10px;
        }
        .filter-buttons button {
            padding: 5px 10px;
            cursor: pointer;
        }
    `;
    document.head.appendChild(style);
}

// Initialize sorting and filtering when the page loads
function initializeSortingAndFiltering() {
    // Add CSS styles
    addStyles();

    // Setup column filters
    setupColumnFilters();

    // Sort the table by date in descending order by default
    sortTable(3, 'date'); // Date is column index 3 (0-based)
}

// Run initialization immediately if the document is already loaded
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    setTimeout(checkAndInitialize, 1);
} else {
    // Otherwise wait for the DOM to be ready
    document.addEventListener('DOMContentLoaded', checkAndInitialize);
}

// Also add a fallback to initialize after window load
window.addEventListener('load', checkAndInitialize);

// Function to check if sorting and filtering are already initialized
function checkAndInitialize() {
    // Check if sorting and filtering are already initialized
    if (document.body.classList.contains('sorting-initialized')) {
        console.log('Sorting and filtering already initialized');
        return;
    }

    // Check if the table headers have filter buttons
    const table = document.getElementById('emailTable');
    if (table) {
        const headers = table.querySelectorAll('th');
        const hasFilters = headers.length > 0 && headers[1].querySelector('span[title="Filter"]');

        // If no filters are found, initialize
        if (!hasFilters) {
            console.log('Initializing sorting and filtering');
            initializeSortingAndFiltering();
            document.body.classList.add('sorting-initialized');
        } else {
            console.log('Filters already exist, not initializing');
            document.body.classList.add('sorting-initialized');
        }
    } else {
        console.log('Table not found');
    }
}
