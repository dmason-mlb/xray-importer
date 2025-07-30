#!/usr/bin/env python3
"""
Create the 9 missing Xray tests using GraphQL API with proper precondition associations.
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    load_dotenv(env_file)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "xray-api"))
from auth_utils import XrayAPIClient

class XrayTestCreator:
    """Create missing Xray tests with proper precondition associations"""
    
    def __init__(self):
        self.client = XrayAPIClient()
        self.token = None
        self.created_count = 0
        self.error_count = 0
        self.results = []
        
        # Load test data
        self.load_test_data()
        
        # Precondition mappings after cleanup - using issue IDs for GraphQL API
        self.precondition_mappings = {
            "universal_setup": "1158175",  # FRAMED-1376: MLB App Setup
            "team_page_setup": "1158177",  # FRAMED-1377: Team Page Navigation
            "opening_day": "1158149",      # FRAMED-1361: Precondition for Jewel Events
            "postseason": "1158153",       # FRAMED-1363: Precondition for Jewel Events
            "multiple_jewel": "1158160",   # FRAMED-1367: Precondition for Jewel Events
            "world_series": "1158154"      # FRAMED-1364: Precondition for Jewel Events
        }
        
    def load_test_data(self):
        """Load test data from JSON file"""
        json_file = Path(__file__).parent.parent / "test-data" / "api_tests_xray.json"
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Extract missing tests (those with jiraKey: null)
        self.missing_tests = []
        for test in data['testSuite']['testCases']:
            if test['jiraKey'] is None:
                self.missing_tests.append(test)
        
        print(f"Loaded {len(self.missing_tests)} missing tests to create")
        
    def authenticate(self):
        """Authenticate with Xray API"""
        try:
            self.token = self.client.get_auth_token()
            print("✓ Authentication successful")
            return True
        except Exception as e:
            print(f"✗ Authentication failed: {e}")
            return False
    
    def create_xray_test(self, test_data):
        """Create a single Xray test using GraphQL"""
        
        # Build test steps
        test_steps = []
        for i, step in enumerate(test_data['testSteps'], 1):
            step_data = {
                "action": step['action'],
                "data": test_data.get('testData', ''),
                "result": ' | '.join(step['expectedResult']) if isinstance(step['expectedResult'], list) else step['expectedResult']
            }
            test_steps.append(step_data)
        
        # Determine preconditions based on test type
        preconditions = [self.precondition_mappings["universal_setup"]]  # Always include universal setup
        
        test_id = test_data['testCaseId']
        if test_id.startswith('API-JE-'):
            # Jewel event tests need additional preconditions
            if test_id == 'API-JE-003':
                preconditions.append(self.precondition_mappings["postseason"])
            elif test_id == 'API-JE-007':
                preconditions.append(self.precondition_mappings["multiple_jewel"])
            elif test_id == 'API-JE-008':
                preconditions.append(self.precondition_mappings["world_series"])
        
        # Build mutation - using correct Xray GraphQL API format
        mutation = """
        mutation CreateTest($jira: JSON!, $testType: UpdateTestTypeInput, $preconditionIssueIds: [String], $steps: [CreateStepInput]) {
            createTest(jira: $jira, testType: $testType, preconditionIssueIds: $preconditionIssueIds, steps: $steps) {
                test {
                    issueId
                    jira(fields: ["key", "summary"])
                }
                warnings
            }
        }
        """
        
        variables = {
            "jira": {
                "fields": {
                    "project": {"key": "FRAMED"},
                    "summary": test_data['title'],
                    "description": self.build_test_description(test_data),
                    "issuetype": {"name": "Test"},
                    "labels": test_data.get('tags', []),
                    "priority": {"name": test_data.get('priority', 'Medium')}
                }
            },
            "testType": {"name": "Manual"},  # API tests are automated but created as Manual in Xray
            "preconditionIssueIds": preconditions,
            "steps": test_steps
        }
        
        try:
            response = self.client.execute_graphql_query(mutation, variables)
            if response and 'createTest' in response:
                test_info = response['createTest']['test']
                jira_key = test_info['jira']['key']
                
                self.results.append({
                    'test_case_id': test_id,
                    'jira_key': jira_key,
                    'issue_id': test_info['issueId'],
                    'title': test_data['title'],
                    'preconditions': preconditions,
                    'status': 'success'
                })
                
                print(f"✓ Created {test_id} → {jira_key}")
                return jira_key
            else:
                print(f"✗ Failed to create {test_id}: No valid response")
                return None
                
        except Exception as e:
            print(f"✗ Error creating {test_id}: {e}")
            self.results.append({
                'test_case_id': test_id,
                'jira_key': None,
                'status': 'error',
                'error': str(e)
            })
            return None
    
    def build_test_description(self, test_data):
        """Build formatted test description"""
        description = f"""**Test Description:**
