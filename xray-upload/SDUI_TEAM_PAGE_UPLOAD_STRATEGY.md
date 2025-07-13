# SDUI Team Page Test Upload Strategy

## Overview
This document outlines the comprehensive strategy for uploading 38 SDUI Team Page functional test cases from `/Users/douglas.mason/Documents/GitHub/MLB-App/sdui-team-page-test-cases.json` to the FRAMED project in JIRA using XRAY.

## Test Case Analysis

### Source Data Summary
- **Total Test Cases**: 38
- **Test Suite**: SDUI Team Page - Functional Test Cases
- **Platforms**: iOS, Android, iPad
- **Priority Distribution**:
  - High: 20 tests
  - Medium: 17 tests  
  - Low: 1 test
- **Test Categories**:
  - Core Navigation: 8 tests
  - Content Display: 4 tests
  - Game States: 10 tests
  - Jewel Events: 8 tests
  - Product Links: 1 test
  - Date Bar: 2 tests
  - Matchup Display: 1 test

### Key Test Attributes
- Each test includes structured test steps with actions and expected results
- Tests have platform-specific requirements (iOS, Android, iPad)
- Tests are tagged with multiple labels for categorization
- Some tests have related FRAMED issues for traceability

## XRAY Upload Approach

### Method: GraphQL API
We will use the XRAY GraphQL API for uploading tests. This method provides the best control and reliability.

**Advantages:**
- Direct folder assignment during creation
- Proper label handling
- Better error tracking and recovery
- Maintains test step structure integrity
- Supports platform-specific metadata
- Avoids CSV encoding and formatting issues
- Enables automated test set creation
- Better suited for CI/CD integration

### Folder Structure in XRAY
```
/Team Page
  /Core Navigation
  /Content Display  
  /Game States
  /Jewel Events
  /Product Links
  /Date Bar
  /Matchup Display
```

## Field Mapping Strategy

### JSON to XRAY Field Mapping
```json
{
  "testCaseId": "External ID (for reference)",
  "title": "summary",
  "priority": "priority.name",
  "platforms": "labels + components",
  "folderStructure": "folder path",
  "tags": "labels",
  "preconditions": "preconditions field",
  "testSteps": "steps array",
  "testData": "description (if present)",
  "relatedIssues": "issue links"
}
```

### Label Taxonomy
Each test will receive labels based on:
1. **Tags from JSON**: Direct mapping (e.g., @team-page, @functional)
2. **Platform labels**: @ios, @android, @ipad (based on platforms array)
3. **Priority labels**: @critical, @high, @medium, @low
4. **Import metadata**: @sdui-import, @team-page-suite

### Test Step Structure
```json
{
  "action": "Step action text",
  "expectedResult": "Expected result (joined if array)"
}
```

## Implementation Phases

### Phase 1: Environment Setup (Completed)
- Created xray-upload directory
- Analyzed test structure
- Documented strategy

### Phase 2: Data Transformation
1. Load JSON test data
2. Transform to XRAY GraphQL format
3. Validate field mappings
4. Generate import batches

### Phase 3: Folder Creation
1. Authenticate with XRAY API
2. Create Team Page root folder
3. Create subfolder structure
4. Verify folder hierarchy

### Phase 4: Test Import
1. Import tests in batches of 10
2. Assign to appropriate folders
3. Apply labels and metadata
4. Link related issues

### Phase 5: Test Set Creation
Create the following test sets:
- **Team Page - Smoke Tests**: Critical tests only
- **Team Page - Full Regression**: All 38 tests
- **Team Page - iOS Only**: iOS-specific tests
- **Team Page - Android Only**: Android-specific tests
- **Team Page - Jewel Events**: Special event tests
- **Team Page - Game States**: All game state tests

### Phase 6: Validation
1. Verify all 38 tests imported
2. Check folder assignments
3. Validate labels applied
4. Confirm issue links
5. Test step integrity

## Technical Implementation

### Required Scripts
1. **transform_tests.py**: Convert JSON to XRAY format
2. **xray_api_uploader.py**: GraphQL API client for upload
3. **validate_tests.py**: Pre-upload validation

### Error Handling
- Retry failed imports with exponential backoff
- Log all operations for audit trail
- Track failed tests for manual review
- Validate each batch before proceeding

## Success Criteria
- [ ] All 38 tests successfully imported
- [ ] Correct folder organization
- [ ] All labels properly applied
- [ ] Test steps maintain integrity
- [ ] Related issues linked
- [ ] Test sets created automatically
- [ ] No data loss or corruption
- [ ] No credentials exposed in any files

## Timeline
- Phase 1-2: Complete today
- Phase 3-4: Import execution
- Phase 5-6: Organization and validation

## Risk Mitigation
1. **Test in staging first** (if available)
2. **Backup existing tests** before import
3. **Import in small batches** for easier rollback
4. **Document custom field IDs** for future reference
5. **Maintain import logs** for troubleshooting