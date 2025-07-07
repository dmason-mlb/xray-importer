# createPrecondition

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/createprecondition.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    createPrecondition(
        preconditionType: { name: "Generic" }
        definition: "Turn on calculator."
        jira: {
            fields: { summary:"Turn on calculator", project: {key: "CALC"} }
        }
    ) {
        precondition {
            issueId
            preconditionType {
                name
            }
            definition
            jira(fields: ["key"])
        }
        warnings
    }
}

```

## Example

The mutation below will create a new Precondition.

```

mutation {
    createPrecondition(
        preconditionType: { name: "Generic" }
        definition: "Turn on calculator."
        jira: {
            fields: { summary:"Turn on calculator", project: {key: "CALC"} }
        }
    ) {
        precondition {
            issueId
            preconditionType {
                name
            }
            definition
            jira(fields: ["key"])
        }
        warnings
    }
}

```