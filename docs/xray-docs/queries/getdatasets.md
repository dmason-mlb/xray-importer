# getDatasets

**Category:** Queries
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/getdatasets.doc.html

## GraphQL Schema Definition

```graphql

{
    getDatasets(
        testIssueIds: ["30000", "40000"],
    ) 
      {
        id
        testIssueId  
        testExecIssueId
        testPlanIssueId
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

The Query below demonstrates how to retrieve multiple Datasets, including their metadata, parameters

```

{
    getDatasets(
        testIssueIds: ["30000", "40000"],
    ) 
      {
        id
        testIssueId  
        testExecIssueId
        testPlanIssueId
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