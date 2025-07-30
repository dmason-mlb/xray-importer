#!/usr/bin/env python3
"""
Add Xray decorators to pytest test files.
This script adds @pytest.mark.xray decorators to existing pytest tests.
"""

import re
import os
from pathlib import Path
from datetime import datetime
import json

class XrayDecoratorAdder:
    """Add Xray decorators to pytest tests."""
    
    def __init__(self):
        self.files_processed = 0
        self.tests_updated = 0
        self.errors = []
        
    def find_test_files(self):
        """Find all pytest test files."""
        test_dir = Path("/Users/douglas.mason/Documents/GitHub/MLB-App/Service/Bullpen/test/pytest-allure/tests/team_page")
        return list(test_dir.glob("test_*.py"))
        
    def extract_test_id_from_docstring(self, docstring):
        """Extract test case ID from docstring."""
        match = re.search(r'Test Case ID:\s*(API-[A-Z]+-\d+)', docstring)
        if match:
            return match.group(1)
        return None
        
    def extract_test_id_from_allure_tag(self, content, test_start_pos):
        """Extract test ID from @allure.tag decorator."""
        # Look backwards from test definition for allure.tag
        before_test = content[:test_start_pos]
        lines = before_test.split('\n')
        
        # Check last 10 lines before test definition
        for line in reversed(lines[-10:]):
            match = re.search(r'@allure\.tag\("(API-[A-Z]+-\d+)"\)', line)
            if match:
                return match.group(1)
        return None
        
    def add_xray_decorator(self, content):
        """Add Xray decorators to test methods."""
        lines = content.split('\n')
        new_lines = []
        i = 0
        modified = False
        
        while i < len(lines):
            line = lines[i]
            
            # Check if this is a test method definition
            if re.match(r'^\s*def test_\w+\(', line):
                # Find the test ID from docstring or allure tag
                test_id = None
                indent = len(line) - len(line.lstrip())
                
                # Look for docstring after the def line
                if i + 1 < len(lines) and '"""' in lines[i + 1]:
                    # Find the complete docstring
                    docstring_start = i + 1
                    docstring_end = docstring_start
                    for j in range(docstring_start + 1, len(lines)):
                        if '"""' in lines[j]:
                            docstring_end = j
                            break
                    
                    # Extract docstring content
                    docstring_lines = lines[docstring_start:docstring_end + 1]
                    docstring = '\n'.join(docstring_lines)
                    test_id = self.extract_test_id_from_docstring(docstring)
                
                # If not found in docstring, check allure tag
                if not test_id:
                    test_pos = len('\n'.join(lines[:i]))
                    test_id = self.extract_test_id_from_allure_tag(content, test_pos)
                
                if test_id:
                    # Check if xray decorator already exists
                    xray_exists = False
                    for j in range(max(0, i - 10), i):
                        if '@pytest.mark.xray' in lines[j]:
                            xray_exists = True
                            break
                    
                    if not xray_exists:
                        # Find where to insert the decorator (after other decorators)
                        insert_pos = i
                        for j in range(i - 1, max(0, i - 15), -1):
                            if lines[j].strip().startswith('@'):
                                insert_pos = j + 1
                            elif lines[j].strip() and not lines[j].strip().startswith('@'):
                                break
                        
                        # Add the xray decorator
                        new_lines.extend(lines[len(new_lines):insert_pos])
                        new_lines.append(f'{" " * indent}@pytest.mark.xray("{test_id}")')
                        new_lines.extend(lines[insert_pos:i + 1])
                        i = insert_pos
                        modified = True
                        self.tests_updated += 1
                        continue
            
            new_lines.append(line)
            i += 1
        
        return '\n'.join(new_lines), modified
        
    def process_file(self, file_path):
        """Process a single test file."""
        print(f"\nProcessing: {file_path.name}")
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check if pytest.mark.xray is imported
            if '@pytest.mark.xray' in content and 'pytest.mark.xray' not in content.split('"""')[0]:
                print("  ⚠️  File uses @pytest.mark.xray but may need import")
            
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
                
                print(f"  ✓ Updated with Xray decorators")
                self.files_processed += 1
            else:
                print("  ℹ️  No updates needed (decorators already present or no test IDs found)")
                
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
            "errors": self.errors
        }
        
        report_file = Path(__file__).parent.parent / "logs" / f"xray_decorator_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        return report_file
        
    def run(self):
        """Main execution."""
        print("Adding Xray Decorators to Pytest Tests")
        print("=" * 50)
        
        # Find test files
        test_files = self.find_test_files()
        print(f"Found {len(test_files)} test files")
        
        # Process each file
        for test_file in test_files:
            self.process_file(test_file)
        
        # Save report
        report_file = self.save_report()
        
        # Summary
        print("\n" + "=" * 50)
        print("SUMMARY")
        print("=" * 50)
        print(f"Files processed: {self.files_processed}")
        print(f"Tests updated: {self.tests_updated}")
        print(f"Errors: {len(self.errors)}")
        print(f"\nReport saved to: {report_file}")
        
        # Note about pytest-xray plugin
        if self.tests_updated > 0:
            print("\n⚠️  IMPORTANT: To use these Xray markers, you'll need:")
            print("   1. Install pytest-xray plugin: pip install pytest-xray")
            print("   2. Configure Xray integration in pytest.ini or conftest.py")
            print("   3. Run tests with: pytest --xray")

def main():
    """Main entry point."""
    adder = XrayDecoratorAdder()
    adder.run()

if __name__ == "__main__":
    main()