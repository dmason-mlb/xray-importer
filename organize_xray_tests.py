#!/usr/bin/env python3
"""
Organize imported XRAY tests into folders using Test Repository Path
Based on the CSV section data from the original import
"""

import csv
import json
import os
import sys
import time
import requests
from requests.auth import HTTPBasicAuth
import argparse
import logging
from typing import Dict, List, Tuple

# Configuration
JIRA_BASE_URL = os.environ.get('JIRA_BASE_URL', 'https://your-domain.atlassian.net')
JIRA_EMAIL = os.environ.get('JIRA_EMAIL', '')
JIRA_TOKEN = os.environ.get('ATLASSIAN_TOKEN', '')
PROJECT_KEY = 'MLBAPP'
RATE_LIMIT_DELAY = 0.5  # Half second between updates

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('organize_xray_tests.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class XrayTestOrganizer:
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
            'success': 0,
            'failed': 0,
            'skipped': 0
        }
        self.custom_field_id = None
        self.test_mapping = {}
    
    def discover_custom_field(self):
        """Discover the Test Repository Path custom field ID"""
        logger.info("Discovering custom field IDs...")
        
        # Method 1: Check all fields
        url = f"{self.base_url}/rest/api/2/field"
        response = self.session.get(url)
        
        if response.status_code == 200:
            fields = response.json()
            for field in fields:
                if 'test repository path' in field['name'].lower():
                    self.custom_field_id = field['id']
                    logger.info(f"Found Test Repository Path field: {field['id']} - {field['name']}")
                    return
                # Log all custom fields for debugging
                if field['id'].startswith('customfield_'):
                    logger.debug(f"Custom field: {field['id']} - {field['name']}")
        
        # Method 2: Check from an existing test
        if not self.custom_field_id:
            self.discover_from_existing_test()
    
    def discover_from_existing_test(self):
        """Try to discover custom field from an existing test"""
        logger.info("Trying to discover custom field from existing test...")
        
        # Get one test
        jql = f'project = {PROJECT_KEY} AND issuetype = "Xray Test" ORDER BY created DESC'
        url = f"{self.base_url}/rest/api/2/search"
        params = {
            'jql': jql,
            'maxResults': 1,
            'expand': 'editmeta'
        }
        
        response = self.session.get(url, params=params)
        if response.status_code == 200 and response.json()['total'] > 0:
            test_key = response.json()['issues'][0]['key']
            
            # Get editmeta for this test
            url = f"{self.base_url}/rest/api/2/issue/{test_key}/editmeta"
            response = self.session.get(url)
            
            if response.status_code == 200:
                fields = response.json()['fields']
                for field_id, field_info in fields.items():
                    if 'repository' in field_info.get('name', '').lower():
                        self.custom_field_id = field_id
                        logger.info(f"Found Test Repository Path field from test: {field_id}")
                        return
    
    def build_repository_path(self, section: str, title: str) -> str:
        """Build Test Repository path from section string"""
        if not section:
            return '/MLBAPP Test Repository/Uncategorized'
        
        # Clean and split section path
        parts = section.replace('\\', '/').split('/')
        clean_parts = [p.strip() for p in parts if p.strip()]
        
        # Determine base path based on section content
        if 'Home Surface' in section or 'THome Surface' in section:
            base = '/MLBAPP Test Repository/Home Surface'
        elif 'News Surface' in section or 'News' in ' '.join(clean_parts):
            base = '/MLBAPP Test Repository/News Surface'
        elif 'MLBAPP' in section:
            base = '/MLBAPP Test Repository/Core App'
        elif 'Additional' in section:
            base = '/MLBAPP Test Repository/News Surface'
        else:
            base = '/MLBAPP Test Repository/Core App'
        
        # Build sub-paths based on content
        sub_paths = []
        
        # Add category based on test title
        if any(keyword in title.lower() for keyword in ['analytics', 'tracking', 'conviva']):
            sub_paths.append('Analytics')
        elif any(keyword in title.lower() for keyword in ['accessibility', 'a11y', 'talkback']):
            sub_paths.append('Accessibility')
        elif any(keyword in title.lower() for keyword in ['mixed feed', 'mxfd', 'feed']):
            sub_paths.append('Mixed Feed')
        elif any(keyword in title.lower() for keyword in ['headline', 'stack']):
            sub_paths.append('Headline Stack')
        elif any(keyword in title.lower() for keyword in ['carousel', 'content carousel']):
            sub_paths.append('Content Carousel')
        elif any(keyword in title.lower() for keyword in ['team snapshot', 'snapshot']):
            sub_paths.append('Team Snapshot')
        elif any(keyword in title.lower() for keyword in ['standings']):
            sub_paths.append('Standings')
        elif any(keyword in title.lower() for keyword in ['player', 'follows']):
            sub_paths.append('Player Features')
        elif any(keyword in title.lower() for keyword in ['video', 'autoplay', 'mlb.tv', 'mlbtv']):
            sub_paths.append('Video')
        elif any(keyword in title.lower() for keyword in ['story', 'stories', 'game stories']):
            sub_paths.append('Stories')
        elif any(keyword in title.lower() for keyword in ['ad', 'advertisement']):
            sub_paths.append('Advertising')
        elif any(keyword in title.lower() for keyword in ['surface', 'contentful', 'module']):
            sub_paths.append('Surface Configuration')
        elif any(keyword in title.lower() for keyword in ['auth', 'login', 'sign']):
            sub_paths.append('Authentication')
        elif any(keyword in title.lower() for keyword in ['settings', 'config']):
            sub_paths.append('Settings')
        
        # Combine paths
        if sub_paths:
            return f"{base}/{'/'.join(sub_paths)}"
        elif len(clean_parts) > 1:
            # Use original section hierarchy
            return f"{base}/{'/'.join(clean_parts[1:])}"
        else:
            return base
    
    def load_csv_mapping(self, csv_files: List[str]):
        """Load CSV files to create test title to section mapping"""
        logger.info("Loading CSV files to build test mapping...")
        
        for filepath in csv_files:
            if not os.path.exists(filepath):
                logger.warning(f"File not found: {filepath}")
                continue
            
            with open(filepath, 'r', encoding='iso-8859-1') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    title = row.get('Title', '').strip()
                    section = row.get('Section', '').strip()
                    if title:
                        self.test_mapping[title] = section
        
        logger.info(f"Loaded {len(self.test_mapping)} test mappings from CSV files")
    
    def get_imported_tests(self) -> List[Dict]:
        """Get all imported tests that need organization"""
        logger.info("Fetching imported tests from JIRA...")
        
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
                'fields': f'summary,{self.custom_field_id}' if self.custom_field_id else 'summary'
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
                break
        
        logger.info(f"Found {len(all_tests)} tests to organize")
        return all_tests
    
    def update_test_path(self, test_key: str, repository_path: str) -> bool:
        """Update a single test's repository path"""
        if not self.custom_field_id:
            logger.error("Custom field ID not found - cannot update tests")
            return False
        
        url = f"{self.base_url}/rest/api/2/issue/{test_key}"
        payload = {
            "fields": {
                self.custom_field_id: repository_path
            }
        }
        
        response = self.session.put(url, json=payload)
        
        if response.status_code == 204:
            return True
        else:
            logger.error(f"Failed to update {test_key}: {response.status_code} - {response.text}")
            return False
    
    def organize_tests(self, dry_run: bool = False):
        """Main method to organize all tests"""
        # Discover custom field
        self.discover_custom_field()
        
        if not self.custom_field_id and not dry_run:
            logger.error("Could not find Test Repository Path custom field ID")
            logger.info("Please manually check for the field ID and update the script")
            return
        
        # Get all tests
        tests = self.get_imported_tests()
        self.stats['total'] = len(tests)
        
        # Organize tests
        for i, test in enumerate(tests):
            test_key = test['key']
            summary = test['fields']['summary']
            
            # Check if already has a path
            current_path = test['fields'].get(self.custom_field_id, '') if self.custom_field_id else ''
            if current_path and current_path != '/':
                logger.debug(f"Skipping {test_key} - already has path: {current_path}")
                self.stats['skipped'] += 1
                continue
            
            # Get section from mapping
            section = self.test_mapping.get(summary, '')
            
            # Build repository path
            repository_path = self.build_repository_path(section, summary)
            
            if dry_run:
                logger.info(f"[DRY RUN] Would move {test_key}: {summary[:50]}... → {repository_path}")
                self.stats['success'] += 1
            else:
                # Update test
                if self.update_test_path(test_key, repository_path):
                    logger.info(f"✓ Moved {test_key} to {repository_path}")
                    self.stats['success'] += 1
                else:
                    self.stats['failed'] += 1
                
                # Rate limiting
                time.sleep(RATE_LIMIT_DELAY)
            
            # Progress update
            if (i + 1) % 50 == 0:
                logger.info(f"Progress: {i + 1}/{len(tests)} tests processed")
    
    def print_summary(self):
        """Print organization summary"""
        logger.info("\n" + "="*50)
        logger.info("ORGANIZATION SUMMARY")
        logger.info("="*50)
        logger.info(f"Total tests found: {self.stats['total']}")
        logger.info(f"Successfully organized: {self.stats['success']}")
        logger.info(f"Failed to organize: {self.stats['failed']}")
        logger.info(f"Skipped (already organized): {self.stats['skipped']}")
        if self.stats['total'] > 0:
            success_rate = (self.stats['success'] / (self.stats['total'] - self.stats['skipped']) * 100) if (self.stats['total'] - self.stats['skipped']) > 0 else 0
            logger.info(f"Success rate: {success_rate:.1f}%")
        logger.info("="*50)

def main():
    parser = argparse.ArgumentParser(description='Organize XRAY tests into folders')
    parser.add_argument('csv_files', nargs='+', help='Original CSV files for section mapping')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--custom-field', help='Custom field ID for Test Repository Path (e.g., customfield_10300)')
    
    args = parser.parse_args()
    
    # Validate environment
    if not JIRA_EMAIL or not JIRA_TOKEN:
        logger.error("Missing JIRA_EMAIL or ATLASSIAN_TOKEN environment variables")
        sys.exit(1)
    
    # Create organizer
    organizer = XrayTestOrganizer(JIRA_BASE_URL, JIRA_EMAIL, JIRA_TOKEN)
    
    # Set custom field if provided
    if args.custom_field:
        organizer.custom_field_id = args.custom_field
        logger.info(f"Using provided custom field ID: {args.custom_field}")
    
    # Load CSV mappings
    organizer.load_csv_mapping(args.csv_files)
    
    # Organize tests
    organizer.organize_tests(args.dry_run)
    
    # Print summary
    organizer.print_summary()

if __name__ == '__main__':
    main()