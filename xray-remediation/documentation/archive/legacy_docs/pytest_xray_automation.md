# PyTest-Xray Integration for API Test Automation

PyTest can be seamlessly integrated with Xray test management in JIRA to enable automated API test execution and result reporting. This integration supports both Xray Cloud and Server/Data Center deployments, with the **pytest-jira-xray** plugin emerging as the most robust solution for MLB's API test automation needs.

## Methods to execute PyTest tests from Xray

PyTest tests can be triggered from Xray through multiple mechanisms, though direct execution from within Xray test cases requires additional orchestration. The primary approach involves **JUnit XML-based integration** where PyTest generates test results that are then imported into Xray via REST APIs.

For automated execution, teams typically implement CI/CD pipeline triggers that run PyTest suites and automatically report results back to Xray. While Xray doesn't natively execute PyTest tests, you can configure webhooks or automation rules in JIRA to trigger external test runs. The most practical approach uses this workflow:

```bash
# Generate JUnit XML from PyTest execution
pytest --junitxml=reports/junit.xml

# Import results to Xray Cloud
curl -H "Content-Type: text/xml" -X POST \
  -H "Authorization: Bearer $token" \
  --data @"junit.xml" \
  "https://xray.cloud.getxray.app/api/v2/import/execution/junit?projectKey=MLB&testPlanKey=PLAN-123"
```

For Server/DC deployments, the endpoint differs slightly, using `/rest/raven/2.0/import/execution/junit` with basic authentication instead of bearer tokens.

## Reporting PyTest results to Xray test cases

The **pytest-jira-xray** plugin provides the most streamlined reporting mechanism. After installation (`pip install pytest-jira-xray`), tests are marked with Xray test case IDs using decorators:

```python
import pytest

@pytest.mark.xray('MLB-123')
def test_player_stats_api():
    """Test player statistics endpoint"""
    response = requests.get('/api/v1/players/stats')
    assert response.status_code == 200
    assert 'batting_average' in response.json()

@pytest.mark.xray(['MLB-124', 'MLB-125'])
def test_game_schedule_api():
    """Test game schedule endpoint - maps to multiple test cases"""
    response = requests.get('/api/v1/schedule')
    assert response.status_code == 200
```

Test results flow back to Xray through either the plugin's automatic reporting or manual import of JUnit XML files. The plugin handles authentication, test mapping, and status translation between PyTest and Xray formats.

## Required plugins, libraries and tools

### Essential Components

**Primary Plugin**: **pytest-jira-xray** (v0.9.2+)
- Actively maintained with support for both Cloud and Server/DC
- Features include test marking, evidence attachment, defect tracking, and custom result hooks
- Installation: `pip install pytest-jira-xray`
- Usage: `pytest --jira-xray --cloud` (for Cloud) or `pytest --jira-xray` (for Server/DC)

**Alternative Options**:
- **pytest-typhoon-xray**: Better for advanced parameterization needs
- **atlassian-python-api**: For Server/DC environments requiring comprehensive API access
- **ska-ser-xray**: Command-line tools for result upload in CI/CD pipelines

### Environment Configuration

```bash
# Xray Cloud authentication
export XRAY_CLIENT_ID="your_client_id"
export XRAY_CLIENT_SECRET="your_client_secret"
export XRAY_API_BASE_URL="https://xray.cloud.getxray.app"

# Xray Server/DC authentication  
export XRAY_API_BASE_URL="https://your-jira.com"
export XRAY_API_USER="username"
export XRAY_API_PASSWORD="password"

# Test execution parameters
export XRAY_EXECUTION_TEST_ENVIRONMENTS="Production API"
export XRAY_EXECUTION_REVISION=$(git rev-parse HEAD)
```

## Best practices for mapping tests to Xray

Effective test mapping requires consistent naming conventions and organizational structure. Use **class-based test organization** to group related API tests, applying Xray markers at both class and method levels:

```python
# conftest.py - Custom markers for enhanced mapping
import pytest

def pytest_collection_modifyitems(session, config, items):
    for item in items:
        for marker in item.iter_markers(name="requirements"):
            requirements = marker.args[0]
            item.user_properties.append(("requirements", requirements))
        for marker in item.iter_markers(name="test_key"):
            test_key = marker.args[0]
            item.user_properties.append(("test_key", test_key))

# test_mlb_api.py
class TestPlayerAPI:
    @pytest.mark.xray('MLB-100')
    @pytest.mark.requirements('MLB-REQ-50')
    def test_get_player_details(self):
        """Verify player details endpoint returns correct data"""
        # Test implementation
```

