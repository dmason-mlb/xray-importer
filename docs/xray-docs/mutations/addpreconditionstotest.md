# addPreconditionsToTest

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/addpreconditionstotest.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    addPreconditionsToTest(
        issueId: "12345",
        preconditionIssueIds: ["54321"]
    ) {
        addedPreconditions
        warning
    }
}

```

## Example

The mutation below will associate the precondition with issue id "54321" to the test "12345".

```

mutation {
    addPreconditionsToTest(
        issueId: "12345",
        preconditionIssueIds: ["54321"]
    ) {
        addedPreconditions
        warning
    }
}

```

The mutation below will associate the precondition with issue id "54321" to the version 3 of the Test "12345".

```

mutation {
    addPreconditionsToTest(
        issueId: "12345",
        versionId: 3,
        preconditionIssueIds: ["54321"]
    ) {
        addedPreconditions
        warning
    }
}

```