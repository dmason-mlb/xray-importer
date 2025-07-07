# getStepStatuses

**Category:** Queries
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/getstepstatuses.doc.html

## GraphQL Schema Definition

```graphql

{
    getStepStatuses {
        name
        description
        color
    }
}

```

## Example

The Query below returns multiple Status

```

{
    getStepStatuses {
        name
        description
        color
    }
}

```