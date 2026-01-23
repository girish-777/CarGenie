/**
 * Main JavaScript for navigation and authentication state
 */

var API_BASE_URL = window.BACKEND_URL;
if (typeof window.API_BASE_URL !== 'undefined') {
    API_BASE_URL = window.API_BASE_URL;
} else {
    window.API_BASE_URL = API_BASE_URL;
}

// Global function to refresh admin status - can be called from anywhere
window.refreshAdminStatus = async function() {
    console.log('[Admin] Refreshing admin status...');
    await updateNavigation();
    
    // Trigger admin button updates on all pages
    if (typeof checkAndShowAdminButtons !== 'undefined') {
        await checkAndShowAdminButtons();
    }
    if (typeof checkAndShowAdminButtonsCarDetail !== 'undefined') {
        await checkAndShowAdminButtonsCarDetail();
    }
};

// Check authentication status on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('[DEBUG] main.js: DOMContentLoaded - Updating navigation');
    updateNavigation();
    
    // Initialize global chatbot if chatbot.js is loaded
    if (typeof initGlobalChatbot !== 'undefined') {
        initGlobalChatbot();
    }
    
    // Refresh admin status after page fully loads
    setTimeout(() => {
        if (typeof window.refreshAdminStatus === 'function') {
            window.refreshAdminStatus();
        }
    }, 1000);
});

/**
 * Check if current user is admin
 */
async function isAdmin() {
    const token = localStorage.getItem('auth_token');
    if (!token) return false;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const user = await response.json();
            return user.is_admin === true;
        }
        return false;
    } catch (error) {
        console.error('[Admin] Error checking admin status:', error);
        return false;
    }
}

/**
 * Update navigation based on authentication status
 */
async function updateNavigation() {
    const token = localStorage.getItem('auth_token');
    const isLoggedIn = !!token;
    const userIsAdmin = await isAdmin();
    
    console.log('[DEBUG] updateNavigation: User logged in?', isLoggedIn);
    console.log('[Admin] User is admin?', userIsAdmin);
    
    const loginLink = document.getElementById('loginLink');
    const signupLink = document.getElementById('signupLink');
    const logoutLink = document.getElementById('logoutLink');
    const profileLink = document.getElementById('profileLink');
    const favoritesLink = document.getElementById('favoritesLink');
    const compareLink = document.getElementById('compareLink');
    // Alerts feature removed
    
    if (isLoggedIn) {
        // User is logged in
        console.log('[DEBUG] updateNavigation: Showing logged-in navigation');
        if (loginLink) loginLink.style.display = 'none';
        if (signupLink) signupLink.style.display = 'none';
        if (logoutLink) logoutLink.style.display = 'inline-block';
        if (profileLink) profileLink.style.display = 'inline-block';
        if (favoritesLink) favoritesLink.style.display = 'inline-block';
        // Alerts feature removed
    } else {
        // User is not logged in
        console.log('[DEBUG] updateNavigation: Showing logged-out navigation');
        if (loginLink) loginLink.style.display = 'inline-block';
        if (signupLink) signupLink.style.display = 'inline-block';
        if (logoutLink) logoutLink.style.display = 'none';
        if (profileLink) profileLink.style.display = 'none';
        if (favoritesLink) favoritesLink.style.display = 'none';
    }
    
    // Compare link only visible when logged in
    if (compareLink) {
        compareLink.style.display = isLoggedIn ? 'inline-block' : 'none';
    }
    console.log('[DEBUG] updateNavigation: Navigation updated');
    
    // Store admin status in window for easy access
    window.userIsAdmin = userIsAdmin;
    
    // Trigger admin button updates on all pages
    if (typeof checkAndShowAdminButtons !== 'undefined') {
        checkAndShowAdminButtons();
    }
    if (typeof checkAndShowAdminButtonsCarDetail !== 'undefined') {
        checkAndShowAdminButtonsCarDetail();
    }
}

/**
 * Logout function
 */
function logout() {
    console.log('[DEBUG] logout: User logging out');
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_email');
    console.log('[DEBUG] logout: Token and email removed, redirecting to home');
    window.location.href = 'index.html';
}

// Add logout event listener if logout link exists
document.addEventListener('DOMContentLoaded', function() {
    const logoutLink = document.getElementById('logoutLink');
    if (logoutLink) {
        logoutLink.addEventListener('click', function(e) {
            e.preventDefault();
            logout();
        });
    }
});

