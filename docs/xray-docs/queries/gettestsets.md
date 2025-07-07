# getTestSets

**Category:** Queries
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/gettestsets.doc.html

## GraphQL Schema Definition

```graphql

{
    getTestSets(limit: 100) {
        total
        start
        limit
        results {
            issueId
            jira(fields: ["assignee", "reporter"])
        }
    }
}

```

## Example

The query below returns the first 100 Test Sets.

```

{
    getTestSets(limit: 100) {
        total
        start
        limit
        results {
            issueId
            jira(fields: ["assignee", "reporter"])
        }
    }
}

```

The query below returns 10 Test Sets that match the provided jql.

```

{
    getTestSets(jql: "project = 'PC'", limit: 10) {
        total
        start
        limit
        results {
            issueId
            tests(limit: 10) {
                results {
                    issueId
                    testType {
                        name
                    }
                }
            }
            jira(fields: ["assignee", "reporter"])
        }
    }
}

```

Note: If the jql returns more than 100 issues an error will be returned asking the user to refine the jql search.