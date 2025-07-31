#!/usr/bin/env python3
"""
Upload SDUI Team Page test cases to XRAY using GraphQL API.
Implements folder creation, test import, and test set management.
"""
import json
import os
import time
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv


class XrayAPIUploader:
    """Handle XRAY GraphQL API operations for test upload."""
    
    def __init__(self):
        # Load .env from root directory
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env_path = os.path.join(root_dir, '.env')
        load_dotenv(env_path)
        
        self.client_id = os.getenv('XRAY_CLIENT')
        self.client_secret = os.getenv('XRAY_SECRET')
        self.project_key = os.getenv('JIRA_PROJECT_KEY', 'FRAMED')
        self.project_id = os.getenv('JIRA_PROJECT_ID', '10000')
        
        # API endpoints
        self.auth_url = "https://xray.cloud.getxray.app/api/v2/authenticate"
        self.graphql_url = "https://xray.cloud.getxray.app/api/v2/graphql"
        
        self.access_token = None
        self.folder_cache = {}
        self.test_cache = {}
        
    def authenticate(self):
        """Authenticate with XRAY API and get access token."""
        print("Authenticating with XRAY API...")
        
        auth_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        try:
            response = requests.post(self.auth_url, json=auth_data)
            response.raise_for_status()
            self.access_token = response.text.strip('"')
            print("Authentication successful!")
            return True
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False
    
    def execute_graphql(self, query: str, variables: Dict = None) -> Dict:
        """Execute a GraphQL query/mutation."""
        if not self.access_token:
            self.authenticate()
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "variables": variables or {}
        }
        
        response = requests.post(self.graphql_url, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        if "errors" in result:
            raise Exception(f"GraphQL errors: {result['errors']}")
        
        return result.get("data", {})
    
    def create_folder(self, name: str, parent_id: str = None) -> str:
        """Create a folder in the test repository."""
        print(f"Creating folder: {name}")
        
        mutation = """
        mutation CreateFolder($projectId: String!, $name: String!, $parentId: String) {
            createFolder(projectId: $projectId, name: $name, parentId: $parentId) {
                folder {
                    id
                    name
                    path
                }
                warnings
            }
        }
        """
        
        variables = {
            "projectId": self.project_id,
            "name": name,
            "parentId": parent_id
        }
        
        try:
            result = self.execute_graphql(mutation, variables)
            folder_data = result.get("createFolder", {}).get("folder", {})
            folder_id = folder_data.get("id")
            
            if folder_id:
                self.folder_cache[name] = folder_id
                print(f"Created folder: {name} (ID: {folder_id})")
                return folder_id
            else:
                print(f"Failed to create folder: {name}")
                return None
        except Exception as e:
            print(f"Error creating folder {name}: {e}")
            return None
    
    def setup_folder_structure(self, folders: Dict[str, List[str]]):
        """Create the complete folder structure."""
        print("\nSetting up folder structure...")
        
        # Create root folder first
        root_name = "Team Page"
        root_id = self.create_folder(root_name)
        
        if root_id and root_name in folders:
            # Create subfolders
            for subfolder in folders[root_name]:
                self.create_folder(subfolder, root_id)
                time.sleep(0.5)  # Rate limiting
    
    def create_test(self, test_data: Dict) -> Optional[str]:
        """Create a single test in XRAY."""
        mutation = """
        mutation CreateTest(
            $projectKey: String!,
            $testType: String!,
            $summary: String!,
            $description: String,
            $priority: String,
            $labels: [String],
            $steps: [CreateStepInput]
        ) {
            createTest(
                projectKey: $projectKey,
                testType: $testType,
                fields: {
                    summary: $summary,
                    description: $description,
                    priority: { name: $priority }
                },
                labels: $labels,
                steps: $steps
            ) {
                test {
                    issueId
                    key
                    summary
                }
                warnings
            }
        }
        """
        
        # Prepare steps for GraphQL
        steps = []
        for step in test_data.get("steps", []):
            steps.append({
                "action": step.get("action", ""),
                "expectedResult": step.get("expectedResult", "")
            })
        
        variables = {
            "projectKey": self.project_key,
            "testType": test_data.get("testType", "Manual"),
            "summary": test_data.get("summary", ""),
            "description": test_data.get("description", ""),
            "priority": test_data.get("priority", "Medium"),
            "labels": test_data.get("labels", []),
            "steps": steps
        }
        
        try:
            result = self.execute_graphql(mutation, variables)
            test_info = result.get("createTest", {}).get("test", {})
            
            if test_info:
                test_key = test_info.get("key")
                test_id = test_info.get("issueId")
                print(f"Created test: {test_key} - {test_info.get('summary')}")
                self.test_cache[test_data.get("originalId")] = {
                    "key": test_key,
                    "id": test_id,
                    "folder": test_data.get("folder")
                }
                return test_key
            else:
                print(f"Failed to create test: {test_data.get('summary')}")
                return None
                
        except Exception as e:
            print(f"Error creating test: {e}")
            return None
    
    def add_test_to_folder(self, test_id: str, folder_path: str):
        """Add a test to a specific folder."""
        mutation = """
        mutation AddTestsToFolder($folderId: String!, $testIds: [String]!) {
            addTestsToFolder(folderId: $folderId, testIds: $testIds) {
                folder {
                    id
                    name
                }
                warnings
            }
        }
        """
        
        # Get folder ID from path
        folder_name = folder_path.split("/")[-1]
        folder_id = self.folder_cache.get(folder_name)
        
        if not folder_id:
            print(f"Folder not found: {folder_name}")
            return False
        
        variables = {
            "folderId": folder_id,
            "testIds": [test_id]
        }
        
        try:
            result = self.execute_graphql(mutation, variables)
            return True
        except Exception as e:
            print(f"Error adding test to folder: {e}")
            return False
    
    def create_test_set(self, name: str, test_keys: List[str]) -> Optional[str]:
        """Create a test set with specified tests."""
        print(f"\nCreating test set: {name}")
        
        mutation = """
        mutation CreateTestSet($projectKey: String!, $summary: String!, $tests: [String]) {
            createTestSet(
                projectKey: $projectKey,
                fields: { summary: $summary },
                tests: $tests
            ) {
                testSet {
                    key
                    summary
                }
                warnings
            }
        }
        """
        
        variables = {
            "projectKey": self.project_key,
            "summary": name,
            "tests": test_keys
        }
        
        try:
            result = self.execute_graphql(mutation, variables)
            test_set = result.get("createTestSet", {}).get("testSet", {})
            
            if test_set:
                print(f"Created test set: {test_set.get('key')} - {name}")
                return test_set.get("key")
            else:
                print(f"Failed to create test set: {name}")
                return None
                
        except Exception as e:
            print(f"Error creating test set: {e}")
            return None
    
    def upload_tests(self, transformed_data: Dict):
        """Upload all tests from transformed data."""
        tests = transformed_data.get("tests", [])
        folders = transformed_data.get("folders", {})
        
        # Setup folders first
        self.setup_folder_structure(folders)
        
        # Upload tests in batches
        print(f"\nUploading {len(tests)} tests...")
        successful_uploads = []
        failed_uploads = []
        
        for i, test in enumerate(tests):
            print(f"\nProcessing test {i+1}/{len(tests)}")
            
            # Create test
            test_key = self.create_test(test)
            
            if test_key:
                successful_uploads.append(test_key)
                
                # Add to folder
                test_info = self.test_cache.get(test.get("originalId"), {})
                if test_info and test.get("folder"):
                    self.add_test_to_folder(test_info["id"], test.get("folder"))
            else:
                failed_uploads.append(test.get("summary"))
            
            # Rate limiting
            time.sleep(1)
        
        print(f"\n\nUpload Summary:")
        print(f"- Successful: {len(successful_uploads)} tests")
        print(f"- Failed: {len(failed_uploads)} tests")
        
        return successful_uploads, failed_uploads
    
    def create_standard_test_sets(self, test_keys: List[str]):
        """Create standard test sets as defined in strategy."""
        print("\nCreating test sets...")
        
        test_sets = {
            "Team Page - Full Regression": test_keys,  # All tests
            "Team Page - Smoke Tests": test_keys[:10],  # First 10 critical tests
            "Team Page - Game States": [k for k, v in self.test_cache.items() 
                                      if "Game States" in v.get("folder", "")],
            "Team Page - Jewel Events": [k for k, v in self.test_cache.items() 
                                       if "Jewel Events" in v.get("folder", "")]
        }
        
        for set_name, keys in test_sets.items():
            if keys:
                self.create_test_set(set_name, keys)
                time.sleep(1)  # Rate limiting
    
    def save_upload_report(self, successful: List[str], failed: List[str]):
        """Save upload report for reference."""
        report = {
            "uploadDate": datetime.now().isoformat(),
            "projectKey": self.project_key,
            "successfulUploads": successful,
            "failedUploads": failed,
            "testMapping": self.test_cache,
            "folderMapping": self.folder_cache
        }
        
        report_file = "/Users/douglas.mason/Documents/GitHub/xray-importer/xray-upload/upload_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nUpload report saved to: {report_file}")


def main():
    """Main execution function."""
    # Create uploader instance (will load .env from root)
    uploader = XrayAPIUploader()
    
    # Check environment variables
    if not uploader.client_id or not uploader.client_secret:
        print("ERROR: XRAY_CLIENT and XRAY_SECRET environment variables must be set!")
        print("Please ensure the .env file in the root directory contains:")
        print("XRAY_CLIENT=your_client_id")
        print("XRAY_SECRET=your_client_secret")
        return
    
    # Load transformed tests
    input_file = "/Users/douglas.mason/Documents/GitHub/xray-importer/xray-upload/transformed_tests.json"
    
    with open(input_file, 'r') as f:
        transformed_data = json.load(f)
    
    # Authenticate
    if not uploader.authenticate():
        print("Authentication failed. Check your credentials.")
        return
    
    # Upload tests
    successful, failed = uploader.upload_tests(transformed_data)
    
    # Create test sets
    if successful:
        uploader.create_standard_test_sets(successful)
    
    # Save report
    uploader.save_upload_report(successful, failed)
    
    print("\nUpload process complete!")


if __name__ == "__main__":
    main()