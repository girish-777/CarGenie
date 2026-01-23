/**
 * Helper script to set BACKEND_URL from environment variable
 * Include this script in your HTML before other scripts
 * 
 * Usage in HTML:
 * <script>
 *   // Set BACKEND_URL (required - no default)
 *   window.BACKEND_URL = 'https://your-backend-url.onrender.com';
 * </script>
 */

(function() {
    // Get BACKEND_URL from environment or window object
    var backendUrl = 
        window.BACKEND_URL ||  // Already set
        (typeof process !== 'undefined' && process.env && process.env.BACKEND_URL);  // Node.js env
    
    if (!backendUrl) {
        console.error('BACKEND_URL is not set! Please set window.BACKEND_URL or process.env.BACKEND_URL.');
    } else {
        window.BACKEND_URL = backendUrl;
        console.log('BACKEND_URL set to:', backendUrl);
    }
})();

