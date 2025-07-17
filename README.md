# XRAY Importer - SDUI Implementation Tools

*Last Updated: July 17, 2025*

## Overview

This repository contains implementation tools, scripts, and data files for SDUI-specific Xray automation and data processing. It serves as the practical implementation companion to the comprehensive Xray documentation maintained in the [sdui-test-docs repository](https://github.com/your-org/MLB-App/tree/main/Test/sdui-test-docs).

## Repository Purpose

**Primary Focus**: Implementation tools and automation for SDUI Xray integration
- Python scripts for data processing and automation
- SDUI-specific GraphQL implementation examples
- CSV data files and processing utilities
- Postman collections and authentication scripts
- Schema reference documentation

**Target Audience**: Developers implementing Xray automation, data processors, automation engineers

## Key Contents

### SDUI-Specific Documentation
- `xray_graphql_api_calls.md` - SDUI-specific GraphQL implementations and examples
- `xray_graphql_documentation.md` - Complete GraphQL schema reference (12K+ lines)
- `xray_graphql_mutations_documentation.md` - Detailed mutation documentation

### Implementation Scripts
- `fetch_all_tests.py` - Retrieve all tests from Xray
- `update_xray_tests.py` - Bulk update test operations
- `get_test_set_tests.py` - Test set management utilities
- `transform_tests.py` - Data transformation tools
- `validate_tests.py` - Test validation utilities

### Data Processing
- `import_data/` - CSV files and test data
- `mlbmob/` - MLBMOB-specific test processing
- `xray-filtering-and-modding/` - Test filtering and modification tools
- `xray-upload/` - Upload procedures and validation

### Authentication & Integration
- `postman-auth-script.js` - Postman authentication scripts
- `xray-postman-collection-vault.json` - Postman collection for API testing
- Authentication examples and token management utilities

## Related Documentation

For comprehensive Xray GraphQL documentation, implementation guides, and strategy documents, see:

**[SDUI Test Documentation Repository](https://github.com/your-org/MLB-App/tree/main/Test/sdui-test-docs)**

Key documentation files:
- `01-Xray-GraphQL-Complete-Reference.md` - Complete API reference and implementation guide
- `02-Xray-Test-Automation-Strategy.md` - Automation strategy and workflows
- `03-Xray-Test-Organization-Strategy.md` - Organization, tagging, and execution strategy

## Quick Start

### Prerequisites
```bash
# Install dependencies
pip install requests python-dotenv pandas tenacity

# Set environment variables
export XRAY_CLIENT="your_client_id"
export XRAY_SECRET="your_client_secret"
export JIRA_PROJECT_KEY="YOUR_PROJECT"
export JIRA_PROJECT_ID="10000"
```

### Authentication Example
```python
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from auth_utils import get_auth_token, execute_graphql_query

# Get token and execute query
token = get_auth_token()
result = execute_graphql_query("""
{
  getTest(issueId: "MLB-1001") {
    issueId
    summary
    testType
  }
}
""")
```

### SDUI-Specific Examples

See `xray_graphql_api_calls.md` for complete SDUI-specific GraphQL implementations including:
- Folder creation for SDUI hierarchy
- Test creation with proper SDUI labeling
- Test set management for smoke and regression suites
- SDUI-specific validation and organization patterns

## Project Structure

```
xray-importer/
├── README.md                               # This file
├── xray_graphql_api_calls.md              # SDUI GraphQL examples
├── xray_graphql_documentation.md          # Complete schema reference
├── xray_graphql_mutations_documentation.md # Mutation reference
├── import_data/                           # CSV data files
├── mlbmob/                               # MLBMOB processing
├── xray-filtering-and-modding/           # Test filtering tools
├── xray-upload/                          # Upload utilities
└── [various Python scripts]             # Implementation tools
```

## Contributing

1. **Implementation Focus**: This repository is for practical implementation tools
2. **Documentation**: General API documentation belongs in sdui-test-docs
3. **SDUI-Specific**: Content should be specific to SDUI implementation needs
4. **Cross-References**: Link to comprehensive docs in sdui-test-docs when appropriate

## Security Notes

- Never commit API credentials to this repository
- Use environment variables for all sensitive configuration
- Follow security best practices outlined in the authentication documentation
- Regularly rotate API keys and credentials

---

**For comprehensive Xray GraphQL documentation and implementation guides, visit:**
[SDUI Test Documentation](https://github.com/your-org/MLB-App/tree/main/Test/sdui-test-docs)