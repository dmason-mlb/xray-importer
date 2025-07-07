# addTestSetsToTest

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/addtestsetstotest.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    addTestSetsToTest(
        issueId: "12345",
        testSetIssueIds: ["54321"]
    ) {
        addedTestSets
        warning
    }
}

```

## Example

The mutation below will associate the test set with issue id "54321" to the test "12345".

```

mutation {
    addTestSetsToTest(
        issueId: "12345",
        testSetIssueIds: ["54321"]
    ) {
        addedTestSets
        warning
    }
}

```