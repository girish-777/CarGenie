/**
 * Car detail page JavaScript
 */

var API_BASE_URL = 'http://localhost:8000';
if (typeof window.API_BASE_URL !== 'undefined') {
    API_BASE_URL = window.API_BASE_URL;
} else {
    window.API_BASE_URL = API_BASE_URL;
}

// Load favorites.js if not already loaded
if (typeof createFavoriteButton === 'undefined') {
    const script = document.createElement('script');
    script.src = 'js/favorites.js';
    document.head.appendChild(script);
}

// Load car details on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('[DEBUG] car-detail.js: DOMContentLoaded - Initializing car detail page');
    console.log('[DEBUG] car-detail.js: Current URL:', window.location.href);
    const urlParams = new URLSearchParams(window.location.search);
    const carId = urlParams.get('id');
    console.log('[DEBUG] car-detail.js: Car ID from URL:', carId);
    console.log('[DEBUG] car-detail.js: All URL params:', Array.from(urlParams.entries()));
    
    if (carId) {
        // Ensure carId is a number
        const numericCarId = parseInt(carId, 10);
        if (isNaN(numericCarId)) {
            console.error('[DEBUG] car-detail.js: Invalid car ID (not a number):', carId);
            showError('Invalid car ID provided');
            return;
        }
        console.log('[DEBUG] car-detail.js: Loading car detail for ID:', numericCarId);
        loadCarDetail(numericCarId);
    } else {
        console.error('[DEBUG] car-detail.js: No car ID provided in URL');
        showError('No car ID provided');
    }
});

/**
 * Load car detail from API
 */
async function loadCarDetail(carId) {
    console.log('[DEBUG] loadCarDetail: Starting to load car detail for ID', carId);
    
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorMessage = document.getElementById('errorMessage');
    const carDetailContainer = document.getElementById('carDetailContainer');
    
    if (!loadingIndicator || !errorMessage || !carDetailContainer) {
        console.error('[DEBUG] loadCarDetail: Required DOM elements not found');
        return;
    }
    
    loadingIndicator.style.display = 'block';
    errorMessage.style.display = 'none';
    carDetailContainer.style.display = 'none';
    
    try {
        const url = `${API_BASE_URL}/api/v1/cars/${carId}`;
        console.log('[DEBUG] loadCarDetail: Fetching from', url);
        
        const response = await fetch(url);
        console.log('[DEBUG] loadCarDetail: Response status', response.status, response.statusText);
        
        if (!response.ok) {
            if (response.status === 404) {
                console.error('[DEBUG] loadCarDetail: Car not found (404)');
                throw new Error('Car not found');
            }
            const errorText = await response.text();
            console.error('[DEBUG] loadCarDetail: Error response:', errorText);
            throw new Error('Failed to load car details');
        }
        
        const car = await response.json();
        console.log('[DEBUG] loadCarDetail: Car data received:', {
            id: car.id,
            make: car.make,
            model: car.model,
            price: car.price,
            image_urls: car.image_urls
        });
        
        // Verify we got a single car object, not an array
        if (Array.isArray(car)) {
            console.error('[DEBUG] loadCarDetail: ERROR - Received array instead of single car object!', car);
            showError('Error: Received multiple cars instead of one. Please check the API endpoint.');
            return;
        }
        
        // Verify the car ID matches
        if (car.id !== parseInt(carId, 10)) {
            console.warn('[DEBUG] loadCarDetail: WARNING - Car ID mismatch. Expected:', carId, 'Got:', car.id);
        }
        
        console.log('[DEBUG] loadCarDetail: Displaying single car:', car.make, car.model, '(ID:', car.id, ')');
        
        // Ensure car has required fields
        if (!car.id || !car.make || !car.model) {
            console.error('[DEBUG] loadCarDetail: Car missing required fields:', car);
            showError('Car data is incomplete. Please try again.');
            return;
        }
        
        displayCarDetail(car);
        console.log('[DEBUG] loadCarDetail: Car detail displayed successfully');
        
    } catch (error) {
        console.error('[DEBUG] loadCarDetail: Error occurred:', error);
        showError(error.message || 'Failed to load car details. Make sure the backend is running.');
    } finally {
        loadingIndicator.style.display = 'none';
        console.log('[DEBUG] loadCarDetail: Finished loading car detail');
    }
}

/**
 * Display car detail
 */
