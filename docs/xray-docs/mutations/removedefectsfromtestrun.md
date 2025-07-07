# removeDefectsFromTestRun

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/removedefectsfromtestrun.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    removeDefectsFromTestRun( id: "5acc7ab0a3fe1b6fcdc3c737", issues: ["XRAY-1234", "12345"])
}

```

## Example

The mutation below removes 2 defects from the Test Run.

```

mutation {
    removeDefectsFromTestRun( id: "5acc7ab0a3fe1b6fcdc3c737", issues: ["XRAY-1234", "12345"])
}

```