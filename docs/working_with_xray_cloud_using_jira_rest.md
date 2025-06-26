# Working with XRAY Cloud Test Cases Using JIRA REST API

Managing XRAY Cloud test cases through JIRA REST API presents unique challenges due to XRAY Cloud's architecture, which differs significantly from XRAY Server/DC. While JIRA REST API provides basic CRUD operations for XRAY entities (as they are JIRA issues), most advanced test management features require XRAY's own APIs. This guide provides practical implementation details for maximizing what's possible with JIRA REST API alone.

## 1. Organizing XRAY Test Cases into Folders Using JIRA REST API

### Understanding XRAY Cloud Architecture

**Critical Finding**: XRAY Cloud exposes very few custom fields through JIRA REST API compared to Server/DC. Most test-specific data is managed through XRAY's internal entities and accessed via GraphQL API rather than standard JIRA custom fields.

### Test Repository Path Field

The **Test Repository Path** custom field is one of the few XRAY-specific fields available through JIRA REST API for organizing tests into folders:

```python
# Setting Test Repository Path when creating a test
def create_test_with_folder(base_url, headers, project_key, test_data):
    url = f"{base_url}/rest/api/2/issue"
    
    payload = {
        "fields": {
            "project": {"key": project_key},
            "summary": test_data['summary'],
            "description": test_data.get('description', ''),
            "issuetype": {"name": "Test"},
            "customfield_XXXXX": "folder1/folder2/subfolder"  # Test Repository Path
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()
```

### Path Structure Requirements

- Use forward slashes "/" as delimiters
- Folders are created automatically if they don't exist
- Path is case-insensitive: "Components/CompA" = "components/compa"
- Leading/trailing spaces in folder names are automatically trimmed
- Invalid/missing folders result in tests appearing in "Orphans" meta-folder

### Recommended Folder Structure

```
Project Root/
├── Core_Features/
│   ├── Authentication/
│   ├── User_Management/
│   └── Data_Processing/
├── Test_Types/
│   ├── API_Tests/
│   ├── UI_Tests/
│   └── Integration_Tests/
└── Environments/
    ├── Staging/
    └── Production/
```

## 2. XRAY Custom Fields Available Through JIRA REST API

### Finding Custom Field IDs

Custom field IDs are instance-specific and must be discovered:

```python
def get_xray_custom_fields(base_url, headers):
    url = f"{base_url}/rest/api/2/field"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        fields = response.json()
        xray_fields = {}
        
        for field in fields:
            if 'xray' in field['name'].lower() or 'test' in field['name'].lower():
                xray_fields[field['name']] = field['id']
        
        return xray_fields
```

### Available XRAY Custom Fields in Cloud

XRAY Cloud exposes only a minimal set of custom fields:

```json
{
  "Test Repository Path": "customfield_10300",
  "Test Environments": "customfield_11805",
  "Test Plan Association": "customfield_11807",
  "Test Type": "customfield_10200"  // If available
}
```

**Important**: Most traditional XRAY fields (test steps, test types, etc.) are NOT exposed as JIRA custom fields in Cloud.

## 3. Setting Test Repository Path via JIRA REST API

### Complete Working Example

```python
import requests
import base64

class XrayTestManager:
    def __init__(self, base_url, email, api_token):
        self.base_url = base_url.rstrip('/')
        self.headers = self._create_auth_headers(email, api_token)
        self.custom_fields = self._discover_custom_fields()
    
    def _create_auth_headers(self, email, api_token):
        credentials = f"{email}:{api_token}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json"
        }
    
    def _discover_custom_fields(self):
        # Get custom field IDs from existing test issue
        test_key = "TEST-1"  # An existing test issue
        url = f"{self.base_url}/rest/api/2/issue/{test_key}/editmeta"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            fields = response.json()['fields']
            custom_fields = {}
            for field_id, field_info in fields.items():
                if field_id.startswith('customfield_'):
                    custom_fields[field_info['name']] = field_id
            return custom_fields
        return {}
    
    def create_test_with_path(self, project_key, summary, repository_path, description=""):
        url = f"{self.base_url}/rest/api/2/issue"
        
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "description": description,
                "issuetype": {"name": "Test"},
                self.custom_fields.get("Test Repository Path", "customfield_10300"): repository_path
            }
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to create test: {response.status_code} - {response.text}")

# Usage
manager = XrayTestManager(
    base_url="https://your-domain.atlassian.net",
    email="your-email@example.com",
    api_token="your-api-token"
)

# Create test with folder path
test = manager.create_test_with_path(
    project_key="PROJ",
    summary="Login functionality test",
    repository_path="Authentication/Login/PositiveCases",
    description="Test user login with valid credentials"
)
print(f"Created test: {test['key']}")
```

