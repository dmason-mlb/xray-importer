# deleteFolder

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/deletefolder.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    deleteFolder(
        projectId: "10000",
        path: "/generic"
    )
}

```

## Example

The mutation below will delete a Folder.

```

mutation {
    deleteFolder(
        projectId: "10000",
        path: "/generic"
    )
}

```