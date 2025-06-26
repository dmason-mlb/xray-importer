#!/usr/bin/env python3
"""
Organize all imported XRAY tests using labels
Adds surface and feature labels for better organization and filtering
"""

import csv
import os
import sys
import time
import requests
from requests.auth import HTTPBasicAuth
import argparse
import logging
from typing import Dict, List, Set, Tuple

# Configuration
JIRA_BASE_URL = os.environ.get('JIRA_BASE_URL', 'https://your-domain.atlassian.net')
JIRA_EMAIL = os.environ.get('JIRA_EMAIL', '')
JIRA_TOKEN = os.environ.get('ATLASSIAN_TOKEN', '')
PROJECT_KEY = 'MLBAPP'
RATE_LIMIT_DELAY = 0.3  # Seconds between updates

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('organize_tests_labels.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class XrayTestLabelOrganizer:
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
        self.test_mapping = {}
        self.label_stats = {}
    
    def create_organizational_labels(self, section: str, title: str) -> List[str]:
        """Create organizational labels based on test content"""
        labels = []
        
        # Surface label (primary categorization)
        if section:
            if 'Home Surface' in section or 'THome Surface' in section:
                labels.append('surface-home')
            elif 'News Surface' in section or 'News' in section:
                labels.append('surface-news')
            else:
                labels.append('surface-core')
        else:
            # Default based on title analysis
            if 'home' in title.lower():
                labels.append('surface-home')
            elif 'news' in title.lower():
                labels.append('surface-news')
            else:
                labels.append('surface-core')
        
        # Feature labels (secondary categorization)
        title_lower = title.lower()
        
        # Analytics & Tracking
        if any(keyword in title_lower for keyword in ['analytics', 'tracking', 'conviva', 'firebase', 'adobe']):
            labels.append('feature-analytics')
        
        # Accessibility
        if any(keyword in title_lower for keyword in ['accessibility', 'a11y', 'talkback', 'voiceover', 'announce']):
            labels.append('feature-accessibility')
        
        # Video & Media
        if any(keyword in title_lower for keyword in ['video', 'autoplay', 'mlb.tv', 'mlbtv', 'playlist', 'stream']):
            labels.append('feature-video')
        
        # Authentication & User Management
        if any(keyword in title_lower for keyword in ['auth', 'login', 'sign up', 'sign in', 'logout', 'password', 'account']):
            labels.append('feature-authentication')
        
        # Content Display
        if any(keyword in title_lower for keyword in ['mixed feed', 'mxfd', 'feed']):
            labels.append('feature-mixed-feed')
        elif any(keyword in title_lower for keyword in ['headline', 'stack']):
            labels.append('feature-headline-stack')
        elif any(keyword in title_lower for keyword in ['carousel']):
            labels.append('feature-carousel')
        
        # Team & Game Features
        if any(keyword in title_lower for keyword in ['team snapshot', 'snapshot']):
            labels.append('feature-team-snapshot')
        elif any(keyword in title_lower for keyword in ['standings']):
            labels.append('feature-standings')
        elif any(keyword in title_lower for keyword in ['scoreboard', 'scores']):
            labels.append('feature-scoreboard')
        elif any(keyword in title_lower for keyword in ['gameday', 'game day']):
            labels.append('feature-gameday')
        
        # Player Features
        if any(keyword in title_lower for keyword in ['player', 'follows', 'my follows']):
            labels.append('feature-player')
        
        # Stories & Articles
        if any(keyword in title_lower for keyword in ['story', 'stories', 'article']):
            labels.append('feature-stories')
        
        # Advertising
        if any(keyword in title_lower for keyword in [' ad ', 'ads ', 'advertisement', 'advertising', 'sponsor']):
            labels.append('feature-advertising')
        
        # Configuration & Settings
        if any(keyword in title_lower for keyword in ['surface', 'contentful', 'module', 'config']):
            labels.append('feature-configuration')
        elif any(keyword in title_lower for keyword in ['settings', 'preference']):
            labels.append('feature-settings')
        
        # Notifications
        if any(keyword in title_lower for keyword in ['notification', 'push', 'alert']):
            labels.append('feature-notifications')
        
        # Onboarding
        if any(keyword in title_lower for keyword in ['onboarding', 'tutorial', 'first time']):
            labels.append('feature-onboarding')
        
        # Live Activities
        if any(keyword in title_lower for keyword in ['live activities', 'live activity']):
            labels.append('feature-live-activities')
        
        # Schedule
        if any(keyword in title_lower for keyword in ['schedule', 'calendar']):
            labels.append('feature-schedule')
        
        # Localization
        if any(keyword in title_lower for keyword in ['spanish', 'japanese', 'localization', 'translation', 'bilingual']):
            labels.append('feature-localization')
        
        # Performance
        if any(keyword in title_lower for keyword in ['performance', 'load time', 'optimization']):
            labels.append('feature-performance')
        
        # Update label statistics
        for label in labels:
            self.label_stats[label] = self.label_stats.get(label, 0) + 1
        
        return labels
    
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
                break
        
        logger.info(f"Found {len(all_tests)} tests to organize")
        return all_tests
    
    def update_test_labels(self, test_key: str, new_labels: List[str], existing_labels: List[str]) -> bool:
        """Update a single test's labels"""
        # Merge with existing labels, preserving import labels
        all_labels = list(set(existing_labels + new_labels))
        
        url = f"{self.base_url}/rest/api/2/issue/{test_key}"
        payload = {
            "fields": {
                "labels": all_labels
            }
        }
        
        response = self.session.put(url, json=payload)
        
        if response.status_code == 204:
            return True
        else:
            logger.error(f"Failed to update {test_key}: {response.status_code} - {response.text}")
            return False
    
    def has_organizational_labels(self, labels: List[str]) -> bool:
        """Check if test already has organizational labels"""
        for label in labels:
            if label.startswith('surface-') or label.startswith('feature-'):
                return True
        return False
    
    def organize_tests(self, dry_run: bool = False):
        """Main method to organize all tests with labels"""
        # Get all tests
        tests = self.get_imported_tests()
        self.stats['total'] = len(tests)
        
        # Organize tests
        for i, test in enumerate(tests):
            test_key = test['key']
            summary = test['fields']['summary']
            existing_labels = test['fields'].get('labels', [])
            
            # Skip if already has organizational labels
            if self.has_organizational_labels(existing_labels):
                logger.debug(f"Skipping {test_key} - already organized")
                self.stats['skipped'] += 1
                continue
            
            # Get section from mapping
            section = self.test_mapping.get(summary, '')
            
            # Create organizational labels
            org_labels = self.create_organizational_labels(section, summary)
            
            if dry_run:
                logger.info(f"[DRY RUN] Would add to {test_key}: {org_labels}")
                self.stats['success'] += 1
            else:
                # Update test
                if self.update_test_labels(test_key, org_labels, existing_labels):
                    logger.info(f"✓ Updated {test_key} with labels: {org_labels}")
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
        logger.info("\n" + "="*60)
        logger.info("LABEL ORGANIZATION SUMMARY")
        logger.info("="*60)
        logger.info(f"Total tests found: {self.stats['total']}")
        logger.info(f"Successfully labeled: {self.stats['success']}")
        logger.info(f"Failed to label: {self.stats['failed']}")
        logger.info(f"Skipped (already organized): {self.stats['skipped']}")
        if self.stats['total'] > 0:
            success_rate = (self.stats['success'] / (self.stats['total'] - self.stats['skipped']) * 100) if (self.stats['total'] - self.stats['skipped']) > 0 else 0
            logger.info(f"Success rate: {success_rate:.1f}%")
        
        # Print label distribution
        logger.info("\n" + "="*60)
        logger.info("LABEL DISTRIBUTION")
        logger.info("="*60)
        
        # Sort by surface labels first, then feature labels
        surface_labels = sorted([(k, v) for k, v in self.label_stats.items() if k.startswith('surface-')], 
                               key=lambda x: x[1], reverse=True)
        feature_labels = sorted([(k, v) for k, v in self.label_stats.items() if k.startswith('feature-')], 
                               key=lambda x: x[1], reverse=True)
        
        logger.info("\nSurface Labels:")
        for label, count in surface_labels:
            logger.info(f"  {label}: {count} tests")
        
        logger.info("\nFeature Labels (top 20):")
        for label, count in feature_labels[:20]:
            logger.info(f"  {label}: {count} tests")
        
        logger.info("="*60)

def main():
    parser = argparse.ArgumentParser(description='Organize XRAY tests using labels')
    parser.add_argument('csv_files', nargs='+', help='Original CSV files for section mapping')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--continue-on-error', action='store_true', help='Continue if update fails')
    
    args = parser.parse_args()
    
    # Validate environment
    if not JIRA_EMAIL or not JIRA_TOKEN:
        logger.error("Missing JIRA_EMAIL or ATLASSIAN_TOKEN environment variables")
        sys.exit(1)
    
    logger.info("Starting XRAY test label organization")
    logger.info(f"JIRA URL: {JIRA_BASE_URL}")
    logger.info(f"Project: {PROJECT_KEY}")
    
    # Create organizer
    organizer = XrayTestLabelOrganizer(JIRA_BASE_URL, JIRA_EMAIL, JIRA_TOKEN)
    
    # Load CSV mappings
    organizer.load_csv_mapping(args.csv_files)
    
    # Organize tests
    organizer.organize_tests(args.dry_run)
    
    # Print summary
    organizer.print_summary()
    
    if not args.dry_run:
        logger.info("\n✅ Label organization complete!")
        logger.info("\nYou can now use JQL queries to filter tests:")
        logger.info('  - labels = "surface-home" AND labels = "feature-video"')
        logger.info('  - labels = "feature-authentication"')
        logger.info('  - labels = "surface-news"')

if __name__ == '__main__':
    main()