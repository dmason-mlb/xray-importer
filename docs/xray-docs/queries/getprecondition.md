# getPrecondition

**Category:** Queries
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/getprecondition.doc.html

## GraphQL Schema Definition

```graphql

{
    getPrecondition {
        issueId
        preconditionType {
            kind
            name
        }
    }
}

```

## Example

The Query below returns a Precondition.

```

{
    getPrecondition {
        issueId
        preconditionType {
            kind
            name
        }
    }
}

```

The Query below returns the Precondition with issue id12345

```

{
    getPrecondition(issueId: "12345") {
        issueId
        definition
        jira(fields: ["assignee", "reporter"])
    }
}

```