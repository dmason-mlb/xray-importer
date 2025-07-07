# addDefectsToTestRun

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/adddefectstotestrun.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    addDefectsToTestRun( id: "5acc7ab0a3fe1b6fcdc3c737", issues: ["XRAY-1234", "12345"]) {
        addedDefects
        warnings
    }
}

```

## Example

The mutation below adds 2 defects to the Test Run.

```

mutation {
    addDefectsToTestRun( id: "5acc7ab0a3fe1b6fcdc3c737", issues: ["XRAY-1234", "12345"]) {
        addedDefects
        warnings
    }
}

```