# SDUI Test Creation Documentation

This folder contains comprehensive documentation and implementation guides for creating and organizing SDUI (Server-Driven UI) tests in XRAY using the GraphQL API.

## Overview

The SDUI Test Creation suite provides everything needed to:
- Authenticate with XRAY's GraphQL API
- Create hierarchical folder structures for test organization
- Import test cases with proper labeling and categorization
- Create test sets for execution planning
- Handle batch operations with error recovery

## Documentation Structure

### 1. [Authentication Guide](01-authentication.md)
- XRAY API authentication process
- Token management
- Security best practices
- Code examples in Python and JavaScript

### 2. [GraphQL API Reference](02-graphql-api-reference.md)
- Complete API reference for all GraphQL operations
- Mutation and query documentation
- Field descriptions and requirements
- Request/response examples

### 3. [JIRA Field Requirements](03-jira-field-requirements.md)
- Detailed JIRA field specifications
- Validation rules and constraints
- Label taxonomy and conventions
- Common issues and solutions

### 4. [Implementation Guide](04-implementation-guide.md)
- Production-ready Python implementation
- Folder creation and management
- Test import with batch processing
- Test set creation and organization
- Error handling and retry logic

## Quick Start

### Prerequisites

1. **XRAY API Credentials**
   - Create an API Key in XRAY Global Settings
   - Note your Client ID and Client Secret

2. **Environment Setup**
   ```bash
   # Create .env file
   XRAY_CLIENT=your_client_id
   XRAY_SECRET=your_client_secret
   JIRA_PROJECT_KEY=MLB
   JIRA_PROJECT_ID=10000
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Basic Usage

1. **Authenticate**
   ```python
   from xray_client import XrayGraphQLClient
   
   client = XrayGraphQLClient()
   token = client.authenticate()
   ```

2. **Create Folder Structure**
   ```python
   from folder_manager import FolderManager
   
   folder_mgr = FolderManager(client, project_id)
   folder_mgr.setup_sdui_folders()
   ```

3. **Import Tests**
   ```python
   from test_manager import TestManager
   
   test_mgr = TestManager(client, project_key)
   test_mgr.import_test_from_dict(test_data)
   ```

## Test Organization Strategy

Based on the Confluence documentation, tests are organized into:

### Folder Structure
```
/Browse Menu
  /Core Navigation
  /Content Display
  /Personalization
  /Jewel Events
    /Opening Day
    /All-Star Week
    /Postseason
  /Game States
/Team Page
  /Date Bar
  /Matchup Display
  /Product Links
  /Jewel Events
/Gameday
  /WebView
  /JS Bridge
  /Game States
  /Jewel Events
/Scoreboard
  /GameCell
  /CalendarBar
  /Jewel Events
  /Game States
```

### Label Taxonomy
- **Feature**: `@browse-menu`, `@team-page`, `@gameday`, `@scoreboard`
- **Test Type**: `@functional`, `@api`, `@integration`, `@e2e`
- **Platform**: `@ios`, `@android`, `@ipad`, `@cross-platform`
- **Priority**: `@critical`, `@high`, `@medium`, `@low`
- **Execution**: `@smoke`, `@regression`, `@nightly`, `@release`
- **Special Events**: `@jewel-event`, `@opening-day`, `@all-star`, `@postseason`
- **Game States**: `@game-state`, `@preview-state`, `@live-state`, `@final-state`

### Test Sets
- **Smoke Tests**: Quick validation suites (10-15 tests each)
- **Feature Complete**: All tests for a feature (89-117 tests)
- **Platform Specific**: iOS-only, Android-only tests
- **Jewel Events**: Special event test suites
- **Game States**: State-specific test collections

## API Operations Summary

### Core Mutations
1. `createFolder` - Create test repository folders
2. `createTest` - Create new test cases
3. `createTestSet` - Create test sets
4. `addTestsToFolder` - Organize tests in folders
5. `addTestsToTestSet` - Add tests to sets

### Core Queries
1. `getFolder` - Retrieve folder information
2. `getTest` - Get test details
3. `getTestSet` - Get test set information

## Error Handling

The implementation includes comprehensive error handling:
- Retry logic with exponential backoff
- Error logging and tracking
- Failed operation recovery
- Batch operation management

## Performance Considerations

- Batch operations in groups of 10-50
- Parallel execution with thread pools
- Rate limiting (60 requests/minute)
- Token caching to minimize auth calls

## Support and Resources

- [XRAY Documentation](https://docs.getxray.app/)
- [JIRA REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [GraphQL Best Practices](https://graphql.org/learn/best-practices/)

## Version

Last Updated: 2025-07-08  
Documentation Version: 1.0

## Contributing

When adding new documentation:
1. Follow the existing numbering scheme
2. Include practical examples
3. Document error scenarios
4. Update this README