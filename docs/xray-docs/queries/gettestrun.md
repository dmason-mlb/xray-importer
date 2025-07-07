# getTestRun

**Category:** Queries
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/gettestrun.doc.html

## GraphQL Schema Definition

```graphql

{
    getTestRun( testIssueId: "11165", testExecIssueId: "11164") {
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
    }
}

```

## Example

The Query below returns a Test Run

```

{
    getTestRun( testIssueId: "11165", testExecIssueId: "11164") {
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
    }
}

```