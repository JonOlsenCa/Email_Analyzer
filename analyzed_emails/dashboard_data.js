// This file contains the data for the dashboard
// It is loaded by dashboard.html

// Global variables - these will be accessible from dashboard.html
window.emailData = [];
window.companyChart = null;
window.subjectChart = null;
window.categoryChart = null;

// Company name mapping - make it globally accessible
window.companyNameMap = {
    "Gulf Stream Construction": "Gulf Stream Construction Co., Inc.",
    "GBI": "Great Basin Industrial",
    "TSU One, Inc.": "Texas State Utilities",
    "TaftElectric": "Taft Electric Company",
    "Doggett Concrete Construction": "Doggett Concrete Construction",
    "Concrete & Materials Placement": "Concrete & Materials Placement",
    "H&M Mechanical Constructors, Inc.": "H&M Mechanical Constructors, Inc.",
    "Haskell Lemon": "Haskell Lemon",
    "NP Mechanical, Inc.": "NP Mechanical, Inc.",
    "S.M. Hentges": "S.M. Hentges"
};

// Required companies (to ensure they appear in filters even if not in data)
window.requiredCompanies = [
    "All Companies",
    "Gulf Stream Construction Co., Inc.",
    "Great Basin Industrial",
    "Texas State Utilities",
    "Taft Electric Company",
    "Doggett Concrete Construction",
    "Concrete & Materials Placement",
    "H&M Mechanical Constructors, Inc.",
    "Haskell Lemon",
    "NP Mechanical, Inc.",
    "S.M. Hentges",
    "Beacon Communications, LLC",
    "Ben H. Construction Co.",
    "Rusty Reservoir Contractors, LLC",
    "Comet System Technology",
    "OGI"
];

// Sample data for testing - make it globally accessible
// This will be replaced with actual data from index.html
window.sampleData = [
    {
        subject: "[SUPPORT] [TaftElectric] System Performance Issues",
        subjectTemplate: "System Performance Issues",
        date: new Date("2025-05-06 10:20:07"),
        description: "GRANT SELECT ON LIC.LicenseHeader TO ApWizardRole; --30-APR-2025 Required for accessing License details Can you please help me with this message I received when accessing the AP Wizard. Thank you, Michelle Dunham - mdunham@taftelectric.com",
        category: "System Bugs & Integration Issues",
        companyName: "Taft Electric Company",
        invoiceId: "f1fe6d7e-ffaf-4391-ba83-7e5106d19f34",
        invoiceNumber: "",
        clientName: "TaftElectric",
        userEmail: "mdunham@taftelectric.com"
    },
    {
        subject: "[SUPPORT] [TaftElectric] Incorrect Vendor Prediction",
        subjectTemplate: "Incorrect Vendor Prediction",
        date: new Date("2025-05-12 10:46:59"),
        description: "The system predicted the wrong vendor for this transaction. Predicted Concrete Pipe & Precast. Should be Martin Marietta.",
        category: "AI Model Prediction & Extraction Issues",
        companyName: "Taft Electric Company",
        invoiceId: "426a70bb-b083-494e-9621-8487b8dfb025",
        invoiceNumber: "",
        clientName: "TaftElectric",
        userEmail: "shageatha@olsenconsulting.ca"
    },
    {
        subject: "[SUPPORT] [TSU One, Inc.] Other",
        subjectTemplate: "Other",
        date: new Date("2025-05-06 06:34:45"),
        description: "Not all invoice line items were correctly retrieved from this invoice - Shageatha",
        category: "AI Model Prediction & Extraction Issues",
        companyName: "Texas State Utilities",
        invoiceId: "fbc46eff-6f93-4631-bd22-b126abcdad4f",
        invoiceNumber: "2740253006",
        clientName: "TSU One, Inc.",
        userEmail: "shageatha@olsenconsulting.ca"
    },
    {
        subject: "[SUPPORT] [Gulf Stream Construction] Incorrect Vendor Prediction",
        subjectTemplate: "Incorrect Vendor Prediction",
        date: new Date("2025-05-13 12:25:37"),
        description: "The system predicted the wrong vendor for this transaction. Predicted Concrete Pipe & Precast. Should be Martin Marietta.",
        category: "AI Model Prediction & Extraction Issues",
        companyName: "Gulf Stream Construction Co., Inc.",
        invoiceId: "bcb32f9d-b563-4486-8247-4dd76856aa60",
        invoiceNumber: "",
        clientName: "Gulf Stream Construction",
        userEmail: "LWysocki@gulfstreamconstruction.com"
    },
    {
        subject: "[SUPPORT] [NP Mechanical, Inc.] Other",
        subjectTemplate: "Other",
        date: new Date("2025-05-02 07:18:22"),
        description: "Is there any way to set up recipients in the email templates? I sent my invoice discrepancies over to the same multiple people. Therefore, I have to copy and paste the same multiple people onto each email that I send out. Its inefficient and time consuming. Please advise",
        category: "Document Processing Failures",
        companyName: "NP Mechanical, Inc.",
        invoiceId: "3816d006-14c4-460f-83f9-749aa6c2537e",
        invoiceNumber: "45652174",
        clientName: "NP Mechanical, Inc.",
        userEmail: "noreply@apwizard.ai"
    }
];