### Bulk Organization of Existing Tests

```python
def organize_tests_into_folders(base_url, headers, test_folder_mapping):
    """
    test_folder_mapping: dict mapping test keys to repository paths
    Example: {"TEST-1": "Authentication/Login", "TEST-2": "API/Users"}
    """
    results = {"success": [], "failed": []}
    
    for test_key, repository_path in test_folder_mapping.items():
        try:
            url = f"{base_url}/rest/api/2/issue/{test_key}"
            update_payload = {
                "fields": {
                    "customfield_10300": repository_path  # Adjust field ID
                }
            }
            
            response = requests.put(url, headers=headers, json=update_payload)
            
            if response.status_code == 204:
                results["success"].append(test_key)
                print(f"✓ Moved {test_key} to {repository_path}")
            else:
                results["failed"].append({
                    "key": test_key, 
                    "error": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            results["failed"].append({"key": test_key, "error": str(e)})
    
    return results
```

## 4. Creating XRAY Test Issues with Folder Organization

### Manual Test with Steps (Server/DC Only)

For XRAY Cloud, test steps cannot be added via JIRA REST API:

```python
def create_manual_test(base_url, headers, project_key, test_data):
    url = f"{base_url}/rest/api/2/issue"
    
    # Basic test creation for Cloud
    test_payload = {
        "fields": {
            "project": {"key": project_key},
            "summary": test_data['summary'],
            "description": test_data.get('description', ''),
            "issuetype": {"name": "Test"},
            "customfield_10300": test_data.get('repository_path', '')
        }
    }
    
    # Add labels for organization
    if 'labels' in test_data:
        test_payload["fields"]["labels"] = test_data['labels']
    
    response = requests.post(url, headers=headers, json=test_payload)
    
    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"Failed to create test: {response.status_code}")

# Usage example
test_data = {
    "summary": "User login validation test",
    "description": "Verify user can login with valid credentials",
    "repository_path": "Authentication/Login/Positive",
    "labels": ["smoke", "regression", "authentication"]
}

result = create_manual_test(base_url, headers, "PROJ", test_data)
```

### Querying Tests by Folder

```python
def query_tests_by_folder(base_url, headers, project_key, folder_path):
    jql = f'project = "{project_key}" AND issuetype = "Test" AND issue in testRepositoryFolderTests("{project_key}", "{folder_path}")'
    
    url = f"{base_url}/rest/api/2/search"
    params = {
        "jql": jql,
        "fields": "key,summary,customfield_10300",
        "maxResults": 100
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()['issues']
    else:
        raise Exception(f"Failed to query tests: {response.status_code}")
```

### JavaScript Implementation

```javascript
const axios = require('axios');

class XrayTestManager {
    constructor(baseURL, email, apiToken) {
        this.client = axios.create({
            baseURL: baseURL,
            auth: {
                username: email,
                password: apiToken
            },
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }
    
    async createTestWithPath(projectKey, testData) {
        const payload = {
            fields: {
                project: { key: projectKey },
                summary: testData.summary,
                description: testData.description || '',
                issuetype: { name: 'Test' },
                customfield_10300: testData.repositoryPath // Adjust field ID
            }
        };
        
        try {
            const response = await this.client.post('/rest/api/2/issue', payload);
            return response.data;
        } catch (error) {
            console.error('Failed to create test:', error.response?.data);
            throw error;
        }
    }
}

// Usage
const manager = new XrayTestManager(
    'https://your-domain.atlassian.net',
    'your-email@example.com',
    'your-api-token'
);

manager.createTestWithPath('PROJ', {
    summary: 'API endpoint validation',
    repositoryPath: 'API/Endpoints/UserManagement',
    description: 'Validate user creation endpoint'
}).then(result => console.log('Created:', result.key));
```

