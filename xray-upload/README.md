# XRAY Upload - SDUI Team Page Tests

This directory contains all artifacts for uploading SDUI Team Page functional tests to XRAY in the FRAMED project using the GraphQL API.

## 📁 Directory Contents

### 📄 Documentation
- **SDUI_TEAM_PAGE_UPLOAD_STRATEGY.md** - Comprehensive upload strategy and planning document
- **UPLOAD_PROCEDURES.md** - Step-by-step upload procedures for API method

### 🐍 Scripts
- **transform_tests.py** - Transforms JSON test cases to XRAY format
- **xray_api_uploader.py** - GraphQL API upload script with folder and test set creation
- **validate_tests.py** - Pre-upload validation to ensure data integrity

### 📊 Data Files
- **transformed_tests.json** - Tests converted to XRAY format (38 tests)
- **transformation_summary.md** - Summary of test transformation results
- **validation_report.md** - Validation results showing all tests are ready

## 🚀 Quick Start

### Prerequisites
1. Ensure `.env` file exists in the repository root directory with:
   ```
   XRAY_CLIENT=your_client_id
   XRAY_SECRET=your_client_secret
   JIRA_PROJECT_KEY=FRAMED
   JIRA_PROJECT_ID=10000
   ```
   
2. Obtain XRAY API credentials:
   - Go to XRAY → API Keys (Global Settings)
   - Create new API Key
   - Copy Client ID and Client Secret
   - Update root .env file

### Upload Process
1. Transform tests (already done): `python3 transform_tests.py`
2. Validate tests (already done): `python3 validate_tests.py`
3. Run upload: `python3 xray_api_uploader.py`
4. Check `upload_report.json` for results

## 📈 Test Summary

- **Total Tests**: 38
- **Test Suite**: SDUI Team Page - Functional Test Cases
- **Platforms**: iOS, Android, iPad
- **Priority Distribution**:
  - High: 24 tests
  - Medium: 13 tests
  - Low: 1 test

### Folder Structure
```
/Team Page
  /Core Navigation (10 tests)
  /Content Display (6 tests)
  /Game States (11 tests)
  /Jewel Events (8 tests)
  /Product Links (1 test)
  /Date Bar (1 test)
  /Matchup Display (1 test)
```

## ✅ Status

All preparation tasks are complete:
- [x] Test transformation completed
- [x] Validation passed (2 minor warnings only)
- [x] API upload script ready
- [x] Documentation complete

The tests are ready for upload to XRAY using the GraphQL API.

## 🔧 Troubleshooting

### Authentication Issues
- **Check**: .env file exists in repository root (not in xray-upload)
- **Check**: Client ID and Secret are correct
- **Check**: API Key is active in XRAY
- **Solution**: Regenerate API credentials if needed

### Upload Failures
- **Rate Limiting**: Script includes delays, but increase if getting 429 errors
- **Permissions**: Ensure JIRA user can create tests in FRAMED project
- **GraphQL Errors**: Review error messages in console for specific issues

## 🔒 Security Notes

- Never commit .env file to git
- Keep API credentials secure
- All scripts load credentials from root .env file
- No credentials are stored in any tracked files

## 📝 Notes

- Original test data from: `/Users/douglas.mason/Documents/GitHub/MLB-App/sdui-team-page-test-cases.json`
- Tests include related FRAMED issues for traceability
- All tests have structured steps with actions and expected results
- Platform-specific tests are properly tagged
- API method provides better control and error handling than CSV import

---
Created: 2025-07-11
Project: FRAMED
Component: SDUI Team Page