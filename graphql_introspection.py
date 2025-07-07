#!/usr/bin/env python3
"""
Script to perform GraphQL introspection on Xray API and generate Postman collection
"""

import requests
import json
import os

# GraphQL introspection query
INTROSPECTION_QUERY = """
query IntrospectionQuery {
  __schema {
    queryType { name }
    mutationType { name }
    types {
      ...FullType
    }
  }
}

fragment FullType on __Type {
  kind
  name
  description
  fields(includeDeprecated: true) {
    name
    description
    args {
      ...InputValue
    }
    type {
      ...TypeRef
    }
    isDeprecated
    deprecationReason
  }
  inputFields {
    ...InputValue
  }
  interfaces {
    ...TypeRef
  }
  enumValues(includeDeprecated: true) {
    name
    description
    isDeprecated
    deprecationReason
  }
  possibleTypes {
    ...TypeRef
  }
}

fragment InputValue on __InputValue {
  name
  description
  type { ...TypeRef }
  defaultValue
}

fragment TypeRef on __Type {
  kind
  name
  ofType {
    kind
    name
    ofType {
      kind
      name
      ofType {
        kind
        name
        ofType {
          kind
          name
          ofType {
            kind
            name
            ofType {
              kind
              name
              ofType {
                kind
                name
              }
            }
          }
        }
      }
    }
  }
}
"""

def get_auth_token():
    """Get authentication token from Xray API"""
    client_id = os.getenv("XRAY_CLIENT")
    client_secret = os.getenv("XRAY_SECRET")
    
    if not client_id or not client_secret:
        print("Error: XRAY_CLIENT and XRAY_SECRET environment variables must be set")
        return None
    
    auth_url = "https://xray.cloud.getxray.app/api/v2/authenticate"
    auth_data = {
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    try:
        response = requests.post(auth_url, json=auth_data)
        response.raise_for_status()
        # Token is returned as a quoted string
        return response.text.strip('"')
    except Exception as e:
        print(f"Authentication failed: {e}")
        return None

def perform_introspection(token):
    """Perform GraphQL introspection"""
    url = "https://xray.cloud.getxray.app/api/v2/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": INTROSPECTION_QUERY
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Introspection failed: {e}")
        print(f"Response: {response.text if 'response' in locals() else 'No response'}")
        return None

def main():
    """Main function"""
    print("Getting authentication token...")
    token = get_auth_token()
    if not token:
        return
    
    print("Performing GraphQL introspection...")
    result = perform_introspection(token)
    
    if result:
        # Save introspection result
        with open("xray_graphql_schema.json", "w") as f:
            json.dump(result, f, indent=2)
        print("Introspection complete! Schema saved to xray_graphql_schema.json")
        
        # Also save just the schema part for analysis
        if "data" in result and "__schema" in result["data"]:
            with open("xray_schema_only.json", "w") as f:
                json.dump(result["data"]["__schema"], f, indent=2)
            print("Schema-only version saved to xray_schema_only.json")
    else:
        print("Failed to get introspection data")

if __name__ == "__main__":
    main()