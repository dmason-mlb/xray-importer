# Test Modification Guide

This guide covers how to modify existing tests in XRAY using the GraphQL API, including labels, test steps, descriptions, preconditions, and more.

## Table of Contents

1. [Overview](#overview)
2. [Modifying Labels](#modifying-labels)
3. [Updating Test Steps](#updating-test-steps)
4. [Modifying Test Content](#modifying-test-content)
5. [Managing Preconditions](#managing-preconditions)
6. [Folder Organization](#folder-organization)
7. [Bulk Operations](#bulk-operations)
8. [Best Practices](#best-practices)

## Overview

XRAY provides comprehensive GraphQL mutations for modifying existing tests. All modifications require:
- Valid authentication token
- Test issue ID (not the key)
- Appropriate permissions in JIRA

### Finding Test IDs

Before modifying tests, you need their issue IDs:

```graphql
query GetTestByKey($jql: String!) {
  getTests(jql: $jql, limit: 1) {
    results {
      issueId
      jira(fields: ["key", "summary"])
    }
  }
}

# Variables:
{
  "jql": "key = MLB-1234"
}
```

## Modifying Labels

### Replace All Labels

To completely replace all existing labels:

```graphql
mutation UpdateTestLabels($issueId: String!, $labels: [String!]!) {
  updateTest(
    issueId: $issueId,
    jira: {
      update: {
        labels: [
          { set: $labels }
        ]
      }
    }
  ) {
    test {
      issueId
      jira(fields: ["key", "labels"])
    }
    warnings
  }
}

# Variables:
{
  "issueId": "12345",
  "labels": ["@smoke", "@critical", "@ios"]
}
```

### Add Labels (Keep Existing)

To add new labels without removing existing ones:

```graphql
mutation AddLabelsToTest($issueId: String!, $label1: String!, $label2: String!) {
  updateTest(
    issueId: $issueId,
    jira: {
      update: {
        labels: [
          { add: $label1 },
          { add: $label2 }
        ]
      }
    }
  ) {
    test {
      jira(fields: ["key", "labels"])
    }
  }
}
```

### Remove Specific Labels

```graphql
mutation RemoveLabels($issueId: String!, $labelsToRemove: [String!]!) {
  updateTest(
    issueId: $issueId,
    jira: {
      update: {
        labels: [
          { remove: $labelsToRemove[0] },
          { remove: $labelsToRemove[1] }
        ]
      }
    }
  ) {
    test {
      jira(fields: ["key", "labels"])
    }
  }
}
```

## Updating Test Steps

### Get Current Steps

First, retrieve the current steps to get their IDs:

```graphql
query GetTestSteps($issueId: String!) {
  getTest(issueId: $issueId) {
    steps {
      id
      action
      data
      result
    }
  }
}
```

### Update Existing Step

```graphql
mutation UpdateTestStep(
  $issueId: String!,
  $stepId: String!,
  $action: String!,
  $data: String,
  $result: String!
) {
  updateTestStep(
    issueId: $issueId,
    stepId: $stepId,
    action: $action,
    data: $data,
    result: $result
  ) {
    id
    action
    data
    result
    warnings
  }
}
```

### Add New Step

```graphql
mutation AddTestStep(
  $issueId: String!,
  $action: String!,
  $data: String,
  $result: String!
) {
  addTestStep(
    issueId: $issueId,
    action: $action,
    data: $data,
    result: $result
  ) {
    id
    warnings
  }
}
```

### Remove Step

```graphql
mutation RemoveTestStep($issueId: String!, $stepId: String!) {
  removeTestStep(issueId: $issueId, stepId: $stepId) {
    message
    warnings
  }
}
```

### Remove All Steps

```graphql
mutation RemoveAllSteps($issueId: String!) {
  removeAllTestSteps(issueId: $issueId) {
    message
    warnings
  }
}
```

## Modifying Test Content

### Update Summary and Description

```graphql
mutation UpdateTestContent(
  $issueId: String!,
  $summary: String!,
  $description: String!
) {
  updateTest(
    issueId: $issueId,
    jira: {
      fields: {
        summary: $summary,
        description: $description
      }
    }
  ) {
    test {
      jira(fields: ["key", "summary", "description"])
    }
  }
}
```

### Update Priority

```graphql
mutation UpdatePriority($issueId: String!, $priority: String!) {
  updateTest(
    issueId: $issueId,
    jira: {
      fields: {
        priority: { name: $priority }
      }
    }
  ) {
    test {
      jira(fields: ["key", "priority"])
    }
  }
}
```

### Update Components

```graphql
mutation UpdateComponents($issueId: String!, $components: [ComponentInput!]!) {
  updateTest(
    issueId: $issueId,
    jira: {
      fields: {
        components: $components
      }
    }
  ) {
    test {
      jira(fields: ["key", "components"])
    }
  }
}

# Variables:
{
  "issueId": "12345",
  "components": [
    { "name": "Team Page" },
    { "name": "Navigation" }
  ]
}
```

## Managing Preconditions

### Add Preconditions

```graphql
mutation AddPreconditions(
  $issueId: String!,
  $preconditionIds: [String!]!
) {
  addPreconditionsToTest(
    issueId: $issueId,
    preconditionIds: $preconditionIds
  ) {
    addedPreconditions
    warning
  }
}
```

### Remove Preconditions

```graphql
mutation RemovePreconditions(
  $issueId: String!,
  $preconditionIds: [String!]!
) {
  removePreconditionsFromTest(
    issueId: $issueId,
    preconditionIds: $preconditionIds
  ) {
    removedPreconditions
    warning
  }
}
```

## Folder Organization

### Move Test to Different Folder

```graphql
mutation MoveTestToFolder(
  $issueId: String!,
  $projectId: String!,
  $folderPath: String!
) {
  updateTestFolder(
    issueId: $issueId,
    projectId: $projectId,
    folderPath: $folderPath
  ) {
    folder {
      name
      path
    }
    warnings
  }
}

# Variables:
{
  "issueId": "12345",
  "projectId": "10000",
  "folderPath": "/Team Page/Core Navigation"
}
```

### Remove from All Folders

Set folderPath to "/" to remove from all folders:

```graphql
{
  "folderPath": "/"
}
```

## Bulk Operations

### Update Multiple Tests

Use GraphQL aliases to update multiple tests in one request:

```graphql
mutation BulkUpdateLabels {
  test1: updateTest(
    issueId: "12345",
    jira: {
      update: {
        labels: [{ set: ["@smoke", "@critical"] }]
      }
    }
  ) {
    test {
      jira(fields: ["key"])
    }
  }
  
  test2: updateTest(
    issueId: "12346",
    jira: {
      update: {
        labels: [{ set: ["@regression", "@nightly"] }]
      }
    }
  ) {
    test {
      jira(fields: ["key"])
    }
  }
}
```

### Batch Processing Pattern

For large-scale updates:

```javascript
// Pseudocode for batch processing
const testIds = [...]; // Array of test IDs
const batchSize = 10;

for (let i = 0; i < testIds.length; i += batchSize) {
  const batch = testIds.slice(i, i + batchSize);
  const query = generateBatchQuery(batch);
  await executeGraphQL(query);
}
```

## Best Practices

### 1. Label Management

- **Naming Convention**: Use consistent prefixes
  - `@feature-*` for features
  - `@priority-*` for priority levels
  - `@platform-*` for platforms
  - `@execution-*` for execution types

- **Label Hierarchies**:
  ```
  @smoke → @regression → @full
  @critical → @high → @medium → @low
  ```

### 2. Step Modifications

- **Preserve Context**: When updating steps, maintain enough detail for clarity
- **Version History**: JIRA tracks all changes automatically
- **Bulk Updates**: Update all related steps together for consistency

### 3. Error Handling

Always check for warnings in responses:

```graphql
{
  test {
    jira(fields: ["key"])
  }
  warnings  # Array of warning messages
}
```

### 4. Performance Tips

- **Batch Operations**: Combine multiple updates in single requests
- **Selective Fields**: Only request fields you need in responses
- **Pagination**: Use limit/offset for large result sets

### 5. Common Patterns

#### Pattern: Add Label If Not Present

```javascript
// Get current labels
const currentLabels = test.jira.labels;

// Check if label exists
if (!currentLabels.includes('@smoke')) {
  // Add label
  addLabel(testId, '@smoke');
}
```

#### Pattern: Progressive Label Updates

```javascript
// Remove old priority, add new one
updateLabels(testId, {
  remove: ['@priority-low'],
  add: ['@priority-high']
});
```

## Troubleshooting

### Common Issues

1. **"Test not found"**: Verify issue ID (not key)
2. **"Permission denied"**: Check JIRA permissions
3. **"Invalid field"**: Ensure field names match JIRA configuration
4. **"Step not found"**: Refresh step IDs before updating

### Validation

Always validate changes:

```graphql
query ValidateChanges($issueId: String!) {
  getTest(issueId: $issueId) {
    jira(fields: ["key", "labels", "summary", "priority"])
    steps {
      id
      action
    }
    folder {
      path
    }
  }
}
```

## Next Steps

- Review [04-implementation-guide.md](04-implementation-guide.md) for complete workflow examples
- Use the Postman collection for interactive testing
- Implement error handling and retry logic for production use