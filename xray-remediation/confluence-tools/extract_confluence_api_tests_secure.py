#!/usr/bin/env python3
"""
Secure API test case extraction from Confluence with proper HTML parsing and input validation.
This version addresses security vulnerabilities identified in the analysis.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass

# Security: Import BeautifulSoup instead of using regex for HTML parsing
try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: BeautifulSoup4 is required. Install with: pip install beautifulsoup4")
    sys.exit(1)

# Add confluence-tool scripts to path
sys.path.append('/Users/douglas.mason/Documents/GitHub/confluence-tool/scripts')

try:
    from confluence_client import ConfluenceClient
    from config import get_config
except ImportError as e:
    print(f"Error importing confluence modules: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TestCase:
    """Data class for test case information."""
    test_id: str
    summary: str
    description: str
    labels: List[str]
    priority: str
    steps: List[Dict]
    expected_results: str
    preconditions: List[str]

class SecureTestExtractor:
    """Secure test case extractor with proper input validation and error handling."""
    
    def __init__(self, confluence_client: ConfluenceClient):
        self.client = confluence_client
        self.logger = logging.getLogger(__name__)
        
    def validate_page_content(self, page_data: Dict) -> bool:
        """Validate Confluence page response structure."""
        required_fields = ['title', 'body', 'version']
        
        for field in required_fields:
            if field not in page_data:
                self.logger.error(f"Missing required field: {field}")
                return False
                
        if 'storage' not in page_data['body']:
            self.logger.error("Missing storage body in page data")
            return False
            
        if 'value' not in page_data['body']['storage']:
            self.logger.error("Missing storage value in page data")
            return False
            
        return True
    
    def sanitize_html_content(self, html_content: str) -> str:
        """Sanitize HTML content to prevent injection attacks."""
        if not html_content or not isinstance(html_content, str):
            return ""
            
        # Basic sanitization - remove potentially dangerous elements
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        return str(soup)
    
    def validate_test_id(self, test_id: str) -> bool:
        """Validate test ID format."""
        if not test_id or not isinstance(test_id, str):
            return False
            
        # API test IDs should match pattern: API-xxx
        import re
        pattern = r'^API-[A-Z0-9]+$'
        return bool(re.match(pattern, test_id.strip()))
    
    def extract_test_cases_from_content(self, content: str) -> List[TestCase]:
        """Extract test cases using BeautifulSoup instead of regex."""
        if not content:
            self.logger.warning("Empty content provided")
            return []
            
        # Sanitize input
        content = self.sanitize_html_content(content)
        
        test_cases = []
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find all test case headings (H3 and H4)
        headings = soup.find_all(['h3', 'h4'])
        
        for heading in headings:
            heading_text = heading.get_text(strip=True)
            
            # Look for API test IDs in heading
            if 'API-' in heading_text:
                # Extract test ID
                import re
                match = re.search(r'API-[A-Z0-9]+', heading_text)
                if match:
                    test_id = match.group(0).strip().rstrip(':')
                    
                    # Validate test ID
                    if not self.validate_test_id(test_id):
                        self.logger.warning(f"Invalid test ID format: {test_id}")
                        continue
                    
                    # Extract content following this heading
                    test_content = self._extract_test_content(heading)
                    
                    if test_content:
                        test_case = self._parse_test_case(test_id, test_content)
                        if test_case:
                            test_cases.append(test_case)
        
        # Remove duplicates based on test ID
        return self._remove_duplicates(test_cases)
    
    def _extract_test_content(self, heading) -> Optional[BeautifulSoup]:
        """Extract content between current heading and next heading."""
        content_elements = []
        
        # Find all siblings after the heading until next heading
        for sibling in heading.next_siblings:
            if sibling.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                break
            if sibling.name:  # Skip text nodes
                content_elements.append(sibling)
        
        if not content_elements:
            return None
            
        # Create a new soup with just the content
        content_soup = BeautifulSoup("", 'html.parser')
        for element in content_elements:
            content_soup.append(element.extract())
            
        return content_soup
    
    def _parse_test_case(self, test_id: str, content: BeautifulSoup) -> Optional[TestCase]:
        """Parse test case information from content."""
        try:
            # Extract table data if present
            table_data = {}
            table = content.find('table')
            if table:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True).replace('*', '')
                        value = cells[1].get_text(strip=True)
                        if key and value:
                            table_data[key] = value
            
            # Extract test information
            summary = table_data.get('Test Case ID', f"Test case {test_id}")
            if summary == test_id or not summary.strip():
                summary = f"Test case {test_id}"
            
            # Build description
            description = ""
            endpoint = table_data.get('Endpoint', '')
            request_info = table_data.get('Request', '')
            headers = table_data.get('Headers', '')
            platforms = table_data.get('Platform/Platforms', 'iOS, Android')
            
            if endpoint:
                description += f"Endpoint: {endpoint}\n"
            if request_info:
                description += f"Request: {request_info}\n"
            if headers:
                description += f"Headers: {headers}\n"
            if platforms:
                description += f"Platforms: {platforms}\n"
            
            # Parse validation steps
            steps = []
            validations = table_data.get('Validations', '')
            if validations:
                validation_items = validations.split('\n')
                for i, item in enumerate(validation_items, 1):
                    item = item.strip()
                    if item:
                        steps.append({
                            "index": i,
                            "action": f"Validate: {item}",
                            "data": "",
                            "result": ""
                        })
            
            # Expected results
            expected_results = table_data.get('Expected Response', validations)
            
            # Parse preconditions
            preconditions = []
            preconditions_text = table_data.get('Preconditions', table_data.get('Precondition', ''))
            if preconditions_text:
                precond_items = preconditions_text.split('\n')
                for item in precond_items:
                    item = item.strip()
                    if item:
                        preconditions.append(item)
            
            # Determine priority and labels
            priority = "Medium"
            labels = ["api", "team_page", "cross_platform"]
            
            # Add specific labels based on test ID patterns
            if "REG" in test_id:
                labels.extend(["regression", "high"])
                priority = "High"
            elif "PERF" in test_id:
                labels.extend(["performance", "high"])
                priority = "High"
            elif "SEC" in test_id:
                labels.extend(["security", "high"])
                priority = "High"
            elif "ERR" in test_id:
                labels.extend(["error_handling", "medium"])
            elif "DATA" in test_id:
                labels.extend(["data_validation", "medium"])
            elif "INT" in test_id:
                labels.extend(["integration", "high"])
                priority = "High"
            elif "GS" in test_id:
                labels.extend(["game_state", "high"])
                priority = "High"
            elif "JE" in test_id:
                labels.extend(["jewel_event", "high"])
                priority = "High"
            
            labels.append(test_id)
            
            return TestCase(
                test_id=test_id,
                summary=summary,
                description=description,
                labels=labels,
                priority=priority,
                steps=steps,
                expected_results=expected_results,
                preconditions=preconditions
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing test case {test_id}: {e}")
            return None
    
    def _remove_duplicates(self, test_cases: List[TestCase]) -> List[TestCase]:
        """Remove duplicate test cases based on test ID."""
        unique_cases = []
        seen_ids: Set[str] = set()
        
        for test_case in test_cases:
            if test_case.test_id not in seen_ids:
                seen_ids.add(test_case.test_id)
                unique_cases.append(test_case)
            else:
                self.logger.warning(f"Duplicate test case removed: {test_case.test_id}")
        
        return unique_cases
    
    def convert_to_xray_format(self, test_cases: List[TestCase], page_info: Dict) -> Dict:
        """Convert test cases to Xray JSON format."""
        xray_tests = []
        
        for test_case in test_cases:
            xray_test = {
                "testInfo": {
                    "summary": test_case.summary,
                    "description": test_case.description,
                    "labels": test_case.labels,
                    "priority": test_case.priority,
                    "testType": "Generic",
                    "steps": test_case.steps,
                    "expectedResults": test_case.expected_results,
                    "preconditions": test_case.preconditions
                },
                "testId": test_case.test_id
            }
            xray_tests.append(xray_test)
        
        # Create Xray JSON structure
        xray_data = {
            "info": {
                "project": "FRAMED",
                "summary": "API Test Cases - Team Page",
                "description": "Automated API test cases for Team Page service endpoints extracted from Confluence",
                "user": "system",  # Don't expose actual user email
                "revision": str(page_info.get('version', {}).get('number', 1)),
                "startDate": "2025-07-17T00:00:00Z",
                "finishDate": "2025-07-17T23:59:59Z",
                "testPlanKey": ""
            },
            "tests": xray_tests
        }
        
        return xray_data

def validate_credentials(config: Dict) -> bool:
    """Validate API credentials without exposing them."""
    required_fields = ['domain', 'email', 'api_token']
    
    for field in required_fields:
        if field not in config or not config[field]:
            logger.error(f"Missing required configuration: {field}")
            return False
    
    # Basic format validation
    if '@' not in config['email']:
        logger.error("Invalid email format")
        return False
        
    if not config['domain'].startswith(('http://', 'https://')):
        logger.error("Invalid domain format")
        return False
    
    return True

def main():
    """Main function with comprehensive error handling."""
    try:
        # Get configuration with validation
        config = get_config()
        if not config:
            logger.error("Failed to load configuration")
            sys.exit(1)
        
        # Validate credentials
        if not validate_credentials(config):
            logger.error("Invalid credentials")
            sys.exit(1)
        
        # Initialize client
        client = ConfluenceClient(config['domain'], config['email'], config['api_token'])
        extractor = SecureTestExtractor(client)
        
        page_id = "4904878140"
        logger.info(f"Fetching Confluence page {page_id}")
        
        # Fetch page with error handling
        try:
            page = client.get_page(page_id, expand=['body.storage'])
        except Exception as e:
            logger.error(f"Failed to fetch page {page_id}: {e}")
            sys.exit(1)
        
        # Validate page response
        if not extractor.validate_page_content(page):
            logger.error("Invalid page content structure")
            sys.exit(1)
        
        content = page['body']['storage']['value']
        
        logger.info(f"Page title: {page['title']}")
        logger.info(f"Page version: {page['version']['number']}")
        
        # Extract test cases
        logger.info("Extracting test cases...")
        test_cases = extractor.extract_test_cases_from_content(content)
        
        if not test_cases:
            logger.warning("No test cases found")
            sys.exit(1)
        
        logger.info(f"Found {len(test_cases)} test cases")
        
        # Convert to Xray format
        xray_data = extractor.convert_to_xray_format(test_cases, page)
        
        # Save to file
        output_file = Path(__file__).parent / "api_tests_xray_secure.json"
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(xray_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Created secure Xray JSON file: {output_file}")
        except Exception as e:
            logger.error(f"Failed to write output file: {e}")
            sys.exit(1)
        
        # Print summary
        logger.info("Test Case Summary:")
        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"{i:2d}. {test_case.test_id}: {test_case.summary}")
        
        logger.info("Extraction completed successfully")
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()