function displayCarDetail(car) {
    console.log('[DEBUG] displayCarDetail: Displaying car detail for', car.make, car.model, '(ID:', car.id, ')');
    
    // Verify it's a single car object, not an array
    if (Array.isArray(car)) {
        console.error('[DEBUG] displayCarDetail: ERROR - Received array instead of single car!', car);
        showError('Error: Received multiple cars. Expected a single car object.');
        return;
    }
    
    const container = document.getElementById('carDetailContainer');
    
    if (!container) {
        console.error('[DEBUG] displayCarDetail: carDetailContainer element not found');
        showError('Car detail container not found');
        return;
    }
    
    // Validate required car fields
    if (!car || !car.id) {
        console.error('[DEBUG] displayCarDetail: Invalid car data:', car);
        showError('Invalid car data received');
        return;
    }
    
    // Ensure container is visible
    container.style.display = 'block';
    
    // Handle image URLs - support multiple images
    const imageUrls = car.image_urls && car.image_urls.length > 0 
        ? car.image_urls 
        : ['images/2023-Toyota-Camry.webp'];
    
    // Encode spaces in local paths
    const processedImages = imageUrls.map(url => {
        if (url.startsWith('images/')) {
            return url.replace(/ /g, '%20');
        }
        return url;
    });
    
    const mainImage = processedImages[0];
    
    // Create image gallery HTML
    const galleryImages = processedImages.map((url, index) => `
        <img src="${url}" alt="${car.make} ${car.model} - Image ${index + 1}" 
             class="gallery-thumb ${index === 0 ? 'active' : ''}"
             onclick="changeMainImage('${url}')"
             onerror="this.src='images/2023-Toyota-Camry.webp'">
    `).join('');
    
    const specs = car.specs || {};
    const scores = car.scores || {};
    
    try {
        container.innerHTML = `
        <div class="car-detail-header">
            <div class="image-gallery-container">
                <img src="${mainImage}" alt="${car.make} ${car.model}" class="car-detail-image" id="mainCarImage"
                     onerror="this.src='https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=800'"
                     onload="this.style.transform='rotate(0deg)'; this.style.imageOrientation='from-image';">
                ${processedImages.length > 1 ? `
                    <div class="image-gallery">
                        ${galleryImages}
                    </div>
                ` : ''}
            </div>
            <div class="car-detail-info">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                    <h1>${car.year || ''} ${car.make || ''} ${car.model || ''}</h1>
                    <div id="favoriteButtonContainer"></div>
                </div>
                <div class="car-detail-price">$${car.price ? car.price.toLocaleString() : 'N/A'}</div>
                
                <div class="car-detail-meta">
                    <div class="meta-item">
                        <span>📍</span>
                        <span>${car.location || 'N/A'}</span>
                    </div>
                    <div class="meta-item">
                        <span>⛽</span>
                        <span>${car.fuel_type}</span>
                    </div>
                    <div class="meta-item">
                        <span>🔧</span>
                        <span>${car.transmission}</span>
                    </div>
                    <div class="meta-item">
                        <span>📊</span>
                        <span>${car.mileage ? car.mileage.toLocaleString() : 'N/A'} miles</span>
                    </div>
                    <div class="meta-item">
                        <span>🎨</span>
                        <span>${car.color || 'N/A'}</span>
                    </div>
                    <div class="meta-item">
                        <span>✓</span>
                        <span>Used${car.engine_condition ? ` • Engine: ${car.engine_condition.charAt(0).toUpperCase() + car.engine_condition.slice(1)}` : ''}</span>
                    </div>
                </div>
                
                ${scores.overall_score ? `
                    <div style="margin-bottom: 1rem;">
                        <strong>Overall Score:</strong> 
                        <span style="font-size: 1.5rem; color: #2563eb; font-weight: 700;">${scores.overall_score.toFixed(1)}/10</span>
                    </div>
                ` : ''}
                
                ${car.description ? `
                    <div style="margin-top: 1.5rem;">
                        <h3>Description</h3>
                        <p style="color: #6b7280; line-height: 1.8;">${car.description}</p>
                    </div>
                ` : ''}
            </div>
        </div>
        
        ${specs.horsepower || specs.engine_size ? `
            <div>
                <h2 style="margin-bottom: 1rem;">Specifications</h2>
                <div class="specs-grid">
                    ${specs.engine_size ? `
                        <div class="spec-item">
                            <label>Engine Size</label>
                            <div class="spec-value">${specs.engine_size}L</div>
                        </div>
                    ` : ''}
                    ${specs.horsepower ? `
                        <div class="spec-item">
                            <label>Horsepower</label>
                            <div class="spec-value">${specs.horsepower} HP</div>
                        </div>
                    ` : ''}
                    ${specs.torque ? `
                        <div class="spec-item">
                            <label>Torque</label>
                            <div class="spec-value">${specs.torque} lb-ft</div>
                        </div>
                    ` : ''}
                    ${specs.acceleration_0_60 ? `
                        <div class="spec-item">
                            <label>0-60 mph</label>
                            <div class="spec-value">${specs.acceleration_0_60}s</div>
                        </div>
                    ` : ''}
                    ${specs.mpg_city && specs.mpg_highway ? `
                        <div class="spec-item">
                            <label>MPG</label>
                            <div class="spec-value">${specs.mpg_city}/${specs.mpg_highway} city/hwy</div>
                        </div>
                    ` : ''}
                    ${specs.drivetrain ? `
                        <div class="spec-item">
                            <label>Drivetrain</label>
                            <div class="spec-value">${specs.drivetrain}</div>
                        </div>
                    ` : ''}
                    ${specs.seating_capacity ? `
                        <div class="spec-item">
                            <label>Seating</label>
                            <div class="spec-value">${specs.seating_capacity} seats</div>
                        </div>
                    ` : ''}
                    ${specs.doors ? `
                        <div class="spec-item">
                            <label>Doors</label>
                            <div class="spec-value">${specs.doors}</div>
                        </div>
                    ` : ''}
                </div>
            </div>
        ` : ''}
        
        ${scores.reliability_score || scores.safety_score ? `
            <div style="margin-top: 2rem;">
                <h2 style="margin-bottom: 1rem;">Scores & Ratings</h2>
                <div class="specs-grid">
                    ${scores.reliability_score ? `
                        <div class="spec-item">
                            <label>Reliability Score</label>
                            <div class="spec-value">${scores.reliability_score.toFixed(1)}/10</div>
                        </div>
                    ` : ''}
                    ${scores.safety_score ? `
                        <div class="spec-item">
                            <label>Safety Score</label>
                            <div class="spec-value">${scores.safety_score.toFixed(1)}/10</div>
                        </div>
                    ` : ''}
                    ${scores.crash_test_rating ? `
                        <div class="spec-item">
                            <label>Crash Test Rating</label>
                            <div class="spec-value">${scores.crash_test_rating}</div>
                        </div>
                    ` : ''}
                </div>
            </div>
        ` : ''}
        
        <div style="margin-top: 2rem; display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
            <a href="listings.html" class="btn btn-secondary">Back to Listings</a>
            ${typeof isInCompare !== 'undefined' ? `
                <button class="compare-btn ${isInCompare(car.id) ? 'in-compare' : ''}" 
                        onclick="if(isInCompare(${car.id})) { removeFromCompare(${car.id}); this.classList.remove('in-compare'); this.textContent='Compare'; } else { if(addToCompare(${car.id})) { this.classList.add('in-compare'); this.textContent='Remove from Compare'; } }">
                    ${isInCompare(car.id) ? 'Remove from Compare' : 'Compare'}
                </button>
            ` : ''}
            <div id="adminButtonsContainer" style="display: none; gap: 1rem;">
                <button class="btn btn-primary" onclick="editCarPrice(${car.id}); return false;" style="background-color: #059669;">
                    ✏️ Edit Price
                </button>
                <button class="btn btn-primary" onclick="deleteCar(${car.id}); return false;" style="background-color: #dc2626;">
                    🗑️ Delete Car
                </button>
            </div>
        </div>
        
        <div id="reviewsContainer" style="margin-top: 3rem;"></div>
        
        <!-- Predictions Section -->
        <div id="predictionsContainer" style="margin-top: 3rem;">
            <h2 style="margin-bottom: 1.5rem;">💰 Cost & Value Predictions</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 2rem;">
                <div id="ownershipCostContainer"></div>
                <div id="futureValueContainer"></div>
            </div>
        </div>
        
        <!-- Personalized Recommendations Section -->
        <div id="recommendationsSection" style="margin-top: 4rem; padding: 3rem 0; border-top: 2px solid #e5e7eb; background-color: #f9fafb;">
            <div class="container" style="max-width: 1200px; margin: 0 auto; padding: 0 20px;">
                <h2 style="text-align: center; margin-bottom: 1rem; color: #1f2937; font-size: 2rem; font-weight: 700;">✨ Personalized Recommendations</h2>
                <p style="text-align: center; color: #6b7280; margin-bottom: 2rem; font-size: 1rem;">Cars you might like based on this listing</p>
                <div id="recommendationsContainer">
                    <div class="loading" style="text-align: center; padding: 2rem;">
                        <p>Loading recommendations...</p>
                    </div>
                </div>
            </div>
        </div>
    `;
    } catch (templateError) {
        console.error('[DEBUG] displayCarDetail: Error generating HTML template:', templateError);
        showError('Error displaying car details. Please try again.');
        return;
    }
    
    // Add favorite button after rendering
    setTimeout(function() {
        const favoriteContainer = document.getElementById('favoriteButtonContainer');
        if (favoriteContainer) {
            const createFn = window.createFavoriteButton || createFavoriteButton;
            if (typeof createFn === 'function') {
                const favoriteBtn = createFn(car.id);
                favoriteContainer.appendChild(favoriteBtn);
            } else {
                // Retry after a delay
                setTimeout(() => {
                    const createFn = window.createFavoriteButton || createFavoriteButton;
                    if (typeof createFn === 'function') {
                        const favoriteBtn = createFn(car.id);
                        favoriteContainer.appendChild(favoriteBtn);
                    }
                }, 500);
            }
        }
    }, 100);
    
    // Show admin buttons if user is admin
    checkAndShowAdminButtonsCarDetail();
    
    // Load reviews
    if (typeof displayReviews !== 'undefined') {
        displayReviews(car.id, 'reviewsContainer');
    }
    
    // Load predictions
    loadPredictions(car.id);
    
    // Load recommendations based on current car
    loadCarRecommendations(car.id);
    
    // Update global chatbot context for this car
    if (typeof updateChatbotContext !== 'undefined') {
        updateChatbotContext(car.id);
    }
}

