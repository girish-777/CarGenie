/**
 * Favorites Page JavaScript
 */

var API_BASE_URL = 'http://localhost:8000';
if (typeof window.API_BASE_URL !== 'undefined') {
    API_BASE_URL = window.API_BASE_URL;
} else {
    window.API_BASE_URL = API_BASE_URL;
}

/**
 * Load and display favorites
 */
async function loadFavorites() {
    const container = document.getElementById('favoritesContainer');
    const emptyDiv = document.getElementById('emptyFavorites');
    
    if (!container) return;
    
    const token = localStorage.getItem('auth_token');
    if (!token) {
        container.innerHTML = '<p style="text-align: center; padding: 2rem;">Please <a href="login.html">login</a> to view your favorites.</p>';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/favorites/`, {
            headers: {
                'Authorization': `Bearer ${token}`.trim()
            }
        });
        
        if (response.status === 401) {
            container.innerHTML = '<p style="text-align: center; padding: 2rem;">Your session has expired. Please <a href="login.html">login</a> again.</p>';
            localStorage.removeItem('auth_token');
            if (typeof updateNavigation === 'function') {
                updateNavigation();
            }
            return;
        }
        
        if (!response.ok) {
            throw new Error('Failed to load favorites');
        }
        
        const favorites = await response.json();
        
        if (favorites.length === 0) {
            container.style.display = 'none';
            emptyDiv.style.display = 'block';
            return;
        }
        
        emptyDiv.style.display = 'none';
        container.style.display = 'grid';
        
        let html = '';
        favorites.forEach(fav => {
            const car = fav.car;
            const imageUrl = car.image_urls && car.image_urls.length > 0 
                ? car.image_urls[0].replace(/ /g, '%20')
                : 'images/2023-Toyota-Camry.webp';
            
            html += `
                <div class="car-card" style="background: white; border-radius: 0.5rem; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); cursor: pointer; transition: transform 0.2s;" onclick="window.location.href='car-detail.html?id=${car.id}'">
                    <div class="car-image" style="width: 100%; height: 200px; overflow: hidden; position: relative;">
                        <button class="favorite-btn favorited" onclick="if(window.toggleFavorite) { window.toggleFavorite(${car.id}, this); event.stopPropagation(); } return false;" title="Remove from favorites">♥</button>
                        <img src="${imageUrl}" alt="${car.make} ${car.model}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.src='images/2023-Toyota-Camry.webp'">
                    </div>
                    <div class="car-info" style="padding: 1.5rem;">
                        <h3 style="margin: 0 0 0.5rem 0; font-size: 1.25rem; color: #1f2937;">${car.year} ${car.make} ${car.model}</h3>
                        <p style="margin: 0 0 0.5rem 0; font-size: 1.5rem; font-weight: 700; color: #2563eb;">$${car.price.toLocaleString()}</p>
                        <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; font-size: 0.875rem; color: #6b7280;">
                            <span>📍 ${car.location || 'N/A'}</span>
                            <span>⛽ ${car.fuel_type}</span>
                            <span>🔧 ${car.transmission}</span>
                            <span>📊 ${car.mileage.toLocaleString()} mi</span>
                        </div>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
        
        // Load recommendations if user has favorites
        if (favorites.length > 0) {
            loadRecommendations();
        }
    } catch (error) {
        console.error('[Favorites Page] Error loading favorites:', error);
        container.innerHTML = '<p style="text-align: center; padding: 2rem; color: #ef4444;">Error loading favorites. Please try again later.</p>';
    }
}

/**
 * Load recommended cars based on favorites
 */
