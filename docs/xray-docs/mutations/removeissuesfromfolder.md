# removeIssuesFromFolder

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/removeissuesfromfolder.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    removeIssuesFromFolder(
        projectId: "10000",
        issueIds: ["10002","12324","12345"]
    )
}

```

## Example

The mutation below will remove issues from a Folder.

```

mutation {
    removeIssuesFromFolder(
        projectId: "10000",
        issueIds: ["10002","12324","12345"]
    )
}

```