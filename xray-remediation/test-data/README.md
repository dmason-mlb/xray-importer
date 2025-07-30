# Test Data - Extracted Test Cases

This directory contains extracted test case data from Confluence documentation that will be used for Xray remediation. The extraction and analysis scripts have been reorganized into dedicated directories.

## 📊 Test Data Files

### `api_tests_xray.json`
Contains **55 API test cases** extracted from Confluence document 4904878140.

**Source**: "API Test Cases - Team Page" Confluence document  
**Format**: Xray JSON import format  
**Test Type**: Automated  
**Test IDs**: API-001 through API-REG-003  
**Status**: ✅ Perfect parity with Confluence documentation

### `functional_tests_xray.json`
Contains **38 functional test cases** extracted from Confluence document 4904976484.

**Source**: "Functional Test Cases - Team Page" Confluence document  
**Format**: Xray JSON import format  
**Test Type**: Manual  
**Test IDs**: TC-001 through TC-038  
**Status**: ✅ Complete extraction with table-based parsing

## 🔧 Related Scripts

### **Extraction Scripts** (`../confluence-tools/`)

#### `extract_confluence_api_tests_secure.py` ✨ **RECOMMENDED**
**Secure** API test extraction using BeautifulSoup for robust HTML parsing.

**Security Features**:
- BeautifulSoup parsing (no regex vulnerabilities)
- Input validation and sanitization
- Comprehensive error handling
- Secure logging without credential exposure
- Timeout protection

#### `extract_confluence_functional_tests_v2.py`
Functional test extraction using table-based parsing for structured data.

#### `extract_confluence_api_tests.py`
Original API extraction script using regex patterns (legacy).

#### `normalize_confluence_document.py`
Normalizes Confluence document formatting using the Confluence API.

#### `document_parameterized_instances.py`
Documents the 11 parameterized test instances found in the analysis.

#### `debug_confluence_page.py`
Generic page structure analysis tool.

### **Analysis Scripts** (`../analysis-utilities/`)

#### `analyze_confluence_structure.py`
Deep structural analysis of Confluence pages.

#### `comprehensive_test_analysis.py`
Comprehensive test case analysis and validation.

#### `deep_parameterized_analysis.py`
Specialized analysis for parameterized test instances.

#### `security_analysis.py`
Security assessment of extraction scripts and processes.

## 🚀 Usage

### **Environment Setup**
```bash
# Required environment variables
export CONFLUENCE_DOMAIN="your_domain"
export CONFLUENCE_EMAIL="your_email"
export CONFLUENCE_API_TOKEN="your_token"
```

### **Basic Operations**
```bash
# Secure API test extraction (recommended)
python ../confluence-tools/extract_confluence_api_tests_secure.py

# Functional test extraction
python ../confluence-tools/extract_confluence_functional_tests_v2.py

# Debug page structure
python ../confluence-tools/debug_confluence_page.py 4904878140

# Normalize document formatting
python ../confluence-tools/normalize_confluence_document.py

# Run comprehensive analysis
python ../analysis-utilities/comprehensive_test_analysis.py
```

### **Import Ready Files**
The JSON files are ready for import into Xray using the Xray JSON import format. Each file contains:
- Test metadata (summary, description, priority, labels)
- Test steps with actions and expected results
- Preconditions where applicable
- Project information and version tracking

### **Data Validation**
- ✅ **55 API test cases** - Perfect parity with Confluence doc 4904878140
- ✅ **38 functional test cases** - Complete extraction from doc 4904976484
- ✅ **11 parameterized instances** - Documented across 3 test cases
- ✅ **Security validated** - No credential exposure or injection vulnerabilities

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

## 📝 Implementation Notes

### **Data Integrity**
- All dates use current date (2025-07-17) as specified in environment
- Test cases maintain original ID structure from Confluence
- Perfect parity between Confluence documentation and extracted JSON
- Deduplication logic prevents duplicate test cases

### **Processing Features**
- Labels automatically generated based on test types and patterns
- HTML content cleaned and converted to plain text
- Step parsing handles arrow notation (→) for action-result separation
- Table-based extraction for structured data
- BeautifulSoup parsing for security and reliability

### **Security Considerations**
- Input validation and sanitization
- No credential exposure in logs or error messages
- Timeout protection against ReDoS attacks
- Comprehensive error handling

### **Parameterized Test Instances**
The analysis identified **11 parameterized instances** beyond the 55 base test cases:
- **API-003**: 5 instances (different user roles)
- **API-004**: 3 instances (different team types)
- **API-005**: 3 instances (different seasons)

**Total Test Coverage**: 55 base + 11 parameterized = **66 test instances**