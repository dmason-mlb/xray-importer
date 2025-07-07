# removeTestsFromFolder

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/removetestsfromfolder.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    removeTestsFromFolder(
        projectId: "10000",
        testIssueIds: ["10002","12324","12345"]
    )
}

```

## Example

The mutation below will remove tests from a Folder.

```

mutation {
    removeTestsFromFolder(
        projectId: "10000",
        testIssueIds: ["10002","12324","12345"]
    )
}

```