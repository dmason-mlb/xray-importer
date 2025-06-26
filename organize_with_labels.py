#!/usr/bin/env python3
"""
Organize XRAY tests using Labels since Test Repository Path is not available via REST API
"""

import os
import sys
import json
import requests
from requests.auth import HTTPBasicAuth
import time
import argparse
import logging
from typing import Dict, List

# Configuration
JIRA_BASE_URL = os.environ.get('JIRA_BASE_URL', 'https://your-domain.atlassian.net')
JIRA_EMAIL = os.environ.get('JIRA_EMAIL', '')
JIRA_TOKEN = os.environ.get('ATLASSIAN_TOKEN', '')
PROJECT_KEY = 'MLBAPP'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_single_update_with_labels(test_key: str, new_labels: List[str]):
    """Test updating a single test with labels for organization"""
    
    session = requests.Session()
    session.auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_TOKEN)
    session.headers.update({
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    })
    
    # Get current test details
    logger.info(f"Getting current details for {test_key}...")
    url = f"{JIRA_BASE_URL}/rest/api/2/issue/{test_key}"
    response = session.get(url)
    
    if response.status_code == 200:
        issue = response.json()
        current_labels = issue['fields'].get('labels', [])
        logger.info(f"Current labels: {current_labels}")
        
        # Merge new labels with existing ones
        all_labels = list(set(current_labels + new_labels))
        
        # Update labels
        logger.info(f"Updating labels to: {all_labels}")
        payload = {
            "fields": {
                "labels": all_labels
            }
        }
        
        response = session.put(url, json=payload)
        
        if response.status_code == 204:
            logger.info("✓ Update successful!")
            
            # Verify
            response = session.get(url)
            if response.status_code == 200:
                updated_labels = response.json()['fields'].get('labels', [])
                logger.info(f"Updated labels: {updated_labels}")
                return True
        else:
            logger.error(f"Update failed: {response.status_code} - {response.text}")
            return False
    else:
        logger.error(f"Failed to get test: {response.status_code}")
        return False

def create_organizational_labels(section: str, title: str) -> List[str]:
    """Create organizational labels based on test content"""
    labels = []
    
    # Add surface label
    if 'Home Surface' in section or 'THome Surface' in section:
        labels.append('surface-home')
    elif 'News Surface' in section or 'News' in section:
        labels.append('surface-news')
    else:
        labels.append('surface-core')
    
    # Add feature labels based on title
    title_lower = title.lower()
    
    if any(keyword in title_lower for keyword in ['analytics', 'tracking', 'conviva']):
        labels.append('feature-analytics')
    elif any(keyword in title_lower for keyword in ['accessibility', 'a11y', 'talkback']):
        labels.append('feature-accessibility')
    elif any(keyword in title_lower for keyword in ['video', 'autoplay', 'mlb.tv', 'mlbtv']):
        labels.append('feature-video')
    elif any(keyword in title_lower for keyword in ['auth', 'login', 'sign']):
        labels.append('feature-authentication')
    elif any(keyword in title_lower for keyword in ['mixed feed', 'mxfd']):
        labels.append('feature-mixed-feed')
    elif any(keyword in title_lower for keyword in ['headline', 'stack']):
        labels.append('feature-headline-stack')
    elif any(keyword in title_lower for keyword in ['team snapshot']):
        labels.append('feature-team-snapshot')
    elif any(keyword in title_lower for keyword in ['standings']):
        labels.append('feature-standings')
    elif any(keyword in title_lower for keyword in ['player', 'follows']):
        labels.append('feature-player')
    elif any(keyword in title_lower for keyword in ['story', 'stories']):
        labels.append('feature-stories')
    elif any(keyword in title_lower for keyword in ['ad', 'advertisement']):
        labels.append('feature-advertising')
    elif any(keyword in title_lower for keyword in ['surface', 'contentful', 'module']):
        labels.append('feature-configuration')
    elif any(keyword in title_lower for keyword in ['settings']):
        labels.append('feature-settings')
    elif any(keyword in title_lower for keyword in ['notification']):
        labels.append('feature-notifications')
    
    return labels

def main():
    parser = argparse.ArgumentParser(description='Test label-based organization for XRAY tests')
    parser.add_argument('test_key', help='Test key to update (e.g., MLBAPP-5177)')
    parser.add_argument('--section', default='News Surface', help='Section from CSV')
    
    args = parser.parse_args()
    
    # Validate environment
    if not JIRA_EMAIL or not JIRA_TOKEN:
        logger.error("Missing JIRA_EMAIL or ATLASSIAN_TOKEN environment variables")
        sys.exit(1)
    
    logger.info(f"Testing label-based organization")
    logger.info(f"Test Key: {args.test_key}")
    
    # Get test summary first
    session = requests.Session()
    session.auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_TOKEN)
    session.headers.update({'Accept': 'application/json'})
    
    response = session.get(f"{JIRA_BASE_URL}/rest/api/2/issue/{args.test_key}")
    if response.status_code == 200:
        summary = response.json()['fields']['summary']
        logger.info(f"Test Summary: {summary}")
        
        # Create organizational labels
        org_labels = create_organizational_labels(args.section, summary)
        logger.info(f"Organizational labels: {org_labels}")
        
        # Test the update
        success = test_single_update_with_labels(args.test_key, org_labels)
        
        if success:
            logger.info("\n✅ SUCCESS: Label-based organization works!")
            logger.info("We can use this approach to organize all tests.")
        else:
            logger.info("\n❌ FAILED: Could not update labels.")
    else:
        logger.error(f"Could not fetch test: {response.status_code}")

if __name__ == '__main__':
    main()