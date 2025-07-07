# getTestExecutions

**Category:** Queries
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/gettestexecutions.doc.html

## GraphQL Schema Definition

```graphql

{
    getTestExecutions(limit: 100) {
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

The Query below returns the first 100 Test Executions

```

{
    getTestExecutions(limit: 100) {
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

The Query below returns 10 Test Executions that match the provided jql.

```

{
    getTestExecutions(jql: "project = 'PC'", limit: 10) {
        total
        start
        limit
        results {
            issueId
            tests(limit: 10) {
                total
                start
                limit
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