#!/usr/bin/env python3
"""
Organize tests into proper folder structure in FRAMED project.
Maps tests to folders based on JSON truth files.
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

sys.path.insert(0, str(Path(__file__).parent.parent / "xray-api"))
from auth_utils import XrayAPIClient

class TestFolderOrganizer:
    """Organize tests into folder structure"""
    
    def __init__(self):
        self.client = XrayAPIClient()
        self.token = None
        self.organized_count = 0
        self.error_count = 0
        self.results = []
        self.folder_mapping = {}
        
    def authenticate(self):
        """Authenticate with Xray API"""
        try:
            self.token = self.client.get_auth_token()
            print("✓ Authentication successful")
            return True
        except Exception as e:
            print(f"✗ Authentication failed: {e}")
            return False
    
    def load_folder_mappings(self):
        """Load folder mappings from JSON truth files"""
        api_json = Path(__file__).parent.parent / "test-data" / "api_tests_xray.json"
        func_json = Path(__file__).parent.parent / "test-data" / "functional_tests_xray.json"
        
        # Load API test mappings
        if api_json.exists():
            with open(api_json) as f:
                api_data = json.load(f)
            
            for test in api_data.get('tests', []):
                test_id = test.get('testId', '')
                # Determine folder based on test ID patterns
                if 'REG' in test_id:
                    folder = "/Team Page/API Tests/Regression Tests"
                elif 'INT' in test_id:
                    folder = "/Team Page/API Tests/Integration Tests"
                elif 'PERF' in test_id:
                    folder = "/Team Page/API Tests/Performance Tests"
                elif 'JE' in test_id:
                    folder = "/Team Page/API Tests/Jewel Events"
                elif 'GS' in test_id:
                    folder = "/Team Page/API Tests/Game States"
                elif 'DATA' in test_id:
                    folder = "/Team Page/API Tests/Data Validation"
                elif 'SEC' in test_id:
                    folder = "/Team Page/API Tests/Security Tests"
                elif 'ERR' in test_id:
                    folder = "/Team Page/API Tests/Error Handling"
                else:
                    folder = "/Team Page/API Tests/Core Endpoints"
                
                self.folder_mapping[test_id] = folder
        
        # Load functional test mappings
        if func_json.exists():
            with open(func_json) as f:
                func_data = json.load(f)
            
            for test in func_data.get('tests', []):
                test_info = test.get('testInfo', {})
                test_id = test.get('testId', '')
                
                # Extract folder from description or use default
                desc = test_info.get('description', '')
                if 'Folder:' in desc:
                    folder_part = desc.split('Folder:')[1].split('\n')[0].strip()
                    folder = f"/{folder_part}"
                else:
                    folder = "/Team Page/Functional Tests/General"
                
                self.folder_mapping[test_id] = folder
        
        print(f"Loaded {len(self.folder_mapping)} folder mappings")
    
    def get_current_tests(self, project_key="FRAMED"):
        """Get all tests from project"""
        query = """
        query GetTests($jql: String!, $limit: Int!) {
            getTests(jql: $jql, limit: $limit) {
                total
                results {
                    issueId
                    jira(fields: ["key", "summary", "labels"])
                    folder {
                        path
                    }
                }
            }
        }
        """
        
        variables = {
            "jql": f"project = {project_key}",
            "limit": 100
        }
        
        try:
            response = self.client.execute_graphql_query(query, variables)
            if response:
                return response['getTests']['results']
            return []
        except Exception as e:
            print(f"Error fetching tests: {e}")
            return []
    
    def create_folder_structure(self, project_key="FRAMED"):
        """Create folder structure in Xray"""
        folders_to_create = set(self.folder_mapping.values())
        created_folders = {}
        
        print("\n2. Creating folder structure...")
        
        for folder_path in sorted(folders_to_create):
            # Build folder hierarchy
            parts = folder_path.strip('/').split('/')
            current_path = ""
            parent_id = None
            
            for part in parts:
                current_path = f"{current_path}/{part}"
                
                if current_path not in created_folders:
                    # Create folder
                    mutation = """
                    mutation CreateFolder($projectKey: String!, $name: String!, $parentId: String) {
                        createFolder(projectKey: $projectKey, name: $name, parentId: $parentId, testRepositoryPath: "") {
                            folder {
                                id
                                name
                                path
                            }
                        }
                    }
                    """
                    
                    variables = {
                        "projectKey": project_key,
                        "name": part,
                        "parentId": parent_id
                    }
                    
                    try:
                        response = self.client.execute_graphql_query(mutation, variables)
                        if response:
                            folder_data = response['createTestFolder']['folder']
                            created_folders[current_path] = folder_data['id']
                            print(f"   ✓ Created folder: {current_path}")
                        else:
                            print(f"   ✗ Failed to create folder: {current_path}")
                    except Exception as e:
                        print(f"   ✗ Error creating folder {current_path}: {e}")
                    
                    time.sleep(0.2)  # Rate limiting
                
                parent_id = created_folders.get(current_path)
        
        return created_folders
    
    def move_test_to_folder(self, test_id, test_key, folder_id):
        """Move test to specified folder"""
        mutation = """
        mutation MoveTest($testId: String!, $folderId: String!) {
            moveTestToFolder(testId: $testId, folderId: $folderId) {
                test {
                    issueId
                    folder
                }
            }
        }
        """
        
        variables = {
            "testId": test_id,
            "folderId": folder_id
        }
        
        try:
            response = self.client.execute_graphql_query(mutation, variables)
            if response:
                return True
            return False
        except Exception as e:
            print(f"Error moving {test_key}: {e}")
            return False
    
    def organize_tests(self, dry_run=False):
        """Main process to organize tests"""
        print("\n" + "="*80)
        print("XRAY TEST FOLDER ORGANIZATION")
        print("="*80)
        
        # Load mappings
        print("\n1. Loading folder mappings from JSON files...")
        self.load_folder_mappings()
        
        # Get current tests
        print("\n2. Fetching tests from FRAMED project...")
        tests = self.get_current_tests()
        print(f"   Found {len(tests)} tests")
        
        if not tests:
            print("   No tests found or error occurred")
            return
        
        # Create folder structure (if not dry run)
        folder_ids = {}
        if not dry_run:
            folder_ids = self.create_folder_structure()
        
        # Analyze which tests need to be moved
        print("\n3. Analyzing test organization...")
        tests_to_move = []
        
        for test in tests:
            test_key = test['jira']['key']
            test_labels = test['jira'].get('labels', [])
            current_folder = test.get('folder', {}).get('path', '') if test.get('folder') else ''
            
            # Find test ID from labels
            test_id = None
            for label in test_labels:
                if label in self.folder_mapping:
                    test_id = label
                    break
            
            if test_id and self.folder_mapping.get(test_id):
                target_folder = self.folder_mapping[test_id]
                if current_folder != target_folder:
                    tests_to_move.append({
                        'issueId': test['issueId'],
                        'key': test_key,
                        'summary': test['jira']['summary'],
                        'current_folder': current_folder or '(root)',
                        'target_folder': target_folder,
                        'folder_id': folder_ids.get(target_folder)
                    })
        
        print(f"   Found {len(tests_to_move)} tests to organize")
        
        if not tests_to_move:
            print("   All tests are already properly organized")
            return
        
        # Show what will be changed
        print("\n4. Tests to be moved:")
        for test in tests_to_move[:5]:  # Show first 5 as examples
            print(f"\n   {test['key']}: {test['summary'][:50]}...")
            print(f"   From: {test['current_folder']}")
            print(f"   To: {test['target_folder']}")
        
        if len(tests_to_move) > 5:
            print(f"\n   ... and {len(tests_to_move) - 5} more tests")
        
        # Confirm or execute
        if dry_run:
            print("\n5. DRY RUN - No changes made")
            return
        
        print("\n5. Moving tests to folders...")
        confirm = input("   Proceed with folder organization? (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("   Operation cancelled")
            return
        
        # Move tests
        for i, test in enumerate(tests_to_move, 1):
            print(f"\n   [{i}/{len(tests_to_move)}] Moving {test['key']}...")
            
            if test['folder_id']:
                success = self.move_test_to_folder(
                    test['issueId'],
                    test['key'],
                    test['folder_id']
                )
                
                if success:
                    self.organized_count += 1
                    self.results.append({
                        'key': test['key'],
                        'status': 'success',
                        'moved_to': test['target_folder']
                    })
                    print(f"   ✓ Moved to: {test['target_folder']}")
                else:
                    self.error_count += 1
                    self.results.append({
                        'key': test['key'],
                        'status': 'error',
                        'moved_to': None
                    })
                    print(f"   ✗ Failed to move")
            else:
                print(f"   ✗ No folder ID found for: {test['target_folder']}")
                self.error_count += 1
            
            # Rate limiting
            time.sleep(0.5)
        
        # Summary
        print("\n" + "="*80)
        print("ORGANIZATION SUMMARY")
        print("="*80)
        print(f"Total tests processed: {len(tests_to_move)}")
        print(f"Successfully organized: {self.organized_count}")
        print(f"Errors: {self.error_count}")
        
        # Save results
        self.save_results()
    
    def save_results(self):
        """Save organization results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = Path(__file__).parent.parent / "logs" / f"folder_organization_results_{timestamp}.json"
        
        results_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_processed': len(self.results),
                'successful': self.organized_count,
                'errors': self.error_count
            },
            'details': self.results
        }
        
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\nResults saved to: {results_file}")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Organize tests into folder structure')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    args = parser.parse_args()
    
    organizer = TestFolderOrganizer()
    
    if organizer.authenticate():
        organizer.organize_tests(dry_run=args.dry_run)
    else:
        print("Failed to authenticate with Xray API")
        sys.exit(1)

if __name__ == "__main__":
    main()