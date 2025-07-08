#!/usr/bin/env python3
"""
Fetch all tests from an Xray project and categorize them by whether they have test steps.

This script retrieves all test cases from a specified Xray project using the GraphQL API.
It handles rate limiting, authentication failures, and network issues with automatic retry logic.
Tests are categorized into two groups: those with test steps and those without.

Usage:
    1. Copy .env.example to .env and fill in your Xray credentials
    2. Run: python fetch_all_xray_tests.py

Output:
    - tests_with_steps.json: Contains all tests that have defined test steps
    - tests_without_steps.json: Contains all tests without test steps
    - fetch_progress.json: Tracks progress for resuming interrupted fetches
"""

import json
import requests
import os
import time
import sys
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration with environment variable overrides
GRAPHQL_URL = "https://xray.cloud.getxray.app/api/v2/graphql"
AUTH_ENDPOINT = "https://xray.cloud.getxray.app/api/v2/authenticate"

# Get configuration from environment variables with defaults
PROJECT_ID = os.getenv('PROJECT_ID', '26420')  # Default to MLBMOB project
BATCH_SIZE = int(os.getenv('BATCH_SIZE', '100'))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '5'))
RETRY_WAIT = int(os.getenv('RETRY_WAIT', '2'))  # Base wait time between retries
RATE_LIMIT_DELAY = float(os.getenv('RATE_LIMIT_DELAY', '1'))  # Delay between successful requests

# Output directory is the same as the script location
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Progress tracking file
PROGRESS_FILE = os.path.join(OUTPUT_DIR, 'fetch_progress.json')

# GraphQL query to fetch expanded test information
QUERY = """
query GetExpandedTests($projectId: String, $limit: Int!, $start: Int) {
    getExpandedTests(projectId: $projectId, limit: $limit, start: $start) {
        total
        results {
            issueId
            jira (fields: ["summary", "key", "description", "labels", "priority", "status"])
            steps {
                id
                data
                action
                result
            }
            preconditions (limit: 100, start: 0) {
                total
                results {
                    issueId
                    projectId
                    definition
                    jira (fields: ["key", "summary"])
                }
            }
            testType {
                name
                kind
            }
            folder {
                name
                path
            }
        }
    }
}
"""