/**
 * Check and show admin buttons on car detail page
 */
async function checkAndShowAdminButtonsCarDetail() {
    const adminButtonsContainer = document.getElementById('adminButtonsContainer');
    if (!adminButtonsContainer) {
        console.log('[Admin] Admin buttons container not found');
        return;
    }
    
    // Check if userIsAdmin is already set
    if (typeof window.userIsAdmin !== 'undefined') {
        console.log('[Admin] Using cached admin status:', window.userIsAdmin);
        adminButtonsContainer.style.display = window.userIsAdmin ? 'flex' : 'none';
        return;
    }
    
    // If not set, check admin status directly
    console.log('[Admin] Checking admin status for car detail...');
    const token = localStorage.getItem('auth_token');
    if (!token) {
        console.log('[Admin] No token found, hiding admin buttons');
        adminButtonsContainer.style.display = 'none';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const user = await response.json();
            const isAdmin = user.is_admin === true;
            window.userIsAdmin = isAdmin;
            console.log('[Admin] User is admin?', isAdmin);
            adminButtonsContainer.style.display = isAdmin ? 'flex' : 'none';
        } else {
            console.log('[Admin] Failed to get user info');
            adminButtonsContainer.style.display = 'none';
        }
    } catch (error) {
        console.error('[Admin] Error checking admin status:', error);
        adminButtonsContainer.style.display = 'none';
    }
}

