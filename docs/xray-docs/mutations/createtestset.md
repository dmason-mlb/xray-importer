# createTestSet

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/createtestset.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    createTestSet(
        testIssueIds: ["54321"]
        jira: {
            fields: { summary: "Test Set for Generic Tests", project: {key: "CALC"} }
        }
    ) {
        testSet {
            issueId
            jira(fields: ["key"])
        }
        warnings
    }
}

```

## Example

The mutation below will create a new Test Set.

```

mutation {
    createTestSet(
        testIssueIds: ["54321"]
        jira: {
            fields: { summary: "Test Set for Generic Tests", project: {key: "CALC"} }
        }
    ) {
        testSet {
            issueId
            jira(fields: ["key"])
        }
        warnings
    }
}

```