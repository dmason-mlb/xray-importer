# getStepStatus

**Category:** Queries
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/getstepstatus.doc.html

## GraphQL Schema Definition

```graphql

{
    getStepStatus( name: "PASSED") {
        name
        description
        color
    }
}

```

## Example

The Query below returns a Status

```

{
    getStepStatus( name: "PASSED") {
        name
        description
        color
    }
}

```