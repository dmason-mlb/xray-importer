// Postman Pre-request Script for Xray API Requests
// Place this in the "Pre-request Script" tab of your Xray GraphQL requests

// Function to check if token is expired
function isTokenExpired() {
    const expirationString = pm.collectionVariables.get("xray_token_expires");
    if (!expirationString) return true;
    
    const expirationTime = new Date(expirationString);
    const currentTime = new Date();
    
    // Add 5 minute buffer before expiration
    const bufferTime = new Date(expirationTime.getTime() - 5 * 60 * 1000);
    
    return currentTime >= bufferTime;
}

// Retrieve token from vault
pm.vault.get("Xray_Token").then((token) => {
    if (token && !isTokenExpired()) {
        // Token exists and is not expired
        pm.request.headers.add({
            key: 'Authorization',
            value: `Bearer ${token}`
        });
        console.log("✅ Using cached Xray token from vault");
    } else {
        // Token doesn't exist or is expired
        console.warn("⚠️ Xray token not found in vault or expired");
        console.warn("Please run the authentication request first");
        
        // Optionally, you can trigger the auth request automatically
        // by setting a flag that your collection runner can check
        pm.collectionVariables.set("needs_auth", true);
    }
}).catch((error) => {
    console.error("❌ Error retrieving token from vault:", error);
});