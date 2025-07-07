# getPreconditions

**Category:** Queries
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/getpreconditions.doc.html

## GraphQL Schema Definition

```graphql

{
    getPreconditions(limit: 100) {
        total
        start
        limit
        results {
            issueId
            preconditionType {
                name
                kind
            }
            definition
            jira(fields: ["assignee", "reporter"])
        }
    }
}

```

## Example

The Query below returns the first 100 Preconditions.

```

{
    getPreconditions(limit: 100) {
        total
        start
        limit
        results {
            issueId
            preconditionType {
                name
                kind
            }
            definition
            jira(fields: ["assignee", "reporter"])
        }
    }
}

```

The Query below returns 10 Preconditions that match the provided jql

```

{
    getPreconditions(jql: "project = 'PC'", limit: 10) {
        results {
            issueId
            preconditionType {
                name
                kind
            }
            jira(fields: ["assignee", "reporter"])
        }
    }
}

```

Note: If the jql returns more than 100 issues an error will be returned asking the user to refine the jql search.