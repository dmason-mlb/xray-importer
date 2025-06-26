#!/usr/bin/env python3
"""
Create XRAY Test Plans based on organizational labels
Alternative to Test Sets - creates Test Plans to organize tests
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
JIRA_BASE_URL = os.environ.get('JIRA_BASE_URL', 'https://baseball.atlassian.net')
JIRA_EMAIL = os.environ.get('JIRA_EMAIL', '')
JIRA_TOKEN = os.environ.get('ATLASSIAN_TOKEN', '')
PROJECT_KEY = 'MLBAPP'
RATE_LIMIT_DELAY = 0.5  # Seconds between API calls

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('create_test_plans.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TestPlanCreator:
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
            'test_plans_created': 0,
            'test_plans_failed': 0,
            'test_plans_skipped': 0
        }
        self.label_test_counts = {}
        self.created_test_plans = {}
        self.test_plan_type_id = None
    
    def find_test_plan_issue_type(self) -> str:
        """Find the Test Plan issue type ID"""
        # First check project issue types
        url = f"{self.base_url}/rest/api/2/project/{PROJECT_KEY}"
        response = self.session.get(url)
        
        if response.status_code == 200:
            project_data = response.json()
            issue_types = project_data.get('issueTypes', [])
            
            for issue_type in issue_types:
                if issue_type['name'] == 'Test Plan':
                    logger.info(f"Found Test Plan issue type: {issue_type['id']}")
                    return issue_type['id']
        
        # If not found, search for existing Test Plans
        jql = f'project = {PROJECT_KEY} AND issuetype = "Test Plan"'
        url = f"{self.base_url}/rest/api/2/search"
        params = {'jql': jql, 'maxResults': 1}
        
        response = self.session.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['total'] > 0:
                issue_type_id = data['issues'][0]['fields']['issuetype']['id']
                logger.info(f"Found Test Plan issue type from existing issue: {issue_type_id}")
                return issue_type_id
        
        logger.error("Could not find Test Plan issue type")
        return None
    
    def get_organizational_labels(self) -> Dict[str, int]:
        """Get all organizational labels and their test counts"""
        logger.info("Fetching organizational labels...")
        
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
    
    def check_existing_test_plan(self, label: str) -> str:
        """Check if a Test Plan already exists for this label"""
        summary = self.get_test_plan_summary(label)
        jql = f'project = {PROJECT_KEY} AND issuetype = "Test Plan" AND summary ~ "{summary}"'
        
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
    
    def get_test_plan_summary(self, label: str) -> str:
        """Generate Test Plan summary from label"""
        if label.startswith('surface-'):
            surface = label.replace('surface-', '').replace('-', ' ').title()
            return f"{surface} Surface Test Plan"
        elif label.startswith('feature-'):
            feature = label.replace('feature-', '').replace('-', ' ').title()
            return f"{feature} Feature Test Plan"
        else:
            return f"{label} Test Plan"
    
    def get_test_plan_description(self, label: str, test_count: int) -> str:
        """Generate Test Plan description"""
        label_type = "Surface" if label.startswith('surface-') else "Feature"
        return f"""Automated Test Plan for {label} tests.

**Label:** `{label}`
**Type:** {label_type}
**Number of Tests:** {test_count}

This Test Plan contains all XRAY tests tagged with the `{label}` label.

To find all tests in this plan, use JQL:
```
project = {PROJECT_KEY} AND issuetype = "Xray Test" AND labels = "{label}"
```

