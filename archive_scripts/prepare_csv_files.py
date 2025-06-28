#!/usr/bin/env python3
"""
CSV Preparation Script for XRAY Import
Converts encoding and validates data before import
"""

import csv
import os
import sys
import argparse
import logging
from collections import Counter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def convert_encoding(input_file: str, output_file: str):
    """Convert CSV from UTF-8 to ISO-8859-1"""
    logger.info(f"Converting {input_file} to ISO-8859-1 encoding")
    
    try:
        # Read with UTF-8
        with open(input_file, 'r', encoding='utf-8') as infile:
            content = infile.read()
        
        # Write with ISO-8859-1
        with open(output_file, 'w', encoding='iso-8859-1', errors='replace') as outfile:
            outfile.write(content)
        
        logger.info(f"Successfully converted to {output_file}")
        return True
    except Exception as e:
        logger.error(f"Encoding conversion failed: {str(e)}")
        return False

def analyze_csv_file(filepath: str):
    """Analyze CSV file structure and data quality"""
    logger.info(f"\nAnalyzing {filepath}")
    logger.info("="*60)
    
    stats = {
        'total_rows': 0,
        'empty_titles': 0,
        'missing_type': 0,
        'priorities': Counter(),
        'types': Counter(),
        'sections': Counter(),
        'users': set()
    }
    
    try:
        with open(filepath, 'r', encoding='iso-8859-1') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                stats['total_rows'] += 1
                
                # Check required fields
                if not row.get('Title', '').strip():
                    stats['empty_titles'] += 1
                
                if not row.get('Type', '').strip():
                    stats['missing_type'] += 1
                
                # Collect statistics
                stats['priorities'][row.get('Priority', 'None')] += 1
                stats['types'][row.get('Type', 'None')] += 1
                
                # Track sections
                section = row.get('Section', '').split('/')[0].strip()
                if section:
                    stats['sections'][section] += 1
                
                # Collect unique users
                for field in ['Created By', 'Updated By']:
                    user = row.get(field, '').strip()
                    if user:
                        stats['users'].add(user)
        
        # Print analysis
        logger.info(f"Total rows: {stats['total_rows']}")
        logger.info(f"Empty titles: {stats['empty_titles']}")
        logger.info(f"Missing type: {stats['missing_type']}")
        
        logger.info("\nTest Types:")
        for test_type, count in stats['types'].most_common():
            logger.info(f"  {test_type}: {count}")
        
        logger.info("\nPriorities:")
        for priority, count in stats['priorities'].most_common():
            logger.info(f"  {priority}: {count}")
        
        logger.info("\nTop Sections:")
        for section, count in list(stats['sections'].most_common())[:10]:
            logger.info(f"  {section}: {count}")
        
        logger.info(f"\nUnique users: {len(stats['users'])}")
        
        # Calculate batches needed
        batch_size = 900
        batches_needed = (stats['total_rows'] + batch_size - 1) // batch_size
        logger.info(f"\nBatches needed (at {batch_size} tests/batch): {batches_needed}")
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")

def clean_csv_file(input_file: str, output_file: str):
    """Clean and prepare CSV file for import"""
    logger.info(f"\nCleaning {input_file}")
    
    cleaned_rows = []
    issues_found = 0
    
    try:
        with open(input_file, 'r', encoding='iso-8859-1') as csvfile:
            reader = csv.DictReader(csvfile)
            fieldnames = reader.fieldnames
            
            for row_num, row in enumerate(reader, 2):  # Start at 2 (header is 1)
                cleaned_row = {}
                row_had_issues = False
                
                for field in fieldnames:
                    value = row.get(field, '')
                    
                    # Clean whitespace
                    if isinstance(value, str):
                        value = value.strip()
                    
                    # Fix common issues
                    if field == 'Type' and not value:
                        value = 'Manual'
                        row_had_issues = True
                    
                    if field == 'Priority' and not value:
                        value = '2 - Medium Priority'
                        row_had_issues = True
                    
                    # Ensure title is not empty
                    if field == 'Title' and not value:
                        value = f"Test Case {row.get('ID', row_num)}"
                        row_had_issues = True
                    
                    cleaned_row[field] = value
                
                cleaned_rows.append(cleaned_row)
                if row_had_issues:
                    issues_found += 1
        
        # Write cleaned file
        with open(output_file, 'w', encoding='iso-8859-1', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(cleaned_rows)
        
        logger.info(f"Cleaned {len(cleaned_rows)} rows ({issues_found} had issues)")
        logger.info(f"Saved to {output_file}")
        
    except Exception as e:
        logger.error(f"Cleaning failed: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Prepare CSV files for XRAY import')
    parser.add_argument('action', choices=['convert', 'analyze', 'clean', 'all'],
                       help='Action to perform')
    parser.add_argument('files', nargs='+', help='CSV files to process')
    parser.add_argument('--output-suffix', default='_prepared',
                       help='Suffix for output files (default: _prepared)')
    
    args = parser.parse_args()
    
    for filepath in args.files:
        if not os.path.exists(filepath):
            logger.error(f"File not found: {filepath}")
            continue
        
        base_name = os.path.splitext(filepath)[0]
        output_file = f"{base_name}{args.output_suffix}.csv"
        
        if args.action in ['convert', 'all']:
            convert_encoding(filepath, output_file)
        
        if args.action in ['analyze', 'all']:
            # Analyze the converted file if it exists
            analyze_file = output_file if os.path.exists(output_file) else filepath
            analyze_csv_file(analyze_file)
        
        if args.action in ['clean', 'all']:
            # Clean the converted file if it exists
            input_for_clean = output_file if os.path.exists(output_file) else filepath
            clean_output = f"{base_name}_cleaned.csv"
            clean_csv_file(input_for_clean, clean_output)

if __name__ == '__main__':
    main()