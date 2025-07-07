# getTestRuns

**Category:** Queries
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/gettestruns.doc.html

## GraphQL Schema Definition

```graphql

{
    getTestRuns( testIssueIds: ["10001", "10002"], testExecIssueIds: ["10001", "10002"], limit: 100 ) {
        total
        limit
        start
        results {
            id
            status {
                name
                color
                description
            }
            gherkin
            examples {
                id
                status {
                name
                color
                description
                }
            }
            test {
                issueId
            }
            testExecution {
                issueId
            }
        }
    }
}

```

## Example

The query below returns the first 100 Test Runs that match the given testIssueIds and testExecIssueIds.

```

{
    getTestRuns( testIssueIds: ["10001", "10002"], testExecIssueIds: ["10001", "10002"], limit: 100 ) {
        total
        limit
        start
        results {
            id
            status {
                name
                color
                description
            }
            gherkin
            examples {
                id
                status {
                name
                color
                description
                }
            }
            test {
                issueId
            }
            testExecution {
                issueId
            }
        }
    }
}

```

The query below returns the first 100 Test Runs that match the given ids.

```

{
    getTestRuns( testIssueIds: ["12345"], limit: 100 ) {
        total
        limit
        start
        results {
            id
            status {
                name
                color
                description
            }
            steps {
                action
                data
                result
                attachments {
                    id
                    filename
                }
                status {
                    name
                    color
                }
            }
            test {
                issueId
            }
            testExecution {
                issueId
            }
        }
    }
}

```