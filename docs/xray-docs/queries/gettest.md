# getTest

**Category:** Queries
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/gettest.doc.html

## GraphQL Schema Definition

```graphql

{
    getTest {
        issueId
        gherkin
        jira(fields: ["assignee", "reporter"])
    }
}

```

## Example

The query below returns a Test.

```

{
    getTest {
        issueId
        gherkin
        jira(fields: ["assignee", "reporter"])
    }
}

```

The query below returns the Test with issue id12345.

```

{
    getTest(issueId: "12345") {
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
        }
    }
}

```