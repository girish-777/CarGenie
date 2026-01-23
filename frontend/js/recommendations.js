/**
 * Personalized recommendations JavaScript
 */

var API_BASE_URL = window.BACKEND_URL;
if (typeof window.API_BASE_URL !== 'undefined') {
    API_BASE_URL = window.API_BASE_URL;
} else {
    window.API_BASE_URL = API_BASE_URL;
}

/**
 * Load personalized recommendations
 */
async function loadRecommendations(containerId, nResults = 10) {
    console.log('[DEBUG] loadRecommendations: Loading recommendations');
    
    const container = document.getElementById(containerId);
    if (!container) {
        console.error('[DEBUG] loadRecommendations: Container not found:', containerId);
        return;
    }
    
    // Show loading state
    container.innerHTML = '<div class="loading"><p>Loading personalized recommendations...</p></div>';
    
    try {
        // Get auth token if available
        const token = localStorage.getItem('auth_token');
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        const url = `${API_BASE_URL}/api/v1/recommendations?n_results=${nResults}`;
        console.log('[DEBUG] loadRecommendations: Fetching from', url);
        
        const response = await fetch(url, {
            method: 'GET',
            headers: headers
        });
        
        console.log('[DEBUG] loadRecommendations: Response status', response.status);
        
        if (!response.ok) {
            throw new Error('Failed to load recommendations');
        }
        
        const data = await response.json();
        console.log('[DEBUG] loadRecommendations: Received', data.total, 'recommendations');
        console.log('[DEBUG] loadRecommendations: User preferences:', data.user_preferences);
        
        if (data.recommendations.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #6b7280; padding: 2rem;">No recommendations available at this time.</p>';
            return;
        }
        
        // Ensure at least 3 recommendations are shown (for home page)
        // If less than 3, we'll show what we have but log a warning
        if (data.recommendations.length < 3) {
            console.warn('[DEBUG] loadRecommendations: Only', data.recommendations.length, 'recommendations available (need at least 3)');
        }
        const recommendationsToShow = data.recommendations.slice(0, Math.max(3, data.recommendations.length));
        
        // Display recommendations
        displayRecommendations(container, recommendationsToShow, data.user_preferences);
        
    } catch (error) {
        console.error('[DEBUG] loadRecommendations: Error', error);
        container.innerHTML = '<p style="text-align: center; color: #dc2626; padding: 2rem;">Failed to load recommendations. Please try again later.</p>';
    }
}

/**
 * Display recommendations in a grid
 */
function displayRecommendations(container, recommendations, userPreferences) {
    console.log('[DEBUG] displayRecommendations: Displaying', recommendations.length, 'recommendations');
    
    let html = '';
    
    // Add header
    html += `
        <div style="margin-bottom: 1.5rem;">
            <h3 style="margin: 0;">⭐ Recommended for You</h3>
            <p style="margin: 0.5rem 0 0 0; color: #6b7280; font-size: 0.9rem;">
                ${!localStorage.getItem('auth_token') ? 'Sign in to get personalized recommendations!' : 'Discover cars that match your preferences.'}
            </p>
        </div>
    `;
    
    // Create grid - show at least 3 cars (or all available if less than 3)
    const carsToShow = recommendations.slice(0, Math.max(3, recommendations.length));
    html += '<div class="cars-grid" style="margin-top: 1.5rem; display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 2rem;">';
    
    carsToShow.forEach((rec) => {
        const imageUrl = rec.image_urls && rec.image_urls.length > 0 
            ? rec.image_urls[0] 
            : 'images/2023-Toyota-Camry.webp';
        
        html += `
            <div class="car-card" onclick="window.location.href='car-detail.html?id=${rec.car_id}'" style="cursor: pointer;">
                <div class="car-image">
                    <img src="${imageUrl}" alt="${rec.make} ${rec.model}" 
                         onerror="this.src='images/2023-Toyota-Camry.webp'">
                    ${rec.similarity_score ? `
                        <div style="position: absolute; top: 0.5rem; right: 0.5rem; background-color: #2563eb; color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem; font-weight: 600;">
                            ${Math.round(rec.similarity_score)}% Match
                        </div>
                    ` : ''}
                </div>
                <div class="car-info">
                    <h3>${rec.year} ${rec.make} ${rec.model}</h3>
                    <p class="car-price">$${rec.price.toLocaleString()}</p>
                    <div class="car-details">
                        <span>⛽ ${rec.fuel_type}</span>
                        <span>🔧 ${rec.transmission}</span>
                        <span>📊 ${rec.mileage.toLocaleString()} mi</span>
                    </div>
                    ${rec.recommendation_reason ? `
                        <p style="margin-top: 0.5rem; color: #6b7280; font-size: 0.875rem; font-style: italic;">
                            💡 ${rec.recommendation_reason}
                        </p>
                    ` : ''}
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    
    container.innerHTML = html;
    console.log('[DEBUG] displayRecommendations: Recommendations displayed');
}

/**
 * Create a recommendation card (for use in other pages)
 */
function createRecommendationCard(rec) {
    const imageUrl = rec.image_urls && rec.image_urls.length > 0 
        ? rec.image_urls[0] 
        : 'https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=800';
    
    const card = document.createElement('div');
    card.className = 'car-card';
    card.style.cursor = 'pointer';
    card.onclick = () => {
        window.location.href = `car-detail.html?id=${rec.car_id}`;
    };
    
    card.innerHTML = `
        <div class="car-image">
            <img src="${imageUrl}" alt="${rec.make} ${rec.model}" 
                 onerror="this.src='https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=800'">
            ${rec.similarity_score ? `
                <div style="position: absolute; top: 0.5rem; right: 0.5rem; background-color: #2563eb; color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem; font-weight: 600;">
                    ${Math.round(rec.similarity_score)}% Match
                </div>
            ` : ''}
        </div>
        <div class="car-info">
            <h3>${rec.year} ${rec.make} ${rec.model}</h3>
            <p class="car-price">$${rec.price.toLocaleString()}</p>
            <div class="car-details">
                <span>⛽ ${rec.fuel_type}</span>
                <span>🔧 ${rec.transmission}</span>
                <span>📊 ${rec.mileage.toLocaleString()} mi</span>
            </div>
            ${rec.recommendation_reason ? `
                <p style="margin-top: 0.5rem; color: #6b7280; font-size: 0.875rem; font-style: italic;">
                    💡 ${rec.recommendation_reason}
                </p>
            ` : ''}
        </div>
    `;
    
    return card;
}

// Make functions globally available
window.loadRecommendations = loadRecommendations;
window.displayRecommendations = displayRecommendations;
window.createRecommendationCard = createRecommendationCard;

