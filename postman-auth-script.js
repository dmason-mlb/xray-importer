// Postman Test Script for Xray Authentication
// Place this in the "Tests" tab of your Xray authentication request

// Check if the request was successful
if (pm.response.code === 200) {
    try {
        // Get the response text (JWT token is returned as a quoted string)
        let responseText = pm.response.text();
        
        // Remove quotes from the token if present
        let token = responseText.replace(/^"|"$/g, '');
        
        // Validate that we have a token
        if (token && token.length > 0) {
            // Store the token in Postman Vault (secure storage)
            pm.vault.set("Xray_Token", token);
            
            // Also set it as a collection variable for immediate use
            pm.collectionVariables.set("xray_token", token);
            
            // Optional: Set token expiration (Xray tokens typically expire after 24 hours)
            const expirationTime = new Date();
            expirationTime.setHours(expirationTime.getHours() + 24);
            pm.collectionVariables.set("xray_token_expires", expirationTime.toISOString());
            
            // Log success message
            console.log("✅ Xray token successfully stored in vault");
            console.log("Token length:", token.length);
            console.log("Token preview:", token.substring(0, 20) + "...");
            console.log("Token expires at:", expirationTime.toISOString());
            
            // Set test result
            pm.test("Authentication successful - Token stored in vault", function () {
                pm.response.to.have.status(200);
                pm.expect(token).to.be.a('string');
                pm.expect(token.length).to.be.above(100);
            });
        } else {
            console.error("❌ No token found in response");
            pm.test("Token extraction failed", function () {
                pm.expect(token).to.not.be.undefined;
            });
        }
    } catch (error) {
        console.error("❌ Error processing authentication response:", error);
        pm.test("Error processing response", function () {
            pm.expect(error).to.be.null;
        });
    }
} else {
    console.error("❌ Authentication failed with status:", pm.response.code);
    pm.test("Authentication failed", function () {
        pm.response.to.have.status(200);
    });
}