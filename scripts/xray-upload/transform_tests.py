#!/usr/bin/env python3
"""
Transform SDUI Team Page test cases from JSON format to XRAY GraphQL format.
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import re


class TestTransformer:
    """Transform test cases from SDUI JSON format to XRAY format."""
    
    def __init__(self, project_key: str = "FRAMED"):
        self.project_key = project_key
        self.transformed_tests = []
        self.folder_structure = set()
        
    def load_test_file(self, file_path: str) -> Dict[str, Any]:
        """Load test cases from JSON file."""
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def transform_priority(self, priority: str) -> str:
        """Convert priority from test format to JIRA format."""
        priority_map = {
            "High": "High",
            "Medium": "Medium",
            "Low": "Low"
        }
        return priority_map.get(priority, "Medium")
    
    def transform_tags(self, tags: List[str], platforms: List[str], priority: str) -> List[str]:
        """Transform tags to XRAY labels."""
        labels = []
        
        # Add original tags (remove @ prefix)
        for tag in tags:
            clean_tag = tag.lstrip('@')
            labels.append(clean_tag)
        
        # Add platform labels
        for platform in platforms:
            platform_label = platform.lower().replace(' ', '-')
            labels.append(platform_label)
        
        # Add priority label based on tags
        if "@critical" in tags:
            labels.append("critical")
        elif priority == "High" and "@critical" not in tags:
            labels.append("high-priority")
        
        # Add import metadata
        labels.extend(["sdui-import", "team-page-suite"])
        
        return list(set(labels))  # Remove duplicates
    
    def transform_test_steps(self, test_steps: List[Dict]) -> List[Dict]:
        """Transform test steps to XRAY format."""
        xray_steps = []
        
        for step in test_steps:
            # Handle expected result - join if array
            expected_result = step.get('expectedResult', '')
            if isinstance(expected_result, list):
                expected_result = '\n'.join(expected_result)
            elif expected_result is None:
                expected_result = ''
            
            xray_step = {
                "action": step.get('action', ''),
                "expectedResult": expected_result
            }
            xray_steps.append(xray_step)
        
        return xray_steps
    
    def create_test_description(self, test_case: Dict) -> str:
        """Create test description from available data."""
        description_parts = []
        
        if test_case.get('preconditions'):
            description_parts.append(f"**Preconditions:**\n{test_case['preconditions']}")
        
        if test_case.get('testData'):
            description_parts.append(f"**Test Data:**\n{test_case['testData']}")
        
        if test_case.get('relatedIssues'):
            issues = ', '.join(test_case['relatedIssues'])
            description_parts.append(f"**Related Issues:** {issues}")
        
        # Add platform info
        platforms = ', '.join(test_case.get('platforms', []))
        description_parts.append(f"**Platforms:** {platforms}")
        
        # Add original test ID
        description_parts.append(f"**Original Test ID:** {test_case.get('testCaseId', 'N/A')}")
        
        return '\n\n'.join(description_parts)
    
    def transform_test_case(self, test_case: Dict) -> Dict:
        """Transform a single test case to XRAY format."""
        # Extract folder path
        folder_path = test_case.get('folderStructure', 'Team Page')
        self.folder_structure.add(folder_path)
        
        # Build the transformed test
        xray_test = {
            "testType": "Manual",
            "summary": test_case.get('title', ''),
            "priority": self.transform_priority(test_case.get('priority', 'Medium')),
            "labels": self.transform_tags(
                test_case.get('tags', []),
                test_case.get('platforms', []),
                test_case.get('priority', 'Medium')
            ),
            "description": self.create_test_description(test_case),
            "folder": f"/{folder_path}",
            "steps": self.transform_test_steps(test_case.get('testSteps', [])),
            "originalId": test_case.get('testCaseId', ''),
            "relatedIssues": test_case.get('relatedIssues', [])
        }
        
        # Add preconditions if available
        if test_case.get('preconditions'):
            xray_test['preconditions'] = test_case['preconditions']
        
        return xray_test
    
    def transform_all_tests(self, test_data: Dict) -> List[Dict]:
        """Transform all test cases from the JSON file."""
        test_suite = test_data.get('testSuite', {})
        test_cases = test_suite.get('testCases', [])
        
        print(f"Found {len(test_cases)} test cases to transform")
        
        for test_case in test_cases:
            transformed = self.transform_test_case(test_case)
            self.transformed_tests.append(transformed)
        
        return self.transformed_tests
    
    def get_folder_hierarchy(self) -> Dict[str, List[str]]:
        """Extract folder hierarchy from transformed tests."""
        folders = {}
        
        for folder_path in self.folder_structure:
            parts = folder_path.split('/')
            parent = "Team Page"
            
            if parent not in folders:
                folders[parent] = []
            
            if len(parts) > 1 and parts[1] not in folders[parent]:
                folders[parent].append(parts[1])
        
        return folders
    
    def save_transformed_tests(self, output_file: str):
        """Save transformed tests to JSON file."""
        output_data = {
            "projectKey": self.project_key,
            "totalTests": len(self.transformed_tests),
            "folders": self.get_folder_hierarchy(),
            "tests": self.transformed_tests,
            "transformedAt": datetime.now().isoformat()
        }
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"Saved {len(self.transformed_tests)} transformed tests to {output_file}")
    
    def generate_summary_report(self) -> str:
        """Generate a summary report of the transformation."""
        report = []
        report.append("# Test Transformation Summary\n")
        report.append(f"Total tests transformed: {len(self.transformed_tests)}\n")
        
        # Count by priority
        priority_counts = {}
        for test in self.transformed_tests:
            priority = test['priority']
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        report.append("## Priority Distribution")
        for priority, count in sorted(priority_counts.items()):
            report.append(f"- {priority}: {count} tests")
        
        # Count by folder
        folder_counts = {}
        for test in self.transformed_tests:
            folder = test['folder']
            folder_counts[folder] = folder_counts.get(folder, 0) + 1
        
        report.append("\n## Folder Distribution")
        for folder, count in sorted(folder_counts.items()):
            report.append(f"- {folder}: {count} tests")
        
        # Tests with related issues
        tests_with_issues = [t for t in self.transformed_tests if t.get('relatedIssues')]
        report.append(f"\n## Tests with Related Issues: {len(tests_with_issues)}")
        
        return '\n'.join(report)


def main():
    """Main execution function."""
    # File paths
    input_file = "/Users/douglas.mason/Documents/GitHub/MLB-App/sdui-team-page-test-cases.json"
    output_file = "/Users/douglas.mason/Documents/GitHub/xray-importer/xray-upload/transformed_tests.json"
    
    # Create transformer
    transformer = TestTransformer(project_key="FRAMED")
    
    # Load and transform tests
    print("Loading test cases...")
    test_data = transformer.load_test_file(input_file)
    
    print("Transforming tests...")
    transformer.transform_all_tests(test_data)
    
    # Save results
    transformer.save_transformed_tests(output_file)
    
    # Generate and save summary
    summary = transformer.generate_summary_report()
    summary_file = "/Users/douglas.mason/Documents/GitHub/xray-importer/xray-upload/transformation_summary.md"
    with open(summary_file, 'w') as f:
        f.write(summary)
    
    print(f"\nTransformation complete!")
    print(f"- Transformed tests: {output_file}")
    print(f"- Summary report: {summary_file}")


if __name__ == "__main__":
    main()