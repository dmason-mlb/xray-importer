# createTestPlan

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/createtestplan.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    createTestPlan(
        testIssueIds: ["54321"]
        jira: {
            fields: { summary: "Test Plan for v1.0", project: {key: "CALC"} }
        }
    ) {
        testPlan {
            issueId
            jira(fields: ["key"])
        }
        warnings
    }
}

```

## Example

The mutation below will create a new Test Plan.

```

mutation {
    createTestPlan(
        testIssueIds: ["54321"]
        jira: {
            fields: { summary: "Test Plan for v1.0", project: {key: "CALC"} }
        }
    ) {
        testPlan {
            issueId
            jira(fields: ["key"])
        }
        warnings
    }
}

```