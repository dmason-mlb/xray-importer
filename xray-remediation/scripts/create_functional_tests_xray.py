#!/usr/bin/env python3
"""
Create functional tests in Xray from JSON definitions.
For Xray Remediation Project - July 31, 2025
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    load_dotenv(env_file)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "xray-api"))
from auth_utils import XrayAPIClient

class FunctionalTestCreator:
    """Create functional tests in Xray from JSON definitions"""
    
    def __init__(self):
        self.client = XrayAPIClient()
        self.token = None
        self.created_count = 0
        self.error_count = 0
        self.results = []
        self.test_mapping = {}  # Map test IDs to JIRA keys
        
        # Load test data
        self.load_test_data()
        
    def load_test_data(self):
        """Load functional test data from JSON file"""
        json_file = Path(__file__).parent.parent / "test-data" / "functional_tests_xray.json"
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        self.functional_tests = data['tests']
        print(f"Loaded {len(self.functional_tests)} functional tests to create")
        
    def authenticate(self):
        """Authenticate with Xray API"""
        try:
            self.token = self.client.get_auth_token()
            print("✓ Authentication successful")
            return True
        except Exception as e:
            print(f"✗ Authentication failed: {e}")
            return False
    
    def create_functional_test(self, test_data):
        """Create a single functional test in Xray using GraphQL"""
        
        # Extract test info
        test_info = test_data['testInfo']
        test_id = test_info['summary']  # e.g., "TC-001"
        
        # Get description and clean it up for summary
        desc_lines = test_info.get('description', '').split('\n')
        first_line = desc_lines[0] if desc_lines else ''
        
        # Clean labels - remove spaces and special characters for JIRA compatibility
        raw_labels = test_info.get('labels', [])
        clean_labels = []
        for label in raw_labels:
            # Replace spaces and colons with underscores for JIRA compatibility
            clean_label = label.replace(' ', '_').replace(':', '-')
            clean_labels.append(clean_label)
        
        print(f"DEBUG: First line of description: '{first_line}'")
        
        # Build test steps
        test_steps = []
        for step in test_info.get('steps', []):
            # Parse the action which contains action -> expected -> result format
            action_text = step.get('action', '')
            parts = action_text.split('→')
            
            step_data = {
                "action": parts[0].strip() if parts else action_text,
                "data": step.get('data', ''),
                "result": parts[1].strip() if len(parts) > 1 else step.get('result', '')
            }
            test_steps.append(step_data)
        
        # Build mutation
        mutation = """
        mutation CreateFunctionalTest($jira: JSON!, $testType: UpdateTestTypeInput, $steps: [CreateStepInput]) {
            createTest(jira: $jira, testType: $testType, steps: $steps) {
                test {
                    issueId
                    jira(fields: ["key"])
                }
                warnings
            }
        }
        """
        
        # Prepare variables - wrap JIRA fields in 'fields' object
        variables = {
            "jira": {
                "fields": {
                    "project": {"key": "FRAMED"},
                    "summary": f"[Functional] Team Page - {test_id} - {first_line}",
                    "description": test_info.get('description', ''),
                    "issuetype": {"name": "Test"},
                    "labels": clean_labels,
                    "priority": {"name": test_info.get('priority', 'Medium')},
                    "components": [{"name": "team_page"}]
                }
            },
            "testType": {"name": "Manual"},
            "steps": test_steps
        }
        
        try:
            result = self.client.execute_graphql_query(mutation, variables)
            
            if result and 'createTest' in result:
                test_result = result['createTest']
                test_data = test_result.get('test', {})
                
                # Extract JIRA key from the nested structure
                jira_key = None
                if 'jira' in test_data and isinstance(test_data['jira'], dict):
                    jira_key = test_data['jira'].get('key')
                
                issue_id = test_data.get('issueId')
                
                if jira_key:
                    self.test_mapping[test_id] = jira_key
                    self.created_count += 1
                    
                    print(f"✓ Created {test_id} -> {jira_key}")
                    
                    self.results.append({
                        'test_id': test_id,
                        'jira_key': jira_key,
                        'issue_id': issue_id,
                        'status': 'created'
                    })
                    
                    return jira_key
                else:
                    error_msg = 'No JIRA key in response'
                    print(f"✗ Failed to create {test_id}: {error_msg}")
                    self.error_count += 1
                    self.results.append({
                        'test_id': test_id,
                        'status': 'error',
                        'error': error_msg
                    })
                    return None
            else:
                error_msg = 'No createTest in response'
                print(f"✗ Failed to create {test_id}: {error_msg}")
                self.error_count += 1
                self.results.append({
                    'test_id': test_id,
                    'status': 'error',
                    'error': error_msg
                })
                return None
                
        except Exception as e:
            print(f"✗ Error creating {test_id}: {str(e)}")
            self.error_count += 1
            self.results.append({
                'test_id': test_id,
                'status': 'error',
                'error': str(e)
            })
            return None
    
    def create_all_tests(self):
        """Create all functional tests"""
        print(f"\n🚀 Creating {len(self.functional_tests)} functional tests in Xray...")
        
        for i, test in enumerate(self.functional_tests, 1):
            print(f"\n[{i}/{len(self.functional_tests)}] Processing test...")
            print(f"Test ID: {test['testInfo']['summary']}")
            self.create_functional_test(test)
            
            # Add a small delay to avoid rate limiting
            if i < len(self.functional_tests):
                time.sleep(0.5)
        
        print(f"\n✅ Summary:")
        print(f"  - Created: {self.created_count}")
        print(f"  - Errors: {self.error_count}")
        
    def save_results(self):
        """Save results to JSON file"""
        output_file = Path(__file__).parent.parent / "logs" / f"functional_test_creation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_file.parent.mkdir(exist_ok=True)
        
        output_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': len(self.functional_tests),
                'created': self.created_count,
                'errors': self.error_count
            },
            'test_mapping': self.test_mapping,
            'results': self.results
        }
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\n📄 Results saved to: {output_file}")
        
        # Also update the test catalog mapping file
        self.update_test_catalog()
    
    def update_test_catalog(self):
        """Update test catalog with new JIRA mappings"""
        if not self.test_mapping:
            return
            
        catalog_file = Path(__file__).parent.parent / "logs" / "functional_test_mapping.json"
        
        # Load existing mapping if it exists
        existing_mapping = {}
        if catalog_file.exists():
            with open(catalog_file, 'r') as f:
                existing_mapping = json.load(f)
        
        # Update with new mappings
        existing_mapping.update(self.test_mapping)
        
        # Save updated mapping
        with open(catalog_file, 'w') as f:
            json.dump(existing_mapping, f, indent=2)
        
        print(f"✓ Updated test catalog mapping: {catalog_file}")

def main():
    """Main execution"""
    creator = FunctionalTestCreator()
    
    # Authenticate
    if not creator.authenticate():
        print("❌ Authentication failed. Exiting.")
        return
    
    # Create all tests
    creator.create_all_tests()
    
    # Save results
    creator.save_results()
    
    print("\n✨ Functional test creation complete!")

if __name__ == "__main__":
    main()