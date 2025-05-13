/**
 * Update the index.html file to ensure proper date sorting
 * This script modifies the JavaScript in index.html to ensure dates sort in descending order by default
 */

const fs = require('fs');
const path = require('path');

// Path to the index.html file
const indexPath = path.join('analyzed_emails', 'index.html');

// Read the file
fs.readFile(indexPath, 'utf8', (err, data) => {
    if (err) {
        console.error('Error reading file:', err);
        return;
    }

    // Update the refresh function to sort by date in descending order
    let updatedContent = data;

    // Find the addNewEmailsToTable function and ensure it sorts by date
    const addNewEmailsPattern = /function addNewEmailsToTable\(newEmails\) \{([\s\S]*?)sortTable\(currentSortColumn[\s\S]*?\);/;
    const addNewEmailsReplacement = `function addNewEmailsToTable(newEmails) {$1sortTable(3, 'date', 'desc');`;
    
    updatedContent = updatedContent.replace(addNewEmailsPattern, addNewEmailsReplacement);

    // Make sure the initial sort is by date in descending order
    const initialSortPattern = /window\.onload = function\(\) \{([\s\S]*?)sortTable\(3, 'date'\);/;
    const initialSortReplacement = `window.onload = function() {$1sortTable(3, 'date', 'desc');`;
    
    updatedContent = updatedContent.replace(initialSortPattern, initialSortReplacement);

    // Update the sortTable function to accept a direction parameter
    const sortTablePattern = /function sortTable\(columnIndex, dataType = 'string'\) \{([\s\S]*?)let direction = 'asc';([\s\S]*?)}/;
    const sortTableReplacement = `function sortTable(columnIndex, dataType = 'string', forceDirection = null) {$1let direction = forceDirection || 'asc';$2}`;
    
    updatedContent = updatedContent.replace(sortTablePattern, sortTableReplacement);

    // Write the updated content back to the file
    fs.writeFile(indexPath, updatedContent, 'utf8', (err) => {
        if (err) {
            console.error('Error writing file:', err);
            return;
        }
        console.log('Successfully updated index.html to sort dates in descending order');
    });
});
