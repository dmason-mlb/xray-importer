#!/usr/bin/env python3
"""
Update ALL pytest.mark.xray decorators with correct JIRA keys for ALL API tests.
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime

class ComprehensivePytestDecoratorUpdater:
    """Update pytest decorators with correct JIRA keys for ALL API tests"""
    
    def __init__(self):
        self.updated_count = 0
        self.results = []
        
        # Load the complete mapping
        self.load_test_mapping()
        
        # Base path to pytest files
        self.pytest_base_path = "/Users/douglas.mason/Documents/GitHub/MLB-App-Worktrees/framed-api-tests/Service/Bullpen/test/pytest-allure/tests"
        
    def load_test_mapping(self):
        """Load complete test mapping"""
        mapping_file = Path(__file__).parent.parent / "complete_test_id_mapping.json"
        with open(mapping_file, 'r') as f:
            self.test_mapping = json.load(f)
        
        print(f"Loaded {len(self.test_mapping)} test mappings")
    
    def find_test_decorator_location(self, file_path, test_case_id):
        """Find where to insert the @pytest.mark.xray decorator for a specific test"""
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            # Look for the test case ID in docstring
            for i, line in enumerate(lines):
                if f"Test Case ID: {test_case_id}" in line:
                    # Go backwards to find the function definition
                    for j in range(i, -1, -1):
                        if re.match(r'\s*def test_', lines[j]):
                            # Go backwards from function def to find where decorators start
                            for k in range(j-1, -1, -1):
                                if not lines[k].strip().startswith('@') and not lines[k].strip() == '':
                                    # Insert position is after this line
                                    return k + 1, j
                            return j, j  # Insert right before function if no decorators found
            return None, None
        except Exception as e:
            print(f"Error finding decorator location in {file_path}: {e}")
            return None, None
    
    def update_file_decorators(self, file_path):
        """Update pytest decorators in a single file"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            original_content = content
            updates_made = []
            
            # Find all API test case IDs in this file
            test_case_matches = re.findall(r'Test Case ID: (API-[A-Z0-9-]+)', content)
            
            for test_case_id in set(test_case_matches):
                if test_case_id in self.test_mapping:
                    jira_key = self.test_mapping[test_case_id]
                    
                    # Check if decorator already exists
                    existing_pattern = rf'@pytest\.mark\.xray\("{jira_key}"\)'
                    if re.search(existing_pattern, content):
                        print(f"  - {test_case_id} already has correct decorator: {jira_key}")
                        continue
                    
                    # Find the function that contains this test case ID
                    # Look for the allure.title or allure.tag that matches
                    title_pattern = rf'@allure\.title\("[^"]*{re.escape(test_case_id)}[^"]*"\)'
                    tag_pattern = rf'@allure\.tag\("{re.escape(test_case_id)}"\)'
                    
                    title_match = re.search(title_pattern, content)
                    tag_match = re.search(tag_pattern, content)
                    
                    if title_match or tag_match:
                        # Find the position to insert the decorator
                        match_pos = title_match.start() if title_match else tag_match.start()
                        
                        # Find the beginning of this decorator block by going backwards
                        lines_before_match = content[:match_pos].split('\n')
                        
                        # Go backwards to find where decorators start
                        insert_line_idx = len(lines_before_match) - 1
                        while insert_line_idx > 0:
                            line = lines_before_match[insert_line_idx - 1].strip()
                            if line.startswith('@') or line == '':
                                insert_line_idx -= 1
                            else:
                                break
                        
                        # Insert the xray decorator
                        lines = content.split('\n')
                        indent = '    '  # Standard pytest indent
                        
                        # Find the actual line in the split content that corresponds to our position
                        char_count = 0
                        line_to_insert = 0
                        for idx, line in enumerate(lines):
                            if char_count >= match_pos:
                                line_to_insert = idx
                                break
                            char_count += len(line) + 1  # +1 for newline
                        
                        # Go back to find the first decorator of this test
                        while line_to_insert > 0 and (lines[line_to_insert - 1].strip().startswith('@') or lines[line_to_insert - 1].strip() == ''):
                            line_to_insert -= 1
                        
                        # Insert the xray decorator
                        xray_decorator = f'{indent}@pytest.mark.xray("{jira_key}")'
                        lines.insert(line_to_insert, xray_decorator)
                        content = '\n'.join(lines)
                        updates_made.append(f"{test_case_id} → {jira_key}")
                    else:
                        print(f"  ⚠ Could not find decorator location for {test_case_id}")
            
            # Save changes if any were made
            if content != original_content:
                with open(file_path, 'w') as f:
                    f.write(content)
                
                self.results.append({
                    'file': str(file_path),
                    'updates': updates_made,
                    'status': 'updated'
                })
                self.updated_count += 1
                print(f"✓ Updated {file_path}")
                for update in updates_made:
                    print(f"  - {update}")
            else:
                print(f"- No updates needed in {file_path}")
                
        except Exception as e:
            print(f"✗ Error updating {file_path}: {e}")
            self.results.append({
                'file': str(file_path),
                'error': str(e),
                'status': 'error'
            })
    
    def update_all_decorators(self):
        """Update decorators in all pytest files"""
        print("=" * 80)
        print("COMPREHENSIVE PYTEST DECORATOR UPDATE - ALL API TESTS")
        print("=" * 80)
        
        # Find all pytest files in team_page directory
        test_files = [
            Path(self.pytest_base_path) / "team_page" / "test_team_page.py",
            Path(self.pytest_base_path) / "team_page" / "test_team_page_extended.py", 
            Path(self.pytest_base_path) / "team_page" / "test_team_page_integration.py"
        ]
        
        print(f"\nFound {len(test_files)} test files:")
        for file_path in test_files:
            print(f"  - {file_path}")
        
        print(f"\nUpdating decorators for ALL API tests...")
        
        # Update each file
        for file_path in test_files:
            if file_path.exists():
                print(f"\nProcessing {file_path.name}...")
                self.update_file_decorators(file_path)
            else:
                print(f"⚠ File not found: {file_path}")
        
        # Summary
        print("\n" + "=" * 80)
        print("UPDATE SUMMARY")
        print("=" * 80)
        print(f"Files processed: {len([r for r in self.results if r['status'] != 'error'])} / {len(test_files)}")
        print(f"Files updated: {self.updated_count}")
        print(f"Errors: {len([r for r in self.results if r['status'] == 'error'])}")
        
        # Count total decorators added
        total_decorators = sum(len(r.get('updates', [])) for r in self.results)
        print(f"Total decorators added: {total_decorators}")
        
        # Save results
        self.save_results()
    
    def save_results(self):
        """Save update results to log file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = Path(__file__).parent.parent / "logs" / f"comprehensive_pytest_decorator_update_{timestamp}.json"
        
        results_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'files_processed': len([r for r in self.results if r['status'] != 'error']),
                'files_updated': self.updated_count,
                'total_decorators_added': sum(len(r.get('updates', [])) for r in self.results),
                'errors': len([r for r in self.results if r['status'] == 'error'])
            },
            'test_mapping_used': self.test_mapping,
            'file_updates': self.results
        }
        
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\nResults saved to: {results_file}")

def main():
    """Main entry point"""
    updater = ComprehensivePytestDecoratorUpdater()
    updater.update_all_decorators()

if __name__ == "__main__":
    main()