Generated automatically from test import labels."""
    
    def create_test_plan(self, label: str, test_count: int) -> str:
        """Create a Test Plan for a label"""
        if not self.test_plan_type_id:
            logger.error("Test Plan issue type not found")
            return None
        
        summary = self.get_test_plan_summary(label)
        description = self.get_test_plan_description(label, test_count)
        
        url = f"{self.base_url}/rest/api/2/issue"
        payload = {
            "fields": {
                "project": {
                    "key": PROJECT_KEY
                },
                "issuetype": {
                    "id": self.test_plan_type_id
                },
                "summary": summary,
                "description": description,
                "labels": [label, "auto-generated-test-plan"]
            }
        }
        
        response = self.session.post(url, json=payload)
        
        if response.status_code == 201:
            issue = response.json()
            test_plan_key = issue['key']
            logger.info(f"✓ Created Test Plan: {test_plan_key} - {summary}")
            return test_plan_key
        else:
            logger.error(f"Failed to create Test Plan for {label}: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None
    
    def add_tests_to_test_plan(self, test_plan_key: str, label: str):
        """Add all tests with a specific label to a Test Plan"""
        logger.info(f"Adding tests with label '{label}' to Test Plan {test_plan_key}...")
        
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
        
        logger.info(f"Found {len(test_keys)} tests to add to Test Plan")
        
        # Add tests to Test Plan using Xray REST API
        xray_url = f"{self.base_url}/rest/raven/1.0/api/testplan/{test_plan_key}/test"
        
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
        
        logger.info(f"✓ Successfully added {len(test_keys)} tests to Test Plan {test_plan_key}")
        return True
    
    def create_all_test_plans(self, dry_run: bool = False, skip_existing: bool = True):
        """Create Test Plans for all organizational labels"""
        # Get Test Plan issue type
        self.test_plan_type_id = self.find_test_plan_issue_type()
        if not self.test_plan_type_id:
            logger.error("Cannot proceed without Test Plan issue type")
            logger.info("\nTest Plans may not be enabled in your project.")
            logger.info("Please check with your JIRA/XRAY administrator.")
            return
        
        # Get all labels
        labels = self.get_organizational_labels()
        self.stats['total_labels'] = len(labels)
        
        # Sort labels
        surface_labels = sorted([(k, v) for k, v in labels.items() if k.startswith('surface-')], 
                               key=lambda x: x[1], reverse=True)
        feature_labels = sorted([(k, v) for k, v in labels.items() if k.startswith('feature-')], 
                               key=lambda x: x[1], reverse=True)
        
        all_sorted_labels = surface_labels + feature_labels
        
        logger.info(f"\nCreating Test Plans for {len(all_sorted_labels)} labels...")
        logger.info("="*60)
        
        for label, test_count in all_sorted_labels:
            logger.info(f"\nProcessing: {label} ({test_count} tests)")
            
            if dry_run:
                summary = self.get_test_plan_summary(label)
                logger.info(f"[DRY RUN] Would create Test Plan: {summary}")
                self.stats['test_plans_created'] += 1
                continue
            
            # Check if Test Plan already exists
            if skip_existing:
                existing_key = self.check_existing_test_plan(label)
                if existing_key:
                    logger.info(f"  Test Plan already exists: {existing_key}")
                    self.stats['test_plans_skipped'] += 1
                    self.created_test_plans[label] = existing_key
                    continue
            
            # Create Test Plan
            test_plan_key = self.create_test_plan(label, test_count)
            
            if test_plan_key:
                self.created_test_plans[label] = test_plan_key
                self.stats['test_plans_created'] += 1
                
                # Add tests to Test Plan
                if not self.add_tests_to_test_plan(test_plan_key, label):
                    logger.warning(f"  Created Test Plan but failed to add all tests")
            else:
                self.stats['test_plans_failed'] += 1
            
            # Rate limiting
            time.sleep(RATE_LIMIT_DELAY)
    
    def print_summary(self):
        """Print creation summary"""
        logger.info("\n" + "="*60)
        logger.info("TEST PLAN CREATION SUMMARY")
        logger.info("="*60)
        logger.info(f"Total organizational labels: {self.stats['total_labels']}")
        logger.info(f"Test Plans created: {self.stats['test_plans_created']}")
        logger.info(f"Test Plans skipped (existing): {self.stats['test_plans_skipped']}")
        logger.info(f"Test Plans failed: {self.stats['test_plans_failed']}")
        
        if self.created_test_plans:
            logger.info("\n" + "="*60)
            logger.info("CREATED TEST PLANS")
            logger.info("="*60)
            
            # Group by type
            surface_plans = [(k, v) for k, v in self.created_test_plans.items() if k.startswith('surface-')]
            feature_plans = [(k, v) for k, v in self.created_test_plans.items() if k.startswith('feature-')]
            
            if surface_plans:
                logger.info("\nSurface Test Plans:")
                for label, key in sorted(surface_plans):
                    count = self.label_test_counts.get(label, 0)
                    logger.info(f"  {key}: {self.get_test_plan_summary(label)} ({count} tests)")
            
            if feature_plans:
                logger.info("\nFeature Test Plans:")
                for label, key in sorted(feature_plans):
                    count = self.label_test_counts.get(label, 0)
                    logger.info(f"  {key}: {self.get_test_plan_summary(label)} ({count} tests)")
        
        logger.info("="*60)

def main():
    parser = argparse.ArgumentParser(description='Create XRAY Test Plans from organizational labels')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be created without making changes')
    parser.add_argument('--skip-existing', action='store_true', default=True, help='Skip creating Test Plans that already exist (default: true)')
    parser.add_argument('--label', help='Create Test Plan for a specific label only')
    
    args = parser.parse_args()
    
    # Get credentials
    global JIRA_EMAIL, JIRA_TOKEN
    
    if not JIRA_EMAIL:
        JIRA_EMAIL = input("Enter JIRA Email: ").strip()
    
    if not JIRA_TOKEN:
        JIRA_TOKEN = getpass.getpass("Enter ATLASSIAN API Token: ").strip()
    
    logger.info("Starting XRAY Test Plan creation from labels")
    logger.info(f"JIRA URL: {JIRA_BASE_URL}")
    logger.info(f"Project: {PROJECT_KEY}")
    
    # Create test plan creator
    creator = TestPlanCreator(JIRA_BASE_URL, JIRA_EMAIL, JIRA_TOKEN)
    
    if args.label:
        # Create single Test Plan
        creator.test_plan_type_id = creator.find_test_plan_issue_type()
        if creator.test_plan_type_id:
            # Get test count for label
            creator.get_organizational_labels()
            test_count = creator.label_test_counts.get(args.label, 0)
            
            if test_count > 0:
                test_plan_key = creator.create_test_plan(args.label, test_count)
                if test_plan_key:
                    creator.add_tests_to_test_plan(test_plan_key, args.label)
                    logger.info(f"\n✅ Created Test Plan {test_plan_key} for label '{args.label}'")
            else:
                logger.error(f"No tests found with label '{args.label}'")
    else:
        # Create all Test Plans
        creator.create_all_test_plans(args.dry_run, args.skip_existing)
        creator.print_summary()
        
        if not args.dry_run:
            logger.info("\n✅ Test Plan creation complete!")
            logger.info("\nYou can now:")
            logger.info("1. View Test Plans in XRAY")
            logger.info("2. Execute tests by Test Plan")
            logger.info("3. Create Test Executions from Test Plans")
            logger.info("4. Track test coverage by surface/feature")

if __name__ == '__main__':
    main()