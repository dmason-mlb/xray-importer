# getExpandedTest

**Category:** Queries
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/getexpandedtest.doc.html

## GraphQL Schema Definition

```graphql

{
    getExpandedTest(issueId: "12345", testVersionId: "2") {
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
        }
        warnings
    }
}

```

## Example

The query below returns the test version 2 of the test with the id "12345".

```

{
    getExpandedTest(issueId: "12345", testVersionId: "2") {
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
        }
        warnings
    }
}

```