/**
 * Admin functions for car management
 */
async function editCarPrice(carId) {
    const currentPrice = parseFloat(prompt('Enter new price:'));
    if (!currentPrice || isNaN(currentPrice) || currentPrice < 0) {
        alert('Invalid price entered');
        return;
    }
    
    const token = localStorage.getItem('auth_token');
    if (!token) {
        alert('Please login as admin');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/cars/${carId}/price?new_price=${currentPrice}`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to update price');
        }
        
        const updatedCar = await response.json();
        
        // Update price in UI without full reload to preserve images
        const priceElement = document.querySelector('.car-detail-price');
        if (priceElement) {
            priceElement.textContent = `$${updatedCar.price.toLocaleString()}`;
        }
        
        if (typeof window.showNotification === 'function') {
            window.showNotification(`Price updated successfully to $${updatedCar.price.toLocaleString()}`, 'success');
        } else {
            alert(`Price updated successfully to $${updatedCar.price.toLocaleString()}`);
        }
        
        // Don't reload the page - just update the price to preserve images
        // Images are preserved on backend, so no need to reload
    } catch (error) {
        console.error('[Admin] Error updating price:', error);
        alert('Error: ' + error.message);
    }
}

async function deleteCar(carId) {
    if (!confirm('Are you sure you want to delete this car? This action cannot be undone.')) {
        return;
    }
    
    const token = localStorage.getItem('auth_token');
    if (!token) {
        alert('Please login as admin');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/cars/${carId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to delete car');
        }
        
        alert('Car deleted successfully!');
        // Redirect to listings
        window.location.href = 'listings.html';
    } catch (error) {
        console.error('[Admin] Error deleting car:', error);
        alert('Error: ' + error.message);
    }
}

/**
 * Load similar cars using AI vector search
 */
async function loadSimilarCars(carId) {
    console.log('[DEBUG] loadSimilarCars: Loading similar cars for car', carId);
    
    const container = document.getElementById('similarCarsContainer');
    if (!container) {
        return;
    }
    
    try {
        const url = `${API_BASE_URL}/api/v1/ai/cars/${carId}/similar?n_results=3`;
        const response = await fetch(url);
        
        if (!response.ok) {
            // If embeddings not available, don't show error, just hide section
            if (response.status === 500 || response.status === 404) {
                console.log('[DEBUG] loadSimilarCars: Similar cars not available (embeddings may not be generated)');
                return;
            }
            throw new Error('Failed to load similar cars');
        }
        
        const data = await response.json();
        const similarCars = data.similar_cars || [];
        
        if (similarCars.length === 0) {
            return;
        }
        
        // Fetch full car details for similar cars
        const carPromises = similarCars.map(sc => 
            fetch(`${API_BASE_URL}/api/v1/cars/${sc.car_id}`).then(r => r.json())
        );
        const cars = await Promise.all(carPromises);
        
        // Build HTML
        let html = `
            <div class="similar-cars-section">
                <h2>🤖 Similar Cars (AI-Powered)</h2>
                <div class="similar-cars-grid">
        `;
        
        cars.forEach((car, index) => {
            // Skip if car data is incomplete
            if (!car || !car.id || !car.make || !car.model) {
                console.warn('[DEBUG] loadSimilarCars: Skipping incomplete car data:', car);
                return;
            }
            
            const similarity = similarCars[index];
            const imageUrl = car.image_urls && car.image_urls.length > 0 
                ? car.image_urls[0].replace(/ /g, '%20')
                : 'images/2023-Toyota-Camry.webp';
            
            html += `
                <div class="similar-car-card" onclick="window.location.href='car-detail.html?id=${car.id}'">
                    <img src="${imageUrl}" alt="${car.make} ${car.model}" 
                         style="width: 100%; height: 180px; object-fit: cover; border-radius: 0.5rem; margin-bottom: 0.5rem;"
                         onerror="this.src='images/2023-Toyota-Camry.webp'">
                    <h4>${car.year || ''} ${car.make} ${car.model}</h4>
                    <p style="color: #2563eb; font-weight: 600; margin: 0.5rem 0;">$${(car.price || 0).toLocaleString()}</p>
                    <div class="similarity-score">
                        ${similarity && similarity.distance !== null ? `Similarity: ${(100 - (similarity.distance * 100)).toFixed(0)}%` : 'Similar car'}
                    </div>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
        
        container.innerHTML = html;
        console.log('[DEBUG] loadSimilarCars: Similar cars displayed');
    } catch (error) {
        console.error('[DEBUG] loadSimilarCars: Error', error);
        // Don't show error, just don't display similar cars
    }
}

