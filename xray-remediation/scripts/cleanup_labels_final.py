#!/usr/bin/env python3
"""
Clean up test case ID labels from existing API tests in FRAMED project.
Uses both Xray GraphQL API to fetch tests and JIRA REST API (via MCP) to update labels.
"""

import os
import sys
import json
import re
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "xray-api"))
from auth_utils import XrayAPIClient

class TestLabelCleaner:
    """Clean test case ID labels from Xray tests"""
    
    def __init__(self):
        self.client = XrayAPIClient()
        self.token = None
        self.cleaned_count = 0
        self.error_count = 0
        self.results = []
        # Pattern to match test case ID labels
        self.test_id_pattern = re.compile(r'^API-[A-Z]*-?\d+$')
        
    def authenticate(self):
        """Authenticate with Xray API"""
        try:
            self.token = self.client.get_auth_token()
            print("✓ Xray authentication successful")
            return True
        except Exception as e:
            print(f"✗ Authentication failed: {e}")
            return False
            
    def get_tests_with_labels(self):
        """Get all tests that have test case ID labels"""
        query = """
        query GetTestsWithLabels {
            getTests(jql: "project = FRAMED AND labels IS NOT EMPTY", limit: 100) {
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
            print("\nFetching tests with labels...")
            result = self.client.execute_graphql_query(query)
            tests = result['getTests']['results']
            print(f"✓ Found {len(tests)} tests with labels")
            
            # Filter tests that have test case ID labels
            tests_to_clean = []
            for test in tests:
                current_labels = test['jira'].get('labels', [])
                test_id_labels = [label for label in current_labels if self.test_id_pattern.match(label)]
                
                if test_id_labels:
                    tests_to_clean.append({
                        'issueId': test['issueId'],
                        'key': test['jira']['key'],
                        'summary': test['jira']['summary'],
                        'current_labels': current_labels,
                        'labels_to_remove': test_id_labels,
                        'new_labels': [label for label in current_labels if not self.test_id_pattern.match(label)]
                    })
                    
            print(f"✓ Found {len(tests_to_clean)} tests with test case ID labels to remove")
            return tests_to_clean
            
        except Exception as e:
            print(f"✗ Error fetching tests: {e}")
            return []

    def display_changes_summary(self, tests_to_clean):
        """Display summary of changes that will be made"""
        print("\n" + "="*80)
        print("LABEL CLEANUP SUMMARY")
        print("="*80)
        
        for test in tests_to_clean[:5]:  # Show first 5 as examples
            print(f"\n{test['key']}: {test['summary'][:60]}...")
            print(f"  Current labels: {test['current_labels']}")
            print(f"  Removing: {test['labels_to_remove']}")
            print(f"  New labels: {test['new_labels']}")
        
        if len(tests_to_clean) > 5:
            print(f"\n... and {len(tests_to_clean) - 5} more tests")
        
        print(f"\nTotal tests to update: {len(tests_to_clean)}")
        print("="*80)
        
    def save_results(self, tests_to_clean):
        """Save results to JSON file"""
        results_file = Path(__file__).parent.parent / 'logs' / f'label_cleanup_plan_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        results_file.parent.mkdir(exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'tests_to_clean': tests_to_clean,
                'total_count': len(tests_to_clean),
                'status': 'ready_for_execution'
            }, f, indent=2)
            
        print(f"\n✓ Cleanup plan saved to: {results_file}")
        return results_file
        
    def run(self):
        """Main execution method"""
        if not self.authenticate():
            return False
            
        # Get tests with labels
        tests_to_clean = self.get_tests_with_labels()
        if not tests_to_clean:
            print("No tests found with test case ID labels to clean")
            return True
            
        # Display summary
        self.display_changes_summary(tests_to_clean)
        
        # Save the plan
        plan_file = self.save_results(tests_to_clean)
        
        print("\n" + "="*80)
        print("NEXT STEPS")
        print("="*80)
        print("The cleanup plan has been generated and saved.")
        print(f"Total tests to update: {len(tests_to_clean)}")
        print("\nTo execute the cleanup, use the JIRA MCP tools to update each test's labels.")
        print("The plan file contains all the necessary information for bulk processing.")
        print("="*80)
        
        return True

def main():
    """Main entry point"""
    cleaner = TestLabelCleaner()
    success = cleaner.run()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()