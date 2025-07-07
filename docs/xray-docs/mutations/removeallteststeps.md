# removeAllTestSteps

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/removeallteststeps.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    removeAllTestSteps(
        issueId: "12345",
    )
}

```

## Example

The mutation below removes all the Steps from test with id "12345".

```

mutation {
    removeAllTestSteps(
        issueId: "12345",
    )
}

```

The mutation below removes all the Steps from the version 3 of the Test with id "12345".

```

mutation {
    removeAllTestSteps(
        issueId: "12345",
        versionId: 3
    )
}

```