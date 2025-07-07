# removePreconditionsFromTest

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/removepreconditionsfromtest.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    removePreconditionsFromTest(issueId: "12345", preconditionIssueIds: ["54321", "67890"])
}

```

## Example

The mutation below will remove the preconditions with issue id "54321" and "67890" from the test "12345".

```

mutation {
    removePreconditionsFromTest(issueId: "12345", preconditionIssueIds: ["54321", "67890"])
}

```

The mutation below will remove the preconditions with issue id "54321" and "67890" from the version 3 of the Test "12345".

```

mutation {
    removePreconditionsFromTest(issueId: "12345", versionId: 3, preconditionIssueIds: ["54321", "67890"])
}

```