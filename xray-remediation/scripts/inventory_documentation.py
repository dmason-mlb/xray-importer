#!/usr/bin/env python3
"""
Create a comprehensive inventory of all documentation files in the xray-remediation project.
This script categorizes files and identifies consolidation opportunities.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class DocumentationInventory:
    """Inventory and categorize all documentation files"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.inventory = defaultdict(list)
        self.file_details = {}
        
    def categorize_file(self, file_path):
        """Categorize a file based on its path and name"""
        path = Path(file_path)
        name = path.name.lower()
        
        # Status/Progress Reports
        if 'status' in name or 'progress' in name or 'phase' in name:
            return 'status_reports'
        
        # Technical Documentation
        if name in ['readme.md', 'claude.md'] or 'guide' in name or 'automation' in name:
            return 'technical_docs'
        
        # Test Data
        if path.suffix == '.json' and ('test' in name or 'api' in name or 'functional' in name):
            return 'test_data'
        
        # Scripts
        if path.suffix == '.py':
            return 'scripts'
        
        # Logs and Reports
        if 'logs' in str(path) or 'report' in name:
            return 'logs_reports'
        
        # Historical/Archive
        if 'old' in name or 'backup' in name or 'archive' in name:
            return 'historical'
        
        return 'other'
    
    def get_file_info(self, file_path):
        """Get detailed information about a file"""
        path = Path(file_path)
        
        info = {
            'path': str(path.relative_to(self.base_path)),
            'name': path.name,
            'size': path.stat().st_size,
            'modified': datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
            'category': self.categorize_file(path)
        }
        
        # Get first few lines for context
        if path.suffix in ['.md', '.py']:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:10]
                    info['header'] = ''.join(lines[:5]).strip()
                    
                    # Check for specific markers
                    content = ''.join(lines).lower()
                    if 'deprecated' in content or 'obsolete' in content:
                        info['status'] = 'deprecated'
                    elif 'final' in content or 'complete' in content:
                        info['status'] = 'final'
                    else:
                        info['status'] = 'active'
            except:
                info['header'] = 'Unable to read file'
                info['status'] = 'unknown'
        
        return info
    
    def scan_directory(self, directory):
        """Scan a directory for documentation files"""
        dir_path = self.base_path / directory
        if not dir_path.exists():
            return
        
        for item in dir_path.rglob('*'):
            if item.is_file() and item.suffix in ['.md', '.json', '.py']:
                info = self.get_file_info(item)
                self.inventory[info['category']].append(info)
                self.file_details[str(item.relative_to(self.base_path))] = info
    
    def analyze_test_data(self):
        """Analyze test data JSON files"""
        test_files = self.inventory.get('test_data', [])
        
        test_summary = {
            'api_tests': 0,
            'functional_tests': 0,
            'total_tests': 0,
            'files': []
        }
        
        for file_info in test_files:
            file_path = self.base_path / file_info['path']
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                if isinstance(data, list):
                    count = len(data)
                elif isinstance(data, dict) and 'tests' in data:
                    count = len(data['tests'])
                else:
                    count = 0
                
                file_summary = {
                    'file': file_info['name'],
                    'test_count': count
                }
                
                if 'api' in file_info['name'].lower():
                    test_summary['api_tests'] += count
                elif 'functional' in file_info['name'].lower():
                    test_summary['functional_tests'] += count
                
                test_summary['total_tests'] += count
                test_summary['files'].append(file_summary)
                
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        return test_summary
    
    def identify_duplicates(self):
        """Identify potential duplicate or redundant documentation"""
        duplicates = []
        
        # Check for multiple status reports
        status_files = [f for f in self.inventory.get('status_reports', [])]
        if len(status_files) > 1:
            duplicates.append({
                'type': 'Multiple Status Reports',
                'files': [f['path'] for f in status_files],
                'recommendation': 'Merge into single PROJECT_STATUS.md'
            })
        
        # Check for similar script names
        scripts = self.inventory.get('scripts', [])
        script_groups = defaultdict(list)
        
        for script in scripts:
            base_name = script['name'].replace('_final', '').replace('_fixed', '').replace('_v2', '')
            script_groups[base_name].append(script)
        
        for base_name, versions in script_groups.items():
            if len(versions) > 1:
                duplicates.append({
                    'type': f'Multiple versions of {base_name}',
                    'files': [v['path'] for v in versions],
                    'recommendation': 'Keep only the latest/working version'
                })
        
        return duplicates
    
    def generate_report(self):
        """Generate comprehensive inventory report"""
        # Scan all directories
        directories = ['documentation', 'logs', 'scripts', 'test-data', 'xray-api']
        for directory in directories:
            self.scan_directory(directory)
        
        # Also scan root level files
        for item in self.base_path.glob('*.md'):
            if item.is_file():
                info = self.get_file_info(item)
                self.inventory[info['category']].append(info)
                self.file_details[str(item.relative_to(self.base_path))] = info
        
        # Analyze test data
        test_summary = self.analyze_test_data()
        
        # Identify duplicates
        duplicates = self.identify_duplicates()
        
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_files': sum(len(files) for files in self.inventory.values()),
                'categories': {cat: len(files) for cat, files in self.inventory.items()},
                'test_summary': test_summary,
                'duplicate_count': len(duplicates)
            },
            'inventory': dict(self.inventory),
            'duplicates': duplicates,
            'consolidation_plan': self.create_consolidation_plan()
        }
        
        return report
    
    def create_consolidation_plan(self):
        """Create a plan for consolidating documentation"""
        plan = {
            'new_structure': {
                'PROJECT_STATUS.md': {
                    'merge_from': [
                        f['path'] for f in self.inventory.get('status_reports', [])
                    ],
                    'description': 'Consolidated project status and progress'
                },
                'TEAM_PAGE_TEST_CATALOG.md': {
                    'generate_from': [
                        f['path'] for f in self.inventory.get('test_data', [])
                    ],
                    'description': 'Complete catalog of all team page tests'
                },
                'IMPLEMENTATION_GUIDE.md': {
                    'merge_from': [
                        'README.md',
                        'documentation/pytest_xray_automation.md',
                        'xray-api/auth_utils.py (docstrings)'
                    ],
                    'description': 'Technical implementation guide'
                },
                'DOCUMENTATION_MAP.md': {
                    'generate': True,
                    'description': 'Navigation guide for all documentation'
                }
            },
            'archive': {
                'files_to_archive': [],
                'criteria': 'Historical status reports, old script versions'
            },
            'cleanup': {
                'duplicate_scripts': [],
                'obsolete_logs': []
            }
        }
        
        return plan
    
    def save_report(self, output_file='documentation_inventory.json'):
        """Save the inventory report"""
        report = self.generate_report()
        
        output_path = self.base_path / 'logs' / output_file
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Also create a markdown summary
        self.create_markdown_summary(report)
        
        print(f"✓ Inventory saved to: {output_path}")
        return report
    
    def create_markdown_summary(self, report):
        """Create a markdown summary of the inventory"""
        summary = [
            "# Documentation Inventory Summary",
            f"\nGenerated: {report['timestamp']}",
            "\n## File Summary",
            f"- Total Files: {report['summary']['total_files']}"
        ]
        
        summary.append("\n### By Category:")
        for cat, count in report['summary']['categories'].items():
            summary.append(f"- {cat.replace('_', ' ').title()}: {count}")
        
        summary.append("\n## Test Summary")
        test_sum = report['summary']['test_summary']
        summary.append(f"- API Tests: {test_sum['api_tests']}")
        summary.append(f"- Functional Tests: {test_sum['functional_tests']}")
        summary.append(f"- Total Tests: {test_sum['total_tests']}")
        
        if report['duplicates']:
            summary.append(f"\n## Duplicates Found: {len(report['duplicates'])}")
            for dup in report['duplicates']:
                summary.append(f"\n### {dup['type']}")
                summary.append(f"**Recommendation**: {dup['recommendation']}")
                summary.append("Files:")
                for file in dup['files']:
                    summary.append(f"- {file}")
        
        summary.append("\n## Consolidation Plan")
        for new_file, details in report['consolidation_plan']['new_structure'].items():
            summary.append(f"\n### {new_file}")
            summary.append(f"{details['description']}")
            if 'merge_from' in details:
                summary.append("Merge from:")
                for file in details['merge_from']:
                    summary.append(f"- {file}")
        
        output_path = self.base_path / 'logs' / 'documentation_inventory_summary.md'
        with open(output_path, 'w') as f:
            f.write('\n'.join(summary))
        
        print(f"✓ Summary saved to: {output_path}")

def main():
    """Main entry point"""
    inventory = DocumentationInventory()
    report = inventory.save_report()
    
    print("\n" + "="*60)
    print("DOCUMENTATION INVENTORY COMPLETE")
    print("="*60)
    print(f"Total Files: {report['summary']['total_files']}")
    print(f"Duplicates Found: {report['summary']['duplicate_count']}")
    print(f"Test Data Files: {report['summary']['categories'].get('test_data', 0)}")
    print("\nReview logs/documentation_inventory_summary.md for details")

if __name__ == "__main__":
    main()