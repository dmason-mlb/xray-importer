# getTestPlan

**Category:** Queries
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/gettestplan.doc.html

## GraphQL Schema Definition

```graphql

{
    getTestPlan {
        issueId
        projectId
        jira(fields: ["assignee", "reporter"])
    }
}

```

## Example

The Query below returns a Test Plan.

```

{
    getTestPlan {
        issueId
        projectId
        jira(fields: ["assignee", "reporter"])
    }
}

```

The Query below returns the Test Plan with issue id12345

```

{
    getTestPlan(issueId: "12345") {
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