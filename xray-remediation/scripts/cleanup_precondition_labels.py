#!/usr/bin/env python3
"""
Script to clean up labels on preconditions in FRAMED project.
Ensures all preconditions only have the 'precondition' label.
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Set
from jira import JIRA

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'xray-api'))
from auth_utils import JiraConfig

class PreconditionLabelCleanup:
    def __init__(self):
        # Initialize JIRA client
        config = JiraConfig()
        self.jira = JIRA(
            server=config.jira_url,
            basic_auth=(config.jira_username, config.jira_api_token)
        )
        self.project_key = "FRAMED"
        self.changes_made = []
        
    def get_all_preconditions(self) -> List[Dict]:
        """Get all preconditions in the FRAMED project"""
        print("Fetching all preconditions...")
        
        jql = f'project = {self.project_key} AND issuetype = "Precondition" ORDER BY key ASC'
        issues = []
        start_at = 0
        max_results = 50
        
        while True:
            batch = self.jira.search_issues(
                jql,
                startAt=start_at,
                maxResults=max_results,
                fields="key,summary,labels"
            )
            
            issues.extend([{
                'key': issue.key,
                'summary': issue.fields.summary,
                'labels': issue.fields.labels or []
            } for issue in batch])
            
            if len(batch) < max_results:
                break
            start_at += max_results
        
        print(f"Found {len(issues)} preconditions")
        return issues
    
    def analyze_labels(self, preconditions: List[Dict]) -> Dict:
        """Analyze current label usage on preconditions"""
        label_stats = {
            'correct': [],  # Only has 'precondition' label
            'missing_precondition': [],  # Missing 'precondition' label
            'extra_labels': [],  # Has extra labels beyond 'precondition'
            'no_labels': []  # Has no labels at all
        }
        
        for precondition in preconditions:
            key = precondition['key']
            labels = set(precondition['labels'])
            
            if labels == {'precondition'}:
                label_stats['correct'].append(key)
            elif not labels:
                label_stats['no_labels'].append(key)
            elif 'precondition' not in labels:
                label_stats['missing_precondition'].append(key)
            else:
                # Has 'precondition' plus other labels
                label_stats['extra_labels'].append({
                    'key': key,
                    'labels': list(labels),
                    'extra': list(labels - {'precondition'})
                })
        
        return label_stats
    
    def update_labels(self, label_stats: Dict) -> Dict:
        """Update labels on preconditions to ensure only 'precondition' label exists"""
        print("\n=== Updating Precondition Labels ===\n")
        
        update_summary = {
            'successful': [],
            'failed': [],
            'skipped': []
        }
        
        # Handle preconditions with no labels
        for key in label_stats['no_labels']:
            try:
                issue = self.jira.issue(key)
                issue.update(fields={'labels': ['precondition']})
                print(f"✓ {key}: Added 'precondition' label")
                update_summary['successful'].append({
                    'key': key,
                    'action': 'added_label',
                    'labels_before': [],
                    'labels_after': ['precondition']
                })
            except Exception as e:
                print(f"✗ {key}: Failed to add label - {str(e)}")
                update_summary['failed'].append({
                    'key': key,
                    'action': 'add_label',
                    'error': str(e)
                })
        
        # Handle preconditions missing 'precondition' label
        for key in label_stats['missing_precondition']:
            try:
                issue = self.jira.issue(key)
                current_labels = issue.fields.labels or []
                new_labels = current_labels + ['precondition']
                issue.update(fields={'labels': new_labels})
                print(f"✓ {key}: Added 'precondition' to existing labels")
                update_summary['successful'].append({
                    'key': key,
                    'action': 'added_to_existing',
                    'labels_before': current_labels,
                    'labels_after': new_labels
                })
            except Exception as e:
                print(f"✗ {key}: Failed to add label - {str(e)}")
                update_summary['failed'].append({
                    'key': key,
                    'action': 'add_to_existing',
                    'error': str(e)
                })
        
        # Handle preconditions with extra labels
        for item in label_stats['extra_labels']:
            key = item['key']
            try:
                issue = self.jira.issue(key)
                issue.update(fields={'labels': ['precondition']})
                print(f"✓ {key}: Removed extra labels {item['extra']}")
                update_summary['successful'].append({
                    'key': key,
                    'action': 'removed_extra',
                    'labels_before': item['labels'],
                    'labels_after': ['precondition'],
                    'removed': item['extra']
                })
            except Exception as e:
                print(f"✗ {key}: Failed to update labels - {str(e)}")
                update_summary['failed'].append({
                    'key': key,
                    'action': 'remove_extra',
                    'error': str(e)
                })
        
        # Skip the ones that are already correct
        for key in label_stats['correct']:
            update_summary['skipped'].append({
                'key': key,
                'reason': 'Already has correct labels'
            })
        
        return update_summary
    
    def generate_report(self, preconditions: List[Dict], label_stats: Dict, update_summary: Dict):
        """Generate a detailed report of the label cleanup operation"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                  'logs', f'precondition_label_cleanup_report_{timestamp}.json')
        
        report = {
            'timestamp': timestamp,
            'total_preconditions': len(preconditions),
            'label_analysis': {
                'correct': len(label_stats['correct']),
                'missing_precondition_label': len(label_stats['missing_precondition']),
                'extra_labels': len(label_stats['extra_labels']),
                'no_labels': len(label_stats['no_labels'])
            },
            'label_details': label_stats,
            'update_summary': {
                'successful': len(update_summary['successful']),
                'failed': len(update_summary['failed']),
                'skipped': len(update_summary['skipped'])
            },
            'update_details': update_summary
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n\n=== Label Cleanup Summary ===")
        print(f"Report saved to: {report_file}")
        print(f"\nLabel Analysis:")
        print(f"  Already correct: {len(label_stats['correct'])}")
        print(f"  Missing 'precondition' label: {len(label_stats['missing_precondition'])}")
        print(f"  Has extra labels: {len(label_stats['extra_labels'])}")
        print(f"  No labels: {len(label_stats['no_labels'])}")
        print(f"\nUpdates:")
        print(f"  Successful: {len(update_summary['successful'])}")
        print(f"  Failed: {len(update_summary['failed'])}")
        print(f"  Skipped: {len(update_summary['skipped'])}")
        
        # Print details of extra labels found
        if label_stats['extra_labels']:
            print("\nExtra labels found and removed:")
            for item in label_stats['extra_labels']:
                print(f"  {item['key']}: {', '.join(item['extra'])}")
        
        return report_file
    
    def run(self):
        """Execute the full label cleanup process"""
        print("Starting Precondition Label Cleanup Process")
        print("=" * 50)
        
        # Step 1: Get all preconditions
        preconditions = self.get_all_preconditions()
        
        # Step 2: Analyze current labels
        label_stats = self.analyze_labels(preconditions)
        
        # Step 3: Update labels
        update_summary = self.update_labels(label_stats)
        
        # Step 4: Generate report
        report_file = self.generate_report(preconditions, label_stats, update_summary)
        
        print("\nLabel cleanup process completed!")
        return report_file


if __name__ == "__main__":
    cleanup = PreconditionLabelCleanup()
    cleanup.run()