async function loadRecommendations() {
    const section = document.getElementById('recommendationsSection');
    const container = document.getElementById('recommendationsContainer');
    
    if (!section || !container) return;
    
    const token = localStorage.getItem('auth_token');
    if (!token) return;
    
    try {
        console.log('[Favorites Page] Loading recommendations...');
        const response = await fetch(`${API_BASE_URL}/api/v1/recommendations?n_results=10`, {
            headers: {
                'Authorization': `Bearer ${token}`.trim()
            }
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('[Favorites Page] Failed to load recommendations:', response.status, errorText);
            section.style.display = 'none';
            return;
        }
        
        const data = await response.json();
        console.log('[Favorites Page] Recommendations response:', data);
        
        // Extract recommendations array from response
        const recommendations = data.recommendations || data || [];
        
        if (!recommendations || recommendations.length === 0) {
            console.log('[Favorites Page] No recommendations found');
            section.style.display = 'none';
            return;
        }
        
        console.log('[Favorites Page] Found', recommendations.length, 'recommendations');
        
        // Show recommendations section
        section.style.display = 'block';
        
        // Get favorite car IDs to exclude them from recommendations
        const favoritesResponse = await fetch(`${API_BASE_URL}/api/v1/favorites/`, {
            headers: {
                'Authorization': `Bearer ${token}`.trim()
            }
        });
        
        let favoriteCarIds = [];
        if (favoritesResponse.ok) {
            const favorites = await favoritesResponse.json();
            favoriteCarIds = favorites.map(f => f.car_id);
            console.log('[Favorites Page] Favorite car IDs:', favoriteCarIds);
        }
        
        // Filter out cars that are already in favorites
        const filteredRecommendations = recommendations.filter(rec => !favoriteCarIds.includes(rec.car_id));
        console.log('[Favorites Page] Filtered recommendations:', filteredRecommendations.length);
        
        // Ensure at least 3 recommendations are shown
        if (filteredRecommendations.length < 3) {
            console.log('[Favorites Page] Less than 3 recommendations available (have:', filteredRecommendations.length, ')');
            section.style.display = 'none';
            return;
        }
        
        // Show at least 3, but up to 6 recommendations
        const numToShow = Math.min(6, Math.max(3, filteredRecommendations.length));
        const recommendationsToShow = filteredRecommendations.slice(0, numToShow);
        
        console.log('[Favorites Page] Showing', recommendationsToShow.length, 'recommendations');
        
        let html = '';
        recommendationsToShow.forEach(rec => {
            const imageUrl = rec.image_urls && rec.image_urls.length > 0 
                ? rec.image_urls[0].replace(/ /g, '%20')
                : 'images/2023-Toyota-Camry.webp';
            
            html += `
                <div class="car-card" style="background: white; border-radius: 0.5rem; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); cursor: pointer; transition: transform 0.2s;" onclick="window.location.href='car-detail.html?id=${rec.car_id}'">
                    <div class="car-image" style="width: 100%; height: 200px; overflow: hidden; position: relative;">
                        <button class="favorite-btn" onclick="if(window.toggleFavorite) { window.toggleFavorite(${rec.car_id}, this); event.stopPropagation(); } return false;" title="Add to favorites">♡</button>
                        <img src="${imageUrl}" alt="${rec.make} ${rec.model}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.src='images/2023-Toyota-Camry.webp'">
                    </div>
                    <div class="car-info" style="padding: 1.5rem;">
                        <h3 style="margin: 0 0 0.5rem 0; font-size: 1.25rem; color: #1f2937;">${rec.year} ${rec.make} ${rec.model}</h3>
                        <p style="margin: 0 0 0.5rem 0; font-size: 1.5rem; font-weight: 700; color: #2563eb;">$${rec.price.toLocaleString()}</p>
                        ${rec.recommendation_reason ? `<p style="margin: 0 0 0.5rem 0; font-size: 0.875rem; color: #10b981; font-style: italic;">✨ ${rec.recommendation_reason}</p>` : ''}
                        <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; font-size: 0.875rem; color: #6b7280;">
                            <span>⛽ ${rec.fuel_type}</span>
                            <span>🔧 ${rec.transmission}</span>
                            <span>📊 ${rec.mileage.toLocaleString()} mi</span>
                        </div>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
        
        // Update favorite button states
        setTimeout(() => {
            recommendationsToShow.forEach(rec => {
                const favoriteBtn = container.querySelector(`.favorite-btn[onclick*="${rec.car_id}"]`);
                if (favoriteBtn && typeof window.updateFavoriteButton !== 'undefined') {
                    window.updateFavoriteButton(rec.car_id, favoriteBtn);
                }
            });
        }, 500);
        
    } catch (error) {
        console.error('[Favorites Page] Error loading recommendations:', error);
        if (section && container) {
            container.innerHTML = '<p style="text-align: center; padding: 1rem; color: #ef4444;">Unable to load recommendations. Please try again later.</p>';
            section.style.display = 'block';
        } else {
            section.style.display = 'none';
        }
    }
}

// Load favorites on page load
document.addEventListener('DOMContentLoaded', function() {
    loadFavorites();
});

