# addTestsToTestSet

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/addteststotestset.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    addTestsToTestSet(
        issueId: "12345",
        testIssueIds: ["54321"]
    ) {
        addedTests
        warning
    }
}

```

## Example

The mutation below will associate the test with issue id "54321" to the Test Set "12345".

```

mutation {
    addTestsToTestSet(
        issueId: "12345",
        testIssueIds: ["54321"]
    ) {
        addedTests
        warning
    }
}

```