class XrayTestFetcher:
    """Handles fetching tests from Xray with retry logic and progress tracking."""
    
    def __init__(self):
        """Initialize the fetcher with configuration and check credentials."""
        self.client_id = os.getenv('XRAY_CLIENT')
        self.client_secret = os.getenv('XRAY_SECRET')
        
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "Missing XRAY_CLIENT or XRAY_SECRET environment variables.\n"
                "Please copy .env.example to .env and fill in your credentials."
            )
        
        self.token = None
        self.token_expiry = None
        self.tests_with_steps = []
        self.tests_without_steps = []
        self.processed_issue_ids = set()
        
    def authenticate(self) -> str:
        """
        Authenticate with Xray API and get JWT token.
        
        Returns:
            str: JWT token for API authentication
            
        Raises:
            Exception: If authentication fails after retries
        """
        auth_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        for attempt in range(MAX_RETRIES):
            try:
                print(f"Authenticating with Xray API (attempt {attempt + 1}/{MAX_RETRIES})...")
                response = requests.post(AUTH_ENDPOINT, json=auth_data, timeout=30)
                
                if response.status_code == 401:
                    raise Exception("Invalid credentials. Please check your XRAY_CLIENT and XRAY_SECRET.")
                
                response.raise_for_status()
                self.token = response.text.strip('"')
                
                # JWT tokens typically expire after 24 hours
                self.token_expiry = time.time() + (23 * 60 * 60)  # 23 hours to be safe
                
                print("✓ Successfully authenticated with Xray API")
                return self.token
                
            except requests.exceptions.RequestException as e:
                if attempt < MAX_RETRIES - 1:
                    wait_time = RETRY_WAIT * (2 ** attempt)  # Exponential backoff
                    print(f"  Authentication failed: {e}")
                    print(f"  Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Failed to authenticate after {MAX_RETRIES} attempts: {e}")
    
    def ensure_valid_token(self):
        """Ensure we have a valid authentication token, refreshing if necessary."""
        if not self.token or time.time() >= self.token_expiry:
            print("Token expired or missing, re-authenticating...")
            self.authenticate()
    
    def fetch_tests_batch(self, start: int) -> Dict[str, Any]:
        """
        Fetch a batch of tests from Xray with retry logic.
        
        Args:
            start: Starting index for the batch
            
        Returns:
            Dict containing the API response
            
        Raises:
            Exception: If the batch cannot be fetched after all retries
        """
        self.ensure_valid_token()
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        variables = {
            "projectId": PROJECT_ID,
            "limit": BATCH_SIZE,
            "start": start
        }
        
        payload = {
            "query": QUERY,
            "variables": variables
        }
        
        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                print(f"  Fetching batch starting at {start} (attempt {attempt + 1}/{MAX_RETRIES})...")
                
                response = requests.post(
                    GRAPHQL_URL, 
                    json=payload, 
                    headers=headers, 
                    timeout=60  # Longer timeout for large batches
                )
                
                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    print(f"  Rate limited. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue
                
                # Handle authentication errors
                if response.status_code == 401:
                    print("  Authentication error, refreshing token...")
                    self.authenticate()
                    headers["Authorization"] = f"Bearer {self.token}"
                    continue
                
                response.raise_for_status()
                result = response.json()
                
                # Check for GraphQL errors
                if 'errors' in result:
                    raise Exception(f"GraphQL errors: {result['errors']}")
                
                # Validate response structure
                if 'data' not in result or 'getExpandedTests' not in result['data']:
                    raise Exception("Invalid response structure")
                
                batch_count = len(result['data']['getExpandedTests']['results'])
                print(f"  ✓ Successfully fetched {batch_count} tests")
                
                return result
                
            except Exception as e:
                last_error = e
                if attempt < MAX_RETRIES - 1:
                    wait_time = RETRY_WAIT * (2 ** attempt)  # Exponential backoff
                    print(f"  Error: {e}")
                    print(f"  Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    print(f"  ✗ Failed to fetch batch after {MAX_RETRIES} attempts")
        
        raise Exception(f"Failed to fetch batch at start={start}: {last_error}")
    
    def process_test_batch(self, results: List[Dict[str, Any]]):
        """
        Process a batch of test results and categorize them.
        
        Args:
            results: List of test objects from the API
        """
        for test in results:
            issue_id = test.get('issueId')
            
            # Skip if we've already processed this test (in case of duplicates)
            if issue_id in self.processed_issue_ids:
                continue
            
            self.processed_issue_ids.add(issue_id)
            
            # Categorize based on whether the test has steps
            if test.get('steps') and len(test['steps']) > 0:
                self.tests_with_steps.append(test)
            else:
                self.tests_without_steps.append(test)
    
    def save_progress(self, current_position: int, total: int):
        """
        Save current progress to allow resuming interrupted fetches.
        
        Args:
            current_position: Current batch starting position
            total: Total number of tests to fetch
        """
        progress_data = {
            'timestamp': datetime.now().isoformat(),
            'project_id': PROJECT_ID,
            'current_position': current_position,
            'total_tests': total,
            'tests_fetched': len(self.processed_issue_ids),
            'tests_with_steps_count': len(self.tests_with_steps),
            'tests_without_steps_count': len(self.tests_without_steps),
            'processed_issue_ids': list(self.processed_issue_ids)
        }
        
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(progress_data, f, indent=2)
    
    def load_progress(self) -> Optional[Dict[str, Any]]:
        """
        Load previous progress if available.
        
        Returns:
            Dict containing progress data or None if no progress file exists
        """
        if os.path.exists(PROGRESS_FILE):
            try:
                with open(PROGRESS_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load progress file: {e}")
        return None
    
    def save_results(self):
        """Save the categorized test results to JSON files."""
        with_steps_file = os.path.join(OUTPUT_DIR, 'tests_with_steps.json')
        without_steps_file = os.path.join(OUTPUT_DIR, 'tests_without_steps.json')
        
        # Save tests with steps
        with open(with_steps_file, 'w') as f:
            json.dump({
                "project_id": PROJECT_ID,
                "fetch_date": datetime.now().isoformat(),
                "total": len(self.tests_with_steps),
                "tests": self.tests_with_steps
            }, f, indent=2)
        
        # Save tests without steps
        with open(without_steps_file, 'w') as f:
            json.dump({
                "project_id": PROJECT_ID,
                "fetch_date": datetime.now().isoformat(),
                "total": len(self.tests_without_steps),
                "tests": self.tests_without_steps
            }, f, indent=2)
        
        print(f"\n✓ Results saved to:")
        print(f"  - {with_steps_file}")
        print(f"  - {without_steps_file}")
    
    def run(self):
        """Main execution method to fetch all tests."""
        print(f"Xray Test Fetcher")
        print(f"================")
        print(f"Project ID: {PROJECT_ID}")
        print(f"Batch Size: {BATCH_SIZE}")
        print(f"Max Retries: {MAX_RETRIES}")
        print(f"Rate Limit Delay: {RATE_LIMIT_DELAY}s\n")
        
        # Check for previous progress
        progress = self.load_progress()
        start_position = 0
        
        if progress and progress.get('project_id') == PROJECT_ID:
            print(f"Found previous progress from {progress['timestamp']}")
            print(f"Tests already fetched: {progress['tests_fetched']}")
            
            resume = input("Resume from previous progress? (y/n): ").lower().strip() == 'y'
            if resume:
                start_position = progress['current_position']
                self.processed_issue_ids = set(progress['processed_issue_ids'])
                print(f"Resuming from position {start_position}...\n")
        
        # Authenticate
        try:
            self.authenticate()
        except Exception as e:
            print(f"❌ Error: {e}")
            return
        
        # Fetch first batch to get total count
        print("Fetching first batch to determine total count...")
        try:
            first_response = self.fetch_tests_batch(0)
        except Exception as e:
            print(f"❌ Failed to fetch initial batch: {e}")
            return
        
        total_tests = first_response['data']['getExpandedTests']['total']
        print(f"\nTotal tests in project: {total_tests}")
        
        # If resuming, load existing data
        if start_position > 0:
            self._load_existing_results()
        else:
            # Process first batch if starting fresh
            results = first_response['data']['getExpandedTests']['results']
            self.process_test_batch(results)
            self.save_progress(BATCH_SIZE, total_tests)
        
        # Calculate batches to fetch
        batches_to_fetch = []
        for batch_start in range(start_position, total_tests, BATCH_SIZE):
            if batch_start > 0:  # Skip first batch if already processed
                batches_to_fetch.append(batch_start)
        
        print(f"Batches to fetch: {len(batches_to_fetch)}")
        print(f"Estimated time: {len(batches_to_fetch) * (RATE_LIMIT_DELAY + 2):.0f} seconds\n")
        
        # Fetch remaining batches
        for i, batch_start in enumerate(batches_to_fetch):
            print(f"\nBatch {i + 1}/{len(batches_to_fetch)}: "
                  f"Fetching tests {batch_start} to {min(batch_start + BATCH_SIZE, total_tests)}...")
            
            try:
                response = self.fetch_tests_batch(batch_start)
                
                # Process batch
                results = response['data']['getExpandedTests']['results']
                self.process_test_batch(results)
                
                # Save progress after each successful batch
                next_position = batch_start + BATCH_SIZE
                self.save_progress(next_position, total_tests)
                
                # Rate limiting delay
                if i < len(batches_to_fetch) - 1:  # Don't delay after last batch
                    time.sleep(RATE_LIMIT_DELAY)
                    
            except Exception as e:
                print(f"❌ Failed to fetch batch at position {batch_start}: {e}")
                print("Progress has been saved. You can resume later.")
                
                # Ask user if they want to continue or stop
                if i < len(batches_to_fetch) - 1:
                    choice = input("\nContinue with next batch? (y/n): ").lower().strip()
                    if choice != 'y':
                        print("Stopping fetch. Progress has been saved.")
                        break
        
        # Save final results
        self.save_results()
        
        # Print summary
        self._print_summary()
        
        # Clean up progress file on successful completion
        if len(self.processed_issue_ids) >= total_tests * 0.95:  # 95% threshold for "complete"
            if os.path.exists(PROGRESS_FILE):
                os.remove(PROGRESS_FILE)
                print("\n✓ Fetch completed successfully. Progress file removed.")
    
    def _load_existing_results(self):
        """Load existing results when resuming."""
        with_steps_file = os.path.join(OUTPUT_DIR, 'tests_with_steps.json')
        without_steps_file = os.path.join(OUTPUT_DIR, 'tests_without_steps.json')
        
        if os.path.exists(with_steps_file):
            with open(with_steps_file, 'r') as f:
                data = json.load(f)
                self.tests_with_steps = data.get('tests', [])
        
        if os.path.exists(without_steps_file):
            with open(without_steps_file, 'r') as f:
                data = json.load(f)
                self.tests_without_steps = data.get('tests', [])
        
        print(f"Loaded {len(self.tests_with_steps)} tests with steps")
        print(f"Loaded {len(self.tests_without_steps)} tests without steps")
    
    def _print_summary(self):
        """Print a summary of the fetch results."""
        total_fetched = len(self.tests_with_steps) + len(self.tests_without_steps)
        
        print("\n" + "=" * 50)
        print("FETCH SUMMARY")
        print("=" * 50)
        print(f"Total tests fetched: {total_fetched}")
        print(f"Tests with steps: {len(self.tests_with_steps)} "
              f"({len(self.tests_with_steps) / max(total_fetched, 1) * 100:.1f}%)")
        print(f"Tests without steps: {len(self.tests_without_steps)} "
              f"({len(self.tests_without_steps) / max(total_fetched, 1) * 100:.1f}%)")
        
        # Show some example tests
        if self.tests_without_steps:
            print("\nExample tests without steps:")
            for test in self.tests_without_steps[:5]:
                jira_data = test.get('jira', {})
                print(f"  - {jira_data.get('key', 'N/A')}: {jira_data.get('summary', 'N/A')}")
            
            if len(self.tests_without_steps) > 5:
                print(f"  ... and {len(self.tests_without_steps) - 5} more")


def main():
    """Main entry point for the script."""
    try:
        fetcher = XrayTestFetcher()
        fetcher.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Fetch interrupted by user. Progress has been saved.")
        print("You can resume by running the script again.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()