## 5. Limitations When Using JIRA REST API Instead of XRAY API

### Major Limitations

1. **No Test Step Management**: Cannot create, update, or retrieve test steps via JIRA REST API
2. **No Test Execution Creation**: Cannot create test runs or import test results directly
3. **Limited Test Type Support**: Cannot set test type (Manual/Automated/Generic) reliably
4. **No Precondition Management**: Cannot link or manage test preconditions
5. **No Folder API Access**: Cannot create or manage folders programmatically
6. **Missing Test-Specific Fields**: Most XRAY-specific data not exposed as custom fields

### Critical Features Only Available Through XRAY API

```
XRAY REST API Exclusive:
- /rest/raven/1.0/import/execution (test result import)
- /rest/raven/1.0/api/test/{key}/step (test step management)
- /rest/raven/1.0/api/testrepository/{projectKey}/folders (folder management)

XRAY GraphQL API (Cloud):
- Test steps, preconditions, test types
- Detailed test metadata
- Bulk operations
```

### Workarounds

1. **For Test Steps**: Store steps in description field as structured text
2. **For Test Results**: Use XRAY REST API endpoint for imports (requires separate authentication)
3. **For Test Types**: Use labels to categorize tests
4. **For Folder Management**: Pre-create folder structure manually

## 6. Best Practices for Test Organization

### Naming Conventions

```
✅ Good Folder Names:
- Core_Authentication
- API_Integration_Tests
- UI_Regression_Suite

❌ Avoid:
- Test/Cases (contains /)
- User's Tests (contains apostrophe)
- Complex*Names (contains *)
```

### Test Naming Pattern

```
[AREA]_[TYPE]_[DESCRIPTION]_[ID]

Examples:
- AUTH_API_LoginValidation_001
- UI_SMOKE_DashboardLoad_002
- PERF_LOAD_DatabaseQuery_003
```

### Organizational Strategy

1. **Use hierarchical structure** for main organization (Test Repository)
2. **Use labels** for cross-cutting concerns (smoke, regression, critical)
3. **Limit folder depth** to 3-4 levels maximum
4. **Create standard folder templates** for consistency across teams

### Performance Optimization

```python
# Rate limiting for API calls
import time
from functools import wraps

def rate_limit(calls_per_second=2):
    def decorator(func):
        last_called = [0.0]
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = 1.0 / calls_per_second - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
            
        return wrapper
    return decorator

@rate_limit(calls_per_second=1)
def create_test_with_rate_limit(*args, **kwargs):
    return create_manual_test(*args, **kwargs)
```

### CI/CD Integration

```groovy
// Jenkins Pipeline Example
pipeline {
    environment {
        JIRA_CREDS = credentials('jira-api-token')
    }
    
    stages {
        stage('Create Test Cases') {
            steps {
                script {
                    def tests = [
                        [summary: "Login Test", path: "Auth/Login"],
                        [summary: "API Test", path: "API/Users"]
                    ]
                    
                    tests.each { test ->
                        sh """
                            curl -X POST \\
                            -H "Content-Type: application/json" \\
                            -u ${JIRA_CREDS} \\
                            -d '{"fields": {"project": {"key": "PROJ"}, 
                                "summary": "${test.summary}", 
                                "issuetype": {"name": "Test"},
                                "customfield_10300": "${test.path}"}}' \\
                            "${JIRA_URL}/rest/api/2/issue"
                        """
                    }
                }
            }
        }
    }
}
```

## Key Recommendations

1. **Acknowledge Limitations**: JIRA REST API alone cannot fully manage XRAY tests. Plan for XRAY API integration for complete functionality.

2. **Focus on Organization**: Use Test Repository Path field effectively since it's one of the few XRAY fields available.

3. **Leverage Labels and Components**: Compensate for missing XRAY fields by using standard JIRA fields creatively.

4. **Implement Robust Error Handling**: Custom field IDs vary by instance; always implement discovery mechanisms.

5. **Consider Hybrid Approach**: Use JIRA REST API for basic operations and XRAY GraphQL API for advanced features when possible.

6. **Document Field Mappings**: Maintain documentation of custom field IDs for your instance to avoid hardcoding.

This approach maximizes what's possible with JIRA REST API while acknowledging its limitations for comprehensive XRAY test management.