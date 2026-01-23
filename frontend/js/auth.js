/**
 * Authentication JavaScript
 */

var API_BASE_URL = 'http://localhost:8000';
if (typeof window.API_BASE_URL !== 'undefined') {
    API_BASE_URL = window.API_BASE_URL;
} else {
    window.API_BASE_URL = API_BASE_URL;
}

// Handle login form submission
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    if (signupForm) {
        signupForm.addEventListener('submit', handleSignup);
    }
});

/**
 * Handle login form submission
 */
async function handleLogin(e) {
    e.preventDefault();
    console.log('[DEBUG] handleLogin: Login form submitted');
    
    const formData = new FormData(e.target);
    const email = formData.get('email');
    const password = formData.get('password');
    console.log('[DEBUG] handleLogin: Email:', email, 'Password length:', password ? password.length : 0);
    
    const errorMessage = document.getElementById('errorMessage');
    if (!errorMessage) {
        console.error('[DEBUG] handleLogin: errorMessage element not found');
        return;
    }
    errorMessage.style.display = 'none';
    
    try {
        // OAuth2PasswordRequestForm expects form-urlencoded data
        const params = new URLSearchParams();
        params.append('username', email); // OAuth2 uses 'username' field
        params.append('password', password);
        
        const url = `${API_BASE_URL}/api/v1/auth/login`;
        console.log('[DEBUG] handleLogin: Sending request to', url);
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: params
        });
        
        console.log('[DEBUG] handleLogin: Response status', response.status, response.statusText);
        
        const data = await response.json();
        console.log('[DEBUG] handleLogin: Response data received');
        
        if (!response.ok) {
            console.error('[DEBUG] handleLogin: Login failed:', data.detail);
            throw new Error(data.detail || 'Login failed');
        }
        
        // Store token
        console.log('[DEBUG] handleLogin: Login successful, storing token');
        localStorage.setItem('auth_token', data.access_token);
        localStorage.setItem('user_email', email);
        console.log('[DEBUG] handleLogin: Token stored, redirecting to home');
        
        // Redirect to home
        window.location.href = 'index.html';
    } catch (error) {
        console.error('[DEBUG] handleLogin: Error occurred:', error);
        errorMessage.textContent = error.message || 'An error occurred during login';
        errorMessage.style.display = 'block';
    }
}

/**
 * Handle signup form submission
 */
async function handleSignup(e) {
    e.preventDefault();
    console.log('[DEBUG] handleSignup: Signup form submitted');
    
    const formData = new FormData(e.target);
    const email = formData.get('email');
    const password = formData.get('password');
    const confirmPassword = formData.get('confirmPassword');
    const fullName = formData.get('fullName');
    console.log('[DEBUG] handleSignup: Email:', email, 'Full name:', fullName, 'Password length:', password ? password.length : 0);
    
    const errorMessage = document.getElementById('errorMessage');
    if (!errorMessage) {
        console.error('[DEBUG] handleSignup: errorMessage element not found');
        return;
    }
    errorMessage.style.display = 'none';
    
    // Validate passwords match
    if (password !== confirmPassword) {
        console.warn('[DEBUG] handleSignup: Passwords do not match');
        errorMessage.textContent = 'Passwords do not match';
        errorMessage.style.display = 'block';
        return;
    }
    
    // Validate password length
    if (password.length < 6) {
        console.warn('[DEBUG] handleSignup: Password too short');
        errorMessage.textContent = 'Password must be at least 6 characters';
        errorMessage.style.display = 'block';
        return;
    }
    
    try {
        const signupData = {
            email: email,
            password: password,
            full_name: fullName || null
        };
        console.log('[DEBUG] handleSignup: Sending signup request with data:', { ...signupData, password: '***' });
        
        const url = `${API_BASE_URL}/api/v1/auth/signup`;
        console.log('[DEBUG] handleSignup: Sending request to', url);
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(signupData)
        });
        
        console.log('[DEBUG] handleSignup: Response status', response.status, response.statusText);
        
        const data = await response.json();
        console.log('[DEBUG] handleSignup: Response data received');
        
        if (!response.ok) {
            console.error('[DEBUG] handleSignup: Signup failed:', data.detail);
            throw new Error(data.detail || 'Signup failed');
        }
        
        console.log('[DEBUG] handleSignup: Signup successful, redirecting to login');
        // Redirect to login page
        alert('Account created successfully! Please login.');
        window.location.href = 'login.html';
    } catch (error) {
        console.error('[DEBUG] handleSignup: Error occurred:', error);
        errorMessage.textContent = error.message || 'An error occurred during signup';
        errorMessage.style.display = 'block';
    }
}

