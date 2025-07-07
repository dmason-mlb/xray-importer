# updateTestRun

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/updatetestrun.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    updateTestRun( id: "5acc7ab0a3fe1b6fcdc3c737", comment: "Everything is OK.", startedOn: "2020-03-09T10:35:09Z", finishedOn: "2020-04-09T10:35:09Z", assigneeId: "e5983db2-90f7-4135-a96f-46907e72290e", executedById: "e5983db2-90f7-4135-a96f-46907e72290e") {
        warnings
    }
}

```

## Example

The mutation below updates a Test Run.

```

mutation {
    updateTestRun( id: "5acc7ab0a3fe1b6fcdc3c737", comment: "Everything is OK.", startedOn: "2020-03-09T10:35:09Z", finishedOn: "2020-04-09T10:35:09Z", assigneeId: "e5983db2-90f7-4135-a96f-46907e72290e", executedById: "e5983db2-90f7-4135-a96f-46907e72290e") {
        warnings
    }
}

```