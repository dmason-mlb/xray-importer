# getExpandedTests

**Category:** Queries
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/getexpandedtests.doc.html

## GraphQL Schema Definition

```graphql

{
    getExpandedTests(limit: 100) {
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
            warnings
        }
    }
}

```

## Example

The query below returns the first 100 tests.

```

{
    getExpandedTests(limit: 100) {
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
            warnings
        }
    }
}

```

The query below returns 10 tests that match the provided jql.

```

{
    getExpandedTests(jql: "project = 'PC'", limit: 10) {
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
                parentTestIssueId
                calledTestIssueId
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
            warnings
        }
    }
}

```

Note: If the jql returns more than 100 issues an error will be returned asking the user to refine the jql search.

The query below returns the tests of each test version.

```

{
    getExpandedTests(tests:[{ issueId:"12345", testVersionId: "1" }, { issueId:"54321", testVersionId: "2" }]) {
        total
        start
        limit
        results {
            issueId
            testType {
                name
                kind
            }
        }
    }
}

```