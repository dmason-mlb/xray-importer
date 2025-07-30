#!/usr/bin/env python3
"""
Associate standalone preconditions with appropriate tests in FRAMED project.
Analyzes precondition content and maps to relevant tests.
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

class PreconditionAssociator:
    """Associate preconditions with tests"""
    
    def __init__(self):
        self.client = XrayAPIClient()
        self.token = None
        self.associated_count = 0
        self.error_count = 0
        self.results = []
        
    def authenticate(self):
        """Authenticate with Xray API"""
        try:
            self.token = self.client.get_auth_token()
            print("✓ Authentication successful")
            return True
        except Exception as e:
            print(f"✗ Authentication failed: {e}")
            return False
    
    def get_standalone_preconditions(self, project_key="FRAMED"):
        """Get standalone preconditions from project"""
        query = """
        query GetPreconditions($jql: String!, $limit: Int!) {
            getPreconditions(jql: $jql, limit: $limit) {
                total
                results {
                    issueId
                    jira(fields: ["key", "summary", "description"])
                    tests(limit: 10) {
                        total
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
                # Filter for standalone preconditions (no associated tests)
                all_preconditions = response['getPreconditions']['results']
                standalone = [p for p in all_preconditions if p['tests']['total'] == 0]
                return standalone
            return []
        except Exception as e:
            print(f"Error fetching preconditions: {e}")
            return []
    
    def get_tests_for_association(self, project_key="FRAMED"):
        """Get tests that could use preconditions"""
        query = """
        query GetTests($jql: String!, $limit: Int!) {
            getTests(jql: $jql, limit: $limit) {
                total
                results {
                    issueId
                    jira(fields: ["key", "summary", "labels"])
                    preconditions(limit: 10) {
                        total
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
    
    def analyze_precondition_mapping(self, precondition, tests):
        """Analyze which tests a precondition should be associated with"""
        prec_summary = precondition['jira']['summary'].lower()
        prec_desc = (precondition['jira'].get('description') or '').lower()
        
        matches = []
        
        for test in tests:
            test_summary = test['jira']['summary'].lower()
            test_labels = [label.lower() for label in test['jira'].get('labels', [])]
            
            # Match based on common keywords
            score = 0
            
            # Check for API/functional type match
            if 'api' in prec_summary and 'api' in test_labels:
                score += 2
            elif 'functional' in prec_summary and 'functional' in test_labels:
                score += 2
            
            # Check for feature match
            keywords = ['team', 'page', 'mig', 'game', 'score', 'language', 'platform']
            for keyword in keywords:
                if keyword in prec_summary and keyword in test_summary:
                    score += 1
            
            # Check for specific test type match
            if 'performance' in prec_summary and 'performance' in test_labels:
                score += 3
            if 'security' in prec_summary and 'security' in test_labels:
                score += 3
            if 'integration' in prec_summary and 'integration' in test_labels:
                score += 3
            
            if score > 0:
                matches.append({
                    'test': test,
                    'score': score
                })
        
        # Sort by score and return top matches
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches[:5]  # Return top 5 matches
    
    def associate_precondition_to_test(self, precondition_id, test_id, test_key):
        """Associate a precondition with a test"""
        mutation = """
        mutation AddPrecondition($testIssueId: String!, $preconditionIssueIds: [String]!) {
            addPreconditionsToTest(testIssueId: $testIssueId, preconditionIssueIds: $preconditionIssueIds) {
                addedPreconditions
                warning
            }
        }
        """
        
        variables = {
            "testIssueId": test_id,
            "preconditionIssueIds": [precondition_id]
        }
        
        try:
            response = self.client.execute_graphql_query(mutation, variables)
            if response:
                return True
            return False
        except Exception as e:
            print(f"Error associating to {test_key}: {e}")
            return False
    
    def associate_preconditions(self, dry_run=False, auto_associate=False):
        """Main process to associate preconditions"""
        print("\n" + "="*80)
        print("XRAY PRECONDITION ASSOCIATION")
        print("="*80)
        
        # Get standalone preconditions
        print("\n1. Fetching standalone preconditions...")
        preconditions = self.get_standalone_preconditions()
        print(f"   Found {len(preconditions)} standalone preconditions")
        
        if not preconditions:
            print("   No standalone preconditions found")
            return
        
        # Get tests
        print("\n2. Fetching tests for association...")
        tests = self.get_tests_for_association()
        print(f"   Found {len(tests)} tests")
        
        if not tests:
            print("   No tests found")
            return
        
        # Analyze associations
        print("\n3. Analyzing precondition associations...")
        associations = []
        
        for prec in preconditions:
            prec_key = prec['jira']['key']
            prec_summary = prec['jira']['summary']
            
            matches = self.analyze_precondition_mapping(prec, tests)
            
            if matches:
                associations.append({
                    'precondition': prec,
                    'matches': matches
                })
        
        print(f"   Found associations for {len(associations)} preconditions")
        
        if not associations:
            print("   No suitable associations found")
            return
        
        # Show associations
        print("\n4. Proposed associations:")
        for assoc in associations[:5]:  # Show first 5
            prec = assoc['precondition']
            print(f"\n   Precondition: {prec['jira']['key']} - {prec['jira']['summary']}")
            print("   Suggested tests:")
            for match in assoc['matches'][:3]:  # Show top 3 matches
                test = match['test']
                print(f"     - {test['jira']['key']}: {test['jira']['summary']} (score: {match['score']})")
        
        if len(associations) > 5:
            print(f"\n   ... and {len(associations) - 5} more preconditions")
        
        # Confirm or execute
        if dry_run:
            print("\n5. DRY RUN - No changes made")
            return
        
        print("\n5. Associating preconditions...")
        
        if auto_associate:
            confirm = input("   Proceed with automatic association (top match only)? (yes/no): ")
        else:
            confirm = input("   Proceed with manual review for each association? (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("   Operation cancelled")
            return
        
        # Process associations
        for i, assoc in enumerate(associations, 1):
            prec = assoc['precondition']
            matches = assoc['matches']
            
            print(f"\n   [{i}/{len(associations)}] Precondition: {prec['jira']['key']}")
            print(f"   {prec['jira']['summary']}")
            
            if auto_associate and matches:
                # Auto-associate with top match
                top_match = matches[0]
                test = top_match['test']
                
                print(f"   Auto-associating with: {test['jira']['key']}")
                
                success = self.associate_precondition_to_test(
                    prec['issueId'],
                    test['issueId'],
                    test['jira']['key']
                )
                
                if success:
                    self.associated_count += 1
                    self.results.append({
                        'precondition': prec['jira']['key'],
                        'test': test['jira']['key'],
                        'status': 'success'
                    })
                    print("   ✓ Associated successfully")
                else:
                    self.error_count += 1
                    self.results.append({
                        'precondition': prec['jira']['key'],
                        'test': test['jira']['key'],
                        'status': 'error'
                    })
                    print("   ✗ Failed to associate")
            else:
                # Manual selection
                print("\n   Suggested tests:")
                for j, match in enumerate(matches[:5], 1):
                    test = match['test']
                    print(f"   {j}. {test['jira']['key']}: {test['jira']['summary']} (score: {match['score']})")
                print("   0. Skip this precondition")
                
                choice = input("\n   Select test number (or 0 to skip): ")
                
                try:
                    choice_num = int(choice)
                    if 0 < choice_num <= len(matches):
                        selected_test = matches[choice_num - 1]['test']
                        
                        success = self.associate_precondition_to_test(
                            prec['issueId'],
                            selected_test['issueId'],
                            selected_test['jira']['key']
                        )
                        
                        if success:
                            self.associated_count += 1
                            self.results.append({
                                'precondition': prec['jira']['key'],
                                'test': selected_test['jira']['key'],
                                'status': 'success'
                            })
                            print("   ✓ Associated successfully")
                        else:
                            self.error_count += 1
                            print("   ✗ Failed to associate")
                    else:
                        print("   Skipped")
                except ValueError:
                    print("   Invalid choice, skipping")
            
            # Rate limiting
            time.sleep(0.5)
        
        # Summary
        print("\n" + "="*80)
        print("ASSOCIATION SUMMARY")
        print("="*80)
        print(f"Total preconditions processed: {len(associations)}")
        print(f"Successfully associated: {self.associated_count}")
        print(f"Errors: {self.error_count}")
        
        # Save results
        self.save_results()
    
    def save_results(self):
        """Save association results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = Path(__file__).parent.parent / "logs" / f"precondition_association_results_{timestamp}.json"
        
        results_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_processed': len(self.results),
                'successful': self.associated_count,
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
    
    parser = argparse.ArgumentParser(description='Associate standalone preconditions with tests')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    parser.add_argument('--auto', action='store_true', help='Automatically associate with top match')
    args = parser.parse_args()
    
    associator = PreconditionAssociator()
    
    if associator.authenticate():
        associator.associate_preconditions(dry_run=args.dry_run, auto_associate=args.auto)
    else:
        print("Failed to authenticate with Xray API")
        sys.exit(1)

if __name__ == "__main__":
    main()