/**
 * Favorites JavaScript
 */

var API_BASE_URL = 'http://localhost:8000';
if (typeof window.API_BASE_URL !== 'undefined') {
    API_BASE_URL = window.API_BASE_URL;
} else {
    window.API_BASE_URL = API_BASE_URL;
}

/**
 * Get authentication token
 */
function getAuthToken() {
    return localStorage.getItem('auth_token');
}

/**
 * Check if user is logged in
 */
function isLoggedIn() {
    return !!getAuthToken();
}

/**
 * Add car to favorites
 */
async function addToFavorites(carId) {
    if (!isLoggedIn()) {
        if (window.showConfirm) {
            const confirmed = await window.showConfirm('Please login to add favorites. Would you like to go to the login page?');
            if (confirmed) {
                window.location.href = 'login.html';
            }
        } else {
            if (confirm('Please login to add favorites. Would you like to go to the login page?')) {
                window.location.href = 'login.html';
            }
        }
        return false;
    }
    
    try {
        const url = `${API_BASE_URL}/api/v1/favorites/`;
        const token = getAuthToken();
        
        const numericCarId = parseInt(carId, 10);
        if (isNaN(numericCarId)) {
            if (window.showNotification) {
                window.showNotification('Invalid car ID. Please refresh the page and try again.', 'error');
            } else {
                alert('Invalid car ID. Please refresh the page and try again.');
            }
            return false;
        }
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`.trim()
            },
            body: JSON.stringify({ 
                car_id: numericCarId,
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('[Favorites] Car added to favorites:', data);
            return true;
        }
        
        if (!response.ok) {
            const errorText = await response.text();
            let data;
            try {
                data = JSON.parse(errorText);
            } catch {
                data = { detail: errorText };
            }
            
            // Handle "already in favorites" - this is not an error, it's success
            if (response.status === 400 && data.detail && data.detail.includes("already in favorites")) {
                if (window.showNotification) {
                    window.showNotification('Car is already in your favorites!', 'info');
                }
                return true; // Already favorited, this is fine
            }
            
            // Handle authentication errors
            if (response.status === 401) {
                if (window.showNotification) {
                    window.showNotification('Your session has expired. Please login again.', 'warning');
                } else {
                    alert('Your session has expired. Please login again.');
                }
                localStorage.removeItem('auth_token');
                if (typeof updateNavigation === 'function') {
                    updateNavigation();
                }
                window.location.href = 'login.html';
                return false;
            }
            
            const errorMsg = data.detail || `Failed to add favorite (Status: ${response.status})`;
            if (window.showNotification) {
                window.showNotification(errorMsg, 'error');
            } else {
                alert(errorMsg);
            }
            return false;
        }
    } catch (error) {
        console.error('[Favorites] Error adding favorite:', error);
        if (window.showNotification) {
            window.showNotification('Failed to add favorite: ' + error.message, 'error');
        } else {
            alert('Failed to add favorite: ' + error.message);
        }
        return false;
    }
}

/**
 * Remove car from favorites
 */
async function removeFromFavorites(carId) {
    if (!isLoggedIn()) {
        return false;
    }
    
    try {
        const url = `${API_BASE_URL}/api/v1/favorites/${carId}`;
        const token = getAuthToken();
        
        const response = await fetch(url, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`.trim()
            }
        });
        
        if (response.ok || response.status === 204) {
            console.log('[Favorites] Car removed from favorites');
            return true;
        }
        
        return false;
    } catch (error) {
        console.error('[Favorites] Error removing favorite:', error);
        return false;
    }
}

/**
 * Check if car is in favorites
 */
async function checkFavorite(carId) {
    if (!isLoggedIn()) {
        return false;
    }
    
    try {
        const url = `${API_BASE_URL}/api/v1/favorites/check/${carId}`;
        const token = getAuthToken();
        
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`.trim()
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            return data.is_favorite || false;
        }
        
        return false;
    } catch (error) {
        console.error('[Favorites] Error checking favorite:', error);
        return false;
    }
}

/**
 * Toggle favorite status
 */
window.toggleFavorite = async function toggleFavorite(carId, buttonElement) {
    if (!isLoggedIn()) {
        if (window.showConfirm) {
            const confirmed = await window.showConfirm('Please login to add favorites. Would you like to go to the login page?');
            if (confirmed) {
                window.location.href = 'login.html';
            }
        } else {
            if (confirm('Please login to add favorites. Would you like to go to the login page?')) {
                window.location.href = 'login.html';
            }
        }
        return;
    }
    
    const isFavorite = buttonElement.classList.contains('favorited');
    
    if (isFavorite) {
        // Remove from favorites
        const success = await removeFromFavorites(carId);
        if (success) {
            buttonElement.classList.remove('favorited');
            buttonElement.innerHTML = '♡';
            buttonElement.title = 'Add to favorites';
            
            if (window.showNotification) {
                window.showNotification('Car removed from favorites!', 'info');
            }
        }
    } else {
        // Add to favorites
        const success = await addToFavorites(carId);
        if (success) {
            buttonElement.classList.add('favorited');
            buttonElement.innerHTML = '♥';
            buttonElement.title = 'Remove from favorites';
            
            // Show success notification
            if (window.showNotification) {
                window.showNotification('Car added to favorites!', 'success');
            } else {
                alert('Car added to favorites!');
            }
            
            // Update navigation
            if (typeof updateNavigation === 'function') {
                updateNavigation();
            }
        }
    }
}

/**
 * Update favorite button state
 */
async function updateFavoriteButton(carId, buttonElement) {
    if (!isLoggedIn()) {
        buttonElement.classList.remove('favorited');
        buttonElement.innerHTML = '♡';
        buttonElement.title = 'Add to favorites';
        return;
    }
    
    const isFavorite = await checkFavorite(carId);
    if (isFavorite) {
        buttonElement.classList.add('favorited');
        buttonElement.innerHTML = '♥';
        buttonElement.title = 'Remove from favorites';
    } else {
        buttonElement.classList.remove('favorited');
        buttonElement.innerHTML = '♡';
        buttonElement.title = 'Add to favorites';
    }
}

/**
 * Create favorite button element
 */
window.createFavoriteButton = function createFavoriteButton(carId) {
    const button = document.createElement('button');
    button.className = 'favorite-btn';
    button.innerHTML = '♡';
    button.title = 'Add to favorites';
    
    button.addEventListener('click', async function(e) {
        e.stopPropagation();
        e.stopImmediatePropagation();
        e.preventDefault();
        e.cancelBubble = true;
        e.returnValue = false;
        
        if (typeof window.toggleFavorite === 'function') {
            await window.toggleFavorite(carId, button);
        }
        
        return false;
    }, true);
    
    button.addEventListener('mousedown', function(e) {
        e.stopPropagation();
        e.preventDefault();
    }, true);
    
    // Update state when created
    updateFavoriteButton(carId, button);
    
    return button;
}