// Function to load data from index.html
function loadDataFromIndexHTML() {
    console.log('Loading data from index.html...');
    const result = [];

    // Check if we're running in a file:// context, which might cause CORS issues
    if (window.location.protocol === 'file:') {
        console.warn('Running from file:// protocol. Fetch may fail due to CORS restrictions.');
        console.log('Falling back to sample data due to file:// protocol');

        // Create a custom event to notify that data is ready (using sample data)
        setTimeout(() => {
            const event = new CustomEvent('dashboardDataReady', {
                detail: {
                    dataLength: window.sampleData.length,
                    usingSampleData: true,
                    source: 'file protocol detection'
                }
            });
            document.dispatchEvent(event);
        }, 0);

        return Promise.resolve(window.sampleData);
    }

    // Use fetch to get the index.html content
    return fetch('index.html')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to fetch index.html: ${response.status} ${response.statusText}`);
            }
            return response.text();
        })
        .then(html => {
            console.log('Successfully fetched index.html');

            // Create a temporary DOM element to parse the HTML
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');

            // Get the table body rows
            const rows = doc.querySelectorAll('#emailTable tbody tr');
            console.log(`Found ${rows.length} rows in index.html`);

            if (rows.length === 0) {
                console.warn('No rows found in index.html table. Falling back to sample data.');
                return window.sampleData;
            }

            // Process each row
            rows.forEach(row => {
                const cells = row.querySelectorAll('td');
                if (cells.length >= 15) {
                    // Extract data from cells
                    const subject = cells[1].textContent.trim();
                    const subjectTemplate = cells[2].textContent.trim();
                    const dateStr = cells[3].textContent.trim();
                    const description = cells[4].textContent.trim();
                    const category = cells[5].textContent.trim();
                    const companyName = cells[6].textContent.trim();

                    // Get invoice ID (might be in an anchor tag)
                    let invoiceId = '';
                    const invoiceLink = cells[8].querySelector('a');
                    if (invoiceLink) {
                        invoiceId = invoiceLink.textContent.trim();
                    } else {
                        invoiceId = cells[8].textContent.trim();
                    }

                    // Get invoice number
                    let invoiceNumber = '';
                    const emptyInvoiceNumber = cells[9].querySelector('.empty-cell');
                    if (!emptyInvoiceNumber) {
                        invoiceNumber = cells[9].textContent.trim();
                    }

                    // Get client name
                    const clientName = cells[10].textContent.trim();

                    // Get user email
                    const userEmail = cells[12].textContent.trim();

                    // Create a date object
                    let date = null;
                    if (dateStr && dateStr !== 'N/A') {
                        date = new Date(dateStr);
                    }

                    // Create an email data object
                    const emailObj = {
                        subject,
                        subjectTemplate,
                        date,
                        description,
                        category,
                        companyName,
                        invoiceId,
                        invoiceNumber,
                        clientName,
                        userEmail
                    };

                    // Add to result array
                    result.push(emailObj);
                }
            });

            console.log(`Processed ${result.length} emails from index.html`);

            if (result.length === 0) {
                console.warn('No data extracted from index.html. Falling back to sample data.');
                return window.sampleData;
            }

            return result;
        })
        .catch(error => {
            console.error('Error loading data from index.html:', error);
            // Fall back to sample data if there's an error
            console.log('Falling back to sample data due to error');
            return window.sampleData;
        });
}

// Initialize with data from index.html
window.loadedData = [];

// Make sure emailData is initialized with sample data as a fallback
window.emailData = window.sampleData.slice();

// Function to initialize the dashboard data
window.initializeDashboardData = function() {
    console.log('Initializing dashboard data...');

    // Make sure we have sample data as a fallback
    if (!window.emailData || !window.emailData.length) {
        window.emailData = window.sampleData.slice();
        console.log('Initialized emailData with sample data');
    }

    // Return a promise that resolves with the email data
    return new Promise((resolve, reject) => {
        try {
            // Try to load data from index.html
            loadDataFromIndexHTML()
                .then(data => {
                    if (data && data.length > 0) {
                        window.loadedData = data;
                        window.emailData = data;
                        console.log(`Loaded ${window.emailData.length} emails from index.html or sample data`);
                    } else {
                        console.warn('No data loaded from index.html, using sample data');
                        window.emailData = window.sampleData.slice();
                    }

                    // Dispatch a custom event to notify dashboard.html that data is ready
                    const event = new CustomEvent('dashboardDataReady', {
                        detail: {
                            dataLength: window.emailData.length,
                            source: 'loadDataFromIndexHTML success'
                        }
                    });
                    document.dispatchEvent(event);

                    resolve(window.emailData);
                })
                .catch(error => {
                    console.error('Error loading data from index.html:', error);
                    // Ensure we have at least sample data
                    window.emailData = window.sampleData.slice();

                    // Dispatch event even if we're using sample data
                    const event = new CustomEvent('dashboardDataReady', {
                        detail: {
                            dataLength: window.emailData.length,
                            usingSampleData: true,
                            source: 'loadDataFromIndexHTML error'
                        }
                    });
                    document.dispatchEvent(event);

                    resolve(window.emailData);
                });
        } catch (error) {
            console.error('Unexpected error in initializeDashboardData:', error);
            // Ensure we have at least sample data
            window.emailData = window.sampleData.slice();

            // Dispatch event even if we're using sample data
            const event = new CustomEvent('dashboardDataReady', {
                detail: {
                    dataLength: window.emailData.length,
                    usingSampleData: true,
                    source: 'initializeDashboardData catch block'
                }
            });
            document.dispatchEvent(event);

            resolve(window.emailData);
        }
    });
};

// Initialize data when the script loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM content loaded in dashboard_data.js');
    window.initializeDashboardData();
});
