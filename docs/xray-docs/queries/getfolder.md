# getFolder

**Category:** Queries
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/getfolder.doc.html

## GraphQL Schema Definition

```graphql

{
    getFolder(projectId: "10000", path: "/") {
        name
        path
        testsCount
        folders
    }
}

```

## Example

The query below returns the root folder and all its child folders.

```

{
    getFolder(projectId: "10000", path: "/") {
        name
        path
        testsCount
        folders
    }
}

```

The query below returns the folder with path "/generic" and all its child folders.

```

{
    getFolder(projectId: "10000", path: "/generic") {
        name
        path
        testsCount
        folders
    }
}

```