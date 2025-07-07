# renameFolder

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/renamefolder.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    renameFolder(
        projectId: "10000",
        path: "/generic",
        newName: "Junit"
    ) {
        folder {
            name
            path
            testsCount
        }
        warnings
    }
}

```

## Example

The mutation below will rename a Folder.

```

mutation {
    renameFolder(
        projectId: "10000",
        path: "/generic",
        newName: "Junit"
    ) {
        folder {
            name
            path
            testsCount
        }
        warnings
    }
}

```