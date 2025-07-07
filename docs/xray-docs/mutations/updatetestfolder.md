# updateTestFolder

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/updatetestfolder.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    updateTestFolder(
        issueId: "12345",
        folderPath: "/Component/UI"
    )
}

```

## Example

The mutation below will add the test to "Component/UI" folder.

```

mutation {
    updateTestFolder(
        issueId: "12345",
        folderPath: "/Component/UI"
    )
}

```

The mutation below will move the Test to the root.

```

mutation {
    updateTestFolder(
        issueId: "12345",
        folderPath: "/"
    )
}

```