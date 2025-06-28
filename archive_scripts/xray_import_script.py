#!/usr/bin/env python3
"""
XRAY Test Import Script for MLBAPP Project
Imports test cases from CSV files to JIRA XRAY using REST API
"""

import csv
import json
import os
import sys
import time
from datetime import datetime
from typing import List, Dict, Any
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
        logging.FileHandler('xray_import.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class XrayImporter:
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
            'batches': 0
        }
    
    def convert_csv_to_xray_test(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Convert CSV row to XRAY test format"""
        
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
                'labels': ['imported-from-csv', 'testrails-migration']
            }
        }
        
        # Add custom fields if available
        if row.get('Preconditions'):
            test['fields']['customfield_23269'] = row['Preconditions']
        
        # Add references as comment
        if row.get('References'):
            test['fields']['comment'] = f"Original References: {row['References']}"
        
        # Process test steps
        steps = self.parse_test_steps(row)
        if steps:
            test['testSteps'] = steps
        
        # Add Test Repository path based on Section
        if row.get('Section'):
            test['testRepositoryPath'] = self.build_repository_path(row['Section'])
        
        return test
    
    def parse_test_steps(self, row: Dict[str, str]) -> List[Dict[str, str]]:
        """Parse test steps from CSV format"""
        steps = []
        
        # Try Steps Separated format first
        if row.get('Steps Separated (Step)') and row.get('Steps Separated (Expected Result)'):
            step_parts = row['Steps Separated (Step)'].split('\n')
            result_parts = row['Steps Separated (Expected Result)'].split('\n')
            
            for i, (step, result) in enumerate(zip(step_parts, result_parts)):
                if step.strip():
                    steps.append({
                        'index': i + 1,
                        'action': step.strip(),
                        'expectedResult': result.strip() if result.strip() else ''
                    })
        
        # Fallback to regular Steps field
        elif row.get('Steps'):
            step_text = row['Steps']
            # Simple parsing - split by numbered lines
            import re
            step_pattern = re.compile(r'(\d+)\.\s*(.*?)(?=\d+\.|$)', re.DOTALL)
            matches = step_pattern.findall(step_text)
            
            for i, (num, content) in enumerate(matches):
                if 'Expected Result:' in content:
                    parts = content.split('Expected Result:', 1)
                    action = parts[0].strip()
                    expected = parts[1].strip() if len(parts) > 1 else ''
                else:
                    action = content.strip()
                    expected = ''
                
                if action:
                    steps.append({
                        'index': i + 1,
                        'action': action,
                        'expectedResult': expected
                    })
        
        return steps
    
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
        
        # First, let's try to create tests individually using JIRA API with Test issue type
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
                
                # Add custom fields if present
                # Commented out - field not available on screen
                # if 'customfield_23269' in test['fields']:
                #     issue_data['fields']['customfield_23269'] = test['fields']['customfield_23269']
                
                # For XRAY Cloud, we need to add test type and steps as custom fields
                # Test Type field (this might be a custom field ID specific to your instance)
                # We'll need to find the correct custom field IDs for XRAY fields
                
                # Create issue via JIRA API
                url = f"{self.base_url}/rest/api/2/issue"
                response = self.session.post(url, json=issue_data)
                
                if response.status_code in [200, 201]:
                    success_count += 1
                    issue_key = response.json().get('key')
                    
                    # Now add test steps if available
                    if 'testSteps' in test and test['testSteps'] and issue_key:
                        self.add_test_steps(issue_key, test['testSteps'])
                    
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
    
    def add_test_steps(self, issue_key: str, steps: List[Dict[str, Any]]):
        """Add test steps to an XRAY test issue"""
        try:
            # For XRAY Cloud, test steps are typically managed through GraphQL API
            # or custom fields. For now, we'll add them to the description
            logger.debug(f"Test steps would be added to {issue_key}")
        except Exception as e:
            logger.error(f"Error adding test steps to {issue_key}: {str(e)}")
    
    def process_csv_file(self, filepath: str, dry_run: bool = False):
        """Process and import tests from a CSV file"""
        logger.info(f"Processing file: {filepath}")
        
        tests = []
        
        # Read and convert CSV with ISO-8859-1 encoding
        with open(filepath, 'r', encoding='iso-8859-1') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                try:
                    test = self.convert_csv_to_xray_test(row)
                    tests.append(test)
                    self.import_stats['total'] += 1
                except Exception as e:
                    logger.error(f"Error converting row {row.get('ID', 'unknown')}: {str(e)}")
        
        logger.info(f"Converted {len(tests)} tests from {filepath}")
        
        if dry_run:
            logger.info("Dry run mode - skipping actual import")
            # Save sample for review
            with open(f"{filepath}_sample.json", 'w') as f:
                json.dump(tests[:5], f, indent=2)
            return
        
        # Import in batches
        total_batches = (len(tests) + BATCH_SIZE - 1) // BATCH_SIZE
        
        for i in range(0, len(tests), BATCH_SIZE):
            batch = tests[i:i + BATCH_SIZE]
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
        logger.info("IMPORT SUMMARY")
        logger.info("="*50)
        logger.info(f"Total tests processed: {self.import_stats['total']}")
        logger.info(f"Successfully imported: {self.import_stats['success']}")
        logger.info(f"Failed to import: {self.import_stats['failed']}")
        logger.info(f"Total batches: {self.import_stats['batches']}")
        logger.info(f"Success rate: {(self.import_stats['success']/self.import_stats['total']*100):.1f}%")
        logger.info("="*50)

def main():
    parser = argparse.ArgumentParser(description='Import test cases to XRAY')
    parser.add_argument('files', nargs='+', help='CSV files to import')
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
    importer = XrayImporter(JIRA_BASE_URL, JIRA_EMAIL, JIRA_TOKEN)
    
    # Process each file
    for filepath in args.files:
        if not os.path.exists(filepath):
            logger.error(f"File not found: {filepath}")
            continue
        
        try:
            importer.process_csv_file(filepath, args.dry_run)
        except Exception as e:
            logger.error(f"Failed to process {filepath}: {str(e)}")
            if not args.continue_on_error:
                break
    
    # Print summary
    importer.print_summary()

if __name__ == '__main__':
    main()