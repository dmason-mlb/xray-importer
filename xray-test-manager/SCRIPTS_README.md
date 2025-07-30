# XRAY Test Manager Scripts Documentation

This directory contains Python scripts that implement all the functionality described in the macOS app specification. These scripts provide a complete backend implementation for interacting with XRAY GraphQL API and demonstrate the core features that would be available in the native app.

## Files Overview

### Core Implementation Files

#### `xray_client.py`
**Primary XRAY GraphQL API Client**

The foundation of the entire system, this module provides:

- **Authentication Management**: Handles XRAY API token refresh and management
- **GraphQL Query Execution**: Executes queries with proper error handling
- **Core API Operations**: Implements all essential XRAY operations

**Key Classes:**
- `XrayCredentials`: Configuration for API access
- `XrayAuthenticator`: Token management and authentication
- `XrayGraphQLClient`: Main API client with all GraphQL operations

**Key Methods:**
- `get_tests()`: Fetch tests with filtering and pagination
- `get_test_details()`: Get detailed test information including steps
- `search_tests_by_labels()`: Search tests by label filters
- `get_tests_without_steps()`: Find tests missing step definitions
- `add_test_step()`: Add new test steps
- `update_test_step()`: Modify existing test steps
- `remove_test_step()`: Delete test steps
- `add_tests_to_folder()`: Organize tests in folders
- `create_test_set()`: Create test sets for organization

#### `test_manager.py`
**High-Level Test Management Operations**

Provides business logic and orchestrates multiple API calls for complex operations:

- **Test Fetching**: Combines GraphQL queries with filtering logic
- **Batch Operations**: Handles multiple test operations efficiently
- **Data Transformation**: Converts API responses to application models
- **Caching**: Implements performance optimizations

**Key Classes:**
- `TestSummary`: Simplified test representation for UI
- `TestStep`: Test step data structure
- `BatchOperationResult`: Results of batch operations
- `XrayTestManager`: Main management class

**Key Methods:**
- `fetch_tests_summary()`: Get paginated test lists with filtering
- `get_tests_without_steps()`: Find tests needing step definitions
- `search_tests_by_keywords()`: Full-text search across tests
- `batch_move_to_folder()`: Move multiple tests to folders
- `get_all_labels()`: Extract all unique labels from project
- `export_tests_to_json()`: Export test data for analysis

#### `ai_step_generator.py`
**AI-Powered Test Step Generation**

Implements intelligent test step proposal system:

- **Content Analysis**: Analyzes test summaries and descriptions
- **Pattern Matching**: Uses templates and patterns for step generation
- **Confidence Scoring**: Provides confidence levels for proposals
- **Contextual Adaptation**: Customizes steps based on test context

**Key Classes:**
- `ProposedStep`: Individual step proposal with confidence
- `StepProposal`: Complete proposal for a test
- `AIStepGenerator`: Main AI logic implementation

**Key Features:**
- **Template System**: Pre-defined step templates for common scenarios
- **Entity Extraction**: Identifies pages, elements, and actions from text
- **Complexity Assessment**: Adjusts proposals based on test complexity
- **Category Detection**: Recognizes test types (login, API, UI, etc.)

#### `cli_demo.py`
**Command-Line Interface Demo**

Demonstrates all functionality through a comprehensive CLI:

- **Interactive Commands**: Shows how each feature works
- **Real Data**: Works with actual XRAY data from your projects
- **Batch Operations**: Demonstrates bulk operations
- **Export Capabilities**: Shows data export functionality

## Environment Setup

### Prerequisites

1. **Python 3.8+** installed on your system
2. **XRAY Cloud access** with API credentials
3. **JIRA Cloud access** with API token

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables:**
Create a `.env` file in the project root with:
```
XRAY_CLIENT_ID=your_client_id
XRAY_CLIENT_SECRET=your_client_secret
ATLASSIAN_BASE_URL=https://your-domain.atlassian.net
ATLASSIAN_EMAIL=your-email@domain.com
ATLASSIAN_TOKEN=your_api_token
```

3. **Test the setup:**
```bash
python3 cli_demo.py list-projects
```

## Usage Examples

### Basic Operations

#### List Available Projects
```bash
python3 cli_demo.py list-projects
```

#### List Tests for a Project
```bash
python3 cli_demo.py list-tests --project MLB --limit 20
```

#### Search Tests by Keywords
```bash
python3 cli_demo.py search-tests --project MLB --keywords "login authentication"
```

#### Show Tests Without Steps
```bash
python3 cli_demo.py tests-without-steps --project MLB --limit 10
```

#### Get Test Details
```bash
python3 cli_demo.py test-details --issue-id "10001"
```

### Advanced Operations

#### Generate AI Step Proposals
```bash
python3 cli_demo.py generate-proposals --project MLB --limit 5
```

#### Show Project Labels
```bash
python3 cli_demo.py project-labels --project MLB
```

#### Export Tests with Filters
```bash
python3 cli_demo.py export-tests --project MLB --output mlb_tests.json --labels "smoke" "regression"
```

### Filtering Options

#### Filter by Labels
```bash
python3 cli_demo.py list-tests --project MLB --labels "smoke" "api" --limit 15
```