/**
 * Load recommendations based on the current car being viewed
 */
async function loadCarRecommendations(carId) {
    console.log('[DEBUG] loadCarRecommendations: Loading recommendations for car', carId);
    
    const container = document.getElementById('recommendationsContainer');
    const section = document.getElementById('recommendationsSection');
    
    if (!container || !section) {
        console.log('[DEBUG] loadCarRecommendations: Container or section not found');
        return;
    }
    
    // Show loading state
    container.innerHTML = '<div class="loading" style="text-align: center; padding: 2rem;"><p>Loading recommendations...</p></div>';
    section.style.display = 'block'; // Ensure section is visible
    
    try {
        // First, try to get similar cars using the AI endpoint (non-blocking)
        let similarCars = [];
        try {
            const similarUrl = `${API_BASE_URL}/api/v1/ai/cars/${carId}/similar?n_results=3`;
            console.log('[DEBUG] loadCarRecommendations: Fetching similar cars from', similarUrl);
            const similarResponse = await fetch(similarUrl);
            
            if (similarResponse.ok) {
                const similarData = await similarResponse.json();
                similarCars = similarData.similar_cars || [];
                console.log('[DEBUG] loadCarRecommendations: Found', similarCars.length, 'similar cars');
            } else {
                console.log('[DEBUG] loadCarRecommendations: Similar cars endpoint returned', similarResponse.status, '- will use fallback');
            }
        } catch (similarError) {
            console.log('[DEBUG] loadCarRecommendations: Similar cars error (will use fallback):', similarError);
        }
        
        // If we have similar cars, try to display them
        if (similarCars.length > 0) {
            try {
                // Filter out invalid car IDs before fetching
                const validSimilarCars = similarCars.filter(sc => sc.car_id && sc.car_id > 0 && sc.car_id !== carId);
                console.log('[DEBUG] loadCarRecommendations: Filtered to', validSimilarCars.length, 'valid similar cars (excluding current car and invalid IDs)');
                
                // Fetch full car details for similar cars
                const carPromises = validSimilarCars.map(sc => 
                    fetch(`${API_BASE_URL}/api/v1/cars/${sc.car_id}`).then(r => {
                        if (!r.ok) {
                            if (r.status === 404) {
                                console.warn(`[DEBUG] loadCarRecommendations: Car ${sc.car_id} not found (404) - skipping`);
                            }
                            return null; // Return null instead of throwing
                        }
                        return r.json();
                    }).catch(err => {
                        console.warn(`[DEBUG] loadCarRecommendations: Error fetching car ${sc.car_id}:`, err);
                        return null;
                    })
                );
                const cars = (await Promise.all(carPromises)).filter(car => car !== null); // Filter out nulls
                console.log('[DEBUG] loadCarRecommendations: Fetched', cars.length, 'car details');
                
                // Display as recommendations - ensure exactly 3 cars
                if (cars.length >= 3 && typeof displayRecommendations === 'function') {
                    const recommendations = cars.slice(0, 3).map((car, index) => ({
                        car_id: car.id,
                        make: car.make,
                        model: car.model,
                        year: car.year,
                        price: car.price,
                        fuel_type: car.fuel_type,
                        transmission: car.transmission,
                        mileage: car.mileage,
                        image_urls: car.image_urls || [],
                        similarity_score: validSimilarCars[index]?.distance ? (100 - (validSimilarCars[index].distance * 100)) : null,
                        recommendation_reason: `Similar to this ${car.make} ${car.model}`
                    }));
                    
                    displayRecommendations(container, recommendations, null);
                    console.log('[DEBUG] loadCarRecommendations: Similar cars displayed as recommendations');
                    return;
                } else if (cars.length > 0 && cars.length < 3) {
                    console.log('[DEBUG] loadCarRecommendations: Only', cars.length, 'similar cars found, using fallback to get more');
                } else {
                    console.warn('[DEBUG] loadCarRecommendations: displayRecommendations function not available or not enough cars, will use fallback');
                }
            } catch (fetchError) {
                console.error('[DEBUG] loadCarRecommendations: Error fetching car details:', fetchError);
                // Continue to fallback
            }
        }
        
        // Fallback: Get all cars except current one and show them as recommendations
        console.log('[DEBUG] loadCarRecommendations: Using fallback - fetching all cars');
        try {
            const allCarsResponse = await fetch(`${API_BASE_URL}/api/v1/cars?page=1&page_size=10`);
            
            if (!allCarsResponse.ok) {
                throw new Error(`Failed to fetch cars: ${allCarsResponse.status}`);
            }
            
            const allCarsData = await allCarsResponse.json();
            const allCars = allCarsData.cars || [];
            console.log('[DEBUG] loadCarRecommendations: Fetched', allCars.length, 'total cars');
            
            // Filter out current car and get exactly 3 others
            const otherCars = allCars.filter(car => car.id !== carId).slice(0, 3);
            console.log('[DEBUG] loadCarRecommendations: Found', otherCars.length, 'other cars to display');
            
            if (otherCars.length < 3) {
                container.innerHTML = '<p style="text-align: center; color: #6b7280; padding: 2rem;">Not enough cars available for recommendations at this time. <a href="listings.html" style="color: #2563eb; text-decoration: underline;">Browse all cars</a> to explore our inventory.</p>';
                return;
            }
            
            // Display as recommendations - use displayRecommendations if available, otherwise create cards manually
            // Ensure exactly 3 cars
            if (typeof displayRecommendations === 'function') {
                const recommendations = otherCars.slice(0, 3).map(car => ({
                    car_id: car.id,
                    make: car.make,
                    model: car.model,
                    year: car.year,
                    price: car.price,
                    fuel_type: car.fuel_type,
                    transmission: car.transmission,
                    mileage: car.mileage,
                    image_urls: car.image_urls || [],
                    similarity_score: null,
                    recommendation_reason: 'Other available listings'
                }));
                
                displayRecommendations(container, recommendations, null);
                console.log('[DEBUG] loadCarRecommendations: Fallback cars displayed as recommendations');
            } else {
                // Manual display if displayRecommendations is not available
                console.log('[DEBUG] loadCarRecommendations: displayRecommendations not available, creating cards manually');
                let html = '<div class="recommendations-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.5rem; margin-top: 1rem;">';
                
                otherCars.slice(0, 3).forEach(car => {
                    const imageUrl = (car.image_urls && car.image_urls.length > 0) 
                        ? (car.image_urls[0].startsWith('images/') ? car.image_urls[0].replace(/ /g, '%20') : car.image_urls[0])
                        : 'images/2023-Toyota-Camry.webp';
                    
                    html += `
                        <div class="car-card" style="background: white; border-radius: 0.5rem; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); cursor: pointer; transition: transform 0.2s;" onclick="window.location.href='car-detail.html?id=${car.id}'">
                            <div class="car-image" style="width: 100%; height: 200px; overflow: hidden;">
                                <img src="${imageUrl}" alt="${car.make} ${car.model}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.src='https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=800'">
                            </div>
                            <div class="car-info" style="padding: 1rem;">
                                <h3 style="margin: 0 0 0.5rem 0; font-size: 1.1rem; color: #1f2937;">${car.year} ${car.make} ${car.model}</h3>
                                <p style="margin: 0 0 0.5rem 0; font-size: 1.25rem; font-weight: 700; color: #2563eb;">$${car.price.toLocaleString()}</p>
                                <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; font-size: 0.875rem; color: #6b7280;">
                                    <span>📊 ${car.mileage.toLocaleString()} mi</span>
                                    <span>⛽ ${car.fuel_type}</span>
                                    <span>🔧 ${car.transmission}</span>
                                </div>
                            </div>
                        </div>
                    `;
                });
                
                html += '</div>';
                container.innerHTML = html;
                console.log('[DEBUG] loadCarRecommendations: Manual cards created');
            }
        } catch (fallbackError) {
            console.error('[DEBUG] loadCarRecommendations: Fallback error:', fallbackError);
            // Last resort: Try general recommendations API
            if (typeof loadRecommendations === 'function') {
                console.log('[DEBUG] loadCarRecommendations: Trying general recommendations API as last resort');
                try {
                    await loadRecommendations('recommendationsContainer', 3);
                    console.log('[DEBUG] loadCarRecommendations: General recommendations loaded');
                    return;
                } catch (recError) {
                    console.error('[DEBUG] loadCarRecommendations: General recommendations error:', recError);
                }
            }
            // Final fallback message
            container.innerHTML = '<p style="text-align: center; color: #6b7280; padding: 2rem;">Unable to load recommendations at this time. <a href="listings.html" style="color: #2563eb; text-decoration: underline;">Browse all cars</a> to explore our inventory.</p>';
        }
        
    } catch (error) {
        console.error('[DEBUG] loadCarRecommendations: Unexpected error', error);
        // Try one more time with a simple fetch
        try {
            const simpleResponse = await fetch(`${API_BASE_URL}/api/v1/cars?page=1&page_size=10`);
            if (simpleResponse.ok) {
                const data = await simpleResponse.json();
                const cars = (data.cars || []).filter(c => c.id !== carId).slice(0, 3);
                
                if (cars.length < 3) {
                    container.innerHTML = '<p style="text-align: center; color: #6b7280; padding: 2rem;">Not enough cars available for recommendations at this time.</p>';
                    return;
                }
                if (cars.length > 0) {
                    // Create cards manually
                    let html = '<div class="recommendations-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.5rem; margin-top: 1rem;">';
                    cars.forEach(car => {
                        const imageUrl = (car.image_urls && car.image_urls.length > 0) 
                            ? (car.image_urls[0].startsWith('images/') ? car.image_urls[0].replace(/ /g, '%20') : car.image_urls[0])
                            : 'images/2023-Toyota-Camry.webp';
                        html += `
                            <div class="car-card" style="background: white; border-radius: 0.5rem; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); cursor: pointer;" onclick="window.location.href='car-detail.html?id=${car.id}'">
                                <div style="width: 100%; height: 200px; overflow: hidden;">
                                    <img src="${imageUrl}" alt="${car.make} ${car.model}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.src='https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=800'">
                                </div>
                                <div style="padding: 1rem;">
                                    <h3 style="margin: 0 0 0.5rem 0; font-size: 1.1rem; color: #1f2937;">${car.year} ${car.make} ${car.model}</h3>
                                    <p style="margin: 0 0 0.5rem 0; font-size: 1.25rem; font-weight: 700; color: #2563eb;">$${car.price.toLocaleString()}</p>
                                    <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; font-size: 0.875rem; color: #6b7280;">
                                        <span>📊 ${car.mileage.toLocaleString()} mi</span>
                                        <span>⛽ ${car.fuel_type}</span>
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                    html += '</div>';
                    container.innerHTML = html;
                    return;
                }
            }
        } catch (finalError) {
            console.error('[DEBUG] loadCarRecommendations: Final fallback error:', finalError);
        }
        // Show helpful message with link instead of error
        container.innerHTML = '<p style="text-align: center; color: #6b7280; padding: 2rem;">Unable to load recommendations at this time. <a href="listings.html" style="color: #2563eb; text-decoration: underline;">Browse all cars</a> to explore our inventory.</p>';
    }
}

/**
 * Load predictions (ownership cost and future value)
 */
async function loadPredictions(carId) {
    console.log('[DEBUG] loadPredictions: Loading predictions for car', carId);
    
    const ownershipCostContainer = document.getElementById('ownershipCostContainer');
    const futureValueContainer = document.getElementById('futureValueContainer');
    
    if (!ownershipCostContainer || !futureValueContainer) {
        console.error('[DEBUG] loadPredictions: Containers not found');
        return;
    }
    
    // Load ownership cost
    try {
        if (typeof loadOwnershipCost === 'function') {
            const costData = await loadOwnershipCost(carId, 5, 12000);
            if (typeof displayOwnershipCost === 'function') {
                displayOwnershipCost(ownershipCostContainer, costData);
            }
        } else {
            console.warn('[DEBUG] loadPredictions: loadOwnershipCost function not available');
        }
    } catch (error) {
        console.error('[DEBUG] loadPredictions: Error loading ownership cost', error);
        ownershipCostContainer.innerHTML = '<p style="color: #6b7280;">Unable to calculate ownership cost.</p>';
    }
    
    // Load future value
    try {
        if (typeof loadFutureValue === 'function') {
            const valueData = await loadFutureValue(carId, 5);
            if (typeof displayFutureValue === 'function') {
                displayFutureValue(futureValueContainer, valueData);
            }
        } else {
            console.warn('[DEBUG] loadPredictions: loadFutureValue function not available');
        }
    } catch (error) {
        console.error('[DEBUG] loadPredictions: Error loading future value', error);
        futureValueContainer.innerHTML = '<p style="color: #6b7280;">Unable to calculate future value.</p>';
    }
}

/**
 * Change main image when gallery thumbnail is clicked
 */
function changeMainImage(imageUrl) {
    const mainImage = document.getElementById('mainCarImage');
    if (mainImage) {
        mainImage.src = imageUrl;
        
        // Update active thumbnail
        document.querySelectorAll('.gallery-thumb').forEach(thumb => {
            thumb.classList.remove('active');
            if (thumb.src === imageUrl || thumb.src.includes(imageUrl.split('/').pop())) {
                thumb.classList.add('active');
            }
        });
    }
}

/**
 * Show error message
 */
function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

