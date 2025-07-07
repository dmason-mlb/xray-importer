# removeTestsFromTestPlan

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/removetestsfromtestplan.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    removeTestsFromTestPlan(issueId: "12345", testIssueIds: ["54321", "67890"])
}

```

## Example

The mutation below will remove the Tests with id "54321" and "67890" from the Test Plan "12345".

```

mutation {
    removeTestsFromTestPlan(issueId: "12345", testIssueIds: ["54321", "67890"])
}

```