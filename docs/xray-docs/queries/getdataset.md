# getDataset

**Category:** Queries
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/getdataset.doc.html

## GraphQL Schema Definition

```graphql

{
    getDataset(testIssueId: "12345") {
        id
        parameters {
            name
            type
            listValues
        }
        rows { 
          order 
          Values
        }
    }
}

```

## Example

The Query below returns a Dataset.

```

{
    getDataset(testIssueId: "12345") {
        id
        parameters {
            name
            type
            listValues
        }
        rows { 
          order 
          Values
        }
    }
}

```