#!/usr/bin/env python3
"""
Update TEAM_PAGE_TEST_CATALOG.md with functional test JIRA keys.
For Xray Remediation Project - July 31, 2025
"""

import json
from pathlib import Path

def load_test_mapping():
    """Load the functional test mapping"""
    mapping_file = Path(__file__).parent.parent / "logs" / "functional_test_mapping.json"
    with open(mapping_file, 'r') as f:
        return json.load(f)

def load_test_data():
    """Load functional test data for descriptions"""
    json_file = Path(__file__).parent.parent / "test-data" / "functional_tests_xray.json"
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Create a dictionary of test info keyed by TC-XXX
    test_info = {}
    for test in data['tests']:
        test_id = test['testInfo']['summary']
        desc = test['testInfo']['description'].split('\n')[0].replace('Folder: Team Page/', '')
        priority = test['testInfo']['priority']
        test_info[test_id] = {
            'description': desc,
            'priority': priority
        }
    
    return test_info

def update_catalog():
    """Update the catalog file"""
    catalog_file = Path(__file__).parent.parent / "TEAM_PAGE_TEST_CATALOG.md"
    mapping = load_test_mapping()
    test_info = load_test_data()
    
    # Read the catalog
    with open(catalog_file, 'r') as f:
        lines = f.readlines()
    
    # Find the functional tests section
    functional_start = None
    functional_end = None
    
    for i, line in enumerate(lines):
        if "## Functional Tests (38 Total)" in line:
            # Found the start, now find the table
            for j in range(i, len(lines)):
                if "| Test ID | Description | Priority | Components | Status |" in lines[j]:
                    functional_start = j + 2  # Skip header and separator
                    break
            # Find the end of the table
            if functional_start is not None:
                for j in range(functional_start, len(lines)):
                    if lines[j].strip() == "" or (not lines[j].startswith("|") and "---" not in lines[j]):
                        functional_end = j
                        break
            break
    
    if functional_start is None or functional_end is None:
        print("Could not find functional tests section")
        print(f"functional_start: {functional_start}, functional_end: {functional_end}")
        return
    
    # Build new table rows matching the expected format
    new_rows = []
    for test_id in sorted(mapping.keys()):
        jira_key = mapping[test_id]
        info = test_info.get(test_id, {})
        desc = info.get('description', '')
        priority = info.get('priority', 'Medium')
        
        # Format: | Test ID | Description | Priority | Components | Status |
        row = f"| {jira_key} | {test_id}: {desc} | {priority} | team_page | ✅ Created |\n"
        new_rows.append(row)
    
    # Replace the old rows
    new_lines = lines[:functional_start] + new_rows + lines[functional_end:]
    
    # Write back
    with open(catalog_file, 'w') as f:
        f.writelines(new_lines)
    
    print(f"✅ Updated {len(new_rows)} functional tests in catalog")
    print(f"📄 Updated: {catalog_file}")

def main():
    """Main execution"""
    print("🔄 Updating TEAM_PAGE_TEST_CATALOG.md with functional test JIRA keys...")
    update_catalog()
    print("✨ Catalog update complete!")

if __name__ == "__main__":
    main()