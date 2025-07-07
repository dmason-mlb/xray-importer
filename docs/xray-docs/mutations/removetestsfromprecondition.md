# removeTestsFromPrecondition

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/removetestsfromprecondition.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    removeTestsFromPrecondition(issueId: "12345", testIssueIds: ["54321", "67890"])
}

```

## Example

The mutation below will remove the Tests with issue id "54321" and "67890" from the Precondition "12345".

```

mutation {
    removeTestsFromPrecondition(issueId: "12345", testIssueIds: ["54321", "67890"])
}

```

The mutation below will remove the version 2 of Test "54321" and the version 3 of Test "67890" from the Precondition "12345".

```

mutation {
    removeTestsFromPrecondition(
        issueId: "12345",
        tests: [{ issueId: "54321", versionId: 2 }, { issueId: "67890", versionId: 3 }]
    )
}

```