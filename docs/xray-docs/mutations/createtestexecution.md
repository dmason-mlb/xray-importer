# createTestExecution

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/createtestexecution.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    createTestExecution(
        testIssueIds: ["54321"]
        testEnvironments: ["android"]
        jira: {
            fields: { summary: "Test Execution for CALC-123", project: {key: "CALC"} }
        }
    ) {
        testExecution {
            issueId
            jira(fields: ["key"])
        }
        warnings
        createdTestEnvironments
    }
}

```

## Example

The mutation below will create a new Test Execution.

```

mutation {
    createTestExecution(
        testIssueIds: ["54321"]
        testEnvironments: ["android"]
        jira: {
            fields: { summary: "Test Execution for CALC-123", project: {key: "CALC"} }
        }
    ) {
        testExecution {
            issueId
            jira(fields: ["key"])
        }
        warnings
        createdTestEnvironments
    }
}

```