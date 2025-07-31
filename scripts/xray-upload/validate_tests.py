#!/usr/bin/env python3
"""
Validate transformed test cases before upload to XRAY.
Checks for required fields, data integrity, and potential issues.
"""
import json
import os
from typing import Dict, List, Any, Tuple
import re
from datetime import datetime


class TestValidator:
    """Validate test cases for XRAY upload."""
    
    def __init__(self):
        self.validation_errors = []
        self.validation_warnings = []
        self.stats = {
            "total_tests": 0,
            "valid_tests": 0,
            "tests_with_warnings": 0,
            "tests_with_errors": 0
        }
    
    def validate_required_fields(self, test: Dict, index: int) -> bool:
        """Check if all required fields are present and valid."""
        required_fields = ["summary", "testType", "priority"]
        missing_fields = []
        
        for field in required_fields:
            if not test.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            self.validation_errors.append(
                f"Test {index + 1} ({test.get('originalId', 'Unknown')}): "
                f"Missing required fields: {', '.join(missing_fields)}"
            )
            return False
        
        return True
    
    def validate_priority(self, test: Dict, index: int) -> bool:
        """Validate priority values."""
        valid_priorities = ["High", "Medium", "Low", "Critical", "Blocker"]
        priority = test.get("priority", "")
        
        if priority not in valid_priorities:
            self.validation_errors.append(
                f"Test {index + 1} ({test.get('summary', '')}): "
                f"Invalid priority '{priority}'. Must be one of: {', '.join(valid_priorities)}"
            )
            return False
        
        return True
    
    def validate_test_steps(self, test: Dict, index: int) -> bool:
        """Validate test steps structure."""
        steps = test.get("steps", [])
        
        if not steps:
            self.validation_warnings.append(
                f"Test {index + 1} ({test.get('summary', '')}): "
                f"No test steps defined"
            )
            return True  # Warning only, not an error
        
        for i, step in enumerate(steps):
            if not step.get("action"):
                self.validation_errors.append(
                    f"Test {index + 1} ({test.get('summary', '')}): "
                    f"Step {i + 1} missing action"
                )
                return False
        
        return True
    
    def validate_labels(self, test: Dict, index: int) -> bool:
        """Validate labels format and content."""
        labels = test.get("labels", [])
        
        # Check for invalid characters in labels
        invalid_labels = []
        for label in labels:
            if not re.match(r'^[a-zA-Z0-9\-_]+$', label):
                invalid_labels.append(label)
        
        if invalid_labels:
            self.validation_warnings.append(
                f"Test {index + 1} ({test.get('summary', '')}): "
                f"Labels with special characters: {', '.join(invalid_labels)}"
            )
        
        # Check for recommended labels
        has_platform = any(label in ["ios", "android", "ipad"] for label in labels)
        if not has_platform:
            self.validation_warnings.append(
                f"Test {index + 1} ({test.get('summary', '')}): "
                f"No platform label found (ios, android, ipad)"
            )
        
        return True
    
    def validate_folder_path(self, test: Dict, index: int) -> bool:
        """Validate folder path format."""
        folder = test.get("folder", "")
        
        if not folder:
            self.validation_warnings.append(
                f"Test {index + 1} ({test.get('summary', '')}): "
                f"No folder path specified"
            )
            return True
        
        if not folder.startswith("/"):
            self.validation_errors.append(
                f"Test {index + 1} ({test.get('summary', '')}): "
                f"Folder path must start with '/': {folder}"
            )
            return False
        
        return True
    
    def validate_summary_length(self, test: Dict, index: int) -> bool:
        """Check summary length constraints."""
        summary = test.get("summary", "")
        
        if len(summary) > 255:
            self.validation_errors.append(
                f"Test {index + 1}: Summary too long ({len(summary)} chars). "
                f"Max 255 characters allowed"
            )
            return False
        
        if len(summary) < 10:
            self.validation_warnings.append(
                f"Test {index + 1}: Very short summary ({len(summary)} chars)"
            )
        
        return True
    
    def check_duplicates(self, tests: List[Dict]) -> List[str]:
        """Check for duplicate test summaries."""
        summaries = {}
        duplicates = []
        
        for i, test in enumerate(tests):
            summary = test.get("summary", "")
            if summary in summaries:
                duplicates.append(
                    f"Duplicate summary found: '{summary}' "
                    f"(tests {summaries[summary] + 1} and {i + 1})"
                )
            else:
                summaries[summary] = i
        
        return duplicates
    
    def validate_all_tests(self, transformed_data: Dict) -> Tuple[bool, Dict]:
        """Validate all tests and return validation results."""
        tests = transformed_data.get("tests", [])
        self.stats["total_tests"] = len(tests)
        
        print(f"Validating {len(tests)} tests...")
        
        # Validate each test
        for i, test in enumerate(tests):
            has_error = False
            has_warning = False
            
            # Run all validations
            if not self.validate_required_fields(test, i):
                has_error = True
            
            if not self.validate_priority(test, i):
                has_error = True
            
            if not self.validate_test_steps(test, i):
                has_error = True
            
            if not self.validate_folder_path(test, i):
                has_error = True
            
            if not self.validate_summary_length(test, i):
                has_error = True
            
            # Warnings don't fail validation
            self.validate_labels(test, i)
            
            # Update stats
            if has_error:
                self.stats["tests_with_errors"] += 1
            elif len(self.validation_warnings) > has_warning:
                self.stats["tests_with_warnings"] += 1
                has_warning = True
            else:
                self.stats["valid_tests"] += 1
        
        # Check for duplicates
        duplicates = self.check_duplicates(tests)
        if duplicates:
            self.validation_warnings.extend(duplicates)
        
        # All tests are valid if no errors
        is_valid = len(self.validation_errors) == 0
        
        return is_valid, self.generate_report()
    
    def generate_report(self) -> Dict:
        """Generate validation report."""
        return {
            "summary": {
                "total_tests": self.stats["total_tests"],
                "valid_tests": self.stats["valid_tests"],
                "tests_with_warnings": self.stats["tests_with_warnings"],
                "tests_with_errors": self.stats["tests_with_errors"],
                "total_errors": len(self.validation_errors),
                "total_warnings": len(self.validation_warnings)
            },
            "errors": self.validation_errors,
            "warnings": self.validation_warnings,
            "is_valid": len(self.validation_errors) == 0
        }
    
    def save_validation_report(self, report: Dict, output_file: str):
        """Save validation report to file."""
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Also create a markdown report
        md_file = output_file.replace('.json', '.md')
        self.save_markdown_report(report, md_file)
    
    def save_markdown_report(self, report: Dict, output_file: str):
        """Save validation report as markdown."""
        md_content = []
        md_content.append("# Test Validation Report\n")
        md_content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Summary
        md_content.append("## Summary")
        summary = report["summary"]
        md_content.append(f"- **Total Tests**: {summary['total_tests']}")
        md_content.append(f"- **Valid Tests**: {summary['valid_tests']}")
        md_content.append(f"- **Tests with Warnings**: {summary['tests_with_warnings']}")
        md_content.append(f"- **Tests with Errors**: {summary['tests_with_errors']}")
        md_content.append(f"- **Total Errors**: {summary['total_errors']}")
        md_content.append(f"- **Total Warnings**: {summary['total_warnings']}")
        
        # Overall status
        md_content.append(f"\n**Validation Status**: {'✅ PASSED' if report['is_valid'] else '❌ FAILED'}\n")
        
        # Errors
        if report["errors"]:
            md_content.append("## Errors (Must Fix)")
            for error in report["errors"]:
                md_content.append(f"- ❌ {error}")
        
        # Warnings
        if report["warnings"]:
            md_content.append("\n## Warnings (Recommended to Fix)")
            for warning in report["warnings"]:
                md_content.append(f"- ⚠️  {warning}")
        
        # Recommendations
        if not report["is_valid"]:
            md_content.append("\n## Next Steps")
            md_content.append("1. Fix all errors listed above")
            md_content.append("2. Re-run the transformation script")
            md_content.append("3. Re-validate before attempting upload")
        else:
            md_content.append("\n## Next Steps")
            md_content.append("✅ All tests are valid and ready for upload!")
            md_content.append("You can proceed with either:")
            md_content.append("1. CSV import using `sdui_team_page_tests.csv`")
            md_content.append("2. API upload using `xray_api_uploader.py`")
        
        with open(output_file, 'w') as f:
            f.write('\n'.join(md_content))


def main():
    """Main execution function."""
    # File paths
    input_file = "/Users/douglas.mason/Documents/GitHub/xray-importer/xray-upload/transformed_tests.json"
    output_dir = "/Users/douglas.mason/Documents/GitHub/xray-importer/xray-upload"
    
    # Load transformed tests
    print("Loading transformed tests...")
    with open(input_file, 'r') as f:
        transformed_data = json.load(f)
    
    # Create validator
    validator = TestValidator()
    
    # Validate all tests
    is_valid, report = validator.validate_all_tests(transformed_data)
    
    # Save report
    report_file = os.path.join(output_dir, "validation_report.json")
    validator.save_validation_report(report, report_file)
    
    # Print summary
    print(f"\nValidation {'PASSED' if is_valid else 'FAILED'}")
    print(f"- Total tests: {report['summary']['total_tests']}")
    print(f"- Errors: {report['summary']['total_errors']}")
    print(f"- Warnings: {report['summary']['total_warnings']}")
    print(f"\nDetailed report saved to:")
    print(f"- {report_file}")
    print(f"- {report_file.replace('.json', '.md')}")


if __name__ == "__main__":
    main()