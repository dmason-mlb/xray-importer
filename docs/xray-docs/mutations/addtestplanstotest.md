# addTestPlansToTest

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/addtestplanstotest.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    addTestPlansToTest(
        issueId: "12345",
        testPlanIssueIds: ["54321"]
    ) {
        addedTestPlans
        warning
    }
}

```

## Example

The mutation below will associate the Test Plan with issue id "54321" to the test "12345".

```

mutation {
    addTestPlansToTest(
        issueId: "12345",
        testPlanIssueIds: ["54321"]
    ) {
        addedTestPlans
        warning
    }
}

```