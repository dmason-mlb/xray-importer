# moveFolder

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/movefolder.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    moveFolder(
        projectId: "10000",
        path: "/generic",
        destinationPath: "/testType"
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

The mutation below will move a Folder.

```

mutation {
    moveFolder(
        projectId: "10000",
        path: "/generic",
        destinationPath: "/testType"
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