Test Case ID: {test_data['testCaseId']}
{test_data['title']}

**Test Tags:**
{', '.join(test_data.get('tags', []))}

**Execution:** Automated via pytest"""
        
        if 'testData' in test_data and test_data['testData']:
            description += f"\n\n**Test Data:**\n{test_data['testData']}"
            
        return description
    
    def create_all_missing_tests(self, dry_run=False, auto_confirm=False):
        """Create all missing Xray tests"""
        print("\n" + "="*80)
        print("XRAY TEST CREATION")
        print("="*80)
        
        print(f"\nMissing tests to create: {len(self.missing_tests)}")
        for test in self.missing_tests:
            print(f"  - {test['testCaseId']}: {test['title']}")
        
        if dry_run:
            print("\n✓ DRY RUN - No tests created")
            return
        
        if not auto_confirm:
            try:
                confirm = input(f"\nProceed with creating {len(self.missing_tests)} Xray tests? (yes/no): ")
                if confirm.lower() != 'yes':
                    print("Operation cancelled")
                    return
            except (EOFError, KeyboardInterrupt):
                print("\nOperation cancelled")
                return
        
        print("\nCreating tests...")
        
        for i, test_data in enumerate(self.missing_tests, 1):
            print(f"\n[{i}/{len(self.missing_tests)}] Creating {test_data['testCaseId']}...")
            
            jira_key = self.create_xray_test(test_data)
            
            if jira_key:
                self.created_count += 1
            else:
                self.error_count += 1
            
            # Rate limiting
            time.sleep(1.0)
        
        # Summary
        print("\n" + "="*80)
        print("CREATION SUMMARY")
        print("="*80)
        print(f"Total tests processed: {len(self.missing_tests)}")
        print(f"Successfully created: {self.created_count}")
        print(f"Errors: {self.error_count}")
        
        # Save results
        self.save_results()
        
        # Update mapping file
        if self.created_count > 0:
            self.update_mapping_file()
    
    def save_results(self):
        """Save creation results to log file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = Path(__file__).parent.parent / "logs" / f"xray_test_creation_{timestamp}.json"
        
        results_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_processed': len(self.missing_tests),
                'successful': self.created_count,
                'errors': self.error_count
            },
            'created_tests': [r for r in self.results if r['status'] == 'success'],
            'errors': [r for r in self.results if r['status'] == 'error'],
            'precondition_mappings_used': self.precondition_mappings
        }
        
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\nResults saved to: {results_file}")
    
    def update_mapping_file(self):
        """Update the complete test ID mapping file with new tests"""
        mapping_file = Path(__file__).parent.parent / "complete_test_id_mapping.json"
        
        # Load existing mapping
        with open(mapping_file, 'r') as f:
            mapping = json.load(f)
        
        # Add new mappings
        for result in self.results:
            if result['status'] == 'success':
                mapping[result['test_case_id']] = result['jira_key']
        
        # Save updated mapping
        with open(mapping_file, 'w') as f:
            json.dump(mapping, f, indent=2, sort_keys=True)
        
        print(f"✓ Updated mapping file with {self.created_count} new tests")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Create missing Xray tests')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be created without making changes')
    args = parser.parse_args()
    
    creator = XrayTestCreator()
    
    if creator.authenticate():
        creator.create_all_missing_tests(dry_run=args.dry_run, auto_confirm=True)
    else:
        print("Failed to authenticate with Xray API")
        sys.exit(1)

if __name__ == "__main__":
    main()