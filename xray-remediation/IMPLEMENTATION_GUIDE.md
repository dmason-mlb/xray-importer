# Xray Test Management Implementation Guide

**Last Updated**: 2025-07-31

## Overview

This guide consolidates technical implementation details for working with Xray test management, including API integration, pytest automation, and data extraction procedures.

## Table of Contents

1. [Environment Setup](#environment-setup)
2. [Authentication System](#authentication-system)
3. [API Integration](#api-integration)
4. [Test Extraction](#test-extraction)
5. [Pytest Integration](#pytest-integration)
6. [Folder Organization](#folder-organization)
7. [Script Reference](#script-reference)

## Environment Setup

### Required Environment Variables

```bash
# Xray Cloud API Authentication
export XRAY_CLIENT_ID="your_client_id"
export XRAY_CLIENT_SECRET="your_client_secret"

# Confluence API (for test extraction)
export CONFLUENCE_DOMAIN="your_domain.atlassian.net"
export CONFLUENCE_EMAIL="your_email@example.com"
export CONFLUENCE_API_TOKEN="your_api_token"
```

### Python Dependencies

```bash
pip install requests beautifulsoup4 python-dotenv pytest pytest-jira-xray
```

## Authentication System

### Core Authentication Utility

All Xray API operations should use the centralized `XrayAPIClient` from `/xray-api/auth_utils.py`:

```python
from auth_utils import XrayAPIClient

# Initialize client
client = XrayAPIClient()

# Execute GraphQL query
query = """
query {
    getTests(jql: "project = FRAMED", limit: 10) {
        results {
            issueId
            testType {
                name
            }
        }
    }
}
"""
result = client.execute_graphql(query)
```

### Key Features
- Automatic token refresh (24-hour expiry)
- Token caching to minimize API calls
- Comprehensive error handling
- Structured logging

## API Integration

### GraphQL Endpoints

**Xray Cloud**: `https://xray.cloud.getxray.app/api/v2/graphql`

### Common Operations

#### 1. Create Test Folder
```python
mutation = """
mutation {
    createFolder(
        projectId: "10000",
        path: "/Team Page/API Tests",
        testRepositoryPath: "/"
    ) {
        folder {
            id
            path
        }
    }
}
"""
```

#### 2. Move Tests to Folder
```python
mutation = """
mutation {
    addTestsToFolder(
        projectId: "10000",
        path: "/Team Page/API Tests",
        testIssueIds: ["FRAMED-1234", "FRAMED-1235"]
    ) {
        folder {
            testsCount
        }
    }
}
"""
```

#### 3. Associate Preconditions
```python
mutation = """
mutation {
    addPreconditionsToTest(
        testIssueId: "FRAMED-1234",
        preconditionIssueIds: ["FRAMED-1200"]
    ) {
        addedPreconditions
    }
}
"""
```

## Test Extraction

### API Test Extraction

Use the secure extraction script with BeautifulSoup parsing:

```bash
python confluence-tools/extract_confluence_api_tests_secure.py
```

**Output**: `/test-data/api_tests_xray.json` (55 test cases)

### Functional Test Extraction

Extract from table-based Confluence documentation:

```bash
python confluence-tools/extract_confluence_functional_tests_v2.py
```

**Output**: `/test-data/functional_tests_xray.json` (38 test cases)

### Data Format

Tests are extracted in Xray JSON format:
```json
{
    "testCaseId": "API-001",
    "objective": "Verify Team Page API returns correct data",
    "precondition": "Valid authentication token",
    "testType": "Automated",
    "testSteps": [
        {
            "description": "Send GET request to /api/team/{teamId}",
            "expected": "200 OK with team data"
        }
    ]
}
```

## Pytest Integration

### Test Decorators

Apply Xray decorators to pytest tests:

```python
import pytest

@pytest.mark.xray('FRAMED-1234')
def test_team_page_api():
    """Test team page API endpoint"""
    response = requests.get('/api/team/123')
    assert response.status_code == 200
```

### Batch Decorator Application

Use the automated script to apply decorators:

```bash
python scripts/update_all_pytest_decorators.py
```

### Test Execution

Execute tests with Xray reporting:

```bash
pytest --jira-xray \
  --cloud \
  --api-key-auth \
  --client-id $XRAY_CLIENT_ID \
  --client-secret $XRAY_CLIENT_SECRET \
  --testplan FRAMED-XXXX \
  --no-test-exec-attachments \
  tests/team_page/
```

## Folder Organization

### Current Structure in Xray

```
Test Repository/
├── Team Page/
│   └── API Tests/              (15 tests)
│       └── Error Handling/     (1 test: FRAMED-1294)
├── Preconditions/              (23 items)
└── [Root - Functional Tests]   (38 pending)
```

### Organization Script

Use the comprehensive folder organizer:

```bash
python scripts/organize_xray_folders.py
```

Features:
- Inventory existing folders
- Create missing folders
- Move tests to appropriate locations
- Move preconditions to dedicated folder

## Script Reference

### Primary Scripts

| Script | Purpose | Location |
|--------|---------|----------|
| `auth_utils.py` | Core authentication | `/xray-api/` |
| `organize_xray_folders.py` | Folder organization | `/scripts/` |
| `update_all_pytest_decorators.py` | Apply decorators | `/scripts/` |
| `associate_preconditions_batch.py` | Link preconditions | `/scripts/` |
| `create_missing_xray_tests.py` | Create tests in Xray | `/scripts/` |

### Extraction Scripts

| Script | Purpose | Location |
|--------|---------|----------|
| `extract_confluence_api_tests_secure.py` | Extract API tests | `/confluence-tools/` |
| `extract_confluence_functional_tests_v2.py` | Extract functional tests | `/confluence-tools/` |
| `normalize_confluence_document.py` | Fix document formatting | `/confluence-tools/` |
| `debug_confluence_page.py` | Debug page structure | `/confluence-tools/` |

### Analysis Scripts

| Script | Purpose | Location |
|--------|---------|----------|
| `analyze_confluence_structure.py` | Document analysis | `/analysis-utilities/` |
| `comprehensive_test_analysis.py` | Test validation | `/analysis-utilities/` |
| `security_analysis.py` | Security assessment | `/analysis-utilities/` |

## Best Practices

### Security
1. **Never log credentials** - Use structured logging
2. **Validate inputs** - Especially for external data
3. **Use BeautifulSoup** - Avoid regex for HTML parsing
4. **Handle errors gracefully** - Comprehensive try/catch blocks

### Code Quality
1. **Use auth_utils.XrayAPIClient** - Don't reimplement authentication
2. **Follow DRY principle** - Centralize common functionality
3. **Document thoroughly** - Include docstrings and comments
4. **Test edge cases** - Handle pagination, timeouts, empty results

### Data Integrity
1. **Verify extraction parity** - Compare source to output
2. **Validate JSON structure** - Before Xray import
3. **Backup before modifications** - Keep original data
4. **Log all operations** - Maintain audit trail

## Troubleshooting

### Common Issues

**Authentication Failures**
```bash
# Check environment variables
echo $XRAY_CLIENT_ID
echo $XRAY_CLIENT_SECRET

# Test authentication
python xray-api/auth_utils.py
```

**GraphQL Errors**
```bash
# Debug query
python analysis-utilities/debug_query.py

# Check API status
curl -X GET https://xray.cloud.getxray.app/api/v2/graphql
```

**Extraction Issues**
```bash
# Debug page structure
python confluence-tools/debug_confluence_page.py <page_id>

# Verify document access
python confluence-tools/analyze_confluence_structure.py
```

### Support Resources

- Xray GraphQL Documentation: https://docs.getxray.app/display/XRAYCLOUD/GraphQL+API
- Pytest-Xray Plugin: https://github.com/fundakol/pytest-jira-xray
- Confluence API: https://developer.atlassian.com/cloud/confluence/rest/v1/

---

*This guide consolidates information from multiple technical documents. For specific implementation details, refer to the script documentation and inline comments.*