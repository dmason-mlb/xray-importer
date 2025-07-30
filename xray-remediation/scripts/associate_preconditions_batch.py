#!/usr/bin/env python3
"""
Associate preconditions with tests - batch version for non-interactive execution.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "xray-api"))
from auth_utils import XrayAPIClient

class PreconditionAssociator:
    """Associate standalone preconditions with tests"""
    
    def __init__(self):
        self.client = XrayAPIClient()
        self.associations = []
        self.associated_count = 0
        self.error_count = 0
        
    def authenticate(self):
        """Authenticate with Xray API"""
        try:
            token = self.client.get_auth_token()
            print("✓ Authentication successful")
            return True
        except Exception as e:
            print(f"✗ Authentication failed: {e}")
            return False
            
    def get_standalone_preconditions(self):
        """Get all standalone preconditions (not linked to any tests)"""
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
        
        try:
            result = self.client.execute_graphql_query(query, {
                "jql": "project = FRAMED",
                "limit": 100
            })
            
            all_preconditions = result['getPreconditions']['results']
            # Filter standalone preconditions (not linked to any tests)
            standalone = [p for p in all_preconditions if p['tests']['total'] == 0]
            
            print(f"\n1. Found {len(standalone)} standalone preconditions (out of {len(all_preconditions)} total)")
            return standalone
            
        except Exception as e:
            print(f"✗ Error fetching preconditions: {e}")
            return []
            
    def get_tests(self):
        """Get all tests for potential association"""
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
        
        try:
            result = self.client.execute_graphql_query(query, {
                "jql": "project = FRAMED",
                "limit": 100
            })
            
            tests = result['getTests']['results']
            print(f"2. Found {len(tests)} tests")
            return tests
            
        except Exception as e:
            print(f"✗ Error fetching tests: {e}")
            return []
            
    def analyze_associations(self, preconditions, tests):
        """Analyze and suggest associations based on keywords"""
        associations = []
        
        # Keywords mapping for better matching
        keyword_map = {
            'game_state': ['game state', 'game-state', 'gamestate', 'state'],
            'jewel_event': ['jewel event', 'jewel-event', 'jewelevent', 'jewel'],
            'navigation': ['navigation', 'navigate', 'nav'],
            'localization': ['localization', 'locale', 'l10n'],
            'performance': ['performance', 'perf', 'speed'],
            'security': ['security', 'auth', 'validation'],
            'integration': ['integration', 'integrate'],
            'error': ['error', 'exception', 'fail'],
            'parametrize': ['parametrize', 'parameter', 'param'],
            'regression': ['regression', 'regress']
        }
        
        for precondition in preconditions:
            pc_key = precondition['jira']['key']
            pc_summary = precondition['jira']['summary'].lower()
            pc_desc = precondition['jira'].get('description', '').lower()
            
            # Find matching tests
            matches = []
            for test in tests:
                test_key = test['jira']['key']
                test_summary = test['jira']['summary'].lower()
                test_labels = [label.lower() for label in test['jira'].get('labels', [])]
                
                score = 0
                
                # Check for keyword matches
                for keyword, variations in keyword_map.items():
                    if keyword in test_labels:
                        for var in variations:
                            if var in pc_summary or var in pc_desc:
                                score += 1
                
                # Check for direct word matches
                pc_words = set(pc_summary.split() + pc_desc.split())
                test_words = set(test_summary.split())
                common_words = pc_words.intersection(test_words)
                # Filter out common words
                common_words = {w for w in common_words if len(w) > 3 and w not in ['test', 'verify', 'that', 'when', 'should']}
                score += len(common_words)
                
                if score > 0:
                    matches.append({
                        'test_key': test_key,
                        'test_id': test['issueId'],
                        'test_summary': test['jira']['summary'],
                        'score': score
                    })
            
            if matches:
                # Sort by score
                matches.sort(key=lambda x: x['score'], reverse=True)
                associations.append({
                    'precondition_key': pc_key,
                    'precondition_id': precondition['issueId'],
                    'precondition_summary': precondition['jira']['summary'],
                    'matches': matches[:3]  # Top 3 matches
                })
        
        print(f"3. Found associations for {len(associations)} preconditions")
        return associations
        
    def associate_precondition(self, test_id, precondition_id):
        """Associate a precondition with a test"""
        mutation = """
        mutation AddPrecondition($testIssueId: String!, $preconditionIssueIds: [String]!) {
            addPreconditionsToTest(issueId: $testIssueId, preconditionIssueIds: $preconditionIssueIds) {
                warning
            }
        }
        """
        
        try:
            result = self.client.execute_graphql_query(mutation, {
                "testIssueId": test_id,
                "preconditionIssueIds": [precondition_id]
            })
            return True
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return False
            
    def execute_associations(self, associations):
        """Execute the associations"""
        results = []
        
        print("\n4. Executing associations...")
        for assoc in associations:
            # Use the top match only for automatic association
            if assoc['matches']:
                top_match = assoc['matches'][0]
                
                print(f"\n   Associating {assoc['precondition_key']} → {top_match['test_key']}")
                
                success = self.associate_precondition(
                    top_match['test_id'],
                    assoc['precondition_id']
                )
                
                if success:
                    print(f"   ✓ Success")
                    self.associated_count += 1
                    results.append({
                        'status': 'success',
                        'precondition': assoc['precondition_key'],
                        'test': top_match['test_key']
                    })
                else:
                    self.error_count += 1
                    results.append({
                        'status': 'error',
                        'precondition': assoc['precondition_key'],
                        'test': top_match['test_key']
                    })
        
        return results
        
    def save_results(self, associations, results):
        """Save association results to file"""
        log_file = Path(__file__).parent.parent / 'logs' / f'precondition_associations_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        log_file.parent.mkdir(exist_ok=True)
        
        with open(log_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_associations': len(associations),
                'executed': len(results),
                'success': self.associated_count,
                'errors': self.error_count,
                'associations': associations,
                'results': results
            }, f, indent=2)
            
        print(f"\n✓ Results saved to: {log_file}")
        
    def run(self):
        """Main execution"""
        if not self.authenticate():
            return False
            
        # Get data
        preconditions = self.get_standalone_preconditions()
        tests = self.get_tests()
        
        if not preconditions or not tests:
            print("No data to process")
            return False
            
        # Analyze associations
        associations = self.analyze_associations(preconditions, tests)
        
        # Display summary
        print("\n" + "="*80)
        print("PRECONDITION ASSOCIATION SUMMARY")
        print("="*80)
        print(f"Standalone preconditions: {len(preconditions)}")
        print(f"Available tests: {len(tests)}")
        print(f"Suggested associations: {len(associations)}")
        
        # Show first 5 associations
        for assoc in associations[:5]:
            print(f"\n{assoc['precondition_key']}: {assoc['precondition_summary']}")
            if assoc['matches']:
                top = assoc['matches'][0]
                print(f"  → {top['test_key']}: {top['test_summary'][:60]}...")
        
        if len(associations) > 5:
            print(f"\n... and {len(associations) - 5} more associations")
        
        # Execute associations
        results = self.execute_associations(associations)
        
        # Save results
        self.save_results(associations, results)
        
        # Final summary
        print("\n" + "="*80)
        print("EXECUTION COMPLETE")
        print("="*80)
        print(f"Total associations executed: {len(results)}")
        print(f"Successful: {self.associated_count}")
        print(f"Errors: {self.error_count}")
        
        return True

def main():
    """Main entry point"""
    associator = PreconditionAssociator()
    success = associator.run()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()