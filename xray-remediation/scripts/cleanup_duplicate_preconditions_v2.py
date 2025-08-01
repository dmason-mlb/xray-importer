#!/usr/bin/env python3
"""
Script to clean up duplicate preconditions in FRAMED project.
This script:
1. Identifies duplicate preconditions based on matching summaries
2. Maps which tests use each precondition
3. Updates tests to reference the original (lower ID) precondition
4. Deletes the duplicate preconditions
5. Cleans up labels on remaining preconditions
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Tuple, Set

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'xray-api'))

from auth_utils import XrayAPIClient

class PreconditionCleanup:
    def __init__(self):
        self.xray_client = XrayAPIClient()
        # Mapping of JIRA keys to numeric issueIds based on GraphQL query results
        self.key_to_id_map = {
            "FRAMED-1355": "1158139",
            "FRAMED-1356": "1158140",
            "FRAMED-1357": "1158142",
            "FRAMED-1358": "1158144",
            "FRAMED-1359": "1158146",
            "FRAMED-1360": "1158147",
            "FRAMED-1361": "1158149",
            "FRAMED-1362": "1158151",
            "FRAMED-1363": "1158153",
            "FRAMED-1364": "1158154",
            "FRAMED-1365": "1158156",
            "FRAMED-1366": "1158158",
            "FRAMED-1367": "1158160",
            "FRAMED-1368": "1158162",
            "FRAMED-1369": "1158163",
            "FRAMED-1370": "1158165",
            "FRAMED-1371": "1158167",
            "FRAMED-1372": "1158169",
            "FRAMED-1373": "1158170",
            "FRAMED-1374": "1158172",
            "FRAMED-1375": "1158174",
            "FRAMED-1575": "1162594",
            "FRAMED-1576": "1162595",
            "FRAMED-1577": "1162596",
            "FRAMED-1578": "1162597",
            "FRAMED-1579": "1162598",
            "FRAMED-1580": "1162599",
            "FRAMED-1581": "1162600",
            "FRAMED-1582": "1162601",
            "FRAMED-1583": "1162602",
            "FRAMED-1584": "1162603",
            "FRAMED-1585": "1162604",
            "FRAMED-1586": "1162605",
            "FRAMED-1587": "1162606",
            "FRAMED-1588": "1162607",
            "FRAMED-1589": "1162608",
            "FRAMED-1590": "1162609",
            "FRAMED-1591": "1162610",
            "FRAMED-1592": "1162611",
            "FRAMED-1593": "1162612",
            "FRAMED-1594": "1162613",
            "FRAMED-1595": "1162614"
        }
        self.duplicate_pairs = [
            ("FRAMED-1355", "FRAMED-1575"),
            ("FRAMED-1356", "FRAMED-1576"),
            ("FRAMED-1357", "FRAMED-1577"),
            ("FRAMED-1358", "FRAMED-1578"),
            ("FRAMED-1359", "FRAMED-1579"),
            ("FRAMED-1360", "FRAMED-1580"),
            ("FRAMED-1361", "FRAMED-1581"),
            ("FRAMED-1362", "FRAMED-1582"),
            ("FRAMED-1363", "FRAMED-1583"),
            ("FRAMED-1364", "FRAMED-1584"),
            ("FRAMED-1365", "FRAMED-1585"),
            ("FRAMED-1366", "FRAMED-1586"),
            ("FRAMED-1367", "FRAMED-1587"),
            ("FRAMED-1368", "FRAMED-1588"),
            ("FRAMED-1369", "FRAMED-1589"),
            ("FRAMED-1370", "FRAMED-1590"),
            ("FRAMED-1371", "FRAMED-1591"),
            ("FRAMED-1372", "FRAMED-1592"),
            ("FRAMED-1373", "FRAMED-1593"),
            ("FRAMED-1374", "FRAMED-1594"),
            ("FRAMED-1375", "FRAMED-1595")
        ]
        self.precondition_data = {}
        self.test_mappings = {}
        
    def get_precondition_with_tests(self, jira_key: str) -> Dict:
        """Query a single precondition with its linked tests"""
        # Convert JIRA key to numeric issueId
        issue_id = self.key_to_id_map.get(jira_key)
        if not issue_id:
            print(f"    ERROR: No issueId mapping found for {jira_key}")
            return {}
            
        query = """
        query GetPreconditionWithTests($issueId: String!) {
            getPrecondition(issueId: $issueId) {
                issueId
                definition
                preconditionType {
                    name
                    kind
                }
                tests(limit: 100, start: 0) {
                    total
                    results {
                        issueId
                        jira(fields: ["key", "summary"])
                    }
                }
                jira(fields: ["key", "summary", "labels"])
            }
        }
        """
        
        variables = {"issueId": issue_id}
        result = self.xray_client.execute_graphql_query(query, variables)
        
        # Debug logging
        if not result:
            print(f"    ERROR: No response for {jira_key} (ID: {issue_id})")
            return {}
            
        # Extract the data from the response
        # The GraphQL response might come in different formats
        if result:
            if 'data' in result and result['data']:
                return result['data']
            elif 'getPrecondition' in result:
                # Direct response format
                return result
            else:
                print(f"    ERROR: Unexpected response format for {jira_key}")
                print(f"    Response: {json.dumps(result, indent=2)}")
                return {}
        else:
            print(f"    ERROR: No response for {jira_key}")
            return {}
    
    def analyze_duplicates(self):
        """Analyze all duplicate pairs and their linked tests"""
        print("\n=== Analyzing Duplicate Preconditions ===\n")
        
        for original_key, duplicate_key in self.duplicate_pairs:
            print(f"\nProcessing pair: {original_key} (keep) / {duplicate_key} (remove)")
            
            # Get data for both preconditions
            original_data = self.get_precondition_with_tests(original_key)
            duplicate_data = self.get_precondition_with_tests(duplicate_key)
            
            # Extract the actual precondition data
            original_precond = original_data.get('getPrecondition', {})
            duplicate_precond = duplicate_data.get('getPrecondition', {})
            
            # Skip if duplicate is already deleted (returns null)
            if duplicate_precond is None:
                print(f"  INFO: {duplicate_key} appears to be already deleted")
                continue
                
            if not original_precond:
                print(f"  ERROR: Could not retrieve data for original precondition {original_key}")
                continue
            
            # Store the data
            self.precondition_data[original_key] = original_precond
            self.precondition_data[duplicate_key] = duplicate_precond
            
            # Extract test information
            original_test_ids = []
            duplicate_test_ids = []
            
            if original_precond.get('tests', {}).get('results'):
                for test in original_precond['tests']['results']:
                    test_id = test.get('issueId')
                    if test_id:
                        original_test_ids.append(test_id)
            
            if duplicate_precond.get('tests', {}).get('results'):
                for test in duplicate_precond['tests']['results']:
                    test_id = test.get('issueId')
                    if test_id:
                        duplicate_test_ids.append(test_id)
            
            # Store mapping with numeric IDs
            original_id = self.key_to_id_map[original_key]
            duplicate_id = self.key_to_id_map[duplicate_key]
            
            self.test_mappings[duplicate_key] = {
                'original_key': original_key,
                'original_id': original_id,
                'duplicate_id': duplicate_id,
                'tests_to_update': duplicate_test_ids,  # Store numeric test IDs
                'original_summary': original_precond.get('jira', {}).get('summary', ''),
                'duplicate_summary': duplicate_precond.get('jira', {}).get('summary', ''),
                'original_labels': original_precond.get('jira', {}).get('labels', []),
                'duplicate_labels': duplicate_precond.get('jira', {}).get('labels', [])
            }
            
            print(f"  Original: {original_key} (ID: {original_id})")
            print(f"    Summary: {self.test_mappings[duplicate_key]['original_summary']}")
            print(f"    Labels: {self.test_mappings[duplicate_key]['original_labels']}")
            print(f"    Tests using it: {len(original_test_ids)}")
            
            print(f"  Duplicate: {duplicate_key} (ID: {duplicate_id})")
            print(f"    Summary: {self.test_mappings[duplicate_key]['duplicate_summary']}")
            print(f"    Labels: {self.test_mappings[duplicate_key]['duplicate_labels']}")
            print(f"    Tests using it: {len(duplicate_test_ids)}")
    
    def update_test_references(self):
        """Update tests to reference the original precondition instead of duplicate"""
        print("\n\n=== Updating Test References ===\n")
        
        update_summary = {
            'successful': [],
            'failed': [],
            'skipped': []
        }
        
        for duplicate_key, mapping in self.test_mappings.items():
            original_id = mapping['original_id']
            duplicate_id = mapping['duplicate_id']
            tests_to_update = mapping['tests_to_update']
            
            if not tests_to_update:
                print(f"\nNo tests to update for {duplicate_key}")
                update_summary['skipped'].append({
                    'duplicate': duplicate_key,
                    'reason': 'No tests linked'
                })
                continue
            
            print(f"\nUpdating tests that reference {duplicate_key} (ID: {duplicate_id}) to use {mapping['original_key']} (ID: {original_id})")
            
            for test_id in tests_to_update:
                try:
                    # First, remove the duplicate precondition from the test
                    remove_mutation = """
                    mutation RemovePreconditionFromTest($testId: String!, $preconditionIds: [String]!) {
                        removePreconditionsFromTest(issueId: $testId, preconditionIds: $preconditionIds)
                    }
                    """
                    
                    remove_variables = {
                        "testId": test_id,
                        "preconditionIds": [duplicate_id]
                    }
                    
                    remove_result = self.xray_client.execute_graphql_query(remove_mutation, remove_variables)
                    
                    # Then add the original precondition to the test
                    add_mutation = """
                    mutation AddPreconditionToTest($testId: String!, $preconditionIds: [String]!) {
                        addPreconditionsToTest(issueId: $testId, preconditionIds: $preconditionIds) {
                            addedPreconditions
                            warning
                        }
                    }
                    """
                    
                    add_variables = {
                        "testId": test_id,
                        "preconditionIds": [original_id]
                    }
                    
                    add_result = self.xray_client.execute_graphql_query(add_mutation, add_variables)
                    
                    if add_result.get('data', {}).get('addPreconditionsToTest'):
                        print(f"  ✓ Updated test {test_id}: {duplicate_key} → {mapping['original_key']}")
                        update_summary['successful'].append({
                            'test_id': test_id,
                            'from_key': duplicate_key,
                            'to_key': mapping['original_key']
                        })
                    else:
                        print(f"  ✗ Failed to update test {test_id}")
                        update_summary['failed'].append({
                            'test_id': test_id,
                            'from_key': duplicate_key,
                            'to_key': mapping['original_key'],
                            'error': add_result.get('errors', 'Unknown error')
                        })
                        
                except Exception as e:
                    print(f"  ✗ Error updating test {test_id}: {str(e)}")
                    update_summary['failed'].append({
                        'test_id': test_id,
                        'from_key': duplicate_key,
                        'to_key': mapping['original_key'],
                        'error': str(e)
                    })
        
        return update_summary
    
    def delete_duplicate_preconditions(self, update_summary):
        """Delete the duplicate preconditions after references are updated"""
        print("\n\n=== Deleting Duplicate Preconditions ===\n")
        
        deletion_summary = {
            'successful': [],
            'failed': [],
            'skipped': []
        }
        
        for duplicate_key, mapping in self.test_mappings.items():
            duplicate_id = mapping['duplicate_id']
            
            # Check if all tests were successfully updated
            tests_to_update = set(mapping['tests_to_update'])
            failed_updates = {item['test_id'] for item in update_summary['failed'] 
                            if item['from_key'] == duplicate_key}
            
            if failed_updates:
                print(f"\nSkipping deletion of {duplicate_key} - some test updates failed")
                deletion_summary['skipped'].append({
                    'precondition': duplicate_key,
                    'reason': f"Failed to update tests: {', '.join(failed_updates)}"
                })
                continue
            
            try:
                # Delete the duplicate precondition using numeric ID
                delete_mutation = """
                mutation DeletePrecondition($issueId: String!) {
                    deletePrecondition(issueId: $issueId)
                }
                """
                
                delete_variables = {"issueId": duplicate_id}
                delete_result = self.xray_client.execute_graphql_query(delete_mutation, delete_variables)
                
                if delete_result.get('data', {}).get('deletePrecondition'):
                    print(f"  ✓ Deleted {duplicate_key} (ID: {duplicate_id})")
                    deletion_summary['successful'].append(duplicate_key)
                else:
                    print(f"  ✗ Failed to delete {duplicate_key}")
                    deletion_summary['failed'].append({
                        'precondition': duplicate_key,
                        'error': delete_result.get('errors', 'Unknown error')
                    })
                    
            except Exception as e:
                print(f"  ✗ Error deleting {duplicate_key}: {str(e)}")
                deletion_summary['failed'].append({
                    'precondition': duplicate_key,
                    'error': str(e)
                })
        
        return deletion_summary
    
    def generate_report(self, update_summary, deletion_summary):
        """Generate a detailed report of the cleanup operation"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                  'logs', f'precondition_cleanup_report_{timestamp}.json')
        
        report = {
            'timestamp': timestamp,
            'duplicate_pairs_processed': len(self.duplicate_pairs),
            'test_updates': update_summary,
            'precondition_deletions': deletion_summary,
            'precondition_analysis': {}
        }
        
        # Add detailed analysis for each pair
        for original_key, duplicate_key in self.duplicate_pairs:
            if duplicate_key in self.test_mappings:
                report['precondition_analysis'][duplicate_key] = {
                    'original_key': original_key,
                    'original_id': self.test_mappings[duplicate_key]['original_id'],
                    'duplicate_id': self.test_mappings[duplicate_key]['duplicate_id'],
                    'duplicate_summary': self.test_mappings[duplicate_key]['duplicate_summary'],
                    'original_summary': self.test_mappings[duplicate_key]['original_summary'],
                    'tests_migrated_count': len(self.test_mappings[duplicate_key]['tests_to_update']),
                    'duplicate_labels': self.test_mappings[duplicate_key]['duplicate_labels'],
                    'original_labels': self.test_mappings[duplicate_key]['original_labels']
                }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n\n=== Cleanup Summary ===")
        print(f"Report saved to: {report_file}")
        print(f"\nTest Updates:")
        print(f"  Successful: {len(update_summary['successful'])}")
        print(f"  Failed: {len(update_summary['failed'])}")
        print(f"  Skipped: {len(update_summary['skipped'])}")
        print(f"\nPrecondition Deletions:")
        print(f"  Successful: {len(deletion_summary['successful'])}")
        print(f"  Failed: {len(deletion_summary['failed'])}")
        print(f"  Skipped: {len(deletion_summary['skipped'])}")
        
        return report_file
    
    def run(self):
        """Execute the full cleanup process"""
        print("Starting Precondition Cleanup Process")
        print("=" * 50)
        
        # Step 1: Analyze duplicates and map test relationships
        self.analyze_duplicates()
        
        # Step 2: Update test references
        update_summary = self.update_test_references()
        
        # Step 3: Delete duplicate preconditions
        deletion_summary = self.delete_duplicate_preconditions(update_summary)
        
        # Step 4: Generate report
        report_file = self.generate_report(update_summary, deletion_summary)
        
        print("\nCleanup process completed!")
        return report_file


if __name__ == "__main__":
    cleanup = PreconditionCleanup()
    cleanup.run()