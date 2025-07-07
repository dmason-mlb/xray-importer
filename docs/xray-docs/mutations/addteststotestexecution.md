# addTestsToTestExecution

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/addteststotestexecution.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    addTestsToTestExecution(
        issueId: "12345",
        testIssueIds: ["54321"]
    ) {
        addedTests
        warning
    }
}

```

## Example

The mutation below will associate the test with issue id "54321" to the Test execution "12345".

```

mutation {
    addTestsToTestExecution(
        issueId: "12345",
        testIssueIds: ["54321"]
    ) {
        addedTests
        warning
    }
}

```