#!/usr/bin/env python3
"""
Add tests to existing Test Sets using alternative methods
"""

import os
import sys
import time
import requests
from requests.auth import HTTPBasicAuth
import argparse
import logging
from typing import List
import getpass
import json

# Configuration
JIRA_BASE_URL = os.environ.get('JIRA_BASE_URL', 'https://baseball.atlassian.net')
JIRA_EMAIL = os.environ.get('JIRA_EMAIL', '')
JIRA_TOKEN = os.environ.get('ATLASSIAN_TOKEN', '')
PROJECT_KEY = 'MLBAPP'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestSetLinker:
    def __init__(self, base_url: str, email: str, token: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(email, token)
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def check_xray_endpoints(self):
        """Check available XRAY endpoints"""
        logger.info("Checking XRAY API endpoints...")
        
        # Try different XRAY API versions and endpoints
        endpoints = [
            "/rest/raven/1.0/api",
            "/rest/raven/2.0/api", 
            "/rest/xray/1.0",
            "/rest/xray/2.0",
            "/plugins/servlet/xray"
        ]
        
        for endpoint in endpoints:
            url = f"{self.base_url}{endpoint}"
            try:
                response = self.session.get(url)
                if response.status_code != 404:
                    logger.info(f"✓ Found endpoint: {endpoint} (Status: {response.status_code})")
            except:
                pass
    
    def get_test_set_info(self, test_set_key: str):
        """Get information about a Test Set"""
        url = f"{self.base_url}/rest/api/2/issue/{test_set_key}"
        response = self.session.get(url)
        
        if response.status_code == 200:
            issue = response.json()
            return {
                'key': issue['key'],
                'summary': issue['fields']['summary'],
                'labels': issue['fields'].get('labels', [])
            }
        return None
    
    def get_tests_for_label(self, label: str) -> List[str]:
        """Get all test keys for a specific label"""
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
                break
        
        return test_keys
    
    def link_tests_using_issue_links(self, test_set_key: str, test_keys: List[str]):
        """Try linking tests using JIRA issue links"""
        logger.info(f"Attempting to link {len(test_keys)} tests using issue links...")
        
        success_count = 0
        for test_key in test_keys[:5]:  # Test with first 5
            url = f"{self.base_url}/rest/api/2/issueLink"
            payload = {
                "type": {
                    "name": "Test"  # This might need adjustment
                },
                "inwardIssue": {
                    "key": test_set_key
                },
                "outwardIssue": {
                    "key": test_key
                }
            }
            
            response = self.session.post(url, json=payload)
            if response.status_code == 201:
                success_count += 1
                logger.info(f"  ✓ Linked {test_key}")
            else:
                logger.debug(f"  ✗ Failed to link {test_key}: {response.status_code}")
        
        return success_count > 0
    
    def try_xray_v2_api(self, test_set_key: str, test_keys: List[str]):
        """Try using XRAY v2 API"""
        logger.info("Trying XRAY v2 API...")
        
        # Try different endpoints
        endpoints = [
            f"/rest/raven/2.0/api/testset/{test_set_key}/test",
            f"/rest/xray/1.0/testset/{test_set_key}/tests",
            f"/rest/api/2/issue/{test_set_key}/remotelink"
        ]
        
        for endpoint in endpoints:
            url = f"{self.base_url}{endpoint}"
            payload = {
                "add": test_keys[:5]  # Test with first 5
            }
            
            response = self.session.post(url, json=payload)
            if response.status_code in [200, 201, 204]:
                logger.info(f"✓ Success with endpoint: {endpoint}")
                return True
            else:
                logger.debug(f"Failed with {endpoint}: {response.status_code}")
        
        return False
    
    def manual_check_instructions(self, test_set_key: str, label: str, test_count: int):
        """Provide manual instructions"""
        logger.info("\n" + "="*60)
        logger.info("MANUAL LINKING INSTRUCTIONS")
        logger.info("="*60)
        logger.info(f"\nTest Set: {test_set_key}")
        logger.info(f"Label: {label}")
        logger.info(f"Tests to add: {test_count}")
        logger.info("\nTo manually add tests to this Test Set:")
        logger.info("1. Go to the Test Set in JIRA")
        logger.info("2. Look for 'Add Tests' or 'Manage Tests' option")
        logger.info("3. Use this JQL to find the tests:")
        logger.info(f'   project = {PROJECT_KEY} AND issuetype = "Xray Test" AND labels = "{label}"')
        logger.info("4. Select all tests and add them to the Test Set")

def main():
    parser = argparse.ArgumentParser(description='Add tests to Test Sets')
    parser.add_argument('--test-set', help='Specific Test Set key to process')
    parser.add_argument('--check-endpoints', action='store_true', help='Check available XRAY endpoints')
    
    args = parser.parse_args()
    
    # Get credentials
    global JIRA_EMAIL, JIRA_TOKEN
    
    if not JIRA_EMAIL:
        JIRA_EMAIL = input("Enter JIRA Email: ").strip()
    
    if not JIRA_TOKEN:
        JIRA_TOKEN = getpass.getpass("Enter ATLASSIAN API Token: ").strip()
    
    linker = TestSetLinker(JIRA_BASE_URL, JIRA_EMAIL, JIRA_TOKEN)
    
    if args.check_endpoints:
        linker.check_xray_endpoints()
        return
    
    # Get all Test Sets created
    test_sets = {
        'surface-home': 'MLBAPP-5178',
        'surface-core': 'MLBAPP-5179',
        'surface-news': 'MLBAPP-5180',
        'feature-stories': 'MLBAPP-5181',
        'feature-video': 'MLBAPP-5182',
        # Add more as needed
    }
    
    if args.test_set:
        # Process single Test Set
        test_set_info = linker.get_test_set_info(args.test_set)
        if test_set_info:
            # Find matching label
            for label in test_set_info['labels']:
                if label.startswith('surface-') or label.startswith('feature-'):
                    logger.info(f"Processing Test Set {args.test_set} for label '{label}'")
                    test_keys = linker.get_tests_for_label(label)
                    logger.info(f"Found {len(test_keys)} tests")
                    
                    # Try different methods
                    if not linker.try_xray_v2_api(args.test_set, test_keys):
                        if not linker.link_tests_using_issue_links(args.test_set, test_keys):
                            linker.manual_check_instructions(args.test_set, label, len(test_keys))
                    break
    else:
        # Check what's needed
        logger.info("Test Sets created but need tests added:")
        for label, test_set_key in test_sets.items():
            test_count = len(linker.get_tests_for_label(label))
            logger.info(f"  {test_set_key}: {label} ({test_count} tests)")

if __name__ == '__main__':
    main()