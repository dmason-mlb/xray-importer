#!/usr/bin/env python3
"""
Normalize Confluence document formatting by standardizing all API test case headings to H3 level.
This addresses the High Priority recommendation from the comprehensive analysis.
"""

import os
import sys
import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Tuple

# Security: Import BeautifulSoup for proper HTML parsing
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

class DocumentNormalizer:
    """Normalize Confluence document formatting for consistent heading levels."""
    
    def __init__(self, confluence_client: ConfluenceClient):
        self.client = confluence_client
        self.logger = logging.getLogger(__name__)
    
    def analyze_heading_structure(self, content: str) -> Dict:
        """Analyze current heading structure to identify inconsistencies."""
        soup = BeautifulSoup(content, 'html.parser')
        
        h3_tests = []
        h4_tests = []
        
        # Find all H3 and H4 headings with API test IDs
        for heading in soup.find_all(['h3', 'h4']):
            heading_text = heading.get_text(strip=True)
            if 'API-' in heading_text:
                # Extract test ID
                match = re.search(r'API-[A-Z0-9]+', heading_text)
                if match:
                    test_id = match.group(0).strip().rstrip(':')
                    
                    if heading.name == 'h3':
                        h3_tests.append(test_id)
                    else:
                        h4_tests.append(test_id)
        
        analysis = {
            'h3_tests': sorted(h3_tests),
            'h4_tests': sorted(h4_tests),
            'h3_count': len(h3_tests),
            'h4_count': len(h4_tests),
            'total_tests': len(h3_tests) + len(h4_tests),
            'duplicates': list(set(h3_tests) & set(h4_tests))
        }
        
        return analysis
    
    def normalize_heading_levels(self, content: str) -> Tuple[str, List[str]]:
        """Normalize all API test case headings to H3 level."""
        soup = BeautifulSoup(content, 'html.parser')
        changes = []
        
        # Find all H4 headings that contain API test IDs
        h4_headings = soup.find_all('h4')
        
        for heading in h4_headings:
            heading_text = heading.get_text(strip=True)
            if 'API-' in heading_text:
                # Extract test ID for logging
                match = re.search(r'API-[A-Z0-9]+', heading_text)
                if match:
                    test_id = match.group(0).strip().rstrip(':')
                    
                    # Change H4 to H3
                    heading.name = 'h3'
                    changes.append(f"Changed {test_id} from H4 to H3")
                    self.logger.info(f"Normalized {test_id}: H4 → H3")
        
        return str(soup), changes
    
    def validate_normalization(self, content: str) -> bool:
        """Validate that normalization was successful."""
        analysis = self.analyze_heading_structure(content)
        
        # After normalization, all API tests should be H3
        if analysis['h4_count'] == 0:
            self.logger.info("✓ All API test cases are now H3 headings")
            return True
        else:
            self.logger.warning(f"⚠️ Still found {analysis['h4_count']} H4 API test headings")
            return False
    
    def create_backup(self, page_data: Dict) -> str:
        """Create a backup of the original page content."""
        backup_file = Path(__file__).parent / f"confluence_backup_{page_data['id']}_v{page_data['version']['number']}.json"
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(page_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Created backup: {backup_file}")
        return str(backup_file)
    
    def update_page_content(self, page_id: str, new_content: str, version: int) -> bool:
        """Update Confluence page with normalized content."""
        try:
            # Get current page to ensure we have the latest version
            current_page = self.client.get_page(page_id)
            current_version = current_page['version']['number']
            
            if current_version != version:
                self.logger.warning(f"Version mismatch: expected {version}, got {current_version}")
                return False
            
            # Update page content
            update_data = {
                'version': {
                    'number': version + 1,
                    'message': 'Normalized API test case heading levels to H3 for consistency'
                },
                'title': current_page['title'],
                'type': 'page',
                'body': {
                    'storage': {
                        'value': new_content,
                        'representation': 'storage'
                    }
                }
            }
            
            updated_page = self.client.update_page(page_id, update_data)
            self.logger.info(f"Successfully updated page to version {updated_page['version']['number']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update page: {e}")
            return False

def main():
    """Main normalization function."""
    try:
        # Get configuration
        config = get_config()
        if not config:
            logger.error("Failed to load configuration")
            sys.exit(1)
        
        # Initialize client
        client = ConfluenceClient(config['domain'], config['email'], config['api_token'])
        normalizer = DocumentNormalizer(client)
        
        page_id = "4904878140"
        logger.info(f"Starting normalization for Confluence page {page_id}")
        
        # Fetch current page
        try:
            page = client.get_page(page_id, expand=['body.storage'])
        except Exception as e:
            logger.error(f"Failed to fetch page {page_id}: {e}")
            sys.exit(1)
        
        content = page['body']['storage']['value']
        
        logger.info(f"Page title: {page['title']}")
        logger.info(f"Page version: {page['version']['number']}")
        
        # Analyze current structure
        logger.info("Analyzing current heading structure...")
        analysis = normalizer.analyze_heading_structure(content)
        
        logger.info(f"Current structure:")
        logger.info(f"  H3 headings: {analysis['h3_count']} test cases")
        logger.info(f"  H4 headings: {analysis['h4_count']} test cases")
        logger.info(f"  Total tests: {analysis['total_tests']}")
        
        if analysis['duplicates']:
            logger.warning(f"Found duplicate test IDs: {analysis['duplicates']}")
        
        # Check if normalization is needed
        if analysis['h4_count'] == 0:
            logger.info("✓ No normalization needed - all API tests are already H3")
            return
        
        # Create backup before making changes
        backup_file = normalizer.create_backup(page)
        
        # Normalize heading levels
        logger.info("Normalizing heading levels...")
        normalized_content, changes = normalizer.normalize_heading_levels(content)
        
        # Validate normalization
        if not normalizer.validate_normalization(normalized_content):
            logger.error("Normalization validation failed")
            sys.exit(1)
        
        # Log changes
        logger.info(f"Made {len(changes)} changes:")
        for change in changes:
            logger.info(f"  - {change}")
        
        # Ask for confirmation before updating
        print("\n" + "="*50)
        print("NORMALIZATION SUMMARY")
        print("="*50)
        print(f"Page: {page['title']}")
        print(f"Changes: {len(changes)} headings normalized from H4 to H3")
        print(f"Backup created: {backup_file}")
        print("\nChanges to be made:")
        for change in changes:
            print(f"  - {change}")
        
        response = input("\nDo you want to apply these changes? (y/N): ")
        if response.lower() != 'y':
            logger.info("Normalization cancelled by user")
            return
        
        # Update page
        logger.info("Updating Confluence page...")
        success = normalizer.update_page_content(page_id, normalized_content, page['version']['number'])
        
        if success:
            logger.info("✓ Document normalization completed successfully")
            
            # Verify the changes
            logger.info("Verifying changes...")
            updated_page = client.get_page(page_id, expand=['body.storage'])
            final_analysis = normalizer.analyze_heading_structure(updated_page['body']['storage']['value'])
            
            logger.info(f"Final structure:")
            logger.info(f"  H3 headings: {final_analysis['h3_count']} test cases")
            logger.info(f"  H4 headings: {final_analysis['h4_count']} test cases")
            
            if final_analysis['h4_count'] == 0:
                logger.info("✓ All API test cases are now consistently formatted as H3 headings")
            else:
                logger.warning("⚠️ Some H4 headings may still exist")
                
        else:
            logger.error("Failed to update page")
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()