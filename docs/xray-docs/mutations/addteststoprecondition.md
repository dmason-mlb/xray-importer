# addTestsToPrecondition

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/addteststoprecondition.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    addTestsToPrecondition(
        issueId: "12345",
        testIssueIds: ["54321"]
    ) {
        addedTests
        warning
    }
}

```

## Example

The mutation below will associate the Test with issue id "54321" to the Precondition "12345"

```

mutation {
    addTestsToPrecondition(
        issueId: "12345",
        testIssueIds: ["54321"]
    ) {
        addedTests
        warning
    }
}

```

The mutation below will associate the version 2 of Test "54321" and the version 3 of Test "67890" to the Precondition "12345"

```

mutation {
    addTestsToPrecondition(
        issueId: "12345",
        tests: [{ issueId: "54321", versionId: 2 }, { issueId: "67890", versionId: 3 }]
    ) {
        addedTests
        warning
    }
}

```