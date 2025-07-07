# getTestSet

**Category:** Queries
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/gettestset.doc.html

## GraphQL Schema Definition

```graphql

{
    getTestSet {
        issueId
        projectId
        jira(fields: ["assignee", "reporter"])
    }
}

```

## Example

The query below returns a test set

```

{
    getTestSet {
        issueId
        projectId
        jira(fields: ["assignee", "reporter"])
    }
}

```

The query below returns the test set with issue id12345

```

{
    getTestSet(issueId: "12345") {
        issueId
        tests(limit: 100) {
            results {
                issueId
                testType {
                    name
                }
            }
        }
    }
}

```