# setTestRunTimer

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/settestruntimer.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    setTestRunTimer( 
        testRunId: "5acc7ab0a3fe1b6fcdc3c737"
        running: true
    ) {
        warnings
    }
}

```

## Example

The mutation below start the timer in Test Run.

```

mutation {
    setTestRunTimer( 
        testRunId: "5acc7ab0a3fe1b6fcdc3c737"
        running: true
    ) {
        warnings
    }
}

```

The mutation below stop the timer in Test Run.

```

mutation {
    setTestRunTimer( 
        testRunId: "5acc7ab0a3fe1b6fcdc3c737"
        reset: true
    ) {
        warnings
    }
}

```