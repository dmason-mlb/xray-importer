# createFolder

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/createfolder.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    createFolder(
        projectId: "10000",
        path: "/generic"
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

The mutation below will create a new Folder.

```

mutation {
    createFolder(
        projectId: "10000",
        path: "/generic"
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

The mutation below will create a new Folder and add tests to it.

```

mutation {
    createFolder(
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

The mutation below will create a new Folder and add tests and/or preconditions to it.

```

mutation {
    createFolder(
        projectId: "10000",
        path: "/generic",
        issueIds: ["10002","12324","12345"]
    ) {
        folder {
            name
            path
            testsCount
            issuesCount
            preconditionsCount
        }
        warnings
    }
}

```

Note: Use createFolder withtestIssueIds(in which all ids must be from Tests)
OR withissueIds(which can be eiter Test ids and/or Precondition ids), but not with both.