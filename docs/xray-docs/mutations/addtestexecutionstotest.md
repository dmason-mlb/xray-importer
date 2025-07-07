# addTestExecutionsToTest

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/addtestexecutionstotest.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    addTestExecutionsToTest(
        issueId: "12345",
        testExecIssueIds: ["54321"]
    ) {
        addedTestExecutions
        warning
    }
}

```

## Example

The mutation below will associate the Test Execution with issue id "54321" to the Test "12345".

```

mutation {
    addTestExecutionsToTest(
        issueId: "12345",
        testExecIssueIds: ["54321"]
    ) {
        addedTestExecutions
        warning
    }
}

```

The mutation below will associate the Test Execution with issue id "54321" to version 3 of the Test "12345".

```

mutation {
    addTestExecutionsToTest(
        issueId: "12345",
        versionId: 3,
        testExecIssueIds: ["54321"]
    ) {
        addedTestExecutions
        warning
    }
}

```