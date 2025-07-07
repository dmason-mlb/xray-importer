# addTestsToFolder

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/addteststofolder.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    addTestsToFolder(
        projectId: "10000",
        path: "/generic",
        testIssueIds: ["10002","12324","12345"]
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

The mutation below will add tests to a Folder.

```

mutation {
    addTestsToFolder(
        projectId: "10000",
        path: "/generic",
        testIssueIds: ["10002","12324","12345"]
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