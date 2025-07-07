# getTests

**Category:** Queries
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/gettests.doc.html

## GraphQL Schema Definition

```graphql

{
    getTests(limit: 100) {
        total
        start
        limit
        results {
            issueId
            testType {
                name
                kind
            }
            jira(fields: ["assignee", "reporter"])
        }
    }
}

```

## Example

The query below returns the first 100 tests.

```

{
    getTests(limit: 100) {
        total
        start
        limit
        results {
            issueId
            testType {
                name
                kind
            }
            jira(fields: ["assignee", "reporter"])
        }
    }
}

```

The query below returns 10 tests that match the provided jql.

```

{
    getTests(jql: "project = 'PC'", limit: 10) {
        total
        start
        limit
        results {
            issueId
            testType {
                name
                kind
            }
            steps {
                id
                data
                action
                result
                attachments {
                    id
                    filename
                }
                customfields {
                    id
                    value
                }
            }
            jira(fields: ["assignee", "reporter"])
        }
    }
}

```

Note: If the jql returns more than 100 issues an error will be returned asking the user to refine the jql search.