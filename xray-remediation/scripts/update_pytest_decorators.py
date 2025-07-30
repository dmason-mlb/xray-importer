#!/usr/bin/env python3
"""
Update pytest.mark.xray decorators with correct JIRA keys for newly created tests.
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime

class PytestDecoratorUpdater:
    """Update pytest decorators with correct JIRA keys"""
    
    def __init__(self):
        self.updated_count = 0
        self.results = []
        
        # Load the complete mapping
        self.load_test_mapping()
        
        # Tests that were just created and need decorator updates
        self.newly_created_tests = {
            "API-001": "FRAMED-1456",
            "API-012": "FRAMED-1459", 
            "API-013": "FRAMED-1460",
            "API-014": "FRAMED-1461",
            "API-015": "FRAMED-1457",
            "API-JE-003": "FRAMED-1462",
            "API-JE-007": "FRAMED-1463",
            "API-JE-008": "FRAMED-1464",
            "API-PERF-001": "FRAMED-1465"
        }
        
    def load_test_mapping(self):
        """Load complete test mapping"""
        mapping_file = Path(__file__).parent.parent / "complete_test_id_mapping.json"
        with open(mapping_file, 'r') as f:
            self.test_mapping = json.load(f)
        
        print(f"Loaded {len(self.test_mapping)} test mappings")
    
    def update_file_decorators(self, file_path):
        """Update pytest decorators in a single file"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            original_content = content
            updates_made = []
            
            # Update @pytest.mark.xray decorators for tests that already exist but need JIRA key updates
            for test_id in ["API-001", "API-012", "API-013", "API-014"]:
                if test_id in self.test_mapping:
                    jira_key = self.test_mapping[test_id]
                    
                    # Pattern to match @pytest.mark.xray("API-XXX")
                    old_pattern = rf'@pytest\.mark\.xray\("{test_id}"\)'
                    new_pattern = f'@pytest.mark.xray("{jira_key}")'
                    
                    if re.search(old_pattern, content):
                        content = re.sub(old_pattern, new_pattern, content)
                        updates_made.append(f"{test_id} → {jira_key}")
            
            # Add @pytest.mark.xray decorators for tests that don't have them yet
            missing_tests = []
            for test_id in ["API-015", "API-JE-003", "API-JE-007", "API-JE-008", "API-PERF-001"]:
                if test_id in self.test_mapping:
                    jira_key = self.test_mapping[test_id]
                    
                    # Check if the test exists in the file but doesn't have xray decorator
                    test_pattern = rf'@allure\.tag\("{test_id}"\)'
                    if re.search(test_pattern, content):
                        # Find the function definition and add the decorator before it
                        func_pattern = rf'(@allure\.tag\("{test_id}"\)\s*def\s+test_[^(]+\([^)]*\):)'
                        
                        def add_decorator(match):
                            existing_code = match.group(1)
                            # Add the decorator just before the @allure.tag line
                            decorator_line = f'    @pytest.mark.xray("{jira_key}")\n    '
                            return decorator_line + existing_code
                        
                        if re.search(func_pattern, content, re.MULTILINE | re.DOTALL):
                            content = re.sub(func_pattern, add_decorator, content, flags=re.MULTILINE | re.DOTALL)
                            updates_made.append(f"Added decorator for {test_id} → {jira_key}")
                        else:
                            missing_tests.append(test_id)
            
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
                
            if missing_tests:
                print(f"⚠ Missing tests in {file_path}: {', '.join(missing_tests)}")
                
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
        print("PYTEST DECORATOR UPDATE")
        print("=" * 80)
        
        # Find all pytest files
        test_files = list(Path(__file__).parent.parent.glob("mlb-app-files/**/test_*.py"))
        
        print(f"\nFound {len(test_files)} test files:")
        for file_path in test_files:
            print(f"  - {file_path}")
        
        print(f"\nUpdating decorators for {len(self.newly_created_tests)} newly created tests...")
        
        # Update each file
        for file_path in test_files:
            self.update_file_decorators(file_path)
        
        # Summary
        print("\n" + "=" * 80)
        print("UPDATE SUMMARY")
        print("=" * 80)
        print(f"Files processed: {len(test_files)}")
        print(f"Files updated: {self.updated_count}")
        print(f"Errors: {len([r for r in self.results if r['status'] == 'error'])}")
        
        # Save results
        self.save_results()
    
    def save_results(self):
        """Save update results to log file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = Path(__file__).parent.parent / "logs" / f"pytest_decorator_update_{timestamp}.json"
        
        results_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'files_processed': len(self.results),
                'files_updated': self.updated_count,
                'errors': len([r for r in self.results if r['status'] == 'error'])
            },
            'newly_created_tests': self.newly_created_tests,
            'file_updates': self.results
        }
        
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\nResults saved to: {results_file}")

def main():
    """Main entry point"""
    updater = PytestDecoratorUpdater()
    updater.update_all_decorators()

if __name__ == "__main__":
    main()