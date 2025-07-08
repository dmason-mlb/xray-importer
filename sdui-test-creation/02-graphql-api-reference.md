# XRAY GraphQL API Reference for SDUI Test Creation

## Table of Contents
1. [API Overview](#api-overview)
2. [Folder Operations](#folder-operations)
3. [Test Creation](#test-creation)
4. [Test Set Management](#test-set-management)
5. [Test Organization](#test-organization)
6. [Query Operations](#query-operations)
7. [Field Requirements](#field-requirements)
8. [Complete Examples](#complete-examples)

## API Overview

The XRAY GraphQL API endpoint is:
```
https://xray.cloud.getxray.app/api/v2/graphql
```

All requests must include:
- `Authorization: Bearer <token>` header
- `Content-Type: application/json` header

## Folder Operations

### createFolder Mutation

Creates folders in the test repository hierarchy for organizing tests.

#### Input Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `projectId` | String | Yes* | JIRA project ID (numeric) |
| `testPlanId` | String | No | Test Plan ID if creating within a plan |
| `path` | String | Yes | Folder path (e.g., "/Browse Menu/Core Navigation") |
| `testIssueIds` | [String] | No | Array of test IDs to add to folder |
| `issueIds` | [String] | No | Array of test/precondition IDs |

*Either `projectId` or `testPlanId` must be provided

#### Return Fields

```graphql
{
  folder: {
    name: String              # Folder name (last path segment)
    path: String              # Full folder path
    testsCount: Int          # Number of tests in folder
    preconditionsCount: Int  # Number of preconditions
    issuesCount: Int         # Total issues count
  }
  warnings: [String]         # Any warnings
}
```

#### Example
```graphql
mutation CreateBrowseMenuFolder {
  createFolder(
    projectId: "10000",
    path: "/Browse Menu/Core Navigation"
  ) {
    folder {
      name
      path
      testsCount
    }
    warnings
  }
}
```

### addTestsToFolder Mutation

Adds existing tests to a folder.

#### Input Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `projectId` | String | Yes* | JIRA project ID |
| `testPlanId` | String | No | Test Plan ID |
| `path` | String | Yes | Target folder path |
| `testIssueIds` | [String] | Yes | Test IDs to add |
| `index` | Int | No | Position index for ordering |

#### Example
```graphql
mutation AddTestsToNavigationFolder {
  addTestsToFolder(
    projectId: "10000",
    path: "/Browse Menu/Core Navigation",
    testIssueIds: ["MLB-1001", "MLB-1002", "MLB-1003"]
  ) {
    folder {
      testsCount
    }
    warnings
  }
}
```

## Test Creation

### createTest Mutation

Creates new test cases with full JIRA integration.

#### Input Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `jira` | JSON | Yes | JIRA issue fields |
| `testType` | UpdateTestTypeInput | No | Test type specification |
| `steps` | [CreateStepInput] | No | Manual test steps |
| `unstructured` | String | No | Generic test content |
| `gherkin` | String | No | BDD/Cucumber content |
| `preconditionIssueIds` | [String] | No | Linked preconditions |
| `folderPath` | String | No | Repository folder path |

#### JIRA Fields Structure

```json
{
  "fields": {
    "project": { "key": "MLB" },
    "summary": "Test title",
    "description": "Test description",
    "issuetype": { "name": "Test" },
    "labels": ["@team-page", "@functional", "@smoke"],
    "priority": { "name": "High" },
    "assignee": { "name": "username" },
    "components": [{ "name": "Team Page" }],
    "customfield_10001": "Custom value"
  }
}
```

#### CreateStepInput Structure

```graphql
{
  action: String          # Step action description
  data: String           # Test data/input
  result: String         # Expected result
  attachments: [{
    filename: String
    mimeType: String
    data: String         # Base64 encoded
  }]
  customFields: [{
    id: String
    value: JSON
  }]
  callTestIssueId: String # For test composition
}
```

#### Return Fields

```graphql
{
  test: {
    issueId: String          # JIRA issue ID
    projectId: String        # Project ID
    testType: {
      name: String           # "Manual", "Automated", etc.
      kind: String           # Test kind
    }
    steps: [{
      id: String
      action: String
      data: String
      result: String
      attachments: [Attachment]
      customStepFields: [CustomStepField]
    }]
    folder: {
      name: String
      path: String
    }
    jira: JSON              # All JIRA fields
    status: {
      name: String
      statusCategory: String
    }
    lastModified: String
  }
  warnings: [String]
}
```

#### Complete Example - Manual Test

```graphql
mutation CreateTeamPageTest {
  createTest(
    jira: {
      fields: {
        project: { key: "MLB" },
        summary: "TC-001: Team Selection via Drawer",
        description: "Verify team selection functionality works correctly",
        issuetype: { name: "Test" },
        labels: [
          "@team-page",
          "@functional",
          "@critical",
          "@smoke",
          "@navigation",
          "@ios",
          "@android"
        ],
        priority: { name: "High" },
        assignee: { name: "douglas.mason" },
        components: [{ name: "Team Page" }]
      }
    },
    testType: { name: "Manual" },
    steps: [
      {
        action: "Navigate to Team Page",
        data: "App is open",
        result: "Team Page is displayed"
      },
      {
        action: "Tap on the team selector dropdown",
        data: "Current team: Yankees",
        result: "Team drawer opens with all 30 MLB teams"
      },
      {
        action: "Select a different team from the list",
        data: "Select: Red Sox",
        result: "Team page updates with Red Sox content"
      }
    ],
    folderPath: "/Team Page/Core Navigation"
  ) {
    test {
      issueId
      testType { name }
      steps {
        action
        data
        result
      }
      folder { path }
      jira(fields: ["key", "labels"])
    }
    warnings
  }
}
```

## Test Set Management

### createTestSet Mutation

Creates test sets for cross-cutting test organization.

#### Input Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `jira` | JSON | Yes | JIRA issue fields |
| `testIssueIds` | [String] | No | Initial tests to include |

#### Example

```graphql
mutation CreateSmokeTestSet {
  createTestSet(
    jira: {
      fields: {
        project: { key: "MLB" },
        summary: "SDUI-Smoke-Tests/Team-Page-Smoke",
        description: "Smoke test suite for Team Page - 12 critical tests",
        issuetype: { name: "Test Set" }
      }
    },
    testIssueIds: [
      "MLB-1001", "MLB-1003", "MLB-1006", "MLB-1007",
      "MLB-1009", "MLB-1011", "MLB-1013", "MLB-1015",
      "MLB-1017", "MLB-1019", "MLB-1021", "MLB-1022"
    ]
  ) {
    testSet {
      issueId
      jira(fields: ["key"])
    }
    warnings
  }
}
```

### addTestsToTestSet Mutation

Adds tests to existing test sets.

#### Input Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `issueId` | String | Yes | Test Set issue ID |
| `testIssueIds` | [String] | Yes | Tests to add |

#### Example

```graphql
mutation AddToJewelEventSet {
  addTestsToTestSet(
    issueId: "MLB-5001",
    testIssueIds: ["MLB-1022", "MLB-1023", "MLB-1024"]
  ) {
    addedTests
    warning
  }
}
```

## Query Operations

### getFolder Query

Retrieves folder information and contents.

```graphql
query GetTeamPageFolder {
  getFolder(projectId: "10000", path: "/Team Page") {
    name
    path
    testsCount
    folders    # Sub-folders
    tests {
      total
      results {
        issueId
        jira(fields: ["key", "summary", "labels"])
      }
    }
  }
}
```

### getTest Query

Retrieves complete test information.

```graphql
query GetTestDetails {
  getTest(issueId: "MLB-1001") {
    issueId
    testType { name }
    steps {
      id
      action
      data
      result
    }
    folder { path }
    testSets {
      total
      results {
        issueId
        jira(fields: ["key", "summary"])
      }
    }
    jira(fields: ["key", "summary", "labels", "priority", "status"])
  }
}
```

### getTestSet Query

Retrieves test set information.

```graphql
query GetSmokeTestSet {
  getTestSet(issueId: "MLB-5001") {
    issueId
    tests(limit: 100) {
      total
      results {
        issueId
        jira(fields: ["key", "summary", "labels"])
      }
    }
    jira(fields: ["key", "summary", "description"])
  }
}
```

## Field Requirements

### Required JIRA Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `project` | Object | Project key or ID | `{ "key": "MLB" }` |
| `summary` | String | Issue title | `"TC-001: Test Name"` |
| `issuetype` | Object | Issue type | `{ "name": "Test" }` |

### Optional JIRA Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `description` | String | Detailed description | `"Test description"` |
| `labels` | [String] | Tag array | `["@smoke", "@ios"]` |
| `priority` | Object | Priority level | `{ "name": "High" }` |
| `assignee` | Object | User assignment | `{ "name": "username" }` |
| `components` | [Object] | Component links | `[{ "name": "Team Page" }]` |
| `fixVersions` | [Object] | Fix versions | `[{ "name": "2.0" }]` |
| `duedate` | String | Due date | `"2025-12-31"` |

### Test Type Values

- `Manual` - Manual test with steps
- `Automated` - Automated test
- `Generic` - Generic/exploratory test
- `Cucumber` - BDD/Gherkin test

### Priority Values

- `Critical`
- `High`
- `Medium`
- `Low`

### Label Convention

Based on the tagging strategy:
- Feature: `@browse-menu`, `@team-page`, `@gameday`, `@scoreboard`
- Test Type: `@functional`, `@api`, `@integration`, `@e2e`
- Platform: `@ios`, `@android`, `@ipad`, `@cross-platform`
- Priority: `@critical`, `@high`, `@medium`, `@low`
- Execution: `@smoke`, `@regression`, `@nightly`, `@release`
- Component: `@navigation`, `@content-display`, `@gamecell`
- Jewel Event: `@jewel-event`, `@opening-day`, `@all-star`, `@postseason`
- Game State: `@game-state`, `@preview-state`, `@live-state`, `@final-state`
- Data: `@requires-live-game`, `@requires-test-account`

## Complete Examples

### 1. Create Folder Structure

```graphql
mutation CreateFolderHierarchy {
  f1: createFolder(projectId: "10000", path: "/Team Page") {
    folder { path }
  }
  f2: createFolder(projectId: "10000", path: "/Team Page/Date Bar") {
    folder { path }
  }
  f3: createFolder(projectId: "10000", path: "/Team Page/Jewel Events") {
    folder { path }
  }
  f4: createFolder(projectId: "10000", path: "/Team Page/Jewel Events/Opening Day") {
    folder { path }
  }
}
```

### 2. Create Jewel Event Test

```graphql
mutation CreateOpeningDayTest {
  createTest(
    jira: {
      fields: {
        project: { key: "MLB" },
        summary: "TC-022: Opening Day Content Display",
        description: "Verify Opening Day branding and content displays correctly on Team Page",
        issuetype: { name: "Test" },
        labels: [
          "@team-page",
          "@functional",
          "@critical",
          "@jewel-event",
          "@opening-day",
          "@ios",
          "@android"
        ],
        priority: { name: "High" },
        components: [{ name: "Team Page" }]
      }
    },
    testType: { name: "Manual" },
    steps: [
      {
        action: "Navigate to Team Page on Opening Day",
        data: "Date: Opening Day",
        result: "Team Page loads successfully"
      },
      {
        action: "Check MIG section for special branding",
        data: "Look for Opening Day graphics",
        result: "Opening Day branding displays in MIG"
      },
      {
        action: "Verify content sections for Opening Day content",
        data: "Check carousels and articles",
        result: "Special Opening Day content is featured"
      },
      {
        action: "Check for special badges or indicators",
        data: "Look for OD badges",
        result: "Appropriate badges/styling applied"
      }
    ],
    preconditionIssueIds: ["MLB-PRE-001"],
    folderPath: "/Team Page/Jewel Events/Opening Day"
  ) {
    test {
      issueId
      jira(fields: ["key"])
    }
    warnings
  }
}
```

### 3. Create and Populate Test Set

```graphql
mutation CreateAndPopulateJewelEventSet {
  # First create the test set
  createSet: createTestSet(
    jira: {
      fields: {
        project: { key: "MLB" },
        summary: "Jewel-Event-Sets/Opening-Day-Suite",
        description: "Complete test suite for Opening Day functionality across all features",
        issuetype: { name: "Test Set" }
      }
    }
  ) {
    testSet {
      issueId
      jira(fields: ["key"])
    }
  }
}

# Then add tests (separate mutation)
mutation PopulateOpeningDaySet {
  addTestsToTestSet(
    issueId: "MLB-SET-001",
    testIssueIds: [
      "MLB-1022", "MLB-1023", "MLB-1024", "MLB-1025",
      "MLB-2022", "MLB-2023", "MLB-3022", "MLB-3023",
      "MLB-4022", "MLB-4023", "MLB-4024", "MLB-4025",
      "MLB-4026", "MLB-4027", "MLB-4028"
    ]
  ) {
    addedTests
    warning
  }
}
```

## Error Handling

Common error scenarios and responses:

| Error | Cause | Solution |
|-------|-------|----------|
| "Project not found" | Invalid project ID/key | Verify project exists and ID is correct |
| "Folder already exists" | Duplicate folder path | Use existing folder or different path |
| "Test not found" | Invalid test ID | Verify test IDs before adding to folders/sets |
| "Invalid issue type" | Wrong issue type name | Check JIRA configuration for valid types |
| "Field 'customfield_X' cannot be set" | Invalid custom field | Verify custom field ID and permissions |
| "Label value is invalid" | Label doesn't exist | Create label in JIRA first or check syntax |

## Performance Considerations

1. **Batch Operations**: Use GraphQL aliases to execute multiple mutations in one request
2. **Pagination**: Use `limit` and `offset` for large result sets
3. **Field Selection**: Only request fields you need to minimize response size
4. **Parallel Execution**: GraphQL allows multiple operations in one request

## Rate Limits

- Maximum 60 requests per minute per API key
- Maximum 1000 tests per folder operation
- Maximum 500 tests per test set
- Maximum request size: 10MB

## Next Steps

1. Set up authentication (see [01-authentication.md](01-authentication.md))
2. Create folder structure for all features
3. Import test cases with appropriate labels
4. Create test sets based on execution needs
5. Implement monitoring and reporting