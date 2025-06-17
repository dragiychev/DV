// Configuration file for API keys and sensitive data
// Copy this file to 'config.js' and add your actual API keys

const CONFIG_SECRETS = {
    mapbox: {
        // Get your free Mapbox token at: https://account.mapbox.com/access-tokens/
        accessToken: 'YOUR_MAPBOX_ACCESS_TOKEN_HERE'
    }
};

// Make available globally
window.CONFIG_SECRETS = CONFIG_SECRETS; 