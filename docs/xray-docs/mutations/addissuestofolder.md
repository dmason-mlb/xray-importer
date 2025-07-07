# addIssuesToFolder

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/addissuestofolder.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    addIssuesToFolder(
        projectId: "10000",
        path: "/generic",
        issueIds: ["10002","12324","12345"]
    ) {
        folder {
            name
            path
            issuesCount
        }
        warnings
    }
}

```

## Example

The mutation below will add issues to a Folder.

```

mutation {
    addIssuesToFolder(
        projectId: "10000",
        path: "/generic",
        issueIds: ["10002","12324","12345"]
    ) {
        folder {
            name
            path
            issuesCount
        }
        warnings
    }
}

```