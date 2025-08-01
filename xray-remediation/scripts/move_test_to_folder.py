#!/usr/bin/env python3
"""
Move a test to a specific folder in the Test Repository using GraphQL API.
This script tests moving FRAMED-1294 to /Team Page/API Tests/Error Handling
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "xray-api"))
from auth_utils import XrayAPIClient

class TestFolderMover:
    """Move tests to specific folders in Test Repository"""
    
    def __init__(self):
        self.client = XrayAPIClient()
        self.project_id = None
        
    def authenticate(self):
        """Authenticate with Xray API"""
        try:
            token = self.client.get_auth_token()
            print("✓ Authentication successful")
            return True
        except Exception as e:
            print(f"✗ Authentication failed: {e}")
            return False
    
    def get_project_info(self):
        """Get FRAMED project ID from a test"""
        query = """
        query GetProjectFromTest($jql: String!) {
            getTests(jql: $jql, limit: 1) {
                results {
                    projectId
                    jira(fields: ["key", "project"])
                }
            }
        }
        """
        
        try:
            result = self.client.execute_graphql_query(query, {
                "jql": "project = FRAMED"
            })
            
            if result['getTests']['results']:
                test = result['getTests']['results'][0]
                self.project_id = test['projectId']
                project_key = test['jira']['project']['key']
                print(f"✓ Found project {project_key} with ID: {self.project_id}")
                return True
            else:
                print("✗ No tests found in project FRAMED")
                return False
                
        except Exception as e:
            print(f"✗ Error getting project info: {e}")
            return False
    
    def create_folder_structure(self, path):
        """Create the folder structure if it doesn't exist"""
        # Split path into components
        parts = [p for p in path.split('/') if p]
        
        # Create each level of the hierarchy
        current_path = ""
        for part in parts:
            current_path += f"/{part}"
            
            mutation = """
            mutation CreateFolder($projectId: String!, $path: String!) {
                createFolder(projectId: $projectId, path: $path) {
                    folder {
                        name
                        path
                    }
                    warnings
                }
            }
            """
            
            try:
                print(f"Creating folder: {current_path}")
                result = self.client.execute_graphql_query(mutation, {
                    "projectId": self.project_id,
                    "path": current_path
                })
                
                if result.get('createFolder'):
                    folder = result['createFolder'].get('folder', {})
                    warnings = result['createFolder'].get('warnings', [])
                    
                    if folder:
                        print(f"  ✓ Folder exists/created: {folder.get('path')}")
                    
                    if warnings:
                        for warning in warnings:
                            print(f"  ⚠ Warning: {warning}")
                            
            except Exception as e:
                # Folder might already exist, which is fine
                print(f"  ℹ {current_path}: {str(e)}")
    
    def move_test_to_folder(self, test_key, folder_path):
        """Move a test to the specified folder"""
        # First ensure the folder structure exists
        self.create_folder_structure(folder_path)
        
        # Get test issue ID from key
        test_id = self.get_test_id(test_key)
        if not test_id:
            print(f"✗ Could not find test {test_key}")
            return False
        
        # Add test to the target folder
        mutation = """
        mutation AddTestToFolder($projectId: String!, $path: String!, $testIssueIds: [String]!) {
            addTestsToFolder(projectId: $projectId, path: $path, testIssueIds: $testIssueIds) {
                folder {
                    name
                    path
                    testsCount
                }
                warnings
            }
        }
        """
        
        try:
            print(f"\nMoving {test_key} to {folder_path}...")
            result = self.client.execute_graphql_query(mutation, {
                "projectId": self.project_id,
                "path": folder_path,
                "testIssueIds": [test_id]
            })
            
            if result.get('addTestsToFolder'):
                folder = result['addTestsToFolder'].get('folder', {})
                warnings = result['addTestsToFolder'].get('warnings', [])
                
                if folder:
                    print(f"✓ Test added to folder: {folder.get('path')}")
                    print(f"  Total tests in folder: {folder.get('testsCount')}")
                    
                if warnings:
                    for warning in warnings:
                        print(f"  ⚠ Warning: {warning}")
                        
                return True
                
        except Exception as e:
            print(f"✗ Error moving test: {e}")
            return False
    
    def get_test_id(self, test_key):
        """Get test issue ID from key"""
        query = """
        query GetTest($jql: String!) {
            getTests(jql: $jql, limit: 1) {
                results {
                    issueId
                    jira(fields: ["key"])
                }
            }
        }
        """
        
        try:
            result = self.client.execute_graphql_query(query, {
                "jql": f"key = {test_key}"
            })
            
            if result['getTests']['results']:
                return result['getTests']['results'][0]['issueId']
            return None
            
        except Exception as e:
            print(f"✗ Error getting test ID: {e}")
            return None
    
    def verify_test_location(self, test_key):
        """Verify the test's current folder location"""
        query = """
        query GetTestLocation($jql: String!) {
            getTests(jql: $jql, limit: 1) {
                results {
                    issueId
                    jira(fields: ["key", "summary"])
                    folder {
                        name
                        path
                    }
                }
            }
        }
        """
        
        try:
            result = self.client.execute_graphql_query(query, {
                "jql": f"key = {test_key}"
            })
            
            if result['getTests']['results']:
                test = result['getTests']['results'][0]
                folder = test.get('folder', {})
                
                print(f"\nTest {test_key}:")
                print(f"  Summary: {test['jira'].get('summary')}")
                print(f"  Current folder: {folder.get('path', 'Root (no folder)')}")
                
                return True
                
        except Exception as e:
            print(f"✗ Error verifying test location: {e}")
            return False
    
    def run(self):
        """Execute the test move operation"""
        if not self.authenticate():
            return False
        
        if not self.get_project_info():
            return False
        
        # Test case details
        test_key = "FRAMED-1294"
        target_folder = "/Team Page/API Tests/Error Handling"
        
        print("\n" + "="*60)
        print(f"Moving {test_key} to {target_folder}")
        print("="*60)
        
        # Check current location
        print("\nChecking current location...")
        self.verify_test_location(test_key)
        
        # Move the test
        success = self.move_test_to_folder(test_key, target_folder)
        
        if success:
            # Verify new location
            print("\nVerifying new location...")
            self.verify_test_location(test_key)
            print("\n✓ Test move completed successfully!")
        else:
            print("\n✗ Test move failed!")
        
        return success

def main():
    """Main entry point"""
    mover = TestFolderMover()
    mover.run()

if __name__ == "__main__":
    main()