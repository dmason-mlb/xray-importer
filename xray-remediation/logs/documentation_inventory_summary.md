# Documentation Inventory Summary

Generated: 2025-07-31T17:16:16.173442

## File Summary
- Total Files: 60

### By Category:
- Historical: 1
- Status Reports: 6
- Technical Docs: 4
- Other: 1
- Test Data: 5
- Logs Reports: 9
- Scripts: 34

## Test Summary
- API Tests: 0
- Functional Tests: 38
- Total Tests: 85

## Duplicates Found: 3

### Multiple Status Reports
**Recommendation**: Merge into single PROJECT_STATUS.md
Files:
- documentation/REMEDIATION_STATUS.md
- documentation/REMEDIATION_PROGRESS_20250718.md
- documentation/REMEDIATION_STATUS_FINAL.md
- documentation/PHASE1_BASIC_ASSESSMENT_20250716_213912.md
- documentation/folder_organization_status.md
- scripts/analyze_folder_status.py

### Multiple versions of add_xray_decorators.py
**Recommendation**: Keep only the latest/working version
Files:
- scripts/add_xray_decorators.py
- scripts/add_xray_decorators_final.py
- scripts/add_xray_decorators_fixed.py

### Multiple versions of organize_test_folders.py
**Recommendation**: Keep only the latest/working version
Files:
- scripts/organize_test_folders_fixed.py
- scripts/organize_test_folders.py

## Consolidation Plan

### PROJECT_STATUS.md
Consolidated project status and progress
Merge from:
- documentation/REMEDIATION_STATUS.md
- documentation/REMEDIATION_PROGRESS_20250718.md
- documentation/REMEDIATION_STATUS_FINAL.md
- documentation/PHASE1_BASIC_ASSESSMENT_20250716_213912.md
- documentation/folder_organization_status.md
- scripts/analyze_folder_status.py

### TEAM_PAGE_TEST_CATALOG.md
Complete catalog of all team page tests

### IMPLEMENTATION_GUIDE.md
Technical implementation guide
Merge from:
- README.md
- documentation/pytest_xray_automation.md
- xray-api/auth_utils.py (docstrings)

### DOCUMENTATION_MAP.md
Navigation guide for all documentation