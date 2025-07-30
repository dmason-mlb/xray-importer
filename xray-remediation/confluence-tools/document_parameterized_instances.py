#!/usr/bin/env python3
"""
Document parameterized instances in the Confluence document structure.
This addresses the Medium Priority recommendation from the comprehensive analysis.
"""

import os
import sys
import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

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

class ParameterizedDocumenter:
    """Document parameterized instances in Confluence test cases."""
    
    def __init__(self, confluence_client: ConfluenceClient):
        self.client = confluence_client
        self.logger = logging.getLogger(__name__)
        
        # Known parameterized test cases from analysis
        self.parameterized_tests = {
            'API-003': {
                'description': 'Invalid Team ID test with 5 parameterized instances',
                'instances': [
                    'teamId=999 (non-existent team)',
                    'teamId=0 (invalid zero value)',
                    'teamId=-1 (negative value)',
                    'teamId=abc (non-numeric value)',
                    'missing teamId parameter'
                ],
                'total_instances': 5
            },
            'API-004': {
                'description': 'English Language validation with 3 parameterized instances',
                'instances': [
                    'Date format validation (MM/DD/YYYY)',
                    'Text content validation (English)',
                    'URL localization validation (en-US)'
                ],
                'total_instances': 3
            },
            'API-005': {
                'description': 'Spanish Language validation with 3 parameterized instances',
                'instances': [
                    'Date format validation (DD/MM/YYYY)',
                    'Text content validation (Spanish)',
                    'URL localization validation (es-ES)'
                ],
                'total_instances': 3
            }
        }
    
    def generate_documentation_content(self) -> str:
        """Generate documentation content for parameterized instances."""
        content = []
        
        # Header
        content.append("<h2>Parameterized Test Instance Documentation</h2>")
        content.append(f"<p><em>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>")
        content.append("<p>This section documents the parameterized instances within the API test cases. ")
        content.append("These instances represent variations of base test cases with different parameter values.</p>")
        
        # Summary
        total_instances = sum(test['total_instances'] for test in self.parameterized_tests.values())
        content.append(f"<p><strong>Summary:</strong> {len(self.parameterized_tests)} test cases with {total_instances} total parameterized instances</p>")
        
        # Detailed documentation for each test case
        for test_id, test_info in self.parameterized_tests.items():
            content.append(f"<h3>{test_id}: {test_info['description']}</h3>")
            
            content.append("<table>")
            content.append("<tr><th>Parameter Instance</th><th>Description</th><th>Test Variation</th></tr>")
            
            for i, instance in enumerate(test_info['instances'], 1):
                content.append(f"<tr>")
                content.append(f"<td>{test_id}-{i}</td>")
                content.append(f"<td>{instance}</td>")
                content.append(f"<td>Variation {i} of {test_id}</td>")
                content.append(f"</tr>")
            
            content.append("</table>")
            content.append(f"<p><strong>Total instances for {test_id}:</strong> {test_info['total_instances']}</p>")
        
        # Footer
        content.append("<h3>Implementation Notes</h3>")
        content.append("<ul>")
        content.append("<li>Each parameterized instance represents a distinct test execution with different parameter values</li>")
        content.append("<li>The base test case structure remains the same, only parameter values change</li>")
        content.append("<li>When importing to Xray, these instances can be represented as test data variations</li>")
        content.append(f"<li>Total test instances: 55 base test cases + {total_instances} parameterized instances = {55 + total_instances} total</li>")
        content.append("</ul>")
        
        return "\n".join(content)
    
    def find_insertion_point(self, content: str) -> int:
        """Find the best insertion point for the parameterized documentation."""
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for existing parameterized section
        for heading in soup.find_all(['h1', 'h2', 'h3']):
            if 'parameterized' in heading.get_text().lower():
                return content.find(str(heading))
        
        # Look for a good insertion point (after introduction, before test cases)
        for heading in soup.find_all(['h2', 'h3']):
            heading_text = heading.get_text().lower()
            if any(word in heading_text for word in ['test case', 'api test', 'functional']):
                return content.find(str(heading))
        
        # Default: insert after first h2
        first_h2 = soup.find('h2')
        if first_h2:
            # Find the end of the first section
            next_h2 = first_h2.find_next('h2')
            if next_h2:
                return content.find(str(next_h2))
        
        # Fallback: insert at the end
        return len(content)
    
    def insert_documentation(self, content: str) -> Tuple[str, bool]:
        """Insert parameterized documentation into the content."""
        # Generate documentation
        doc_content = self.generate_documentation_content()
        
        # Find insertion point
        insertion_point = self.find_insertion_point(content)
        
        # Insert documentation
        new_content = (
            content[:insertion_point] + 
            "\n\n" + doc_content + "\n\n" + 
            content[insertion_point:]
        )
        
        return new_content, True
    
    def create_standalone_documentation(self) -> str:
        """Create standalone documentation file."""
        doc_file = Path(__file__).parent / "parameterized_instances_documentation.md"
        
        # Convert HTML to Markdown for standalone file
        md_content = []
        md_content.append("# Parameterized Test Instance Documentation\n")
        md_content.append(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        md_content.append("This document details the parameterized instances within the API test cases.\n")
        
        # Summary
        total_instances = sum(test['total_instances'] for test in self.parameterized_tests.values())
        md_content.append(f"**Summary:** {len(self.parameterized_tests)} test cases with {total_instances} total parameterized instances\n")
        
        # Detailed documentation
        for test_id, test_info in self.parameterized_tests.items():
            md_content.append(f"## {test_id}: {test_info['description']}\n")
            
            md_content.append("| Parameter Instance | Description | Test Variation |")
            md_content.append("|-------------------|-------------|----------------|")
            
            for i, instance in enumerate(test_info['instances'], 1):
                md_content.append(f"| {test_id}-{i} | {instance} | Variation {i} of {test_id} |")
            
            md_content.append(f"\n**Total instances for {test_id}:** {test_info['total_instances']}\n")
        
        # Implementation notes
        md_content.append("## Implementation Notes\n")
        md_content.append("- Each parameterized instance represents a distinct test execution with different parameter values")
        md_content.append("- The base test case structure remains the same, only parameter values change")
        md_content.append("- When importing to Xray, these instances can be represented as test data variations")
        md_content.append(f"- Total test instances: 55 base test cases + {total_instances} parameterized instances = {55 + total_instances} total\n")
        
        # Write to file
        with open(doc_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(md_content))
        
        return str(doc_file)

def main():
    """Main documentation function."""
    try:
        # Get configuration
        config = get_config()
        if not config:
            logger.error("Failed to load configuration")
            sys.exit(1)
        
        # Initialize client
        client = ConfluenceClient(config['domain'], config['email'], config['api_token'])
        documenter = ParameterizedDocumenter(client)
        
        # Create standalone documentation
        logger.info("Creating standalone parameterized instances documentation...")
        doc_file = documenter.create_standalone_documentation()
        logger.info(f"Created standalone documentation: {doc_file}")
        
        # Generate summary report
        total_instances = sum(test['total_instances'] for test in documenter.parameterized_tests.values())
        
        print("\n" + "="*50)
        print("PARAMETERIZED INSTANCES DOCUMENTATION")
        print("="*50)
        print(f"Test cases with parameterized instances: {len(documenter.parameterized_tests)}")
        print(f"Total parameterized instances: {total_instances}")
        print(f"Total test instances: 55 base + {total_instances} parameterized = {55 + total_instances}")
        print("\nBreakdown:")
        
        for test_id, test_info in documenter.parameterized_tests.items():
            print(f"  {test_id}: {test_info['total_instances']} instances")
            print(f"    - {test_info['description']}")
        
        print(f"\nStandalone documentation created: {doc_file}")
        
        # Ask if user wants to update Confluence page
        response = input("\nDo you want to add this documentation to the Confluence page? (y/N): ")
        if response.lower() == 'y':
            page_id = "4904878140"
            logger.info(f"Adding documentation to Confluence page {page_id}")
            
            # Fetch current page
            try:
                page = client.get_page(page_id, expand=['body.storage'])
                content = page['body']['storage']['value']
                
                # Insert documentation
                new_content, success = documenter.insert_documentation(content)
                
                if success:
                    # Update page
                    update_data = {
                        'version': {
                            'number': page['version']['number'] + 1,
                            'message': 'Added parameterized instances documentation'
                        },
                        'title': page['title'],
                        'type': 'page',
                        'body': {
                            'storage': {
                                'value': new_content,
                                'representation': 'storage'
                            }
                        }
                    }
                    
                    updated_page = client.update_page(page_id, update_data)
                    logger.info(f"Successfully updated page to version {updated_page['version']['number']}")
                    
                else:
                    logger.error("Failed to insert documentation")
                    
            except Exception as e:
                logger.error(f"Failed to update Confluence page: {e}")
        
        logger.info("✓ Parameterized instances documentation completed")
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()