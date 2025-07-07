# addTestsToTestPlan

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/addteststotestplan.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    addTestsToTestPlan(
        issueId: "12345",
        testIssueIds: ["54321"]
    ) {
        addedTests
        warning
    }
}

```

## Example

The mutation below will associate the test with issue id "54321" to the Test Plan "12345".

```

mutation {
    addTestsToTestPlan(
        issueId: "12345",
        testIssueIds: ["54321"]
    ) {
        addedTests
        warning
    }
}

```