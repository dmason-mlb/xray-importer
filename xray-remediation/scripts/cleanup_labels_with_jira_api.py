#!/usr/bin/env python3
"""
Clean up test case ID labels from existing API tests in FRAMED project.
Uses JIRA REST API via MCP tools to update labels.
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
        
    def confirm_changes(self):
        """Ask user to confirm before making changes"""
        print("\nDo you want to proceed with these changes? (yes/no): ", end='')
        response = input().strip().lower()
        return response == 'yes'
        
    def run(self, dry_run=False):
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
        
        if dry_run:
            print("\n✓ DRY RUN - No changes made")
            return True
            
        # Confirm changes
        if not self.confirm_changes():
            print("✗ Changes cancelled by user")
            return False
            
        # Note: Since we can't update labels via Xray GraphQL API directly,
        # we'll need to use JIRA REST API or MCP tools
        print("\n⚠️  Note: Label updates require JIRA REST API access")
        print("Tests identified for cleanup have been logged.")
        
        # Save results to file for manual processing or future automation
        results_file = Path(__file__).parent.parent / 'logs' / f'label_cleanup_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        results_file.parent.mkdir(exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'tests_to_clean': tests_to_clean,
                'total_count': len(tests_to_clean)
            }, f, indent=2)
            
        print(f"\n✓ Results saved to: {results_file}")
        print(f"  - {len(tests_to_clean)} tests identified for label cleanup")
        
        return True

def main():
    """Main entry point"""
    import argparse
    parser = argparse.ArgumentParser(description='Clean up test case ID labels from Xray tests')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    args = parser.parse_args()
    
    cleaner = TestLabelCleaner()
    success = cleaner.run(dry_run=args.dry_run)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()