# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Xray Remediation project is a sophisticated test management system that extracts test cases from Confluence documentation, manages them in Xray, and maintains comprehensive test organization. The project handles 93 unique tests (55 API + 38 functional) with complete pytest integration, folder organization, and automated workflows.

## Core Architecture

### Authentication & API Client (`/xray-api/auth_utils.py`)
- **Primary Entry Point**: Always use `XrayAPIClient` for all Xray operations
- **Features**: OAuth 2.0 token management, automatic refresh, comprehensive error handling
- **Pattern**: All scripts should import and use this client - never reimplement authentication

### Directory Organization
```
xray-remediation/
├── xray-api/              # Core authentication (use this for all API operations)
├── scripts/               # Operational scripts for test management
├── confluence-tools/      # Confluence extraction utilities
├── analysis-utilities/    # Test analysis and validation tools
├── test-data/            # JSON test definitions (api_tests_xray.json, functional_tests_xray.json)
├── logs/                 # Execution logs and reports
└── documentation/        # Project documentation and archives
```

## Essential Commands

### Test Management Operations
```bash
# Organize tests into folders
python scripts/organize_xray_folders.py

# Create missing tests in Xray
python scripts/create_missing_xray_tests.py

# Apply pytest decorators to external test files
python scripts/update_all_pytest_decorators.py

# Associate preconditions with tests
python scripts/associate_preconditions_batch.py

# Update test labels via JIRA API
python scripts/update_labels_via_jira.py
```

### Analysis & Validation
```bash
# Analyze folder organization status
python scripts/analyze_folder_status.py

# Check precondition associations
python scripts/check_preconditions_graphql.py

# Generate comprehensive test catalog
python scripts/generate_test_catalog.py

# Validate test extraction results
python analysis-utilities/comprehensive_test_analysis.py
```

### Confluence Extraction (if needed)
```bash
# Extract API tests (secure version)
python confluence-tools/extract_confluence_api_tests_secure.py

# Extract functional tests
python confluence-tools/extract_confluence_functional_tests_v2.py

# Debug Confluence page structure
python confluence-tools/debug_confluence_page.py <page_id>
```

## High-Level Architecture

### 1. Data Flow Pipeline
```
Confluence Docs → Extraction Scripts → JSON Files → Xray Import → Organization Scripts
    ↓                     ↓                ↓              ↓                ↓
  HTML Content      BeautifulSoup     Test Objects    GraphQL API    Folder/Label Mgmt
```

### 2. Test Organization Hierarchy
```
FRAMED Project/
├── Team Page/
│   ├── API Tests/         # 55 API test cases
│   └── Functional Tests/  # 38 functional test cases
└── Preconditions/         # 23 shared preconditions
```

### 3. Authentication Flow
- Scripts request token via `XrayAPIClient.get_auth_token()`
- Client manages OAuth 2.0 flow with Xray Cloud
- Tokens cached for 1 hour with automatic refresh
- All API calls use bearer token authentication

### 4. Key Integration Points
- **External Test Files**: `/MLB-App-Worktrees/framed-api-tests/` - pytest test files
- **Xray GraphQL API**: `https://xray.cloud.getxray.app/api/v2/graphql`
- **JIRA REST API**: For label and metadata updates
- **Confluence API**: For test extraction from documentation

## Critical Implementation Details

### GraphQL Query Patterns
```python
# Standard test query with pagination
query = """
query($jql: String!, $limit: Int!) {
    getTests(jql: $jql, limit: $limit, start: 0) {
        total
        results {
            issueId
            jira(fields: ["key", "summary", "labels"])
            folder { name path }
        }
    }
}
"""

# Always check response['data']['getTests']['total'] for pagination needs
```

### Batch Processing Requirements
- **GraphQL Limit**: Max 100 items per query
- **Folder Operations**: Process in batches of 50
- **Label Updates**: Use JIRA REST API for bulk operations
- **Import Operations**: Max 1000 tests per import

### Error Handling Standards
```python
# Required pattern for all API operations
try:
    response = client.execute_query(query, variables)
    if 'errors' in response:
        logger.error(f"GraphQL errors: {response['errors']}")
        return None
    return response['data']
except Exception as e:
    logger.error(f"API call failed: {e}")
    # Implement exponential backoff for retries
```

## Security & Quality Standards

### Mandatory Security Practices
1. **No Credentials in Code**: All auth via environment variables
2. **Input Validation**: Sanitize all external inputs before API calls
3. **HTML Parsing**: Use BeautifulSoup, never regex for HTML
4. **Error Messages**: Never expose credentials or sensitive data in logs
5. **Timeout Protection**: Set timeouts on all HTTP requests

### Code Quality Requirements
1. **Import Pattern**: Always use `from xray_api.auth_utils import XrayAPIClient`
2. **Logging**: Use structured logging with appropriate levels
3. **Documentation**: Include docstrings for all functions
4. **Error Handling**: Graceful degradation for all failures
5. **Testing**: Validate with small datasets before bulk operations

## Common Workflows

### 1. Complete Test Organization Flow
```bash
# 1. Check current status
python scripts/analyze_folder_status.py

# 2. Organize into folders
python scripts/organize_xray_folders.py

# 3. Update labels
python scripts/update_labels_via_jira.py

# 4. Verify organization
python scripts/generate_test_catalog.py > TEAM_PAGE_TEST_CATALOG.md
```

### 2. Pytest Integration Flow
```bash
# 1. Build test mapping
python scripts/build_complete_test_mapping.py

# 2. Apply decorators
python scripts/update_all_pytest_decorators.py

# 3. Verify decorators
grep -r "@pytest.mark.xray" /path/to/test/files/
```

### 3. Precondition Management Flow
```bash
# 1. Check existing preconditions
python scripts/check_preconditions_graphql.py

# 2. Associate with tests
python scripts/associate_preconditions_batch.py

# 3. Verify associations
python scripts/analyze_preconditions.py
```

## Known Gotchas & Solutions

### Issue: GraphQL Query Limits
**Problem**: Queries fail with >100 results  
**Solution**: Always implement pagination using `start` parameter and check `total`

### Issue: Folder Assignment Failures
**Problem**: Cannot assign test to non-existent folder  
**Solution**: Create parent folders first using `create_test_folders.py`

### Issue: Authentication Token Expiry
**Problem**: 401 errors after ~1 hour  
**Solution**: XrayAPIClient handles refresh automatically - ensure using latest version

### Issue: Duplicate Test Creation
**Problem**: Running creation scripts multiple times creates duplicates  
**Solution**: Always check existing tests first with JQL queries

## Script Categories & Usage

### Core Operations (Use Daily)
- `organize_xray_folders.py` - Primary folder management
- `update_all_pytest_decorators.py` - Pytest integration
- `generate_test_catalog.py` - Documentation generation

### Maintenance Scripts (Use As Needed)
- `cleanup_duplicate_preconditions_v2.py` - Remove duplicates
- `cleanup_labels_final.py` - Label standardization
- `analyze_folder_status.py` - Health checks

### Migration Scripts (One-Time Use)
- `create_missing_xray_tests.py` - Initial test creation
- `extract_confluence_*.py` - Initial extraction
- `upload_tests_to_xray.py` - Bulk import

## Performance Optimization

### API Call Reduction
- Cache authentication tokens (handled by XrayAPIClient)
- Batch GraphQL queries where possible
- Use JQL to filter at source, not in code

### Processing Efficiency
- Process tests in batches of 50-100
- Use concurrent.futures for parallel operations
- Implement progress bars for long operations

### Memory Management
- Stream large JSON files instead of loading entirely
- Clear caches between batch operations
- Use generators for large result sets