Key mapping strategies include:
- Use descriptive test names matching Xray test case summaries
- Implement consistent test ID patterns (e.g., MLB-XXXX)
- Group tests by API feature or endpoint
- Maintain bidirectional traceability with requirements

## Example configurations and code

### pytest.ini Configuration
```ini
[pytest]
markers =
    xray: mark test for Xray integration
    requirements: link test with Jira requirements
    test_key: map to existing Xray test
addopts = --junitxml=reports/junit.xml --tb=short
junit_family = legacy
testpaths = tests/api
python_files = test_*.py
python_classes = TestMLB*
python_functions = test_*
```

### Jenkins Pipeline Integration
```groovy
pipeline {
    agent any
    
    environment {
        XRAY_CLIENT_ID = credentials('mlb-xray-client-id')
        XRAY_CLIENT_SECRET = credentials('mlb-xray-client-secret')
    }
    
    stages {
        stage('API Tests') {
            steps {
                sh '''
                    pip install pytest pytest-jira-xray requests
                    pytest --jira-xray --cloud --junitxml=reports/junit.xml tests/api/
                '''
            }
        }
        
        stage('Report to Xray') {
            steps {
                script {
                    // Plugin automatically handles import when using --jira-xray flag
                    archiveArtifacts artifacts: 'reports/*.xml'
                }
            }
        }
    }
}
```

### Advanced API Test Example
```python
import pytest
import requests
from datetime import datetime

class TestMLBStatsAPI:
    
    @pytest.fixture(autouse=True)
    def api_client(self):
        """Setup API client with authentication"""
        self.base_url = "https://api.mlb.com/v1"
        self.headers = {"Authorization": f"Bearer {os.getenv('MLB_API_TOKEN')}"}
    
    @pytest.mark.xray('MLB-201')
    @pytest.mark.parametrize("team_id,expected_division", [
        ("NYY", "AL East"),
        ("LAD", "NL West"),
        ("CHC", "NL Central")
    ])
    def test_team_information_api(self, team_id, expected_division):
        """Verify team information endpoint returns correct division data"""
        response = requests.get(
            f"{self.base_url}/teams/{team_id}",
            headers=self.headers
        )
        
        assert response.status_code == 200
        team_data = response.json()
        assert team_data['division'] == expected_division
        assert 'roster' in team_data
        assert len(team_data['roster']) >= 25  # MLB roster minimum
    
    @pytest.mark.xray('MLB-202')
    def test_live_game_updates_api(self, xray_evidence):
        """Test live game updates endpoint performance and accuracy"""
        game_id = "2024_07_13_NYY_BOS"
        response = requests.get(
            f"{self.base_url}/games/{game_id}/live",
            headers=self.headers
        )
        
        # Add response as evidence in Xray
        xray_evidence(
            filename=f"game_response_{game_id}.json",
            data=response.text.encode()
        )
        
        assert response.status_code == 200
        assert response.elapsed.total_seconds() < 2.0  # Performance requirement
        
        game_data = response.json()
        assert 'innings' in game_data
        assert 'current_batter' in game_data
        assert game_data['game_status'] in ['live', 'final', 'postponed']
```

## Xray Cloud vs Server/DC implementation differences

The implementation approach varies significantly between Xray Cloud and Server/Data Center deployments:

### Authentication and API Access

**Xray Cloud** uses OAuth-style authentication with Client ID/Secret pairs that generate 24-hour bearer tokens. The API is split between REST (for imports) and GraphQL (for queries), with enforced rate limits of 300-1000 requests per 5 minutes depending on plan.

**Xray Server/DC** leverages Jira's native authentication (basic auth or personal access tokens) with comprehensive REST API v1.0/v2.0 endpoints. No built-in rate limiting exists, but performance depends on server infrastructure.

### Key Implementation Differences

1. **Test Status Format**: Cloud uses "PASSED/FAILED" while Server/DC uses "PASS/FAIL"
2. **API Endpoints**: Cloud uses `xray.cloud.getxray.app` while Server/DC uses `/rest/raven/`
3. **Plugin Usage**: Must add `--cloud` flag for pytest-jira-xray when using Cloud
4. **Features**: Cloud lacks Automated Step Library and Historic Test Coverage reports

### Platform Selection for MLB

For MLB's API test automation, consider:
- **Choose Cloud** if preferring managed infrastructure with automatic updates and GraphQL capabilities
- **Choose Server/DC** for unlimited API usage, advanced customization, and if already using Jira Server

The pytest-jira-xray plugin abstracts most differences, making the integration code largely portable between platforms. Focus on proper environment configuration and authentication setup based on your chosen deployment model.