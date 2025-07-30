"""
XRAY GraphQL API Client

This module provides a comprehensive client for interacting with XRAY Cloud's GraphQL API.
It handles authentication, query execution, and provides methods for all major test management operations.
"""

import os
import json
import time
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class XrayCredentials:
    """XRAY API credentials configuration"""
    client_id: str
    client_secret: str
    base_url: str
    email: str
    token: str

class XrayAuthenticator:
    """Handles XRAY API authentication and token management"""
    
    def __init__(self, credentials: XrayCredentials):
        self.credentials = credentials
        self.access_token = None
        self.token_expires_at = None
        self.session = requests.Session()
        
    def get_access_token(self) -> str:
        """Get a valid access token, refreshing if necessary"""
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token
            
        return self._refresh_token()
    
    def _refresh_token(self) -> str:
        """Refresh the XRAY access token"""
        url = "https://xray.cloud.getxray.app/api/v1/authenticate"
        headers = {"Content-Type": "application/json"}
        payload = {
            "client_id": self.credentials.client_id,
            "client_secret": self.credentials.client_secret
        }
        
        try:
            response = self.session.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            self.access_token = response.text.strip('"')
            # Tokens typically expire after 1 hour, refresh 5 minutes early
            self.token_expires_at = datetime.now() + timedelta(minutes=55)
            
            logger.info("XRAY access token refreshed successfully")
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to refresh XRAY token: {e}")
            raise

