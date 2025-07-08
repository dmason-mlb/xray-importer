# XRAY GraphQL API Authentication

## Overview

The XRAY GraphQL API uses a token-based authentication system. Before making any GraphQL requests, you must obtain an authentication token using your API credentials.

## Prerequisites

1. **XRAY API Key**: You need to create an API Key in XRAY's Global Settings
   - Navigate to: XRAY → Global Settings → API Keys
   - Create a new API Key
   - Note down the **Client ID** and **Client Secret**

2. **Environment Variables**: Store your credentials securely
   ```bash
   export XRAY_CLIENT="your_client_id"
   export XRAY_SECRET="your_client_secret"
   ```

## Authentication Process

### Step 1: Obtain Authentication Token

**Endpoint**: `https://xray.cloud.getxray.app/api/v2/authenticate`  
**Method**: `POST`  
**Content-Type**: `application/json`

**Request Body**:
```json
{
  "client_id": "32A27E69C0AC4E539C1401643709E8E7",
  "client_secret": "d62f81eb9ed859e22e54356dd8a00e4a5f0d0c2b2b52340776f6c7d6d757b962"
}
```

**cURL Example**:
```bash
# Using a JSON file
curl -H "Content-Type: application/json" -X POST \
  --data @"cloud_auth.json" \
  https://xray.cloud.getxray.app/api/v2/authenticate

# Direct JSON
curl -H "Content-Type: application/json" -X POST \
  --data '{"client_id": "YOUR_CLIENT_ID", "client_secret": "YOUR_CLIENT_SECRET"}' \
  https://xray.cloud.getxray.app/api/v2/authenticate

# Store token in variable
token=$(curl -H "Content-Type: application/json" -X POST \
  --data @"cloud_auth.json" \
  https://xray.cloud.getxray.app/api/v2/authenticate | tr -d '"')
```

**Response**:
- **200 OK**: Returns a JWT token as a JSON string (with quotes)
  ```
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  ```
- **400 Bad Request**: Wrong request syntax
- **401 Unauthorized**: Invalid license or credentials
- **500 Internal Server Error**: Server error during authentication

### Step 2: Use Token in GraphQL Requests

**GraphQL Endpoint**: `https://xray.cloud.getxray.app/api/v2/graphql`

**Headers**:
```
Authorization: Bearer <your_token>
Content-Type: application/json
```

**Example GraphQL Request**:
```bash
curl -H "Authorization: Bearer $token" \
     -H "Content-Type: application/json" \
     -X POST \
     --data '{"query": "{ getTest(issueId: \"12345\") { issueId } }"}' \
     https://xray.cloud.getxray.app/api/v2/graphql
```

## Python Implementation

```python
import requests
import os

def get_auth_token():
    """Get authentication token from Xray API"""
    client_id = os.getenv("XRAY_CLIENT")
    client_secret = os.getenv("XRAY_SECRET")
    
    if not client_id or not client_secret:
        raise ValueError("XRAY_CLIENT and XRAY_SECRET environment variables must be set")
    
    auth_url = "https://xray.cloud.getxray.app/api/v2/authenticate"
    auth_data = {
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    try:
        response = requests.post(auth_url, json=auth_data)
        response.raise_for_status()
        # Token is returned as a quoted string, remove quotes
        return response.text.strip('"')
    except requests.exceptions.RequestException as e:
        raise Exception(f"Authentication failed: {e}")

def execute_graphql_query(query, variables=None):
    """Execute a GraphQL query with authentication"""
    token = get_auth_token()
    
    url = "https://xray.cloud.getxray.app/api/v2/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()
```

## JavaScript/Node.js Implementation

```javascript
const axios = require('axios');

async function getAuthToken() {
    const clientId = process.env.XRAY_CLIENT;
    const clientSecret = process.env.XRAY_SECRET;
    
    if (!clientId || !clientSecret) {
        throw new Error('XRAY_CLIENT and XRAY_SECRET environment variables must be set');
    }
    
    const authUrl = 'https://xray.cloud.getxray.app/api/v2/authenticate';
    const authData = {
        client_id: clientId,
        client_secret: clientSecret
    };
    
    try {
        const response = await axios.post(authUrl, authData);
        // Remove quotes from token
        return response.data.replace(/"/g, '');
    } catch (error) {
        throw new Error(`Authentication failed: ${error.message}`);
    }
}

async function executeGraphQLQuery(query, variables = null) {
    const token = await getAuthToken();
    
    const url = 'https://xray.cloud.getxray.app/api/v2/graphql';
    const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };
    
    const payload = { query };
    if (variables) {
        payload.variables = variables;
    }
    
    const response = await axios.post(url, payload, { headers });
    return response.data;
}
```

## Token Expiration

- Tokens expire after approximately 24 hours
- Implement token refresh logic in production applications
- Cache tokens to avoid unnecessary authentication calls

## Security Best Practices

1. **Never hardcode credentials** in your source code
2. **Use environment variables** or secure vaults for credentials
3. **Rotate API keys** regularly
4. **Limit API key permissions** to only what's needed
5. **Use HTTPS** for all API calls
6. **Validate SSL certificates** in production
7. **Log authentication attempts** for security monitoring
8. **Implement rate limiting** to avoid API abuse

## Common Authentication Errors

| Error | Cause | Solution |
|-------|-------|----------|
| 400 Bad Request | Malformed JSON or missing fields | Check request format and required fields |
| 401 Unauthorized | Invalid credentials or expired license | Verify API key and XRAY license status |
| 403 Forbidden | Insufficient permissions | Check API key permissions in XRAY |
| 429 Too Many Requests | Rate limit exceeded | Implement backoff and retry logic |
| 500 Internal Server Error | Server issue | Retry with exponential backoff |

## Next Steps

Once authenticated, you can proceed to make GraphQL queries and mutations as documented in the following sections.