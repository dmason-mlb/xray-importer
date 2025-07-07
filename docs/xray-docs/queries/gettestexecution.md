# getTestExecution

**Category:** Queries
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/gettestexecution.doc.html

## GraphQL Schema Definition

```graphql

{
    getTestExecution {
        issueId
        projectId
        jira(fields: ["assignee", "reporter"])
    }
}

```

## Example

The Query below returns a Test Execution.

```

{
    getTestExecution {
        issueId
        projectId
        jira(fields: ["assignee", "reporter"])
    }
}

```

The Query below returns the Test Execution with issue id12345.

```

{
    getTestExecution(issueId: "12345") {
        issueId
        tests(limit: 100) {
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
    }
}

```