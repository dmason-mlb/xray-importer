# createTest

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/createtest.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    createTest(
        testType: { name: "Generic" },
        unstructured: "Perform exploratory tests on calculator.",
        jira: {
            fields: { summary:"Exploratory Test", project: {key: "CALC"} }
        }
    ) {
        test {
            issueId
            testType {
                name
            }
            unstructured
            jira(fields: ["key"])
        }
        warnings
    }
}

```

## Example

The mutation below will create a new Test.

```

mutation {
    createTest(
        testType: { name: "Generic" },
        unstructured: "Perform exploratory tests on calculator.",
        jira: {
            fields: { summary:"Exploratory Test", project: {key: "CALC"} }
        }
    ) {
        test {
            issueId
            testType {
                name
            }
            unstructured
            jira(fields: ["key"])
        }
        warnings
    }
}

```

The mutation below will create a new Test.

```

mutation {
    createTest(
        testType: { name: "Manual" },
        steps: [
            {
                action: "Create first example step",
                result: "First step was created"
            },
            {
                action: "Create second example step with data",
                data: "Data for the step",
                result: "Second step was created with data"
            }
        ],
        jira: {
            fields: { summary:"Exploratory Test", project: {key: "CALC"} }
        }
    ) {
        test {
            issueId
            testType {
                name
            }
            steps {
                action
                data
                result
            }
            jira(fields: ["key"])
        }
        warnings
    }
}

```