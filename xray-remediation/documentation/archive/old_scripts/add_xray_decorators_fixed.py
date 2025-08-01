#!/usr/bin/env python3
"""
FIXED VERSION: Add Xray decorators to pytest test files while keeping @allure.tag decorators.
Maps Test Case IDs to actual JIRA issue keys.
"""

import re
import os
import json
from pathlib import Path
from datetime import datetime

class XrayDecoratorAdder:
    """Add Xray decorators to pytest tests using JIRA issue key mappings."""
    
    def __init__(self):
        self.files_processed = 0
        self.tests_updated = 0
        self.tests_skipped = 0
        self.missing_mappings = []
        self.errors = []
        self.load_test_mapping()
        
    def load_test_mapping(self):
        """Load Test Case ID to JIRA issue key mapping."""
        mapping_file = Path(__file__).parent.parent / "complete_test_id_mapping.json"
        try:
            with open(mapping_file, 'r') as f:
                self.test_mapping = json.load(f)
            print(f"✓ Loaded {len(self.test_mapping)} test mappings")
        except FileNotFoundError:
            print(f"⚠️  Mapping file not found: {mapping_file}")
            self.test_mapping = {}
        
    def find_test_files(self):
        """Find all pytest test files."""
        test_dir = Path("/Users/douglas.mason/Documents/GitHub/MLB-App/Service/Bullpen/test/pytest-allure/tests/team_page")
        return list(test_dir.glob("test_*.py"))
        
    def extract_test_id_from_allure_tag(self, line):
        """Extract test ID from @allure.tag decorator."""
        match = re.search(r'@allure\.tag\("(API-[A-Z0-9-]+)"\)', line)
        if match:
            return match.group(1)
        return None
        
    def add_xray_decorator(self, content):
        """Add Xray decorators to test methods while keeping @allure.tag."""
        lines = content.split('\n')
        new_lines = []
        modified = False
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check if this is a test method definition
            if re.match(r'^\s*def test_\w+\(', line):
                # Look backwards for @allure.tag decorator to get test ID
                test_id = None
                indent = len(line) - len(line.lstrip())
                
                # Check previous lines for @allure.tag
                for j in range(i - 1, max(-1, i - 20), -1):
                    if j >= 0 and '@allure.tag(' in lines[j]:
                        test_id = self.extract_test_id_from_allure_tag(lines[j])
                        if test_id:
                            break
                
                if test_id:
                    # Check if we have a JIRA mapping for this test ID
                    jira_key = self.test_mapping.get(test_id)
                    
                    if jira_key:
                        # Check if xray decorator already exists
                        xray_exists = False
                        for j in range(max(0, i - 15), i):
                            if '@pytest.mark.xray(' in lines[j]:
                                xray_exists = True
                                break
                        
                        if not xray_exists:
                            # Add the decorator right before the test method
                            new_lines.append(f'{" " * indent}@pytest.mark.xray("{jira_key}")')
                            new_lines.append(line)
                            modified = True
                            self.tests_updated += 1
                            print(f"    ✓ Added @pytest.mark.xray(\"{jira_key}\") for {test_id}")
                            i += 1
                            continue
                    else:
                        # No JIRA mapping found
                        if f"{test_id} (no JIRA mapping)" not in self.missing_mappings:
                            self.missing_mappings.append(f"{test_id} (no JIRA mapping)")
                        self.tests_skipped += 1
                        print(f"    ⚠️  Skipped {test_id} - no JIRA mapping found")
                else:
                    self.tests_skipped += 1
                    print(f"    ⚠️  Skipped test method - no @allure.tag found")
            
            new_lines.append(line)
            i += 1
        
        return '\n'.join(new_lines), modified
        
    def process_file(self, file_path):
        """Process a single test file."""
        print(f"\nProcessing: {file_path.name}")
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Add decorators
            new_content, modified = self.add_xray_decorator(content)
            
            if modified:
                # Backup original
                backup_path = file_path.with_suffix('.py.backup')
                with open(backup_path, 'w') as f:
                    f.write(content)
                
                # Write updated content
                with open(file_path, 'w') as f:
                    f.write(new_content)
                
                print(f"  ✓ Updated file with decorators (backup: {backup_path.name})")
                self.files_processed += 1
            else:
                print("  ℹ️  No updates needed (decorators already present or no mappings available)")
                
        except Exception as e:
            error_msg = f"Error processing {file_path}: {e}"
            print(f"  ✗ {error_msg}")
            self.errors.append(error_msg)
            
    def save_report(self):
        """Save processing report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "files_processed": self.files_processed,
            "tests_updated": self.tests_updated,
            "tests_skipped": self.tests_skipped,
            "missing_mappings": self.missing_mappings,
            "errors": self.errors,
            "mappings_used": len(self.test_mapping)
        }
        
        report_file = Path(__file__).parent.parent / "logs" / f"xray_decorator_fixed_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        return report_file
        
    def run(self):
        """Main execution."""
        print("Adding Xray Decorators to Pytest Tests (FIXED VERSION)")
        print("=" * 60)
        print("Strategy: Keep @allure.tag, add @pytest.mark.xray with JIRA issue keys")
        print("=" * 60)
        
        # Find test files
        test_files = self.find_test_files()
        print(f"Found {len(test_files)} test files")
        
        # Process each file
        for test_file in test_files:
            self.process_file(test_file)
        
        # Save report
        report_file = self.save_report()
        
        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Files processed: {self.files_processed}")
        print(f"Tests updated: {self.tests_updated}")
        print(f"Tests skipped: {self.tests_skipped}")
        print(f"Missing mappings: {len(self.missing_mappings)}")
        print(f"Errors: {len(self.errors)}")
        print(f"\nReport saved to: {report_file}")
        
        if self.missing_mappings:
            print(f"\n⚠️  Tests skipped due to missing JIRA mappings:")
            for missing in self.missing_mappings:
                print(f"   - {missing}")
            print("\nThese Test Case IDs need JIRA Xray tests created or verified.")
        
        # Note about pytest-xray plugin
        if self.tests_updated > 0:
            print(f"\n✅ SUCCESS: Added @pytest.mark.xray decorators to {self.tests_updated} tests")
            print("   Tests now have both @allure.tag (for Test Case ID) and @pytest.mark.xray (for JIRA key)")
            print("\n📋 NEXT STEPS:")
            print("   1. Install pytest-xray plugin: pip install pytest-xray")
            print("   2. Configure Xray integration in pytest.ini or conftest.py")
            print("   3. Run tests with: pytest --xray")

def main():
    """Main entry point."""
    adder = XrayDecoratorAdder()
    adder.run()

if __name__ == "__main__":
    main()