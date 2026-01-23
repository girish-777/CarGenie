/**
 * Configuration file for frontend
 * Sets API_BASE_URL from BACKEND_URL environment variable or window.BACKEND_URL
 */
(function() {
    // Get BACKEND_URL from environment or window object
    var BACKEND_URL = (typeof window !== 'undefined' && window.BACKEND_URL) 
        || (typeof process !== 'undefined' && process.env && process.env.BACKEND_URL);
    
    if (!BACKEND_URL) {
        console.error('BACKEND_URL is not set! Please set window.BACKEND_URL before loading scripts.');
    }
    
    // Set global API_BASE_URL
    window.API_BASE_URL = BACKEND_URL;
    var API_BASE_URL = BACKEND_URL;
    
    // Export for use in other scripts
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = { API_BASE_URL, BACKEND_URL };
    }
})();

