# updatePreconditionFolder

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/updatepreconditionfolder.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    updatePreconditionFolder(
        issueId: "12345",
        folderPath: "/Component/UI"
    )
}

```

## Example

The mutation below will add the precondition to "Component/UI" folder.

```

mutation {
    updatePreconditionFolder(
        issueId: "12345",
        folderPath: "/Component/UI"
    )
}

```

The mutation below will move the Precondition to the root.

```

mutation {
    updatePreconditionFolder(
        issueId: "12345",
        folderPath: "/"
    )
}

```