/**
 * Environment Configuration
 * Automatically sets BACKEND_URL based on environment
 * Works for both local development and Render deployment
 */
(function() {
    // Check if we're on Render (production)
    const isRender = window.location.hostname.includes('onrender.com') || 
                     window.location.hostname.includes('render.com');
    
    // Check if we're on localhost
    const isLocalhost = window.location.hostname === 'localhost' || 
                        window.location.hostname === '127.0.0.1';
    
    // If BACKEND_URL is already set, use it
    if (window.BACKEND_URL) {
        console.log('BACKEND_URL already set to:', window.BACKEND_URL);
        return;
    }
    
    // Set BACKEND_URL based on environment
    if (isRender) {
        // On Render: Try multiple methods to get backend URL
        // Method 1: Check for meta tag with backend URL
        const backendMeta = document.querySelector('meta[name="backend-url"]');
        if (backendMeta) {
            window.BACKEND_URL = backendMeta.getAttribute('content');
            console.log('[ENV-CONFIG] BACKEND_URL from meta tag:', window.BACKEND_URL);
        } else {
            // Method 2: Use naming convention (frontend name -> backend name)
            // If frontend is "cargenie-frontend", backend might be "cargenie-backend"
            const frontendName = window.location.hostname.split('.')[0];
            let backendName = frontendName.replace('-frontend', '-backend');
            
            // If no -frontend suffix, try common patterns
            if (backendName === frontendName) {
                // Try adding -backend suffix
                backendName = frontendName + '-backend';
            }
            
            window.BACKEND_URL = `https://${backendName}.onrender.com`;
            console.log('[ENV-CONFIG] Render environment detected.');
            console.log('[ENV-CONFIG] Frontend name:', frontendName);
            console.log('[ENV-CONFIG] BACKEND_URL set to:', window.BACKEND_URL);
            console.log('[ENV-CONFIG] If this is wrong, add: <meta name="backend-url" content="https://your-backend-url.onrender.com"> in <head>');
        }
    } else if (isLocalhost) {
        // Local development: Use localhost
        window.BACKEND_URL = 'http://localhost:8000';
        console.log('[ENV-CONFIG] Local development detected. BACKEND_URL set to:', window.BACKEND_URL);
    } else {
        // Fallback: Try to detect or use a default
        window.BACKEND_URL = 'http://localhost:8000';
        console.warn('[ENV-CONFIG] Could not detect environment. Using default BACKEND_URL:', window.BACKEND_URL);
    }
    
    // Also set API_BASE_URL for compatibility
    window.API_BASE_URL = window.BACKEND_URL;
    console.log('[ENV-CONFIG] Final BACKEND_URL:', window.BACKEND_URL);
    console.log('[ENV-CONFIG] Final API_BASE_URL:', window.API_BASE_URL);
})();

