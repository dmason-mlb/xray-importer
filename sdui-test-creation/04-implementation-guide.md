# SDUI Test Creation Implementation Guide

This guide provides practical code examples and scripts for implementing the SDUI test creation strategy using XRAY's GraphQL API.

## Table of Contents
1. [Setup and Configuration](#setup-and-configuration)
2. [Python Implementation](#python-implementation)
3. [Folder Structure Creation](#folder-structure-creation)
4. [Test Case Import](#test-case-import)
5. [Test Set Management](#test-set-management)
6. [Batch Operations](#batch-operations)
7. [Error Handling and Logging](#error-handling-and-logging)
8. [Complete Working Example](#complete-working-example)

## Setup and Configuration

### Environment Setup

Create a `.env` file:
```bash
# XRAY API Credentials
XRAY_CLIENT=your_client_id_here
XRAY_SECRET=your_client_secret_here

# JIRA Configuration
JIRA_PROJECT_KEY=MLB
JIRA_PROJECT_ID=10000

# API URLs
XRAY_AUTH_URL=https://xray.cloud.getxray.app/api/v2/authenticate
XRAY_GRAPHQL_URL=https://xray.cloud.getxray.app/api/v2/graphql

# Logging
LOG_LEVEL=INFO
LOG_FILE=sdui_test_import.log
```

### Requirements

Create `requirements.txt`:
```
requests==2.31.0
python-dotenv==1.0.0
pandas==2.0.3
openpyxl==3.1.2
tenacity==8.2.3
```

## Python Implementation

### Base Client Class

```python
# xray_client.py
import os
import requests
import json
import logging
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from tenacity import retry, wait_exponential, stop_after_attempt

load_dotenv()

class XrayGraphQLClient:
    """Client for interacting with XRAY GraphQL API"""
    
    def __init__(self):
        self.client_id = os.getenv('XRAY_CLIENT')
        self.client_secret = os.getenv('XRAY_SECRET')
        self.auth_url = os.getenv('XRAY_AUTH_URL')
        self.graphql_url = os.getenv('XRAY_GRAPHQL_URL')
        self.token = None
        self.logger = logging.getLogger(__name__)
        
    def authenticate(self) -> str:
        """Get authentication token from XRAY"""
        if not self.client_id or not self.client_secret:
            raise ValueError("XRAY_CLIENT and XRAY_SECRET must be set")
        
        auth_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        try:
            response = requests.post(self.auth_url, json=auth_data)
            response.raise_for_status()
            self.token = response.text.strip('"')
            self.logger.info("Successfully authenticated with XRAY")
            return self.token
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            raise
    
    @retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
    def execute_query(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """Execute GraphQL query with retry logic"""
        if not self.token:
            self.authenticate()
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        try:
            response = requests.post(self.graphql_url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            if "errors" in result:
                self.logger.error(f"GraphQL errors: {result['errors']}")
                raise Exception(f"GraphQL errors: {result['errors']}")
            
            return result
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                # Token expired, re-authenticate
                self.logger.info("Token expired, re-authenticating...")
                self.authenticate()
                # Retry will handle the request
                raise
            else:
                self.logger.error(f"HTTP error: {e}")
                raise
```

## Folder Structure Creation

### Folder Manager Class

```python
# folder_manager.py
from typing import List, Dict, Optional
import logging

class FolderManager:
    """Manages XRAY test folder operations"""
    
    def __init__(self, client: XrayGraphQLClient, project_id: str):
        self.client = client
        self.project_id = project_id
        self.logger = logging.getLogger(__name__)
    
    def create_folder(self, path: str, test_ids: Optional[List[str]] = None) -> Dict:
        """Create a single folder"""
        query = """
        mutation CreateFolder($projectId: String!, $path: String!, $testIssueIds: [String]) {
            createFolder(projectId: $projectId, path: $path, testIssueIds: $testIssueIds) {
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
            "projectId": self.project_id,
            "path": path
        }
        
        if test_ids:
            variables["testIssueIds"] = test_ids
        
        result = self.client.execute_query(query, variables)
        folder_data = result.get('data', {}).get('createFolder', {})
        
        if folder_data.get('warnings'):
            self.logger.warning(f"Warnings for folder {path}: {folder_data['warnings']}")
        
        return folder_data
    
    def create_folder_structure(self, structure: Dict[str, List[str]]) -> Dict[str, Dict]:
        """Create complete folder structure from dictionary"""
        results = {}
        
        # Sort paths to ensure parent folders are created first
        sorted_paths = sorted(structure.keys(), key=lambda x: x.count('/'))
        
        for path in sorted_paths:
            try:
                self.logger.info(f"Creating folder: {path}")
                result = self.create_folder(path)
                results[path] = result
                
                # If there are sub-paths defined, create them
                for sub_path in structure[path]:
                    full_sub_path = f"{path}/{sub_path}"
                    self.logger.info(f"Creating sub-folder: {full_sub_path}")
                    sub_result = self.create_folder(full_sub_path)
                    results[full_sub_path] = sub_result
                    
            except Exception as e:
                self.logger.error(f"Failed to create folder {path}: {e}")
                results[path] = {"error": str(e)}
        
        return results
    
    def setup_sdui_folders(self) -> Dict[str, Dict]:
        """Create complete SDUI folder structure"""
        sdui_structure = {
            "/Browse Menu": [
                "Core Navigation",
                "Content Display",
                "Personalization",
                "Jewel Events",
                "Game States"
            ],
            "/Team Page": [
                "Date Bar",
                "Matchup Display",
                "Product Links",
                "Jewel Events"
            ],
            "/Gameday": [
                "WebView",
                "JS Bridge",
                "Game States",
                "Jewel Events"
            ],
            "/Scoreboard": [
                "GameCell",
                "CalendarBar",
                "Jewel Events",
                "Game States"
            ]
        }
        
        # Add jewel event sub-folders
        jewel_events = [
            "Opening Day",
            "All-Star Week",
            "Postseason",
            "Spring Training",
            "International Series"
        ]
        
        # Create base structure
        results = self.create_folder_structure(sdui_structure)
        
        # Create jewel event sub-folders
        for feature in ["/Browse Menu", "/Team Page", "/Gameday", "/Scoreboard"]:
            for event in jewel_events:
                event_path = f"{feature}/Jewel Events/{event}"
                try:
                    self.logger.info(f"Creating jewel event folder: {event_path}")
                    result = self.create_folder(event_path)
                    results[event_path] = result
                except Exception as e:
                    self.logger.error(f"Failed to create folder {event_path}: {e}")
                    results[event_path] = {"error": str(e)}
        
        return results
```

## Test Case Import

### Test Manager Class

```python
# test_manager.py
from typing import List, Dict, Optional
import logging

class TestManager:
    """Manages XRAY test operations"""
    
    def __init__(self, client: XrayGraphQLClient, project_key: str):
        self.client = client
        self.project_key = project_key
        self.logger = logging.getLogger(__name__)
    
    def create_manual_test(self, 
                          summary: str,
                          description: str,
                          steps: List[Dict],
                          labels: List[str],
                          priority: str = "Medium",
                          assignee: Optional[str] = None,
                          components: Optional[List[str]] = None,
                          folder_path: Optional[str] = None) -> Dict:
        """Create a manual test with steps"""
        
        query = """
        mutation CreateManualTest(
            $jira: JSON!,
            $testType: UpdateTestTypeInput,
            $steps: [CreateStepInput!],
            $folderPath: String
        ) {
            createTest(
                jira: $jira,
                testType: $testType,
                steps: $steps,
                folderPath: $folderPath
            ) {
                test {
                    issueId
                    testType { name }
                    steps {
                        id
                        action
                        data
                        result
                    }
                    folder { path }
                    jira(fields: ["key", "labels", "priority"])
                }
                warnings
            }
        }
        """
        
        # Build JIRA fields
        jira_fields = {
            "project": {"key": self.project_key},
            "summary": summary,
            "description": description,
            "issuetype": {"name": "Test"},
            "labels": labels,
            "priority": {"name": priority}
        }
        
        if assignee:
            jira_fields["assignee"] = {"name": assignee}
        
        if components:
            jira_fields["components"] = [{"name": c} for c in components]
        
        # Format steps
        formatted_steps = []
        for step in steps:
            formatted_step = {
                "action": step.get("action", ""),
                "data": step.get("data", ""),
                "result": step.get("result", "")
            }
            formatted_steps.append(formatted_step)
        
        variables = {
            "jira": {"fields": jira_fields},
            "testType": {"name": "Manual"},
            "steps": formatted_steps
        }
        
        if folder_path:
            variables["folderPath"] = folder_path
        
        result = self.client.execute_query(query, variables)
        test_data = result.get('data', {}).get('createTest', {})
        
        if test_data.get('warnings'):
            self.logger.warning(f"Warnings for test {summary}: {test_data['warnings']}")
        
        return test_data
    
    def import_test_from_dict(self, test_data: Dict) -> Dict:
        """Import a test from dictionary data"""
        try:
            # Extract test information
            summary = test_data.get('summary', '')
            description = test_data.get('description', '')
            steps = test_data.get('steps', [])
            labels = test_data.get('labels', [])
            priority = test_data.get('priority', 'Medium')
            assignee = test_data.get('assignee')
            components = test_data.get('components', [])
            folder_path = test_data.get('folder_path')
            
            # Create the test
            result = self.create_manual_test(
                summary=summary,
                description=description,
                steps=steps,
                labels=labels,
                priority=priority,
                assignee=assignee,
                components=components,
                folder_path=folder_path
            )
            
            if result.get('test'):
                self.logger.info(f"Successfully created test: {result['test']['jira']['key']}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to import test {test_data.get('summary', 'Unknown')}: {e}")
            return {"error": str(e)}
    
    def batch_import_tests(self, tests: List[Dict], batch_size: int = 10) -> Dict[str, Dict]:
        """Import multiple tests in batches"""
        results = {}
        total_tests = len(tests)
        
        for i in range(0, total_tests, batch_size):
            batch = tests[i:i + batch_size]
            self.logger.info(f"Processing batch {i//batch_size + 1} ({i+1}-{min(i+batch_size, total_tests)} of {total_tests})")
            
            for test in batch:
                test_id = test.get('test_id', test.get('summary', f'test_{i}'))
                result = self.import_test_from_dict(test)
                results[test_id] = result
        
        return results
```

## Test Set Management

### Test Set Manager Class

```python
# test_set_manager.py
from typing import List, Dict
import logging

class TestSetManager:
    """Manages XRAY test set operations"""
    
    def __init__(self, client: XrayGraphQLClient, project_key: str):
        self.client = client
        self.project_key = project_key
        self.logger = logging.getLogger(__name__)
    
    def create_test_set(self, name: str, description: str, 
                       test_ids: Optional[List[str]] = None) -> Dict:
        """Create a test set"""
        query = """
        mutation CreateTestSet($jira: JSON!, $testIssueIds: [String]) {
            createTestSet(jira: $jira, testIssueIds: $testIssueIds) {
                testSet {
                    issueId
                    jira(fields: ["key", "summary"])
                }
                warnings
            }
        }
        """
        
        jira_fields = {
            "project": {"key": self.project_key},
            "summary": name,
            "description": description,
            "issuetype": {"name": "Test Set"}
        }
        
        variables = {
            "jira": {"fields": jira_fields}
        }
        
        if test_ids:
            variables["testIssueIds"] = test_ids
        
        result = self.client.execute_query(query, variables)
        return result.get('data', {}).get('createTestSet', {})
    
    def add_tests_to_set(self, test_set_id: str, test_ids: List[str]) -> Dict:
        """Add tests to existing test set"""
        query = """
        mutation AddTestsToSet($issueId: String!, $testIssueIds: [String!]!) {
            addTestsToTestSet(issueId: $issueId, testIssueIds: $testIssueIds) {
                addedTests
                warning
            }
        }
        """
        
        variables = {
            "issueId": test_set_id,
            "testIssueIds": test_ids
        }
        
        result = self.client.execute_query(query, variables)
        return result.get('data', {}).get('addTestsToTestSet', {})
    
    def create_sdui_test_sets(self, test_mapping: Dict[str, List[str]]) -> Dict:
        """Create all SDUI test sets based on strategy"""
        test_sets = {
            # Smoke Test Sets
            "SDUI-Smoke-Tests/Browse-Menu-Smoke": {
                "description": "Smoke test suite for Browse Menu - 15 critical tests",
                "tests": []  # To be populated from test_mapping
            },
            "SDUI-Smoke-Tests/Team-Page-Smoke": {
                "description": "Smoke test suite for Team Page - 12 critical tests",
                "tests": []
            },
            "SDUI-Smoke-Tests/Gameday-Smoke": {
                "description": "Smoke test suite for Gameday - 10 critical tests",
                "tests": []
            },
            "SDUI-Smoke-Tests/Scoreboard-Smoke": {
                "description": "Smoke test suite for Scoreboard - 13 critical tests",
                "tests": []
            },
            
            # Feature Complete Sets
            "Feature-Complete-Sets/Browse-Menu-Complete": {
                "description": "Complete test suite for Browse Menu - 101 tests",
                "tests": []
            },
            "Feature-Complete-Sets/Team-Page-Complete": {
                "description": "Complete test suite for Team Page - 89 tests",
                "tests": []
            },
            "Feature-Complete-Sets/Gameday-Complete": {
                "description": "Complete test suite for Gameday - 117 tests",
                "tests": []
            },
            "Feature-Complete-Sets/Scoreboard-Complete": {
                "description": "Complete test suite for Scoreboard - 102 tests",
                "tests": []
            },
            
            # Platform Sets
            "Platform-Sets/iOS-Only-Tests": {
                "description": "Tests specific to iOS platform",
                "tests": []
            },
            "Platform-Sets/Android-Only-Tests": {
                "description": "Tests specific to Android platform",
                "tests": []
            },
            "Platform-Sets/iPad-Specific-Tests": {
                "description": "Tests specific to iPad",
                "tests": []
            },
            
            # Jewel Event Sets
            "Jewel-Event-Sets/Opening-Day-Suite": {
                "description": "Test suite for Opening Day functionality - 15 tests",
                "tests": []
            },
            "Jewel-Event-Sets/All-Star-Week-Suite": {
                "description": "Test suite for All-Star Week - 12 tests",
                "tests": []
            },
            "Jewel-Event-Sets/Postseason-Suite": {
                "description": "Test suite for Postseason - 15 tests",
                "tests": []
            },
            
            # Game State Sets
            "Game-State-Sets/Preview-State-Suite": {
                "description": "Tests for preview game states - 10 tests",
                "tests": []
            },
            "Game-State-Sets/Live-State-Suite": {
                "description": "Tests for live game states - 15 tests",
                "tests": []
            }
        }
        
        # Populate test IDs from mapping
        for set_name, set_info in test_sets.items():
            if set_name in test_mapping:
                set_info["tests"] = test_mapping[set_name]
        
        # Create test sets
        results = {}
        for set_name, set_info in test_sets.items():
            try:
                self.logger.info(f"Creating test set: {set_name}")
                result = self.create_test_set(
                    name=set_name,
                    description=set_info["description"],
                    test_ids=set_info["tests"]
                )
                results[set_name] = result
            except Exception as e:
                self.logger.error(f"Failed to create test set {set_name}: {e}")
                results[set_name] = {"error": str(e)}
        
        return results
```

## Batch Operations

### Batch Processor

```python
# batch_processor.py
import pandas as pd
from typing import List, Dict
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

class BatchProcessor:
    """Handles batch operations for test import"""
    
    def __init__(self, client: XrayGraphQLClient):
        self.client = client
        self.logger = logging.getLogger(__name__)
    
    def load_tests_from_csv(self, file_path: str) -> List[Dict]:
        """Load test cases from CSV file"""
        df = pd.read_csv(file_path)
        
        tests = []
        for _, row in df.iterrows():
            # Parse steps if they're in separate columns
            steps = []
            step_num = 1
            while f'step_{step_num}_action' in df.columns:
                if pd.notna(row[f'step_{step_num}_action']):
                    steps.append({
                        'action': row[f'step_{step_num}_action'],
                        'data': row.get(f'step_{step_num}_data', ''),
                        'result': row.get(f'step_{step_num}_result', '')
                    })
                step_num += 1
            
            # Parse labels
            labels = []
            if 'labels' in row and pd.notna(row['labels']):
                labels = [label.strip() for label in row['labels'].split(',')]
            
            # Parse components
            components = []
            if 'components' in row and pd.notna(row['components']):
                components = [comp.strip() for comp in row['components'].split(',')]
            
            test = {
                'test_id': row.get('test_id', ''),
                'summary': row.get('summary', ''),
                'description': row.get('description', ''),
                'steps': steps,
                'labels': labels,
                'priority': row.get('priority', 'Medium'),
                'assignee': row.get('assignee'),
                'components': components,
                'folder_path': row.get('folder_path')
            }
            
            tests.append(test)
        
        return tests
    
    def parallel_import(self, operations: List[Dict], max_workers: int = 5) -> Dict:
        """Execute operations in parallel"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all operations
            future_to_operation = {
                executor.submit(self._execute_operation, op): op 
                for op in operations
            }
            
            # Process completed operations
            for future in as_completed(future_to_operation):
                operation = future_to_operation[future]
                try:
                    result = future.result()
                    results[operation['id']] = result
                except Exception as e:
                    self.logger.error(f"Operation {operation['id']} failed: {e}")
                    results[operation['id']] = {"error": str(e)}
        
        return results
    
    def _execute_operation(self, operation: Dict) -> Dict:
        """Execute a single operation"""
        op_type = operation.get('type')
        
        if op_type == 'create_folder':
            return self._create_folder(operation)
        elif op_type == 'create_test':
            return self._create_test(operation)
        elif op_type == 'create_test_set':
            return self._create_test_set(operation)
        else:
            raise ValueError(f"Unknown operation type: {op_type}")
```

## Error Handling and Logging

### Error Handler

```python
# error_handler.py
import logging
import json
from datetime import datetime
from typing import Dict, List

class ErrorHandler:
    """Centralized error handling and logging"""
    
    def __init__(self, log_file: str = "sdui_import_errors.log"):
        self.log_file = log_file
        self.errors = []
        self.logger = logging.getLogger(__name__)
    
    def log_error(self, operation: str, error: Exception, context: Dict = None):
        """Log error with context"""
        error_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "error": str(error),
            "error_type": type(error).__name__,
            "context": context or {}
        }
        
        self.errors.append(error_entry)
        self.logger.error(f"{operation} failed: {error}", extra={"context": context})
        
        # Write to error log file
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(error_entry) + '\n')
    
    def get_error_summary(self) -> Dict:
        """Get summary of all errors"""
        summary = {
            "total_errors": len(self.errors),
            "errors_by_type": {},
            "errors_by_operation": {}
        }
        
        for error in self.errors:
            # Count by error type
            error_type = error["error_type"]
            summary["errors_by_type"][error_type] = \
                summary["errors_by_type"].get(error_type, 0) + 1
            
            # Count by operation
            operation = error["operation"]
            summary["errors_by_operation"][operation] = \
                summary["errors_by_operation"].get(operation, 0) + 1
        
        return summary
    
    def generate_retry_file(self, output_file: str = "retry_operations.json"):
        """Generate file with failed operations for retry"""
        retry_operations = []
        
        for error in self.errors:
            if error["context"].get("retryable", True):
                retry_operations.append({
                    "operation": error["operation"],
                    "context": error["context"],
                    "original_error": error["error"]
                })
        
        with open(output_file, 'w') as f:
            json.dump(retry_operations, f, indent=2)
        
        self.logger.info(f"Generated retry file with {len(retry_operations)} operations")
```

## Complete Working Example

### Main Import Script

```python
# import_sdui_tests.py
import logging
import json
from datetime import datetime
import argparse
from pathlib import Path

# Import our modules
from xray_client import XrayGraphQLClient
from folder_manager import FolderManager
from test_manager import TestManager
from test_set_manager import TestSetManager
from batch_processor import BatchProcessor
from error_handler import ErrorHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sdui_import.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class SDUITestImporter:
    """Main class for importing SDUI tests"""
    
    def __init__(self):
        self.client = XrayGraphQLClient()
        self.error_handler = ErrorHandler()
        self.project_key = os.getenv('JIRA_PROJECT_KEY')
        self.project_id = os.getenv('JIRA_PROJECT_ID')
        
        # Initialize managers
        self.folder_manager = FolderManager(self.client, self.project_id)
        self.test_manager = TestManager(self.client, self.project_key)
        self.test_set_manager = TestSetManager(self.client, self.project_key)
        self.batch_processor = BatchProcessor(self.client)
        
        self.results = {
            "folders": {},
            "tests": {},
            "test_sets": {}
        }
    
    def setup_folder_structure(self):
        """Create complete folder structure"""
        logger.info("Setting up SDUI folder structure...")
        try:
            folder_results = self.folder_manager.setup_sdui_folders()
            self.results["folders"] = folder_results
            
            # Count successful folders
            successful = sum(1 for r in folder_results.values() if 'error' not in r)
            logger.info(f"Created {successful} folders successfully")
            
        except Exception as e:
            self.error_handler.log_error("setup_folders", e)
            raise
    
    def import_tests_from_file(self, file_path: str):
        """Import tests from CSV or JSON file"""
        logger.info(f"Importing tests from {file_path}...")
        
        try:
            if file_path.endswith('.csv'):
                tests = self.batch_processor.load_tests_from_csv(file_path)
            elif file_path.endswith('.json'):
                with open(file_path, 'r') as f:
                    tests = json.load(f)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
            
            logger.info(f"Loaded {len(tests)} tests from file")
            
            # Import tests in batches
            test_results = self.test_manager.batch_import_tests(tests, batch_size=10)
            self.results["tests"] = test_results
            
            # Count successful imports
            successful = sum(1 for r in test_results.values() if 'error' not in r)
            logger.info(f"Imported {successful}/{len(tests)} tests successfully")
            
        except Exception as e:
            self.error_handler.log_error("import_tests", e, {"file": file_path})
            raise
    
    def create_test_sets(self, test_mapping_file: str = None):
        """Create test sets based on imported tests"""
        logger.info("Creating test sets...")
        
        try:
            # Load test mapping if provided
            test_mapping = {}
            if test_mapping_file and Path(test_mapping_file).exists():
                with open(test_mapping_file, 'r') as f:
                    test_mapping = json.load(f)
            else:
                # Build mapping from imported tests based on labels
                test_mapping = self._build_test_mapping_from_results()
            
            # Create test sets
            test_set_results = self.test_set_manager.create_sdui_test_sets(test_mapping)
            self.results["test_sets"] = test_set_results
            
            # Count successful test sets
            successful = sum(1 for r in test_set_results.values() if 'error' not in r)
            logger.info(f"Created {successful} test sets successfully")
            
        except Exception as e:
            self.error_handler.log_error("create_test_sets", e)
            raise
    
    def _build_test_mapping_from_results(self) -> Dict[str, List[str]]:
        """Build test set mapping from imported test results"""
        mapping = {
            "SDUI-Smoke-Tests/Browse-Menu-Smoke": [],
            "SDUI-Smoke-Tests/Team-Page-Smoke": [],
            "SDUI-Smoke-Tests/Gameday-Smoke": [],
            "SDUI-Smoke-Tests/Scoreboard-Smoke": [],
            "Platform-Sets/iOS-Only-Tests": [],
            "Platform-Sets/Android-Only-Tests": [],
            "Jewel-Event-Sets/Opening-Day-Suite": [],
            "Game-State-Sets/Live-State-Suite": []
        }
        
        # Analyze imported tests
        for test_id, result in self.results["tests"].items():
            if "error" not in result and result.get("test"):
                test = result["test"]
                labels = test.get("jira", {}).get("labels", [])
                issue_key = test.get("jira", {}).get("key")
                
                if not issue_key:
                    continue
                
                # Smoke tests
                if "@smoke" in labels:
                    if "@browse-menu" in labels:
                        mapping["SDUI-Smoke-Tests/Browse-Menu-Smoke"].append(issue_key)
                    elif "@team-page" in labels:
                        mapping["SDUI-Smoke-Tests/Team-Page-Smoke"].append(issue_key)
                    elif "@gameday" in labels:
                        mapping["SDUI-Smoke-Tests/Gameday-Smoke"].append(issue_key)
                    elif "@scoreboard" in labels:
                        mapping["SDUI-Smoke-Tests/Scoreboard-Smoke"].append(issue_key)
                
                # Platform-specific
                if "@ios" in labels and "@android" not in labels:
                    mapping["Platform-Sets/iOS-Only-Tests"].append(issue_key)
                elif "@android" in labels and "@ios" not in labels:
                    mapping["Platform-Sets/Android-Only-Tests"].append(issue_key)
                
                # Jewel events
                if "@opening-day" in labels:
                    mapping["Jewel-Event-Sets/Opening-Day-Suite"].append(issue_key)
                
                # Game states
                if "@live-state" in labels:
                    mapping["Game-State-Sets/Live-State-Suite"].append(issue_key)
        
        return mapping
    
    def generate_report(self, output_file: str = "import_report.json"):
        """Generate comprehensive import report"""
        report = {
            "import_date": datetime.utcnow().isoformat(),
            "summary": {
                "folders": {
                    "total": len(self.results["folders"]),
                    "successful": sum(1 for r in self.results["folders"].values() if 'error' not in r),
                    "failed": sum(1 for r in self.results["folders"].values() if 'error' in r)
                },
                "tests": {
                    "total": len(self.results["tests"]),
                    "successful": sum(1 for r in self.results["tests"].values() if 'error' not in r),
                    "failed": sum(1 for r in self.results["tests"].values() if 'error' in r)
                },
                "test_sets": {
                    "total": len(self.results["test_sets"]),
                    "successful": sum(1 for r in self.results["test_sets"].values() if 'error' not in r),
                    "failed": sum(1 for r in self.results["test_sets"].values() if 'error' in r)
                }
            },
            "errors": self.error_handler.get_error_summary(),
            "details": self.results
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Import report generated: {output_file}")
        
        # Generate retry file if there were errors
        if report["errors"]["total_errors"] > 0:
            self.error_handler.generate_retry_file()
    
    def run_full_import(self, test_file: str):
        """Run complete import process"""
        logger.info("Starting SDUI test import process...")
        
        try:
            # Step 1: Create folder structure
            self.setup_folder_structure()
            
            # Step 2: Import tests
            self.import_tests_from_file(test_file)
            
            # Step 3: Create test sets
            self.create_test_sets()
            
            # Step 4: Generate report
            self.generate_report()
            
            logger.info("Import process completed successfully!")
            
        except Exception as e:
            logger.error(f"Import process failed: {e}")
            self.generate_report("import_report_failed.json")
            raise

def main():
    parser = argparse.ArgumentParser(description='Import SDUI tests to XRAY')
    parser.add_argument('test_file', help='Path to test file (CSV or JSON)')
    parser.add_argument('--folders-only', action='store_true', 
                       help='Only create folder structure')
    parser.add_argument('--tests-only', action='store_true',
                       help='Only import tests (assumes folders exist)')
    parser.add_argument('--test-sets-only', action='store_true',
                       help='Only create test sets (assumes tests exist)')
    parser.add_argument('--mapping-file', help='Test set mapping JSON file')
    
    args = parser.parse_args()
    
    importer = SDUITestImporter()
    
    try:
        if args.folders_only:
            importer.setup_folder_structure()
        elif args.tests_only:
            importer.import_tests_from_file(args.test_file)
        elif args.test_sets_only:
            importer.create_test_sets(args.mapping_file)
        else:
            importer.run_full_import(args.test_file)
        
        importer.generate_report()
        
    except Exception as e:
        logger.error(f"Import failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()
```

## Usage Examples

### 1. Full Import
```bash
python import_sdui_tests.py tests.csv
```

### 2. Create Folders Only
```bash
python import_sdui_tests.py tests.csv --folders-only
```

### 3. Import Tests Only
```bash
python import_sdui_tests.py tests.csv --tests-only
```

### 4. Create Test Sets with Mapping
```bash
python import_sdui_tests.py tests.csv --test-sets-only --mapping-file test_mapping.json
```

### 5. Retry Failed Operations
```bash
python retry_operations.py retry_operations.json
```

## Test Data Format

### CSV Format
```csv
test_id,summary,description,priority,labels,components,folder_path,step_1_action,step_1_data,step_1_result
TC-001,Team Selection via Drawer,Verify team selection functionality,High,"@team-page,@functional,@smoke",Team Page,/Team Page/Core Navigation,Navigate to Team Page,App is open,Team Page is displayed
```

### JSON Format
```json
[
  {
    "test_id": "TC-001",
    "summary": "Team Selection via Drawer",
    "description": "Verify team selection functionality works correctly",
    "priority": "High",
    "labels": ["@team-page", "@functional", "@smoke"],
    "components": ["Team Page"],
    "folder_path": "/Team Page/Core Navigation",
    "steps": [
      {
        "action": "Navigate to Team Page",
        "data": "App is open",
        "result": "Team Page is displayed"
      }
    ]
  }
]
```

This implementation provides a complete, production-ready solution for importing SDUI tests into XRAY using the GraphQL API.