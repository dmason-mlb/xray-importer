# XRAY Test Import Strategy for MLBAPP Project

## Overview
This document outlines the strategy for importing three CSV test files into XRAY for the MLBAPP JIRA project:
- **home_surface.csv**: 8,699 test cases for Home Surface functionality
- **mlbapp.csv**: 6,276 test cases for general MLB app functionality  
- **news_surface.csv**: 725 test cases for News Surface functionality

Total: ~15,700 test cases requiring batch processing due to XRAY's 1000 test limit per import.

## Key Constraints & Requirements
Based on the XRAY documentation analysis:
- **Maximum 1000 tests per import operation** (both CSV and API)
- **ISO-8859-1 encoding required** for CSV files (not UTF-8)
- **Test types supported**: Manual, Generic, Cucumber (CSV v6.2+)
- **Each test can only belong to one folder** in Test Repository
- **Naming convention**: `[Component] - [Function] - [Expected Outcome]`

## CSV Structure Analysis

### Common Fields Across All Files:
- ID (external reference)
- Title
- Type (mostly "Manual")
- Priority (e.g., "2 - Medium Priority")
- Created By / Updated By
- Created On / Updated On
- Preconditions
- Expected Result
- Steps / Steps Separated
- Section (for organization)
- Suite / Suite ID
- References (JIRA tickets)

### File-Specific Characteristics:
1. **home_surface.csv**: Contains "Automation Type" field (e.g., "fasttrack-automatable")
2. **mlbapp.csv**: Has duplicate "Forecast" columns
3. **news_surface.csv**: Well-structured with clear section hierarchies

## Proposed Test Repository Structure

```
MLBAPP Test Repository/
├── Home Surface/
│   ├── Main Page/
│   ├── Scoreboard/
│   ├── Mixed Feed/
│   ├── Content Carousels/
│   ├── Headline Stack/
│   └── Surface Builder/
├── Core App/
│   ├── Deep Links/
│   ├── Navigation/
│   ├── Settings/
│   └── Authentication/
└── News Surface/
    ├── Editorial Modules/
    ├── Content Display/
    └── Analytics/
```

## Import Strategy

### Phase 1: Data Preparation
1. **Encoding Conversion**: Convert CSV files from UTF-8 to ISO-8859-1
2. **Field Mapping**: Map CSV columns to JIRA/XRAY fields
3. **Data Validation**: Ensure all referenced users exist in JIRA
4. **Batch Creation**: Split files into <1000 test chunks

### Phase 2: API-Based Import Approach
Using REST API for better control and automation:

**Advantages:**
- Better performance (200-500 tests/minute)
- Programmatic error handling
- Supports all test types
- CI/CD integration potential

**API Endpoint**: `POST /rest/raven/1.0/import/test/bulk`

### Phase 3: Import Sequence
1. **Create folder structure** in Test Repository first
2. **Import in batches**:
   - home_surface.csv: 9 batches
   - mlbapp.csv: 7 batches  
   - news_surface.csv: 1 batch
3. **Validate each batch** before proceeding
4. **Create Test Sets** for cross-cutting concerns (smoke, regression)

## Field Mapping

```json
{
  "testType": "Manual",
  "fields": {
    "summary": "Title",
    "description": "Expected Result",
    "priority": {"name": "Medium"},
    "labels": ["imported", "testrails-migration"],
    "customfield_23269": "Preconditions",  // PreCondition(TestRails)
    "components": [{"name": "iOS"}, {"name": "Android"}]
  },
  "testSteps": [
    {
      "action": "Steps",
      "expectedResult": "Expected Result"
    }
  ]
}
```

## Implementation Recommendations

1. **Start with smallest file** (news_surface.csv) for testing
2. **Use test environment first** if available
3. **Monitor API rate limits** during import
4. **Maintain import logs** for audit trail
5. **Schedule imports during off-peak hours**
6. **Create backup** of JIRA project before mass import

## Error Handling

Common issues to handle:
- Missing user references → Map to default test user
- Invalid priorities → Default to "Medium"
- Encoding issues → Pre-process with iconv
- Duplicate test names → Append unique identifier

## Post-Import Tasks

1. **Verify test counts** match source CSVs
2. **Update Test Sets** with appropriate tests
3. **Configure test execution plans**
4. **Train team** on new test organization
5. **Document** custom field mappings for future imports

## Success Metrics

- All 15,700 tests successfully imported
- Tests properly organized in folder hierarchy
- No data loss or corruption
- Import completed within maintenance window
- Team can locate and execute tests efficiently