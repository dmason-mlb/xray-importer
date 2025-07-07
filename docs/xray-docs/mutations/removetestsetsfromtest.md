# removeTestSetsFromTest

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/removetestsetsfromtest.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    removeTestSetsFromTest(issueId: "12345", testSetIssueIds: ["54321", "67890"])
}

```

## Example

The mutation below will remove the Test Sets with issue id "54321" and "67890" from the test "12345".

```

mutation {
    removeTestSetsFromTest(issueId: "12345", testSetIssueIds: ["54321", "67890"])
}

```