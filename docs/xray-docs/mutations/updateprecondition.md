# updatePrecondition

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/updateprecondition.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    updatePrecondition(
        issueId: "49137",
        data: { preconditionType: {name: "Manual" }, definition: "Turn on calculator" }
    ) {
        issueId
        preconditionType {
            kind
            name
        }
        definition
    }
}

```

## Example

The mutation below will update the Precondition with id "49137"

```

mutation {
    updatePrecondition(
        issueId: "49137",
        data: { preconditionType: {name: "Manual" }, definition: "Turn on calculator" }
    ) {
        issueId
        preconditionType {
            kind
            name
        }
        definition
    }
}

```

The mutation below will update the Precondition with id "12345" and move it to the specified folder

```

mutation {
    updatePrecondition(
        issueId: "12345",
        data: { folderPath: "/generic" }
    ) {
        issueId
        preconditionType {
            kind
            name
        }
        definition
    }
}

```