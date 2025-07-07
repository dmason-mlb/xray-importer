# removeTestPlansFromTest

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/removetestplansfromtest.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    removeTestPlansFromTest(issueId: "12345", testPlanIssueIds: ["54321", "67890"])
}

```

## Example

The mutation below will remove the Test Plans with issue id "54321" and "67890" from the Test "12345".

```

mutation {
    removeTestPlansFromTest(issueId: "12345", testPlanIssueIds: ["54321", "67890"])
}

```