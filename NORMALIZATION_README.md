# Data Normalization System

This system provides programmatic normalization for company names, support categories, and subject templates in the Email Analyzer. It replaces the hard-coded constants in the dashboard.html file with a dynamic, maintainable solution.

## Overview

The normalization system consists of:

1. **Core Normalization Module** (`data_normalizer.py`): Provides classes for normalizing entities
2. **Mapping Files** (in `mappings/` directory): Store known mappings and standardized forms
3. **Integration Scripts**:
   - `normalize_email_data.py`: Normalizes data in existing files
   - `update_dashboard.py`: Updates the dashboard with normalized data
   - `review_mappings.py`: Interactive tool to review and approve new mappings

## How It Works

### Entity Normalization

The system normalizes three types of entities:

1. **Company Names**: Standardizes variations of company names (e.g., "BluSky" → "BluSky Restoration Contractors, LLC")
2. **Support Categories**: Standardizes support ticket categories
3. **Subject Templates**: Standardizes email subject templates

When a new entity is encountered:
- The system checks if it matches a known mapping
- If not, it uses fuzzy matching to find similar standardized entities
- Very high-confidence matches (90%+) are automatically accepted
- Moderate-confidence matches (70-90%) are flagged for manual review
- Low-confidence matches (<70%) are added as new standardized entities

**Important**: Once a standardized entity is established, it will not change. This ensures stability while still allowing new entities to be added.

### Mapping Files

The system maintains three JSON mapping files:

- `company_mappings.json`: Maps company name variations to standardized names
- `category_mappings.json`: Maps category variations to standardized categories
- `template_mappings.json`: Maps template variations to standardized templates

Each file contains:
- `mappings`: Dictionary of variations → standardized forms
- `standardized_entities`: List of approved standardized forms

### Dashboard Integration

The dashboard is updated to use the normalized data:
- Hard-coded constants are removed from the HTML/JavaScript
- Normalized data is injected when the dashboard is generated
- A template file is used to maintain the dashboard structure

### Index.html Integration

The system normalizes data before it's written to index.html:
- Company names, support categories, and subject templates are normalized during email processing
- The `create_html_index` function in both `monitor_new_emails.py` and `analyze_outlook_emails.py` is modified to use normalizers
- Support category column is added to the index.html table if it doesn't exist
- After index.html is created, the dashboard is automatically updated with normalized data

## Usage

### Initial Setup

1. Integrate normalization with email processing:
   ```
   python integrate_normalization.py
   ```
   This modifies the email processing files to normalize data before writing to index.html.

2. Run the initial setup to create mapping files:
   ```
   python update_dashboard.py
   ```

3. Normalize existing data:
   ```
   python normalize_email_data.py
   ```

### Ongoing Usage

The normalization system integrates with the email processing workflow:

1. When new emails are processed, entities are automatically normalized
2. New entities are detected and either:
   - Automatically mapped to existing standardized forms (very high confidence, 90%+)
   - Flagged for review (moderate confidence, 70-90%)
   - Added as new standardized entities (low confidence, <70%)

3. Run the refresh normalization script after each email refresh:
   ```
   python refresh_normalization.py
   ```
   This script:
   - Extracts entities from index.html
   - Normalizes new entities while preserving established ones
   - Updates the dashboard if changes were made

4. Periodically review pending mappings:
   ```
   python refresh_normalization.py --review
   ```
   This will interactively prompt you to review any pending mappings.

5. Force an update of the dashboard even if no changes were made:
   ```
   python refresh_normalization.py --force
   ```

### Reviewing Mappings

The `review_mappings.py` script provides an interactive interface to:
- View pending mappings that need review
- Accept suggested mappings
- Reject mappings and create new standardized entities
- Provide custom mappings

## Customization

### Adjusting Confidence Thresholds

You can adjust the confidence thresholds in `data_normalizer.py`:
- `DEFAULT_AUTO_THRESHOLD`: Threshold for automatic acceptance (default: 0.8)
- `DEFAULT_SUGGEST_THRESHOLD`: Threshold for suggesting matches (default: 0.6)

### Adding New Standardized Entities

To add a new standardized entity manually:

1. Edit the appropriate mapping file (e.g., `mappings/company_mappings.json`)
2. Add the entity to the `standardized_entities` list
3. Add any known variations to the `mappings` dictionary

## Maintenance

### Backing Up Mapping Files

It's recommended to back up the mapping files regularly:
```
cp -r mappings/ mappings_backup_$(date +%Y%m%d)/
```

### Troubleshooting

If you encounter issues:

1. Check the mapping files for inconsistencies
2. Run `normalize_email_data.py` to re-normalize existing data
3. Run `update_dashboard.py` to regenerate the dashboard

## Benefits

This normalization system provides several benefits:

1. **Consistency**: Ensures consistent naming across the application
2. **Maintainability**: Centralizes entity management in one place
3. **Adaptability**: Automatically handles new entities as they appear
4. **Flexibility**: Allows for manual review and customization
5. **Scalability**: Works with growing numbers of entities
