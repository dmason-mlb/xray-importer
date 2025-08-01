#!/usr/bin/env python3
"""
Organize Xray tests and preconditions into appropriate folders.
This script:
1. Inventories all API tests and checks if their target folders exist
2. Moves all preconditions into a dedicated folder
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "xray-api"))
from auth_utils import XrayAPIClient

class XrayFolderOrganizer:
    """Organize tests and preconditions into folders"""
    
    def __init__(self):
        self.client = XrayAPIClient()
        self.project_id = None
        self.api_tests = []
        self.preconditions = []
        self.folder_structure = defaultdict(list)
        self.missing_folders = set()
        
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
        """Get FRAMED project ID"""
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
                print(f"✓ Found project FRAMED with ID: {self.project_id}")
                return True
            else:
                print("✗ No tests found in project FRAMED")
                return False
                
        except Exception as e:
            print(f"✗ Error getting project info: {e}")
            return False
    
    def get_api_tests(self):
        """Get all API tests from Xray"""
        query = """
        query GetAPITests($jql: String!, $limit: Int!) {
            getTests(jql: $jql, limit: $limit) {
                total
                results {
                    issueId
                    jira(fields: ["key", "summary", "labels"])
                    folder {
                        name
                        path
                    }
                }
            }
        }
        """
        
        try:
            # Get all tests with API label
            result = self.client.execute_graphql_query(query, {
                "jql": "project = FRAMED AND labels = 'api'",
                "limit": 200
            })
            
            self.api_tests = result['getTests']['results']
            print(f"✓ Found {len(self.api_tests)} API tests")
            return True
            
        except Exception as e:
            print(f"✗ Error fetching API tests: {e}")
            return False
    
    def get_preconditions(self):
        """Get all preconditions from Xray"""
        query = """
        query GetPreconditions($jql: String!, $limit: Int!) {
            getPreconditions(jql: $jql, limit: $limit) {
                total
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
                "jql": "project = FRAMED",
                "limit": 100
            })
            
            self.preconditions = result['getPreconditions']['results']
            print(f"✓ Found {len(self.preconditions)} preconditions")
            return True
            
        except Exception as e:
            print(f"✗ Error fetching preconditions: {e}")
            return False
    
    def analyze_folder_structure(self):
        """Analyze the expected folder structure for API tests"""
        # Define expected folder structure based on test categories
        folder_mapping = {
            # Team Page tests
            'team_page': '/Team Page/API Tests',
            'error_handling': '/Team Page/API Tests/Error Handling',
            'authentication': '/Team Page/API Tests/Authentication',
            'localization': '/Team Page/API Tests/Localization',
            'performance': '/Team Page/API Tests/Performance',
            
            # Other surface areas (examples based on common patterns)
            'home_surface': '/Home Surface/API Tests',
            'news_surface': '/News Surface/API Tests',
            'standings': '/Standings/API Tests',
            'schedule': '/Schedule/API Tests',
            'player': '/Player/API Tests',
            'game': '/Game/API Tests',
            
            # Common categories
            'security': '/Security/API Tests',
            'integration': '/Integration/API Tests',
            'regression': '/Regression/API Tests'
        }
        
        # Analyze each API test
        for test in self.api_tests:
            test_key = test['jira']['key']
            test_summary = test['jira']['summary'].lower()
            test_labels = [label.lower() for label in test['jira'].get('labels', [])]
            current_folder = test.get('folder', {}).get('path', '/')
            
            # Determine expected folder
            expected_folder = None
            
            # Check based on summary and labels
            if 'team_page' in test_labels or 'team page' in test_summary:
                if 'error' in test_summary or 'error_handling' in test_labels:
                    expected_folder = folder_mapping['error_handling']
                elif 'auth' in test_summary or 'authentication' in test_labels:
                    expected_folder = folder_mapping['authentication']
                elif 'localization' in test_summary or 'l10n' in test_labels:
                    expected_folder = folder_mapping['localization']
                elif 'performance' in test_summary or 'perf' in test_labels:
                    expected_folder = folder_mapping['performance']
                else:
                    expected_folder = folder_mapping['team_page']
            elif 'home_surface' in test_labels or 'home surface' in test_summary:
                expected_folder = folder_mapping['home_surface']
            elif 'news_surface' in test_labels or 'news surface' in test_summary:
                expected_folder = folder_mapping['news_surface']
            elif 'security' in test_labels:
                expected_folder = folder_mapping['security']
            elif 'integration' in test_labels:
                expected_folder = folder_mapping['integration']
            elif 'regression' in test_labels:
                expected_folder = folder_mapping['regression']
            
            # If no specific match, use generic API Tests folder
            if not expected_folder:
                expected_folder = '/API Tests'
            
            # Store the analysis
            self.folder_structure[expected_folder].append({
                'key': test_key,
                'summary': test['jira']['summary'],
                'current_folder': current_folder,
                'needs_move': current_folder != expected_folder
            })
            
            # Track if folder needs to be created
            if current_folder != expected_folder:
                self.missing_folders.add(expected_folder)
    
    def create_folder_if_needed(self, path):
        """Create a folder structure if it doesn't exist"""
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
            result = self.client.execute_graphql_query(mutation, {
                "projectId": self.project_id,
                "path": path
            })
            
            if result.get('createFolder'):
                warnings = result['createFolder'].get('warnings', [])
                if warnings:
                    # Folder already exists
                    return True
                else:
                    print(f"  ✓ Created folder: {path}")
                    return True
                    
        except Exception as e:
            # Folder might already exist
            if "already exists" in str(e):
                return True
            print(f"  ✗ Error creating folder {path}: {e}")
            return False
    
    def move_items_to_folder(self, item_ids, folder_path, item_type="tests"):
        """Move tests or preconditions to a folder"""
        if item_type == "preconditions":
            mutation = """
            mutation AddIssuesToFolder($projectId: String!, $path: String!, $issueIds: [String]!) {
                addIssuesToFolder(projectId: $projectId, path: $path, issueIds: $issueIds) {
                    folder {
                        name
                        path
                        preconditionsCount
                        issuesCount
                    }
                    warnings
                }
            }
            """
        else:
            mutation = """
            mutation AddTestsToFolder($projectId: String!, $path: String!, $testIssueIds: [String]!) {
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
            variables = {
                "projectId": self.project_id,
                "path": folder_path
            }
            
            if item_type == "preconditions":
                variables["issueIds"] = item_ids
            else:
                variables["testIssueIds"] = item_ids
            
            result = self.client.execute_graphql_query(mutation, variables)
            return True
            
        except Exception as e:
            print(f"  ✗ Error moving items: {e}")
            return False
    
    def organize_preconditions(self):
        """Move all preconditions to a dedicated folder"""
        precondition_folder = "/Preconditions"
        
        print(f"\n{'='*60}")
        print("ORGANIZING PRECONDITIONS")
        print('='*60)
        
        # Create preconditions folder
        if self.create_folder_if_needed(precondition_folder):
            print(f"✓ Preconditions folder ready: {precondition_folder}")
        
        # Get preconditions not in the folder
        to_move = []
        for pc in self.preconditions:
            current_path = pc.get('folder', {}).get('path', '/')
            if current_path != precondition_folder:
                to_move.append({
                    'id': pc['issueId'],
                    'key': pc['jira']['key'],
                    'summary': pc['jira']['summary']
                })
        
        if to_move:
            print(f"\nMoving {len(to_move)} preconditions to {precondition_folder}...")
            
            # Move in batches of 10
            batch_size = 10
            for i in range(0, len(to_move), batch_size):
                batch = to_move[i:i + batch_size]
                ids = [item['id'] for item in batch]
                keys = [item['key'] for item in batch]
                
                print(f"\nBatch {i//batch_size + 1}: {', '.join(keys)}")
                
                if self.move_items_to_folder(ids, precondition_folder, "preconditions"):
                    print(f"  ✓ Moved {len(batch)} preconditions")
                else:
                    print(f"  ✗ Failed to move batch")
        else:
            print("✓ All preconditions already in correct folder")
    
    def print_inventory_report(self):
        """Print detailed inventory report"""
        print(f"\n{'='*80}")
        print("API TEST FOLDER INVENTORY REPORT")
        print('='*80)
        
        total_tests = sum(len(tests) for tests in self.folder_structure.values())
        needs_move = sum(1 for tests in self.folder_structure.values() 
                        for test in tests if test['needs_move'])
        
        print(f"\nSummary:")
        print(f"  Total API tests: {total_tests}")
        print(f"  Tests needing folder move: {needs_move}")
        print(f"  Unique target folders: {len(self.folder_structure)}")
        
        print("\nFolder Analysis:")
        for folder, tests in sorted(self.folder_structure.items()):
            print(f"\n{folder}:")
            print(f"  Expected tests: {len(tests)}")
            
            # Show tests that need to be moved
            needs_move_list = [t for t in tests if t['needs_move']]
            if needs_move_list:
                print(f"  Tests to move here ({len(needs_move_list)}):")
                for test in needs_move_list[:5]:  # Show first 5
                    print(f"    - {test['key']}: {test['summary'][:50]}...")
                    print(f"      Current: {test['current_folder']}")
                if len(needs_move_list) > 5:
                    print(f"    ... and {len(needs_move_list) - 5} more")
    
    def save_report(self):
        """Save detailed report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = Path(__file__).parent.parent / 'logs' / f'folder_organization_report_{timestamp}.json'
        report_file.parent.mkdir(exist_ok=True)
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_api_tests': len(self.api_tests),
                'total_preconditions': len(self.preconditions),
                'target_folders': len(self.folder_structure),
                'tests_needing_move': sum(1 for tests in self.folder_structure.values() 
                                        for test in tests if test['needs_move'])
            },
            'folder_structure': dict(self.folder_structure),
            'api_tests': [
                {
                    'key': test['jira']['key'],
                    'summary': test['jira']['summary'],
                    'labels': test['jira'].get('labels', []),
                    'current_folder': test.get('folder', {}).get('path', '/')
                }
                for test in self.api_tests
            ],
            'preconditions': [
                {
                    'key': pc['jira']['key'],
                    'summary': pc['jira']['summary'],
                    'current_folder': pc.get('folder', {}).get('path', '/')
                }
                for pc in self.preconditions
            ]
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n✓ Detailed report saved to: {report_file}")
    
    def run(self, move_preconditions=True, create_folders=False, move_tests=False):
        """Execute the folder organization"""
        if not self.authenticate():
            return False
        
        if not self.get_project_info():
            return False
        
        # Get all data
        print("\nFetching data from Xray...")
        if not self.get_api_tests():
            return False
        
        if not self.get_preconditions():
            return False
        
        # Analyze folder structure
        print("\nAnalyzing folder structure...")
        self.analyze_folder_structure()
        
        # Print inventory report
        self.print_inventory_report()
        
        # Create missing folders if requested
        if create_folders and self.missing_folders:
            print(f"\n{'='*60}")
            print("CREATING MISSING FOLDERS")
            print('='*60)
            for folder in sorted(self.missing_folders):
                print(f"\nCreating: {folder}")
                self.create_folder_if_needed(folder)
        
        # Move preconditions if requested
        if move_preconditions:
            self.organize_preconditions()
        
        # Move tests if requested
        if move_tests:
            print(f"\n{'='*60}")
            print("MOVING API TESTS TO TARGET FOLDERS")
            print('='*60)
            
            for folder, tests in self.folder_structure.items():
                tests_to_move = [t for t in tests if t['needs_move']]
                if tests_to_move:
                    print(f"\nMoving {len(tests_to_move)} tests to {folder}")
                    
                    # Create folder first
                    self.create_folder_if_needed(folder)
                    
                    # Get issue IDs
                    test_keys = [t['key'] for t in tests_to_move]
                    test_ids = []
                    
                    # Get issue IDs for each test
                    for test in self.api_tests:
                        if test['jira']['key'] in test_keys:
                            test_ids.append(test['issueId'])
                    
                    if test_ids:
                        if self.move_items_to_folder(test_ids, folder):
                            print(f"  ✓ Moved {len(test_ids)} tests")
                        else:
                            print(f"  ✗ Failed to move tests")
        
        # Save report
        self.save_report()
        
        return True

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Organize Xray tests and preconditions into folders')
    parser.add_argument('--move-preconditions', action='store_true', 
                       help='Move all preconditions to /Preconditions folder')
    parser.add_argument('--create-folders', action='store_true',
                       help='Create missing folders for API tests')
    parser.add_argument('--move-tests', action='store_true',
                       help='Move API tests to their target folders')
    parser.add_argument('--all', action='store_true',
                       help='Perform all operations')
    
    args = parser.parse_args()
    
    # If --all is specified, enable all operations
    if args.all:
        args.move_preconditions = True
        args.create_folders = True
        args.move_tests = True
    
    # If no operations specified, just do inventory
    if not any([args.move_preconditions, args.create_folders, args.move_tests]):
        print("Running inventory only (no changes will be made)")
        print("Use --move-preconditions, --create-folders, --move-tests, or --all to make changes")
    
    organizer = XrayFolderOrganizer()
    organizer.run(
        move_preconditions=args.move_preconditions,
        create_folders=args.create_folders,
        move_tests=args.move_tests
    )

if __name__ == "__main__":
    main()