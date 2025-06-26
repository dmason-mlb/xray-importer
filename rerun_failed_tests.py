#!/usr/bin/env python3
"""
Re-run failed test imports from previous import attempt
This script will read the import log and retry failed tests without the problematic custom field
"""

import csv
import json
import os
import sys
import time
import re
from datetime import datetime
from typing import List, Dict, Any, Set
import requests
from requests.auth import HTTPBasicAuth
import argparse
import logging

# Configuration
JIRA_BASE_URL = os.environ.get('JIRA_BASE_URL', 'https://your-domain.atlassian.net')
JIRA_EMAIL = os.environ.get('JIRA_EMAIL', '')
JIRA_TOKEN = os.environ.get('ATLASSIAN_TOKEN', '')
PROJECT_KEY = 'MLBAPP'
BATCH_SIZE = 900  # Stay under 1000 limit with buffer
RATE_LIMIT_DELAY = 2  # Seconds between batches

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('xray_rerun_failed.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class FailedTestImporter:
    def __init__(self, base_url: str, email: str, token: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(email, token)
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        self.import_stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'batches': 0,
            'skipped': 0
        }
        self.failed_tests = []
        self.successful_tests = set()
    
    def parse_import_log(self, log_file: str):
        """Parse the import log to identify failed tests"""
        logger.info(f"Parsing import log: {log_file}")
        
        with open(log_file, 'r') as f:
            for line in f:
                # Look for successful test creations
                if "Successfully imported:" in line:
                    # Extract the success count
                    match = re.search(r'Successfully imported: (\d+)', line)
                    if match:
                        logger.info(f"Previous run had {match.group(1)} successful imports")
                
                # Look for failed test entries
                if "Failed to create test" in line:
                    # Extract test title
                    match = re.search(r"Failed to create test '([^']+)'", line)
                    if match:
                        test_title = match.group(1)
                        self.failed_tests.append(test_title)
                
                # Look for successful issue creation
                if "created successfully" in line or "Progress:" in line:
                    # These indicate successful tests, but we'll rely on searching JIRA
                    pass
        
        logger.info(f"Found {len(self.failed_tests)} failed test titles from log")
    
    def get_existing_tests(self):
        """Query JIRA to get all existing test issues in MLBAPP"""
        logger.info("Querying JIRA for existing tests...")
        
        all_tests = []
        start_at = 0
        max_results = 100
        
        while True:
            jql = f'project = {PROJECT_KEY} AND issuetype = "Xray Test" AND labels = "imported-from-csv"'
            url = f"{self.base_url}/rest/api/2/search"
            params = {
                'jql': jql,
                'startAt': start_at,
                'maxResults': max_results,
                'fields': 'summary'
            }
            
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                issues = data.get('issues', [])
                
                for issue in issues:
                    summary = issue['fields']['summary']
                    self.successful_tests.add(summary)
                
                all_tests.extend(issues)
                
                if len(issues) < max_results:
                    break
                
                start_at += max_results
            else:
                logger.error(f"Failed to query JIRA: {response.status_code}")
                break
        
        logger.info(f"Found {len(self.successful_tests)} existing tests in MLBAPP")
        return all_tests
    
    def convert_csv_to_xray_test(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Convert CSV row to XRAY test format (without problematic custom field)"""
        
        # Map priority
        priority_map = {
            '1 - Highest Priority': 'Highest',
            '2 - High Priority': 'High',
            '2 - Medium Priority': 'Medium',
            '3 - Low Priority': 'Low',
            '4 - Lowest Priority': 'Lowest'
        }
        priority = priority_map.get(row.get('Priority', ''), 'Medium')
        
        # Build description from available fields
        description_parts = []
        
        # Add preconditions if available
        if row.get('Preconditions'):
            description_parts.append(f"**Preconditions:**\n{row['Preconditions']}")
        
        if row.get('Section Description'):
            description_parts.append(f"**Section Description:**\n{row['Section Description']}")
        
        # Format test steps more clearly
        test_steps_info = []
        
        # Check for separated steps format
        if row.get('Steps Separated (Step)') and row.get('Steps Separated (Expected Result)'):
            description_parts.append("**Test Steps:**")
            step_actions = row['Steps Separated (Step)'].split('\n')
            expected_results = row['Steps Separated (Expected Result)'].split('\n')
            
            for i, (action, result) in enumerate(zip(step_actions, expected_results), 1):
                if action.strip():
                    test_steps_info.append(f"\n**Step {i}:**")
                    test_steps_info.append(f"Action: {action.strip()}")
                    if result.strip():
                        test_steps_info.append(f"Expected Result: {result.strip()}")
            
            description_parts.extend(test_steps_info)
        
        # Fallback to regular steps field
        elif row.get('Steps'):
            description_parts.append(f"**Test Steps:**\n{row['Steps']}")
        
        # Add expected result if not already included
        if row.get('Expected Result') and not row.get('Steps Separated (Expected Result)'):
            description_parts.append(f"**Expected Result:**\n{row['Expected Result']}")
        
        # Add references if available
        if row.get('References'):
            description_parts.append(f"**References:** {row['References']}")
        
        description = '\n\n'.join(description_parts) if description_parts else ''
        
        # Build test object
        test = {
            'testType': row.get('Type', 'Manual'),
            'fields': {
                'project': {'key': PROJECT_KEY},
                'summary': row.get('Title', ''),
                'description': description,
                'priority': {'name': priority},
                'labels': ['imported-from-csv', 'testrails-migration', 'rerun-import']
            }
        }
        
        # NOTE: We're NOT adding customfield_23269 anymore as it was causing failures
        
        # Add Test Repository path based on Section
        if row.get('Section'):
            test['testRepositoryPath'] = self.build_repository_path(row['Section'])
        
        return test
    
    def build_repository_path(self, section: str) -> str:
        """Build Test Repository path from section string"""
        # Clean and split section path
        parts = section.replace('\\', '/').split('/')
        clean_parts = [p.strip() for p in parts if p.strip()]
        
        # Map to our repository structure
        if 'Home Surface' in section or 'THome Surface' in section:
            base = '/MLBAPP Test Repository/Home Surface'
        elif 'News Surface' in section or 'News' in ' '.join(clean_parts):
            base = '/MLBAPP Test Repository/News Surface'
        elif 'MLBAPP' in section:
            base = '/MLBAPP Test Repository/Core App'
        elif 'Additional' in section:
            # These seem to be news-related based on the content
            base = '/MLBAPP Test Repository/News Surface'
        else:
            base = '/MLBAPP Test Repository/Core App'
        
        # Add sub-paths
        if len(clean_parts) > 1:
            return f"{base}/{'/'.join(clean_parts[1:])}"
        return base
    
    def import_batch(self, tests: List[Dict[str, Any]], batch_num: int, total_batches: int) -> bool:
        """Import a batch of tests via XRAY API"""
        logger.info(f"Importing batch {batch_num}/{total_batches} ({len(tests)} tests)")
        
        success_count = 0
        failed_count = 0
        
        for i, test in enumerate(tests):
            try:
                # Create test as JIRA issue with Xray Test issue type
                issue_data = {
                    'fields': {
                        'project': {'key': PROJECT_KEY},
                        'issuetype': {'id': '16824'},  # Xray Test issue type ID for MLBAPP
                        'summary': test['fields']['summary'],
                        'description': test['fields']['description'],
                        'priority': test['fields']['priority'],
                        'labels': test['fields']['labels']
                    }
                }
                
                # Create issue via JIRA API
                url = f"{self.base_url}/rest/api/2/issue"
                response = self.session.post(url, json=issue_data)
                
                if response.status_code in [200, 201]:
                    success_count += 1
                    issue_key = response.json().get('key')
                    logger.info(f"Created test: {issue_key} - {test['fields']['summary']}")
                    
                    if (i + 1) % 10 == 0:
                        logger.info(f"Progress: {i + 1}/{len(tests)} tests in batch {batch_num}")
                    # Small delay to avoid rate limiting
                    time.sleep(0.2)
                else:
                    failed_count += 1
                    logger.error(f"Failed to create test '{test['fields']['summary']}': {response.status_code} - {response.text}")
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"Error creating test: {str(e)}")
        
        logger.info(f"Batch {batch_num} completed: {success_count} success, {failed_count} failed")
        self.import_stats['success'] += success_count
        self.import_stats['failed'] += failed_count
        
        return failed_count == 0
    
    def process_csv_files(self, filepaths: List[str], dry_run: bool = False):
        """Process CSV files and import only failed tests"""
        
        # First, get existing tests from JIRA
        self.get_existing_tests()
        
        all_tests_to_import = []
        
        for filepath in filepaths:
            logger.info(f"Processing file: {filepath}")
            
            if not os.path.exists(filepath):
                logger.error(f"File not found: {filepath}")
                continue
            
            # Read and convert CSV with ISO-8859-1 encoding
            with open(filepath, 'r', encoding='iso-8859-1') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    try:
                        test_title = row.get('Title', '')
                        
                        # Skip if already imported successfully
                        if test_title in self.successful_tests:
                            self.import_stats['skipped'] += 1
                            continue
                        
                        # Convert and add to import list
                        test = self.convert_csv_to_xray_test(row)
                        all_tests_to_import.append(test)
                        self.import_stats['total'] += 1
                        
                    except Exception as e:
                        logger.error(f"Error converting row {row.get('ID', 'unknown')}: {str(e)}")
        
        logger.info(f"Found {len(all_tests_to_import)} tests to import (skipped {self.import_stats['skipped']} already imported)")
        
        if dry_run:
            logger.info("Dry run mode - skipping actual import")
            # Save sample for review
            with open("failed_tests_sample.json", 'w') as f:
                json.dump(all_tests_to_import[:5], f, indent=2)
            return
        
        # Import in batches
        total_batches = (len(all_tests_to_import) + BATCH_SIZE - 1) // BATCH_SIZE
        
        for i in range(0, len(all_tests_to_import), BATCH_SIZE):
            batch = all_tests_to_import[i:i + BATCH_SIZE]
            batch_num = (i // BATCH_SIZE) + 1
            self.import_stats['batches'] += 1
            
            success = self.import_batch(batch, batch_num, total_batches)
            
            if not success and not args.continue_on_error:
                logger.error("Stopping import due to batch failure")
                break
            
            # Rate limiting
            if batch_num < total_batches:
                logger.info(f"Waiting {RATE_LIMIT_DELAY} seconds before next batch...")
                time.sleep(RATE_LIMIT_DELAY)
    
    def print_summary(self):
        """Print import summary statistics"""
        logger.info("\n" + "="*50)
        logger.info("RERUN IMPORT SUMMARY")
        logger.info("="*50)
        logger.info(f"Total tests to process: {self.import_stats['total']}")
        logger.info(f"Already imported (skipped): {self.import_stats['skipped']}")
        logger.info(f"Successfully imported: {self.import_stats['success']}")
        logger.info(f"Failed to import: {self.import_stats['failed']}")
        logger.info(f"Total batches: {self.import_stats['batches']}")
        if self.import_stats['total'] > 0:
            logger.info(f"Success rate: {(self.import_stats['success']/self.import_stats['total']*100):.1f}%")
        logger.info("="*50)

def main():
    parser = argparse.ArgumentParser(description='Re-import failed test cases to XRAY')
    parser.add_argument('files', nargs='+', help='CSV files to import')
    parser.add_argument('--log-file', default='xray_import.log', help='Previous import log file to analyze')
    parser.add_argument('--dry-run', action='store_true', help='Convert but do not import')
    parser.add_argument('--continue-on-error', action='store_true', help='Continue if batch fails')
    parser.add_argument('--batch-size', type=int, default=900, help='Tests per batch (max 1000)')
    
    global args
    args = parser.parse_args()
    
    # Validate environment
    if not JIRA_EMAIL or not JIRA_TOKEN:
        logger.error("Missing JIRA_EMAIL or ATLASSIAN_TOKEN environment variables")
        sys.exit(1)
    
    # Update batch size if specified
    global BATCH_SIZE
    BATCH_SIZE = min(args.batch_size, 1000)
    
    # Create importer
    importer = FailedTestImporter(JIRA_BASE_URL, JIRA_EMAIL, JIRA_TOKEN)
    
    # Parse previous log if provided
    if os.path.exists(args.log_file):
        importer.parse_import_log(args.log_file)
    
    # Process CSV files
    importer.process_csv_files(args.files, args.dry_run)
    
    # Print summary
    importer.print_summary()

if __name__ == '__main__':
    main()