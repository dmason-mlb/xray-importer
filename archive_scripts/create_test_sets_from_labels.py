#!/usr/bin/env python3
"""
Create XRAY Test Sets based on organizational labels
Creates one Test Set for each surface and feature label
"""

import os
import sys
import time
import requests
from requests.auth import HTTPBasicAuth
import argparse
import logging
from typing import Dict, List, Set, Tuple
import getpass
import json

# Configuration
JIRA_BASE_URL = os.environ.get('JIRA_BASE_URL', '')
JIRA_EMAIL = os.environ.get('JIRA_EMAIL', '')
JIRA_TOKEN = os.environ.get('ATLASSIAN_TOKEN', '')
PROJECT_KEY = 'MLBAPP'
RATE_LIMIT_DELAY = 0.5  # Seconds between API calls

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('create_test_sets.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TestSetCreator:
    def __init__(self, base_url: str, email: str, token: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(email, token)
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        self.stats = {
            'total_labels': 0,
            'test_sets_created': 0,
            'test_sets_failed': 0,
            'test_sets_skipped': 0
        }
        self.label_test_counts = {}
        self.created_test_sets = {}
    
    def get_xray_test_set_issue_type(self) -> str:
        """Get the issue type ID for Xray Test Set"""
        # First check project-specific issue types
        url = f"{self.base_url}/rest/api/2/project/{PROJECT_KEY}"
        response = self.session.get(url)
        
        if response.status_code == 200:
            project_data = response.json()
            issue_types = project_data.get('issueTypes', [])
            
            for issue_type in issue_types:
                if issue_type['name'] == 'Test Set':
                    logger.info(f"Found Test Set issue type: {issue_type['id']}")
                    return issue_type['id']
        
        # Fallback to global issue types
        url = f"{self.base_url}/rest/api/2/issuetype"
        response = self.session.get(url)
        
        if response.status_code == 200:
            issue_types = response.json()
            for issue_type in issue_types:
                if issue_type['name'] == 'Test Set':
                    logger.info(f"Found Test Set issue type: {issue_type['id']}")
                    return issue_type['id']
        
        logger.error("Could not find Test Set issue type")
        return None
    
    def get_organizational_labels(self) -> Dict[str, int]:
        """Get all organizational labels and their test counts"""
        logger.info("Fetching organizational labels...")
        
        # Get all tests with organizational labels
        # Note: JQL doesn't support wildcards in labels, so we need to get all tests and filter
        jql = f'project = {PROJECT_KEY} AND issuetype = "Xray Test" AND labels is not EMPTY'
        url = f"{self.base_url}/rest/api/2/search"
        
        all_labels = {}
        start_at = 0
        max_results = 100
        
        while True:
            params = {
                'jql': jql,
                'startAt': start_at,
                'maxResults': max_results,
                'fields': 'labels'
            }
            
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                issues = data.get('issues', [])
                
                # Extract organizational labels
                for issue in issues:
                    labels = issue['fields'].get('labels', [])
                    for label in labels:
                        if label.startswith('surface-') or label.startswith('feature-'):
                            all_labels[label] = all_labels.get(label, 0) + 1
                
                if len(issues) < max_results:
                    break
                
                start_at += max_results
            else:
                logger.error(f"Failed to query JIRA: {response.status_code}")
                break
        
        self.label_test_counts = all_labels
        logger.info(f"Found {len(all_labels)} unique organizational labels")
        return all_labels
    
    def check_existing_test_set(self, label: str) -> str:
        """Check if a Test Set already exists for this label"""
        # Search for existing test set with matching summary
        summary = self.get_test_set_summary(label)
        jql = f'project = {PROJECT_KEY} AND issuetype = "Test Set" AND summary ~ "{summary}"'
        
        url = f"{self.base_url}/rest/api/2/search"
        params = {
            'jql': jql,
            'maxResults': 1,
            'fields': 'summary'
        }
        
        response = self.session.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['total'] > 0:
                return data['issues'][0]['key']
        
        return None
    
    def get_test_set_summary(self, label: str) -> str:
        """Generate Test Set summary from label"""
        # Convert label to readable format
        if label.startswith('surface-'):
            surface = label.replace('surface-', '').replace('-', ' ').title()
            return f"{surface} Surface Tests"
        elif label.startswith('feature-'):
            feature = label.replace('feature-', '').replace('-', ' ').title()
            return f"{feature} Feature Tests"
        else:
            return f"{label} Tests"
    
    def get_test_set_description(self, label: str, test_count: int) -> str:
        """Generate Test Set description"""
        label_type = "Surface" if label.startswith('surface-') else "Feature"
        return f"""Automated Test Set for {label} tests.

**Label:** `{label}`
**Type:** {label_type}
**Number of Tests:** {test_count}

This Test Set contains all XRAY tests tagged with the `{label}` label.

To find all tests in this set, use JQL:
```
project = {PROJECT_KEY} AND issuetype = "Xray Test" AND labels = "{label}"
```

Generated automatically from test import labels."""
    
    def create_test_set(self, label: str, test_count: int, test_set_type_id: str) -> str:
        """Create a Test Set for a label"""
        summary = self.get_test_set_summary(label)
        description = self.get_test_set_description(label, test_count)
        
        # Create the Test Set
        url = f"{self.base_url}/rest/api/2/issue"
        payload = {
            "fields": {
                "project": {
                    "key": PROJECT_KEY
                },
                "issuetype": {
                    "id": test_set_type_id
                },
                "summary": summary,
                "description": description,
                "labels": [label, "auto-generated-test-set"]
            }
        }
        
        response = self.session.post(url, json=payload)
        
        if response.status_code == 201:
            issue = response.json()
            test_set_key = issue['key']
            logger.info(f"✓ Created Test Set: {test_set_key} - {summary}")
            return test_set_key
        else:
            logger.error(f"Failed to create Test Set for {label}: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None
    
    def add_tests_to_test_set(self, test_set_key: str, label: str):
        """Add all tests with a specific label to a Test Set"""
        logger.info(f"Adding tests with label '{label}' to Test Set {test_set_key}...")
        
        # Get all tests with this label
        jql = f'project = {PROJECT_KEY} AND issuetype = "Xray Test" AND labels = "{label}"'
        url = f"{self.base_url}/rest/api/2/search"
        
        test_keys = []
        start_at = 0
        max_results = 100
        
        while True:
            params = {
                'jql': jql,
                'startAt': start_at,
                'maxResults': max_results,
                'fields': 'key'
            }
            
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                issues = data.get('issues', [])
                test_keys.extend([issue['key'] for issue in issues])
                
                if len(issues) < max_results:
                    break
                
                start_at += max_results
            else:
                logger.error(f"Failed to get tests: {response.status_code}")
                return False
        
        if not test_keys:
            logger.warning(f"No tests found with label '{label}'")
            return True
        
        logger.info(f"Found {len(test_keys)} tests to add to Test Set")
        
        # Add tests to Test Set using Xray REST API
        xray_url = f"{self.base_url}/rest/raven/1.0/api/testset/{test_set_key}/test"
        
        # Add tests in batches
        batch_size = 50
        for i in range(0, len(test_keys), batch_size):
            batch = test_keys[i:i+batch_size]
            payload = {
                "add": batch
            }
            
            response = self.session.post(xray_url, json=payload)
            
            if response.status_code in [200, 201, 204]:
                logger.info(f"  Added batch {i//batch_size + 1}: {len(batch)} tests")
            else:
                logger.error(f"  Failed to add tests: {response.status_code}")
                logger.error(f"  Response: {response.text}")
                return False
            
            time.sleep(RATE_LIMIT_DELAY)
        
        logger.info(f"✓ Successfully added {len(test_keys)} tests to Test Set {test_set_key}")
        return True
    
    def create_all_test_sets(self, dry_run: bool = False, skip_existing: bool = True):
        """Create Test Sets for all organizational labels"""
        # Get Test Set issue type
        test_set_type_id = self.get_xray_test_set_issue_type()
        if not test_set_type_id:
            logger.error("Cannot proceed without Test Set issue type")
            return
        
        # Get all labels
        labels = self.get_organizational_labels()
        self.stats['total_labels'] = len(labels)
        
        # Sort labels: surface labels first, then feature labels by count
        surface_labels = sorted([(k, v) for k, v in labels.items() if k.startswith('surface-')], 
                               key=lambda x: x[1], reverse=True)
        feature_labels = sorted([(k, v) for k, v in labels.items() if k.startswith('feature-')], 
                               key=lambda x: x[1], reverse=True)
        
        all_sorted_labels = surface_labels + feature_labels
        
        logger.info(f"\nCreating Test Sets for {len(all_sorted_labels)} labels...")
        logger.info("="*60)
        
        for label, test_count in all_sorted_labels:
            logger.info(f"\nProcessing: {label} ({test_count} tests)")
            
            if dry_run:
                summary = self.get_test_set_summary(label)
                logger.info(f"[DRY RUN] Would create Test Set: {summary}")
                self.stats['test_sets_created'] += 1
                continue
            
            # Check if Test Set already exists
            if skip_existing:
                existing_key = self.check_existing_test_set(label)
                if existing_key:
                    logger.info(f"  Test Set already exists: {existing_key}")
                    self.stats['test_sets_skipped'] += 1
                    self.created_test_sets[label] = existing_key
                    continue
            
            # Create Test Set
            test_set_key = self.create_test_set(label, test_count, test_set_type_id)
            
            if test_set_key:
                self.created_test_sets[label] = test_set_key
                self.stats['test_sets_created'] += 1
                
                # Add tests to Test Set
                if not self.add_tests_to_test_set(test_set_key, label):
                    logger.warning(f"  Created Test Set but failed to add all tests")
            else:
                self.stats['test_sets_failed'] += 1
            
            # Rate limiting
            time.sleep(RATE_LIMIT_DELAY)
    
    def print_summary(self):
        """Print creation summary"""
        logger.info("\n" + "="*60)
        logger.info("TEST SET CREATION SUMMARY")
        logger.info("="*60)
        logger.info(f"Total organizational labels: {self.stats['total_labels']}")
        logger.info(f"Test Sets created: {self.stats['test_sets_created']}")
        logger.info(f"Test Sets skipped (existing): {self.stats['test_sets_skipped']}")
        logger.info(f"Test Sets failed: {self.stats['test_sets_failed']}")
        
        if self.created_test_sets:
            logger.info("\n" + "="*60)
            logger.info("CREATED TEST SETS")
            logger.info("="*60)
            
            # Group by type
            surface_sets = [(k, v) for k, v in self.created_test_sets.items() if k.startswith('surface-')]
            feature_sets = [(k, v) for k, v in self.created_test_sets.items() if k.startswith('feature-')]
            
            if surface_sets:
                logger.info("\nSurface Test Sets:")
                for label, key in sorted(surface_sets):
                    count = self.label_test_counts.get(label, 0)
                    logger.info(f"  {key}: {self.get_test_set_summary(label)} ({count} tests)")
            
            if feature_sets:
                logger.info("\nFeature Test Sets:")
                for label, key in sorted(feature_sets):
                    count = self.label_test_counts.get(label, 0)
                    logger.info(f"  {key}: {self.get_test_set_summary(label)} ({count} tests)")
        
        logger.info("="*60)

def main():
    parser = argparse.ArgumentParser(description='Create XRAY Test Sets from organizational labels')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be created without making changes')
    parser.add_argument('--skip-existing', action='store_true', default=True, help='Skip creating Test Sets that already exist (default: true)')
    parser.add_argument('--label', help='Create Test Set for a specific label only')
    
    args = parser.parse_args()
    
    # Get credentials
    global JIRA_BASE_URL, JIRA_EMAIL, JIRA_TOKEN
    
    if not JIRA_BASE_URL:
        JIRA_BASE_URL = input("Enter JIRA Base URL (e.g., https://baseball.atlassian.net): ").strip()
    
    if not JIRA_EMAIL:
        JIRA_EMAIL = input("Enter JIRA Email: ").strip()
    
    if not JIRA_TOKEN:
        JIRA_TOKEN = getpass.getpass("Enter ATLASSIAN API Token: ").strip()
    
    logger.info("Starting XRAY Test Set creation from labels")
    logger.info(f"JIRA URL: {JIRA_BASE_URL}")
    logger.info(f"Project: {PROJECT_KEY}")
    
    # Create test set creator
    creator = TestSetCreator(JIRA_BASE_URL, JIRA_EMAIL, JIRA_TOKEN)
    
    if args.label:
        # Create single Test Set
        test_set_type_id = creator.get_xray_test_set_issue_type()
        if test_set_type_id:
            # Get test count for label
            creator.get_organizational_labels()
            test_count = creator.label_test_counts.get(args.label, 0)
            
            if test_count > 0:
                test_set_key = creator.create_test_set(args.label, test_count, test_set_type_id)
                if test_set_key:
                    creator.add_tests_to_test_set(test_set_key, args.label)
                    logger.info(f"\n✅ Created Test Set {test_set_key} for label '{args.label}'")
            else:
                logger.error(f"No tests found with label '{args.label}'")
    else:
        # Create all Test Sets
        creator.create_all_test_sets(args.dry_run, args.skip_existing)
        creator.print_summary()
        
        if not args.dry_run:
            logger.info("\n✅ Test Set creation complete!")
            logger.info("\nYou can now:")
            logger.info("1. View Test Sets in XRAY Test Repository")
            logger.info("2. Execute tests by Test Set")
            logger.info("3. Create Test Plans from Test Sets")
            logger.info("4. Track test coverage by surface/feature")

if __name__ == '__main__':
    main()