#### Filter by Priority
```bash
python3 cli_demo.py list-tests --project MLB --priority "High" --limit 10
```

## Script Integration

### Using in Your Own Code

#### Basic Client Usage
```python
from xray_client import create_client_from_env

# Create client
client = create_client_from_env()

# Get tests
tests = client.get_tests("MLB", limit=10)
print(f"Found {tests['getTests']['total']} tests")
```

#### Using Test Manager
```python
from test_manager import XrayTestManager

# Create manager
manager = XrayTestManager()

# Get tests without steps
tests = manager.get_tests_without_steps("MLB", limit=5)
for test in tests:
    print(f"{test.key}: {test.summary}")
```

#### Using AI Step Generator
```python
from ai_step_generator import AIStepGenerator
from test_manager import XrayTestManager

# Create components
manager = XrayTestManager()
generator = AIStepGenerator(manager)

# Generate proposals
tests = manager.get_tests_without_steps("MLB", limit=3)
proposals = generator.generate_steps_for_multiple_tests(tests)

# Display results
for proposal in proposals:
    print(f"{proposal.test_key}: {len(proposal.proposed_steps)} steps")
```

## API Operations Reference

### GraphQL Queries Used

#### Test Retrieval
```graphql
query GetTests($projectKey: String!, $limit: Int!, $jql: String) {
    getTests(projectKey: $projectKey, limit: $limit, jql: $jql) {
        total
        results {
            issueId
            testType { name kind }
            steps { id action data result }
            jira(fields: ["key", "summary", "labels", "priority"])
            folder { name path }
        }
    }
}
```

#### Test Details
```graphql
query GetTest($issueId: String!) {
    getTest(issueId: $issueId) {
        issueId
        testType { name kind }
        steps { id action data result attachments { filename } }
        jira(fields: ["key", "summary", "description", "labels"])
        folder { name path }
    }
}
```

### GraphQL Mutations Used

#### Add Test Step
```graphql
mutation AddTestStep($issueId: String!, $step: CreateStepInput!) {
    addTestStep(issueId: $issueId, step: $step) {
        step { id action data result }
        warnings
    }
}
```

#### Update Test Step
```graphql
mutation UpdateTestStep($issueId: String!, $stepId: String!, $step: UpdateStepInput!) {
    updateTestStep(issueId: $issueId, stepId: $stepId, step: $step) {
        step { id action data result }
        warnings
    }
}
```

#### Move Tests to Folder
```graphql
mutation AddTestsToFolder($projectKey: String!, $folderPath: String!, $testIssueIds: [String!]!) {
    addTestsToFolder(projectKey: $projectKey, path: $folderPath, testIssueIds: $testIssueIds) {
        folder { name path testsCount }
        warnings
    }
}
```

## Error Handling

### Common Issues and Solutions

#### Authentication Errors
- **Issue**: "Invalid credentials" or "Token expired"
- **Solution**: Check `.env` file credentials and ensure tokens are valid

#### GraphQL Errors
- **Issue**: "Field not found" or "Invalid query"
- **Solution**: Check API documentation and ensure field names match schema

#### Rate Limiting
- **Issue**: "Too many requests" errors
- **Solution**: Implement delays between requests or use batch operations

#### Network Issues
- **Issue**: Connection timeouts or network errors
- **Solution**: Check internet connection and XRAY Cloud status

### Logging and Debugging

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check GraphQL responses:
```python
result = client.execute_query(query, variables)
print(json.dumps(result, indent=2))
```

## Performance Considerations

### Pagination
- **GraphQL Limit**: Maximum 100 results per query
- **Implementation**: Use `start` parameter for pagination
- **Best Practice**: Use smaller limits for UI responsiveness

### Caching
- **Token Caching**: Tokens cached for 55 minutes
- **Data Caching**: Implement local caching for frequently accessed data
- **Cache Invalidation**: Clear cache when data is modified

### Batch Operations
- **Batch Size**: Keep batch sizes reasonable (10-50 items)
- **Error Handling**: Handle partial failures gracefully
- **Progress Tracking**: Provide feedback for long operations

## Future Enhancements

### Planned Features
1. **Async Operations**: Convert to async/await for better performance
2. **Real-time Updates**: WebSocket support for live updates
3. **Advanced AI**: More sophisticated step generation algorithms
4. **Integration APIs**: Support for CI/CD pipeline integration
5. **Mobile Support**: Cross-platform mobile application

### Extension Points
1. **Custom Templates**: User-defined step templates
2. **Plugin System**: Third-party integrations
3. **Export Formats**: Additional export formats (CSV, Excel, XML)
4. **Webhook Support**: Event-driven integrations

## Contributing

### Code Style
- Follow PEP 8 guidelines
- Use type hints for all function parameters
- Include docstrings for all public methods
- Use meaningful variable names

### Testing
- Write unit tests for all new functionality
- Include integration tests for API operations
- Test error conditions and edge cases
- Maintain test coverage above 80%

### Documentation
- Update this README for new features
- Include inline code comments for complex logic
- Provide usage examples for new functionality
- Document any breaking changes

This comprehensive script collection provides a solid foundation for building the full macOS application while demonstrating all the core functionality through practical, working examples.