#!/usr/bin/env python3
"""
Remove unnecessary migration labels from XRAY tests
Removes: imported-from-csv, rerun-import, testrails-migration
Preserves all organizational labels (surface-*, feature-*)
"""

import os
import sys
import time
import requests
from requests.auth import HTTPBasicAuth
import argparse
import logging
from typing import Dict, List, Set
import getpass

# Configuration
JIRA_BASE_URL = os.environ.get('JIRA_BASE_URL', '')
JIRA_EMAIL = os.environ.get('JIRA_EMAIL', '')
JIRA_TOKEN = os.environ.get('ATLASSIAN_TOKEN', '')
PROJECT_KEY = 'MLBAPP'
RATE_LIMIT_DELAY = 0.3  # Seconds between updates

# Labels to remove (both cases)
LABELS_TO_REMOVE = [
    'imported-from-csv',
    'rerun-import', 
    'testrails-migration',
    'IMPORTED-FROM-CSV',
    'RERUN-IMPORT',
    'TESTRAILS-MIGRATION'
]

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cleanup_labels.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class LabelCleanup:
    def __init__(self, base_url: str, email: str, token: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(email, token)
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        self.stats = {
            'total': 0,
            'cleaned': 0,
            'failed': 0,
            'skipped': 0
        }
        self.labels_removed = {}
    
    def should_remove_label(self, label: str) -> bool:
        """Check if a label should be removed"""
        return label in LABELS_TO_REMOVE
    
    def clean_labels(self, current_labels: List[str]) -> List[str]:
        """Remove migration labels, preserve organizational labels"""
        cleaned_labels = []
        removed_labels = []
        
        for label in current_labels:
            if self.should_remove_label(label):
                removed_labels.append(label)
                # Track which labels we're removing
                self.labels_removed[label] = self.labels_removed.get(label, 0) + 1
            else:
                cleaned_labels.append(label)
        
        return cleaned_labels, removed_labels
    
    def get_tests_with_migration_labels(self) -> List[Dict]:
        """Get all tests that have migration labels"""
        logger.info("Fetching tests with migration labels...")
        
        all_tests = []
        start_at = 0
        max_results = 100
        
        # Build JQL to find tests with any of the migration labels
        label_conditions = ' OR '.join([f'labels = "{label}"' for label in LABELS_TO_REMOVE])
        jql = f'project = {PROJECT_KEY} AND issuetype = "Xray Test" AND ({label_conditions})'
        
        while True:
            url = f"{self.base_url}/rest/api/2/search"
            params = {
                'jql': jql,
                'startAt': start_at,
                'maxResults': max_results,
                'fields': 'summary,labels'
            }
            
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                issues = data.get('issues', [])
                all_tests.extend(issues)
                
                if len(issues) < max_results:
                    break
                
                start_at += max_results
            else:
                logger.error(f"Failed to query JIRA: {response.status_code}")
                logger.error(f"Response: {response.text}")
                break
        
        logger.info(f"Found {len(all_tests)} tests with migration labels")
        return all_tests
    
    def update_test_labels(self, test_key: str, new_labels: List[str]) -> bool:
        """Update a test's labels"""
        url = f"{self.base_url}/rest/api/2/issue/{test_key}"
        payload = {
            "fields": {
                "labels": new_labels
            }
        }
        
        response = self.session.put(url, json=payload)
        
        if response.status_code == 204:
            return True
        else:
            logger.error(f"Failed to update {test_key}: {response.status_code} - {response.text}")
            return False
    
    def test_single_cleanup(self, test_key: str) -> bool:
        """Test cleanup on a single test"""
        logger.info(f"\nTesting cleanup on {test_key}...")
        
        # Get current test details
        url = f"{self.base_url}/rest/api/2/issue/{test_key}"
        response = self.session.get(url)
        
        if response.status_code != 200:
            logger.error(f"Failed to get test: {response.status_code}")
            return False
        
        issue = response.json()
        current_labels = issue['fields'].get('labels', [])
        summary = issue['fields']['summary']
        
        logger.info(f"Test: {summary}")
        logger.info(f"Current labels: {current_labels}")
        
        # Clean labels
        cleaned_labels, removed_labels = self.clean_labels(current_labels)
        
        if not removed_labels:
            logger.info("No migration labels to remove")
            return True
        
        logger.info(f"Labels to remove: {removed_labels}")
        logger.info(f"Labels after cleanup: {cleaned_labels}")
        
        # Update test
        if self.update_test_labels(test_key, cleaned_labels):
            logger.info("✓ Update successful!")
            
            # Verify
            response = self.session.get(url)
            if response.status_code == 200:
                updated_labels = response.json()['fields'].get('labels', [])
                logger.info(f"Verified labels: {updated_labels}")
                return True
        
        return False
    
    def cleanup_all_tests(self, dry_run: bool = False):
        """Clean up migration labels from all tests"""
        # Get all tests with migration labels
        tests = self.get_tests_with_migration_labels()
        self.stats['total'] = len(tests)
        
        if self.stats['total'] == 0:
            logger.info("No tests found with migration labels!")
            return
        
        # Process tests
        start_time = time.time()
        for i, test in enumerate(tests):
            test_key = test['key']
            summary = test['fields']['summary']
            current_labels = test['fields'].get('labels', [])
            
            # Clean labels
            cleaned_labels, removed_labels = self.clean_labels(current_labels)
            
            if not removed_labels:
                logger.debug(f"Skipping {test_key} - no migration labels found")
                self.stats['skipped'] += 1
                continue
            
            if dry_run:
                logger.info(f"[DRY RUN] Would remove from {test_key}: {removed_labels}")
                logger.info(f"          Keeping: {cleaned_labels}")
                self.stats['cleaned'] += 1
            else:
                # Update test
                if self.update_test_labels(test_key, cleaned_labels):
                    logger.info(f"✓ Cleaned {test_key} - removed: {removed_labels}")
                    self.stats['cleaned'] += 1
                else:
                    self.stats['failed'] += 1
                
                # Rate limiting
                time.sleep(RATE_LIMIT_DELAY)
            
            # Progress update
            if (i + 1) % 50 == 0:
                elapsed = time.time() - start_time
                rate = self.stats['cleaned'] / elapsed if elapsed > 0 else 0
                remaining = (self.stats['total'] - self.stats['cleaned'] - self.stats['skipped']) / rate if rate > 0 else 0
                logger.info(f"Progress: {i + 1}/{len(tests)} tests processed ({rate:.1f} tests/sec, ~{remaining:.0f}s remaining)")
    
    def print_summary(self):
        """Print cleanup summary"""
        logger.info("\n" + "="*60)
        logger.info("LABEL CLEANUP SUMMARY")
        logger.info("="*60)
        logger.info(f"Total tests with migration labels: {self.stats['total']}")
        logger.info(f"Successfully cleaned: {self.stats['cleaned']}")
        logger.info(f"Failed to clean: {self.stats['failed']}")
        logger.info(f"Skipped (no labels to remove): {self.stats['skipped']}")
        
        if self.labels_removed:
            logger.info("\n" + "="*60)
            logger.info("LABELS REMOVED")
            logger.info("="*60)
            for label, count in sorted(self.labels_removed.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"  {label}: {count} occurrences")
        
        logger.info("="*60)

def main():
    parser = argparse.ArgumentParser(description='Clean up migration labels from XRAY tests')
    parser.add_argument('--test', help='Test on a single issue first (e.g., MLBAPP-5177)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    
    args = parser.parse_args()
    
    # Get credentials
    global JIRA_BASE_URL, JIRA_EMAIL, JIRA_TOKEN
    
    if not JIRA_BASE_URL:
        JIRA_BASE_URL = input("Enter JIRA Base URL (e.g., https://baseball.atlassian.net): ").strip()
    
    if not JIRA_EMAIL:
        JIRA_EMAIL = input("Enter JIRA Email: ").strip()
    
    if not JIRA_TOKEN:
        JIRA_TOKEN = getpass.getpass("Enter ATLASSIAN API Token: ").strip()
    
    logger.info("Starting migration label cleanup")
    logger.info(f"JIRA URL: {JIRA_BASE_URL}")
    logger.info(f"Project: {PROJECT_KEY}")
    logger.info(f"Labels to remove: {', '.join(LABELS_TO_REMOVE)}")
    
    # Create cleanup instance
    cleanup = LabelCleanup(JIRA_BASE_URL, JIRA_EMAIL, JIRA_TOKEN)
    
    if args.test:
        # Test mode - single issue
        success = cleanup.test_single_cleanup(args.test)
        if success:
            logger.info("\n✅ Test cleanup successful!")
            logger.info("You can now run the full cleanup with: python3 cleanup_migration_labels.py")
        else:
            logger.info("\n❌ Test cleanup failed!")
    else:
        # Full cleanup
        cleanup.cleanup_all_tests(args.dry_run)
        cleanup.print_summary()
        
        if not args.dry_run:
            logger.info("\n✅ Label cleanup complete!")
            logger.info("\nYour tests now have clean organizational labels without migration artifacts.")

if __name__ == '__main__':
    main()