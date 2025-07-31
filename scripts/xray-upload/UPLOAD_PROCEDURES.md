# SDUI Team Page Test Upload Procedures

## Overview
This document provides step-by-step procedures for uploading SDUI Team Page tests to XRAY in the FRAMED project using the GraphQL API.

## Pre-Upload Checklist
- [ ] Tests transformed to XRAY format (`transformed_tests.json` exists)
- [ ] Tests validated (`validation_report.md` shows PASSED)
- [ ] JIRA/XRAY access confirmed
- [ ] Environment variables configured in root .env file
- [ ] XRAY API credentials obtained

## GraphQL API Upload Procedure

### Step 1: Configure Environment
Ensure `.env` file exists in the repository root directory (NOT in xray-upload):
```
XRAY_CLIENT=your_client_id_here
XRAY_SECRET=your_client_secret_here
JIRA_PROJECT_KEY=FRAMED
JIRA_PROJECT_ID=10000
```

**Security Note**: Never commit the .env file to git. It should be in .gitignore.

### Step 2: Get XRAY API Credentials
1. Log into JIRA
2. Go to Apps → XRAY → API Keys (in Global Settings)
3. Click "Create API Key"
4. Enter a descriptive name (e.g., "SDUI Test Upload")
5. Copy the Client ID and Client Secret
6. Update the root .env file with these credentials

### Step 3: Verify Setup
Before running the upload:
1. Check that .env exists in repository root
2. Verify transformation is complete: `transformed_tests.json` exists
3. Confirm validation passed: check `validation_report.md`

### Step 4: Run Upload Script
```bash
cd /Users/douglas.mason/Documents/GitHub/xray-importer/xray-upload
python3 xray_api_uploader.py
```

### Step 5: Monitor Progress
The script will:
1. Load credentials from root .env file
2. Authenticate with XRAY API
3. Create folder structure:
   - /Team Page (root folder)
   - Subfolders for each test category
4. Upload tests one by one with progress indicators
5. Assign tests to appropriate folders
6. Create standard test sets
7. Generate upload report

Expected output:
```
Authenticating with XRAY API...
Authentication successful!

Setting up folder structure...
Creating folder: Team Page
Created folder: Team Page (ID: xxx)
Creating folder: Core Navigation
...

Uploading 38 tests...
Processing test 1/38
Created test: FRAMED-xxxx - Team Selection via Drawer
...

Creating test sets...
Creating test set: Team Page - Full Regression
Created test set: FRAMED-xxxx - Team Page - Full Regression
...

Upload Summary:
- Successful: 38 tests
- Failed: 0 tests

Upload report saved to: upload_report.json
Upload process complete!
```

### Step 6: Review Upload Report
Check `upload_report.json` for:
- **uploadDate**: Timestamp of upload
- **successfulUploads**: Array of test keys created
- **failedUploads**: Any tests that failed (should be empty)
- **testMapping**: Maps original IDs to XRAY test keys
- **folderMapping**: Maps folder names to XRAY folder IDs

### Step 7: Post-Upload Verification
1. Log into JIRA/XRAY
2. Navigate to Apps → XRAY → Test Repository
3. Verify folder structure:
   - Team Page folder exists
   - All subfolders created
   - Test counts match expected numbers
4. Check a few random tests:
   - Open test details
   - Verify steps imported correctly
   - Check labels and priority
   - Confirm folder assignment

## Test Sets Created Automatically

The script creates these test sets:
1. **Team Page - Full Regression** (all 38 tests)
2. **Team Page - Smoke Tests** (first 10 critical tests)
3. **Team Page - Game States** (tests in Game States folder)
4. **Team Page - Jewel Events** (tests in Jewel Events folder)

## Troubleshooting

### Authentication Fails
- **Symptom**: "Authentication failed" error
- **Check**: .env file is in repository root (not xray-upload)
- **Check**: No quotes around credentials in .env
- **Check**: Client ID and Secret are correct (no extra spaces)
- **Check**: API Key is active in XRAY settings
- **Solution**: Regenerate API credentials and update .env

### Script Can't Find .env
- **Symptom**: "XRAY_CLIENT and XRAY_SECRET environment variables must be set!"
- **Check**: .env file location (must be in repository root)
- **Check**: File is named exactly `.env` (with the dot)
- **Solution**: Create .env in correct location

### Rate Limiting Errors
- **Symptom**: 429 errors or "Too Many Requests"
- **Note**: Script includes 1-second delays between operations
- **Solution**: Increase delay in script if needed
- **Info**: XRAY limit is approximately 60 requests/minute

### GraphQL Errors
- **Check**: Project key is "FRAMED" (case sensitive)
- **Check**: User has permission to create tests in FRAMED
- **Check**: All required fields are populated
- **Solution**: Review specific error message in console

### Folder Creation Fails
- **Check**: User has folder creation permissions
- **Check**: No duplicate folder names
- **Solution**: Create folders manually if needed, script will continue

### Test Creation Fails
- **Check**: Priority values are valid (High, Medium, Low)
- **Check**: Test summary not too long (255 char max)
- **Check**: No invalid characters in labels
- **Solution**: Fix in transform_tests.py and re-run

## Rollback Procedures

If you need to remove uploaded tests:

1. **Using Upload Report**:
   - Open `upload_report.json`
   - Get test keys from `successfulUploads`
   - In JIRA, search for these keys
   - Bulk delete if needed

2. **Using Labels**:
   - Search JIRA: `labels = "sdui-import" AND labels = "team-page-suite"`
   - Select all results
   - Bulk delete or move to archive

3. **Manual Cleanup**:
   - Navigate to Test Repository
   - Delete Team Page folder (will delete all tests inside)
   - Or selectively delete test subfolders

## Best Practices

1. **Test First**: If available, test with 2-3 tests in staging
2. **Backup**: Export any existing tests before major imports
3. **Communication**: Notify team before upload
4. **Timing**: Upload during low-usage periods
5. **Documentation**: Keep upload reports for audit trail
6. **Security**: Never share or commit API credentials

## Support Resources

- **XRAY Documentation**: https://docs.getxray.app/
- **GraphQL API Docs**: Available in XRAY settings
- **JIRA Admin**: Contact for permissions issues

---
Last Updated: 2025-07-11
Version: 2.0 (API-only version)