# addTestExecutionsToTestPlan

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/addtestexecutionstotestplan.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    addTestExecutionsToTestPlan(
        issueId: "12345",
        testExecIssueIds: ["54321"]
    ) {
        addedTestExecutions
        warning
    }
}

```

## Example

The mutation below will associate the Test Execution with issue id "54321" to the test Plan "12345".

```

mutation {
    addTestExecutionsToTestPlan(
        issueId: "12345",
        testExecIssueIds: ["54321"]
    ) {
        addedTestExecutions
        warning
    }
}

```