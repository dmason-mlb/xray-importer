# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains utilities and documentation for importing and managing test cases in JIRA XRAY. It includes scripts for bulk test imports, test organization, and comprehensive GraphQL API documentation for XRAY Cloud.

## Repository Structure

```
xray-importer/
├── scripts/               # Active Python utilities for XRAY operations
│   ├── mlbmob/           # MLBMOB project test updates
│   ├── xray-upload/      # Bulk upload tools
│   ├── xray-test-manager/# Test management application
│   ├── applause-tests/   # External test data processing
│   └── integration/      # Postman collections for API testing
├── xray-remediation/     # Separate project for Confluence→XRAY migration
│   ├── xray-api/        # Core API client with auth utilities
│   ├── tests/           # pytest test suite
│   └── mlbmob_*_tests/  # Project-specific test suites
├── docs/                 # Documentation and references
│   └── xray-docs/       # Complete XRAY GraphQL API documentation
└── import_data/          # CSV test data and SQLite database
```

## Environment Configuration

Required environment variables for scripts:

```bash
# JIRA/Atlassian credentials
export JIRA_BASE_URL="https://your-domain.atlassian.net"
export JIRA_EMAIL="user@example.com"
export ATLASSIAN_TOKEN="your-api-token"

# XRAY API credentials
export XRAY_CLIENT_ID="your-client-id"
export XRAY_CLIENT_SECRET="your-client-secret"

# Optional project filtering
export JIRA_PROJECT_KEY="MLBAPP"

# For Confluence operations (xray-remediation project)
export CONFLUENCE_DOMAIN="your-domain"
export CONFLUENCE_API_TOKEN="your-token"
```

## Key Commands

### Python Dependencies
```bash
# Core dependencies for most scripts
pip install requests python-dotenv

# For xray-test-manager
cd scripts/xray-test-manager && pip install -r requirements.txt

# For xray-remediation project
cd xray-remediation && pip install -r requirements.txt
```

### Running Scripts
Scripts are self-contained and include usage instructions in headers:
```bash
# Test management
python3 scripts/delete_test.py MLBAPP-XXXX
python3 scripts/list_organizational_labels.py
python3 scripts/get_test_runs_by_test_execution.py MLBAPP-1234

# Bulk operations
python3 scripts/xray-upload/upload_csv_to_xray.py input.csv
python3 scripts/xray-upload/validate_csv.py input.csv

# xray-remediation workflows
cd xray-remediation
python3 upload_all_tests.py        # Upload tests with chunking
python3 apply_labels_all_tests.py  # Apply organization labels
python3 assign_to_folders.py       # Create folder hierarchy
```

### Testing
```bash
# Run xray-remediation tests
cd xray-remediation
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=xray-api --cov-report=html
```

## Architecture & Key Components

### 1. XRAY GraphQL API Documentation (`docs/xray-docs/`)
- **Consolidated References**: Complete API documentation organized by entity type
  - `TESTS_COMPLETE_REFERENCE.md` - All test operations
  - `TESTRUN_COMPLETE_REFERENCE.md` - Test execution tracking
  - `TESTEXECUTION_COMPLETE_REFERENCE.md` - Test cycles
  - Additional references for TestPlans, TestSets, Folders, etc.
- **Schema Files**: GraphQL schema definitions for all XRAY entities
- **Import Strategies**: Detailed guides for CSV and REST API imports

### 2. Test Import System
- **CSV Import**: Supports bulk import with 1000-test batches
- **Encoding**: CSV files must use ISO-8859-1 (not UTF-8)
- **Organization**: Tests organized using labels (surface-*, feature-*)
- **JQL Queries**: Filter tests using JIRA Query Language
- **Retry Logic**: Built-in exponential backoff for API rate limits

### 3. xray-remediation Project
- **Separate authentication**: Uses `xray-api/auth_utils.py` with XrayAPIClient
- **Confluence extraction**: Tools for migrating tests from Confluence docs
- **Security focus**: BeautifulSoup parsing, input validation, no credential exposure
- **Workflow pattern**: Extract → Transform → Upload → Organize

### 4. API Client Architecture
```python
# Common pattern across all scripts
from xray_api.auth_utils import XrayAPIClient
client = XrayAPIClient()
client.get_access_token()  # OAuth 2.0 authentication
```

## Important Technical Constraints

### XRAY Limitations
- Maximum 1000 tests per import operation
- CSV importer supports Manual, Generic, and Cucumber test types
- Test Repository: Single folder membership per test
- Test Sets: Allow multiple membership for cross-cutting concerns
- Rate limits: 60 requests/minute for most endpoints

### GraphQL API Patterns
- Pagination: Maximum 100 items per query
- JQL queries returning >100 issues will error
- Test versions only accessible through expanded queries
- Use consolidated reference guides for comprehensive API usage
- Always check `total` field before assuming all results returned

### Authentication Patterns
```python
# XRAY OAuth 2.0
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# JIRA Basic Auth
auth = HTTPBasicAuth(JIRA_EMAIL, ATLASSIAN_TOKEN)
```

## Working with Test Data

### Test Organization Strategy
- **Primary Labels**: `surface-home`, `surface-core`, `surface-news`
- **Secondary Labels**: `feature-*` categories for cross-cutting concerns
- **Naming Convention**: `[Component] - [Function] - [Expected Outcome]`
- **Folder Structure**: `/MLBAPP/Surfaces/[Surface Name]/[Feature]`

### Common JQL Queries
```jql
project = MLBAPP AND issuetype = "Xray Test" AND labels = "surface-home"
project = MLBAPP AND issuetype = "Xray Test" AND labels = "feature-video"
project = MLBAPP AND issuetype = "Xray Test" AND (labels is EMPTY OR labels not in ("surface-home", "surface-core"))
```

### CSV Format Requirements
```csv
TCID,Name,Objective,Precondition,Test Type,Test Step,Test Data,Expected Result,Label,Component
TEST001,"Test Name","Objective text","Preconditions",Manual,1,"Input data","Expected outcome","surface-home;feature-video",UI
```

## Code Quality Standards

### Security Requirements (from xray-remediation)
- No credential exposure in logs or error messages
- Input validation for all external data
- Timeout protection against ReDoS attacks
- Comprehensive error handling with graceful degradation

### Best Practices
- Use existing authentication utilities (don't reimplement)
- Environment variables for all configuration
- Structured logging with appropriate levels
- Test with error conditions and edge cases
- Always handle pagination in API responses
- Implement retry logic for transient failures

## Common Development Patterns

### Error Handling Pattern
```python
try:
    response = client.make_request(...)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    logger.error(f"API request failed: {e}")
    # Graceful degradation
```

### Batch Processing Pattern
```python
def process_in_batches(items, batch_size=50):
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        yield batch
```

### Retry Pattern (from scripts)
```python
for attempt in range(max_retries):
    try:
        # API call
        break
    except Exception as e:
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff
        else:
            raise
```

## Troubleshooting

### Common Issues
1. **Authentication Failures**: Check token expiration and environment variables
2. **Rate Limiting**: Implement proper retry logic with exponential backoff
3. **CSV Encoding**: Use ISO-8859-1, not UTF-8 for special characters
4. **Missing Tests**: Check JQL query limits (max 100 results)
5. **Folder Assignment**: Ensure parent folders exist before assignment

### Debug Mode
Most scripts support verbose logging:
```bash
export DEBUG=true
python3 script.py
```