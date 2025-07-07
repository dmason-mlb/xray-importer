# getTestRunsById

**Category:** Queries
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/gettestrunsbyid.doc.html

## GraphQL Schema Definition

```graphql

{
    getTestRunsById( ids: ["5acc7ab0a3fe1b6fcdc3c737"], limit: 10 ) {
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

The query below returns the first 100 Test Runs that match the given ids.

```

{
    getTestRunsById( ids: ["5acc7ab0a3fe1b6fcdc3c737"], limit: 10 ) {
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