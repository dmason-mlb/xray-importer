# XRAY Test Import Guide for MLBAPP

## Overview
This guide provides step-by-step instructions for importing test cases from CSV files into XRAY for the MLBAPP JIRA project.

## Prerequisites

1. **Environment Variables**:
   ```bash
   export JIRA_BASE_URL="https://your-domain.atlassian.net"
   export JIRA_EMAIL="your-email@example.com"
   export ATLASSIAN_TOKEN="your-atlassian-api-token"
   ```

2. **Python Requirements**:
   ```bash
   pip install requests
   ```

3. **JIRA Permissions**:
   - Create Issues permission in MLBAPP project
   - Bulk Change permission
   - XRAY Test Management access

## Import Process

### Step 1: Prepare CSV Files

First, analyze and prepare your CSV files:

```bash
# Analyze current CSV files
python3 prepare_csv_files.py analyze home_surface.csv mlbapp.csv news_surface.csv

# Convert encoding and clean data
python3 prepare_csv_files.py all home_surface.csv mlbapp.csv news_surface.csv
```

This will create cleaned versions of your files:
- `home_surface_cleaned.csv`
- `mlbapp_cleaned.csv`
- `news_surface_cleaned.csv`

### Step 2: Test Import (Dry Run)

Test the import process without actually creating tests:

```bash
# Test with smallest file first
python3 xray_import_script.py --dry-run news_surface_cleaned.csv
```

Review the generated `news_surface_cleaned.csv_sample.json` to verify field mapping.

### Step 3: Import Test Files

Import tests in order from smallest to largest:

```bash
# 1. Import News Surface tests (725 tests - 1 batch)
python3 xray_import_script.py news_surface_cleaned.csv

# 2. Import MLB App tests (6,276 tests - 7 batches)
python3 xray_import_script.py mlbapp_cleaned.csv

# 3. Import Home Surface tests (8,699 tests - 10 batches)
python3 xray_import_script.py home_surface_cleaned.csv
```

### Step 4: Import All Files with Error Handling

To import all files in one command with error continuation:

```bash
python3 xray_import_script.py --continue-on-error \
    news_surface_cleaned.csv \
    mlbapp_cleaned.csv \
    home_surface_cleaned.csv
```

## Monitoring Progress

The import script provides real-time progress updates:
- Batch progress: "Importing batch 1/7 (900 tests)"
- Success/failure status for each batch
- Final summary statistics

Check `xray_import.log` for detailed import logs.

## Test Repository Organization

Tests will be organized in XRAY as follows:

```
MLBAPP Test Repository/
├── Home Surface/
│   ├── Main Page/
│   ├── Scoreboard/
│   ├── Mixed Feed/
│   └── ...
├── Core App/
│   ├── Deep Links/
│   ├── Navigation/
│   └── ...
└── News Surface/
    ├── Editorial Modules/
    └── ...
```

## Troubleshooting

### Common Issues

1. **Authentication Error**:
   - Verify ATLASSIAN_TOKEN is set correctly
   - Ensure token has proper permissions

2. **Encoding Errors**:
   - Run the prepare script with 'convert' action
   - Check for special characters in CSV

3. **Field Mapping Errors**:
   - Review custom field IDs in the script
   - Verify fields exist in MLBAPP project

4. **Rate Limiting**:
   - Increase RATE_LIMIT_DELAY in script
   - Import during off-peak hours

### Recovery from Failed Import

If import fails partway through:

1. Check logs to identify last successful batch
2. Modify CSV to remove already-imported tests
3. Resume import with remaining tests

## Post-Import Tasks

1. **Verify Import**:
   ```
   project = MLBAPP AND issuetype = Test AND labels = "imported-from-csv"
   ```

2. **Create Test Sets**:
   - Smoke Tests
   - Regression Suite
   - Feature-specific sets

3. **Update Test Execution Plans**

4. **Notify Team**:
   - Share new test organization structure
   - Provide JQL queries for finding tests
   - Schedule training if needed

## Advanced Options

### Custom Batch Size
```bash
python3 xray_import_script.py --batch-size 500 file.csv
```

### Import Specific Test Types
Modify the script to filter by test type before import.

### Custom Field Mapping
Edit `xray_import_script.py` to map additional custom fields.

## Support

- Review import logs in `xray_import.log`
- Check JIRA audit log for created issues
- Contact JIRA admin for permission issues

## Important Notes

- Total import time: ~2-3 hours for all files
- Each batch takes 2-5 seconds plus rate limit delay
- Monitor JIRA performance during import
- Consider scheduling during maintenance window