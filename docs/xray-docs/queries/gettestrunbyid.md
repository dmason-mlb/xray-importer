# getTestRunById

**Category:** Queries
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/gettestrunbyid.doc.html

## GraphQL Schema Definition

```graphql

{
    getTestRunById( id: "5acc7ab0a3fe1b6fcdc3c737") {
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
    }
}

```

## Example

The Query below returns a Test Run.

```

{
    getTestRunById( id: "5acc7ab0a3fe1b6fcdc3c737") {
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
    }
}

```