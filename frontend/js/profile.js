/**
 * Profile page JavaScript
 */

var API_BASE_URL = window.BACKEND_URL;
if (typeof window.API_BASE_URL !== 'undefined') {
    API_BASE_URL = window.API_BASE_URL;
} else {
    window.API_BASE_URL = API_BASE_URL;
}

// Load user data on page load
document.addEventListener('DOMContentLoaded', function() {
    loadUserData();
    
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', handleProfileUpdate);
    }
});

/**
 * Load current user data
 */
async function loadUserData() {
    const token = localStorage.getItem('auth_token');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.status === 401) {
            localStorage.removeItem('auth_token');
            window.location.href = 'login.html';
            return;
        }
        
        if (!response.ok) {
            throw new Error('Failed to load user data');
        }
        
        const user = await response.json();
        
        // Populate form fields
        document.getElementById('email').value = user.email || '';
        document.getElementById('fullName').value = user.full_name || '';
        
    } catch (error) {
        console.error('Error loading user data:', error);
        if (window.showNotification) {
            window.showNotification('Failed to load user data. Please try again.', 'error');
        }
    }
}

/**
 * Handle profile form submission
 */
async function handleProfileUpdate(e) {
    e.preventDefault();
    
    const errorMessage = document.getElementById('errorMessage');
    const successMessage = document.getElementById('successMessage');
    errorMessage.style.display = 'none';
    successMessage.style.display = 'none';
    
    const token = localStorage.getItem('auth_token');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }
    
    const fullName = document.getElementById('fullName').value.trim();
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    try {
        // Update name if changed
        if (fullName) {
            const updateResponse = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    full_name: fullName
                })
            });
            
            if (!updateResponse.ok) {
                const errorData = await updateResponse.json();
                throw new Error(errorData.detail || 'Failed to update profile');
            }
        }
        
        // Change password if provided
        if (currentPassword || newPassword || confirmPassword) {
            if (!currentPassword || !newPassword || !confirmPassword) {
                throw new Error('All password fields are required to change password');
            }
            
            if (newPassword !== confirmPassword) {
                throw new Error('New password and confirm password do not match');
            }
            
            if (newPassword.length < 6) {
                throw new Error('New password must be at least 6 characters');
            }
            
            const passwordResponse = await fetch(`${API_BASE_URL}/api/v1/auth/me/change-password`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword
                })
            });
            
            if (!passwordResponse.ok) {
                const errorData = await passwordResponse.json();
                throw new Error(errorData.detail || 'Failed to change password');
            }
            
            // Clear password fields
            document.getElementById('currentPassword').value = '';
            document.getElementById('newPassword').value = '';
            document.getElementById('confirmPassword').value = '';
        }
        
        // Show success message
        if (window.showNotification) {
            window.showNotification('Profile updated successfully!', 'success');
        } else {
            successMessage.textContent = 'Profile updated successfully!';
            successMessage.style.display = 'block';
        }
        
    } catch (error) {
        console.error('Error updating profile:', error);
        if (window.showNotification) {
            window.showNotification(error.message || 'Failed to update profile. Please try again.', 'error');
        } else {
            errorMessage.textContent = error.message || 'Failed to update profile. Please try again.';
            errorMessage.style.display = 'block';
        }
    }
}

