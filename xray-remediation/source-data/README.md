# Source Data - Extracted Test Cases

This directory contains extracted test case data from Confluence documentation that will be used for Xray remediation.

## Files

### `api_tests_xray.json`
Contains 55 API test cases extracted from Confluence document 4904878140.

**Source**: "API Test Cases - Team Page" Confluence document  
**Format**: Xray JSON import format  
**Test Type**: Automated  
**Test IDs**: API-001 through API-REG-003

### `functional_tests_xray.json`
Contains 38 functional test cases extracted from Confluence document 4904976484.

**Source**: "Functional Test Cases - Team Page" Confluence document  
**Format**: Xray JSON import format  
**Test Type**: Manual  
**Test IDs**: TC-001 through TC-038

## Extraction Scripts

### `extract_confluence_api_tests.py`
Extracts API test cases from Confluence doc 4904878140 using regex patterns to parse test sections.

**Key Features**:
- Parses test sections starting with `API-` prefixes
- Extracts test metadata including steps, expected results, and preconditions
- Generates appropriate labels based on test ID patterns (REG, PERF, SEC, etc.)
- Creates Xray JSON structure with `testInfo` elements

### `extract_confluence_functional_tests_v2.py`
Extracts functional test cases from Confluence doc 4904976484 using table-based parsing.

**Key Features**:
- Parses table-formatted test data with TC- prefixes
- Extracts structured test information from field-value pairs
- Handles HTML cleaning and step parsing with arrow notation
- Creates manual test definitions with detailed step-by-step instructions

### `extract_confluence_functional_tests.py`
Initial version of functional test extraction (replaced by v2).

### `debug_functional_page.py`
Debug script used to analyze Confluence page structure and discover the correct parsing approach.

## Usage

These JSON files are ready for import into Xray using the Xray JSON import format. Each file contains:
- Test metadata (summary, description, priority, labels)
- Test steps with actions and expected results
- Preconditions where applicable
- Project information and version tracking

## Schema

The Xray JSON format follows this structure:

```json
{
  "info": {
    "project": "FRAMED",
    "summary": "Test Case Collection",
    "description": "Test cases extracted from Confluence",
    "user": "email@example.com",
    "revision": "page_version",
    "startDate": "2025-07-17T00:00:00Z",
    "finishDate": "2025-07-17T23:59:59Z",
    "testPlanKey": ""
  },
  "tests": [
    {
      "testInfo": {
        "summary": "Test name",
        "description": "Test description",
        "labels": ["functional", "api", "etc"],
        "priority": "Medium",
        "testType": "Manual|Automated",
        "steps": [
          {
            "index": 1,
            "action": "Step action",
            "data": "Test data",
            "result": "Expected result"
          }
        ],
        "expectedResults": "Overall expected result",
        "preconditions": ["Precondition 1", "Precondition 2"]
      },
      "testId": "TEST-001"
    }
  ]
}
```

## Notes

- All dates use current date (2025-07-17) as specified in environment
- Test cases maintain original ID structure from Confluence
- Labels are automatically generated based on test types and patterns
- HTML content is cleaned and converted to plain text
- Step parsing handles arrow notation (→) for action-result separation