class XrayGraphQLClient:
    """Main client for XRAY GraphQL API operations"""
    
    def __init__(self, credentials: XrayCredentials):
        self.authenticator = XrayAuthenticator(credentials)
        self.graphql_url = "https://xray.cloud.getxray.app/api/v1/graphql"
        self.session = requests.Session()
        
    def execute_query(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """Execute a GraphQL query with proper authentication"""
        token = self.authenticator.get_access_token()
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        payload = {
            "query": query,
            "variables": variables or {}
        }
        
        try:
            response = self.session.post(self.graphql_url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            if "errors" in result:
                logger.error(f"GraphQL errors: {result['errors']}")
                raise Exception(f"GraphQL errors: {result['errors']}")
                
            return result.get("data", {})
            
        except requests.exceptions.RequestException as e:
            logger.error(f"GraphQL request failed: {e}")
            raise
    
    def get_tests(self, project_key: str, limit: int = 100, start: int = 0, 
                  jql: Optional[str] = None, folder_path: Optional[str] = None) -> Dict:
        """
        Fetch tests from a project with optional filtering
        
        Args:
            project_key: JIRA project key (e.g., "MLB")
            limit: Maximum number of tests to return (max 100)
            start: Starting offset for pagination
            jql: JQL query for filtering
            folder_path: Filter by Test Repository folder path
        """
        query = """
        query GetTests($projectKey: String!, $limit: Int!, $start: Int!, $jql: String) {
            getTests(projectKey: $projectKey, limit: $limit, start: $start, jql: $jql) {
                total
                results {
                    issueId
                    testType {
                        name
                        kind
                    }
                    steps {
                        id
                        action
                        data
                        result
                        attachments {
                            id
                            filename
                        }
                        customFields {
                            id
                            name
                            value
                        }
                    }
                    jira(fields: ["key", "summary", "description", "labels", "priority", "assignee", "components", "created", "updated"])
                    folder {
                        name
                        path
                    }
                    lastModified
                }
            }
        }
        """
        
        variables = {
            "projectKey": project_key,
            "limit": limit,
            "start": start,
            "jql": jql
        }
        
        return self.execute_query(query, variables)
    
    def get_test_details(self, issue_id: str) -> Dict:
        """Get detailed information for a specific test"""
        query = """
        query GetTest($issueId: String!) {
            getTest(issueId: $issueId) {
                issueId
                testType {
                    name
                    kind
                }
                steps {
                    id
                    action
                    data
                    result
                    attachments {
                        id
                        filename
                        url
                    }
                    customFields {
                        id
                        name
                        value
                    }
                }
                gherkin
                unstructured
                jira(fields: ["key", "summary", "description", "labels", "priority", "assignee", "components", "created", "updated", "reporter"])
                folder {
                    name
                    path
                }
                lastModified
            }
        }
        """
        
        variables = {"issueId": issue_id}
        return self.execute_query(query, variables)
    
    def search_tests_by_labels(self, project_key: str, labels: List[str], 
                              limit: int = 100, start: int = 0) -> Dict:
        """Search tests by specific labels"""
        label_query = " OR ".join([f'labels = "{label}"' for label in labels])
        jql = f'project = "{project_key}" AND issuetype = "Test" AND ({label_query})'
        
        return self.get_tests(project_key, limit, start, jql)
    
    def get_tests_without_steps(self, project_key: str, limit: int = 100, start: int = 0) -> Dict:
        """Get tests that have no test steps defined"""
        query = """
        query GetTestsWithoutSteps($projectKey: String!, $limit: Int!, $start: Int!) {
            getTests(projectKey: $projectKey, limit: $limit, start: $start) {
                total
                results {
                    issueId
                    testType {
                        name
                        kind
                    }
                    steps {
                        id
                        action
                    }
                    jira(fields: ["key", "summary", "description", "labels", "priority", "assignee"])
                    folder {
                        name
                        path
                    }
                    lastModified
                }
            }
        }
        """
        
        variables = {
            "projectKey": project_key,
            "limit": limit,
            "start": start
        }
        
        result = self.execute_query(query, variables)
        
        # Filter out tests that have steps
        if "getTests" in result and "results" in result["getTests"]:
            tests_without_steps = [
                test for test in result["getTests"]["results"] 
                if not test.get("steps") or len(test["steps"]) == 0
            ]
            result["getTests"]["results"] = tests_without_steps
            result["getTests"]["total"] = len(tests_without_steps)
        
        return result
    
    def add_test_step(self, issue_id: str, action: str, data: str = "", result: str = "") -> Dict:
        """Add a new test step to an existing test"""
        query = """
        mutation AddTestStep($issueId: String!, $step: CreateStepInput!) {
            addTestStep(issueId: $issueId, step: $step) {
                step {
                    id
                    action
                    data
                    result
                }
                warnings
            }
        }
        """
        
        variables = {
            "issueId": issue_id,
            "step": {
                "action": action,
                "data": data,
                "result": result
            }
        }
        
        return self.execute_query(query, variables)
    
    def update_test_step(self, issue_id: str, step_id: str, action: str, 
                        data: str = "", result: str = "") -> Dict:
        """Update an existing test step"""
        query = """
        mutation UpdateTestStep($issueId: String!, $stepId: String!, $step: UpdateStepInput!) {
            updateTestStep(issueId: $issueId, stepId: $stepId, step: $step) {
                step {
                    id
                    action
                    data
                    result
                }
                warnings
            }
        }
        """
        
        variables = {
            "issueId": issue_id,
            "stepId": step_id,
            "step": {
                "action": action,
                "data": data,
                "result": result
            }
        }
        
        return self.execute_query(query, variables)
    
    def remove_test_step(self, issue_id: str, step_id: str) -> Dict:
        """Remove a test step from a test"""
        query = """
        mutation RemoveTestStep($issueId: String!, $stepId: String!) {
            removeTestStep(issueId: $issueId, stepId: $stepId) {
                warnings
            }
        }
        """
        
        variables = {
            "issueId": issue_id,
            "stepId": step_id
        }
        
        return self.execute_query(query, variables)
    
    def get_test_sets(self, project_key: str, limit: int = 100, start: int = 0) -> Dict:
        """Get test sets for a project"""
        query = """
        query GetTestSets($projectKey: String!, $limit: Int!, $start: Int!) {
            getTestSets(projectKey: $projectKey, limit: $limit, start: $start) {
                total
                results {
                    issueId
                    tests(limit: 100) {
                        total
                        results {
                            issueId
                            jira(fields: ["key", "summary"])
                        }
                    }
                    jira(fields: ["key", "summary", "description", "labels"])
                }
            }
        }
        """
        
        variables = {
            "projectKey": project_key,
            "limit": limit,
            "start": start
        }
        
        return self.execute_query(query, variables)
    
    def create_test_set(self, project_key: str, name: str, test_issue_ids: List[str]) -> Dict:
        """Create a new test set with specified tests"""
        query = """
        mutation CreateTestSet($projectKey: String!, $name: String!, $testIssueIds: [String!]!) {
            createTestSet(
                testIssueIds: $testIssueIds,
                jira: {
                    fields: {
                        summary: $name,
                        project: { key: $projectKey }
                    }
                }
            ) {
                testSet {
                    issueId
                    jira(fields: ["key", "summary"])
                }
                warnings
            }
        }
        """
        
        variables = {
            "projectKey": project_key,
            "name": name,
            "testIssueIds": test_issue_ids
        }
        
        return self.execute_query(query, variables)
    
    def get_folder_structure(self, project_key: str, folder_path: str = "/") -> Dict:
        """Get the folder structure for a project"""
        query = """
        query GetFolder($projectKey: String!, $folderPath: String!) {
            getFolder(projectKey: $projectKey, path: $folderPath) {
                name
                path
                testsCount
                tests {
                    issueId
                    jira(fields: ["key", "summary", "labels"])
                }
            }
        }
        """
        
        variables = {
            "projectKey": project_key,
            "folderPath": folder_path
        }
        
        return self.execute_query(query, variables)
    
    def add_tests_to_folder(self, project_key: str, folder_path: str, test_issue_ids: List[str]) -> Dict:
        """Add tests to a specific folder"""
        query = """
        mutation AddTestsToFolder($projectKey: String!, $folderPath: String!, $testIssueIds: [String!]!) {
            addTestsToFolder(
                projectKey: $projectKey,
                path: $folderPath,
                testIssueIds: $testIssueIds
            ) {
                folder {
                    name
                    path
                    testsCount
                }
                warnings
            }
        }
        """
        
        variables = {
            "projectKey": project_key,
            "folderPath": folder_path,
            "testIssueIds": test_issue_ids
        }
        
        return self.execute_query(query, variables)

def create_client_from_env() -> XrayGraphQLClient:
    """Create an XRAY client using environment variables"""
    credentials = XrayCredentials(
        client_id=os.getenv("XRAY_CLIENT_ID"),
        client_secret=os.getenv("XRAY_CLIENT_SECRET"),
        base_url=os.getenv("ATLASSIAN_BASE_URL"),
        email=os.getenv("ATLASSIAN_EMAIL"),
        token=os.getenv("ATLASSIAN_TOKEN")
    )
    
    if not all([credentials.client_id, credentials.client_secret, credentials.base_url]):
        raise ValueError("Missing required environment variables for XRAY authentication")
    
    return XrayGraphQLClient(credentials)

# Example usage
if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Create client
    client = create_client_from_env()
    
    # Example: Get tests from MLB project
    try:
        tests = client.get_tests("MLB", limit=10)
        print(f"Found {tests['getTests']['total']} tests")
        
        for test in tests['getTests']['results']:
            print(f"- {test['jira']['key']}: {test['jira']['summary']}")
            
    except Exception as e:
        print(f"Error: {e}")