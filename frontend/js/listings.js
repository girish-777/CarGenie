/**
 * Car listings JavaScript
 */

// Get API_BASE_URL from window.BACKEND_URL or window.API_BASE_URL
var API_BASE_URL = window.BACKEND_URL || window.API_BASE_URL;

// If still undefined, use fallback
if (!API_BASE_URL) {
    // Check if we're on Render
    const isRender = window.location.hostname.includes('onrender.com');
    if (isRender) {
        // Try to construct backend URL from frontend name
        const frontendName = window.location.hostname.split('.')[0];
        const backendName = frontendName.replace('-frontend', '-backend');
        API_BASE_URL = `https://${backendName}.onrender.com`;
        console.warn('API_BASE_URL not set, using constructed URL:', API_BASE_URL);
    } else {
        // Local development
        API_BASE_URL = 'http://localhost:8000';
        console.warn('API_BASE_URL not set, using localhost:', API_BASE_URL);
    }
}

window.API_BASE_URL = API_BASE_URL;
console.log('[DEBUG] listings.js: API_BASE_URL set to:', API_BASE_URL);

// Make variables globally available for inline script
window.currentPage = 1;
window.currentFilters = {};
let currentPage = window.currentPage;
let currentFilters = window.currentFilters;

console.log('[DEBUG] listings.js: Script loading, variables initialized');

// Simple search function - override the inline version with full implementation
window.handleSearch = function handleSearch() {
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) {
        console.error('Search input not found');
        return;
    }
    
    const searchTerm = searchInput.value.trim();
    console.log('handleSearch called with:', searchTerm);
    
    // Use local variables, sync to window
    currentFilters.search = searchTerm || null;
    window.currentFilters = currentFilters;
    currentPage = 1;
    window.currentPage = currentPage;
    
    // Call loadCars (should be available by now)
    loadCars(currentPage);
};

// Load favorites.js if not already loaded
if (typeof createFavoriteButton === 'undefined') {
    const script = document.createElement('script');
    script.src = 'js/favorites.js';
    document.head.appendChild(script);
}

if (typeof isInCompare === 'undefined') {
    const script = document.createElement('script');
    script.src = 'js/compare.js';
    document.head.appendChild(script);
}

// Admin functions - Add Car feature removed
async function checkAndShowAdminButtons() {
    // Add Car button functionality removed
    // This function kept for potential future admin features
}

// Check admin status when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Try immediately first
    checkAndShowAdminButtons();
    // Also check after a delay in case main.js is still loading
    setTimeout(checkAndShowAdminButtons, 500);
    setTimeout(checkAndShowAdminButtons, 1000);
});

// Add Car feature removed

// Load cars on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('[DEBUG] DOMContentLoaded: Starting initialization');
    
    // Load makes and fuel types
    loadMakes();
    loadFuelTypes();
    
    // Load cars
    loadCars();
    
    // Add Enter key support
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                handleSearch();
            }
        });
    }
    
    // Also try loading makes after a short delay in case DOM wasn't ready
    setTimeout(function() {
        const makeSelect = document.getElementById('makeFilter');
        if (makeSelect && makeSelect.children.length <= 1) {
            console.log('[DEBUG] Retrying loadMakes after delay');
            loadMakes();
        }
    }, 500);
});


/**
 * Load list of makes for filter dropdown
 */
async function loadMakes() {
    console.log('[DEBUG] loadMakes: Starting to load makes');
    const makeSelect = document.getElementById('makeFilter');
    if (!makeSelect) {
        console.error('[DEBUG] loadMakes: makeFilter element not found');
        // Try again after a short delay
        setTimeout(loadMakes, 100);
        return;
    }
    
    try {
        const url = `${API_BASE_URL}/api/v1/cars/makes/list`;
        console.log('[DEBUG] loadMakes: Fetching from', url);
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const makes = await response.json();
        console.log('[DEBUG] loadMakes: Received makes', makes);
        
        // Clear existing options except "All Makes"
        while (makeSelect.children.length > 1) {
            makeSelect.removeChild(makeSelect.lastChild);
        }
        
        // Add makes to dropdown
        if (makes && makes.length > 0) {
            makes.forEach(make => {
                const option = document.createElement('option');
                option.value = make;
                option.textContent = make;
                makeSelect.appendChild(option);
            });
            console.log('[DEBUG] loadMakes: Added', makes.length, 'makes to dropdown');
        } else {
            console.warn('[DEBUG] loadMakes: No makes received, using fallback');
            // Fallback: use only Toyota, BMW, Kia, Ford, Mercedes-Benz
            const fallbackMakes = ['Toyota', 'BMW', 'Kia', 'Ford', 'Mercedes-Benz'];
            fallbackMakes.forEach(make => {
                const option = document.createElement('option');
                option.value = make;
                option.textContent = make;
                makeSelect.appendChild(option);
            });
        }
        
        // Filter to only show allowed makes (Toyota, BMW, Kia, Ford, Mercedes-Benz) even if API returns more
        const allowedMakes = ['Toyota', 'BMW', 'Kia', 'Ford', 'Mercedes-Benz'];
        const options = Array.from(makeSelect.options);
        options.forEach(option => {
            if (option.value && !allowedMakes.includes(option.value)) {
                makeSelect.removeChild(option);
            }
        });
    } catch (error) {
        console.error('[DEBUG] loadMakes: Error loading makes:', error);
        // Fallback: use only Toyota, BMW, Kia, Ford, Mercedes-Benz if API fails
        console.log('[DEBUG] loadMakes: Using fallback makes list');
        const fallbackMakes = ['Toyota', 'BMW', 'Kia', 'Ford', 'Mercedes-Benz'];
        fallbackMakes.forEach(make => {
            const option = document.createElement('option');
            option.value = make;
            option.textContent = make;
            makeSelect.appendChild(option);
        });
    }
}

// Make it globally available
window.loadMakes = loadMakes;

/**
 * Load list of fuel types for filter dropdown
 */
async function loadFuelTypes() {
    console.log('[DEBUG] loadFuelTypes: Starting to load fuel types');
    const fuelSelect = document.getElementById('fuelTypeFilter');
    if (!fuelSelect) {
        console.error('[DEBUG] loadFuelTypes: fuelTypeFilter element not found');
        // Try again after a short delay
        setTimeout(loadFuelTypes, 100);
        return;
    }
    
    try {
        const url = `${API_BASE_URL}/api/v1/cars/fuel-types/list`;
        console.log('[DEBUG] loadFuelTypes: Fetching from', url);
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const fuelTypes = await response.json();
        console.log('[DEBUG] loadFuelTypes: Received fuel types', fuelTypes);
        
        // Clear existing options except "All Types"
        while (fuelSelect.children.length > 1) {
            fuelSelect.removeChild(fuelSelect.lastChild);
        }
        
        // Add fuel types to dropdown
        if (fuelTypes && fuelTypes.length > 0) {
            fuelTypes.forEach(type => {
                const option = document.createElement('option');
                option.value = type;
                option.textContent = type.charAt(0).toUpperCase() + type.slice(1);
                fuelSelect.appendChild(option);
            });
            console.log('[DEBUG] loadFuelTypes: Added', fuelTypes.length, 'fuel types to dropdown');
        } else {
            console.warn('[DEBUG] loadFuelTypes: No fuel types received, using fallback');
            // Fallback: use only gasoline and electric
            const fallbackTypes = ['gasoline', 'electric'];
            fallbackTypes.forEach(type => {
                const option = document.createElement('option');
                option.value = type;
                option.textContent = type.charAt(0).toUpperCase() + type.slice(1);
                fuelSelect.appendChild(option);
            });
        }
        
        // Filter to only show gasoline and electric (even if API returns more)
        const allowedTypes = ['gasoline', 'electric'];
        const options = Array.from(fuelSelect.options);
        options.forEach(option => {
            if (option.value && !allowedTypes.includes(option.value.toLowerCase())) {
                fuelSelect.removeChild(option);
            }
        });
    } catch (error) {
        console.error('[DEBUG] loadFuelTypes: Error loading fuel types:', error);
        // Fallback: use only gasoline and electric if API fails
        console.log('[DEBUG] loadFuelTypes: Using fallback fuel types list');
        const fallbackTypes = ['gasoline', 'electric'];
        fallbackTypes.forEach(type => {
            const option = document.createElement('option');
            option.value = type;
            option.textContent = type.charAt(0).toUpperCase() + type.slice(1);
            fuelSelect.appendChild(option);
        });
    }
}

// Make it globally available
window.loadFuelTypes = loadFuelTypes;

/**
 * Load cars from API
 */
async function loadCars(page = 1) {
    // Use global variables if available
    if (window.currentFilters) {
        currentFilters = window.currentFilters;
    }
    console.log('[DEBUG] loadCars: Starting to load cars, page:', page);
    console.log('[DEBUG] loadCars: Current filters:', currentFilters);
    
    // Make sure we're using the right variables
    if (window.currentFilters && !currentFilters.search && window.currentFilters.search) {
        currentFilters = window.currentFilters;
    }
    
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorMessage = document.getElementById('errorMessage');
    const carsGrid = document.getElementById('carsGrid');
    
    if (!loadingIndicator || !errorMessage || !carsGrid) {
        console.error('[DEBUG] loadCars: Required DOM elements not found');
        return;
    }
    
    loadingIndicator.style.display = 'block';
    errorMessage.style.display = 'none';
    carsGrid.innerHTML = '';
    
    try {
        // Build query parameters
        const params = new URLSearchParams({
            page: page.toString(),
            page_size: '12'
        });
        
        // Add filters
        if (currentFilters.search && typeof currentFilters.search === 'string' && currentFilters.search.trim() !== '') {
            const searchValue = currentFilters.search.trim();
            params.append('search', searchValue);
            console.log('[DEBUG] loadCars: Adding search parameter:', searchValue);
        } else {
            console.log('[DEBUG] loadCars: No search parameter (search is empty or null)');
        }
        if (currentFilters.make) params.append('make', currentFilters.make);
        if (currentFilters.fuel_type) params.append('fuel_type', currentFilters.fuel_type);
        if (currentFilters.transmission) params.append('transmission', currentFilters.transmission);
        if (currentFilters.condition) params.append('condition', currentFilters.condition);
        if (currentFilters.min_price) params.append('min_price', currentFilters.min_price);
        if (currentFilters.max_price) params.append('max_price', currentFilters.max_price);
        if (currentFilters.min_year) params.append('min_year', currentFilters.min_year);
        if (currentFilters.max_year) params.append('max_year', currentFilters.max_year);
        if (currentFilters.sort_by) params.append('sort_by', currentFilters.sort_by);
        if (currentFilters.sort_order) params.append('sort_order', currentFilters.sort_order);
        
        if (!API_BASE_URL) {
            throw new Error('API_BASE_URL is not set. Please check BACKEND_URL configuration.');
        }
        
        const url = `${API_BASE_URL}/api/v1/cars/?${params}`;
        console.log('[DEBUG] loadCars: Fetching from', url);
        console.log('[DEBUG] loadCars: API_BASE_URL =', API_BASE_URL);
        console.log('[DEBUG] loadCars: Query params', params.toString());
        
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        console.log('[DEBUG] loadCars: Response status', response.status, response.statusText);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('[DEBUG] loadCars: Response not OK:', errorText);
            throw new Error('Failed to load cars');
        }
        
        const data = await response.json();
        console.log('[DEBUG] loadCars: Received data:', {
            total: data.total,
            page: data.page,
            page_size: data.page_size,
            total_pages: data.total_pages,
            cars_count: data.cars.length
        });
        
        if (data.cars.length > 0) {
            console.log('[DEBUG] loadCars: First car:', {
                id: data.cars[0].id,
                make: data.cars[0].make,
                model: data.cars[0].model,
                image_urls: data.cars[0].image_urls
            });
        }
        
        // Display cars
        if (data.cars.length === 0) {
            console.log('[DEBUG] loadCars: No cars found, showing empty message');
            const searchTerm = currentFilters.search || '';
            const emptyMessage = searchTerm 
                ? `<p style="text-align: center; grid-column: 1 / -1; color: #6b7280; padding: 2rem;">No cars found matching "${searchTerm}". Try a different search term.</p>`
                : '<p style="text-align: center; grid-column: 1 / -1; color: #6b7280; padding: 2rem;">No cars found matching your criteria.</p>';
            carsGrid.innerHTML = emptyMessage;
            carsGrid.style.display = 'grid';
        } else {
            console.log('[DEBUG] loadCars: Creating', data.cars.length, 'car cards');
            carsGrid.style.display = 'grid';
            data.cars.forEach((car, index) => {
                console.log(`[DEBUG] loadCars: Creating card ${index + 1} for car ID ${car.id}`);
                carsGrid.appendChild(createCarCard(car));
            });
            console.log('[DEBUG] loadCars: All car cards created');
        }
        
        // Display pagination
        if (data.total_pages > 1) {
            console.log('[DEBUG] loadCars: Displaying pagination, total pages:', data.total_pages);
            displayPagination(data.page, data.total_pages);
        } else {
            console.log('[DEBUG] loadCars: No pagination needed (1 page or less)');
            document.getElementById('pagination').style.display = 'none';
        }
        
        currentPage = data.page;
        window.currentPage = currentPage; // Sync to window
        console.log('[DEBUG] loadCars: Successfully loaded cars, current page:', currentPage);
        
    } catch (error) {
        console.error('[DEBUG] loadCars: Error occurred:', error);
        errorMessage.textContent = 'Failed to load cars. Make sure the backend is running.';
        errorMessage.style.display = 'block';
    } finally {
        loadingIndicator.style.display = 'none';
        console.log('[DEBUG] loadCars: Finished loading cars');
    }
}

// Make loadCars globally available
window.loadCars = loadCars;

/**
 * Create a car card element
 */
function createCarCard(car) {
    console.log('[DEBUG] createCarCard: Creating card for car ID', car.id, car.make, car.model);
    
    const card = document.createElement('div');
    card.className = 'car-card';
    card.onclick = () => {
        console.log('[DEBUG] createCarCard: Card clicked, navigating to car detail:', car.id);
        window.location.href = `car-detail.html?id=${car.id}`;
    };
    
    // Handle image URL - encode spaces if it's a local path
    // Use first available local image as default instead of Unsplash
    let imageUrl = car.image_urls && car.image_urls.length > 0 
        ? car.image_urls[0] 
        : 'images/2023-Toyota-Camry.webp';  // Default local image
    
    // Encode spaces in local image paths
    if (imageUrl.startsWith('images/')) {
        imageUrl = imageUrl.replace(/ /g, '%20');
    }
    
    console.log('[DEBUG] createCarCard: Image URL for car', car.id, ':', imageUrl);
    
    const score = car.scores ? car.scores.overall_score : null;
    const scoreDisplay = score ? `<div class="car-score">⭐ ${score.toFixed(1)}</div>` : '';
    
    card.innerHTML = `
        <div class="car-image" style="position: relative !important;">
            <button class="favorite-btn" onclick="event.stopPropagation(); if(window.toggleFavorite) { window.toggleFavorite(${car.id}, this); } return false;" title="Add to favorites">♡</button>
            <img src="${imageUrl}" alt="${car.make} ${car.model}" 
                 onerror="console.error('Image failed to load:', '${imageUrl}'); this.src='images/2023-Toyota-Camry.webp'">
            ${scoreDisplay}
        </div>
        <div class="car-info">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <h3>${car.year} ${car.make} ${car.model}</h3>
            </div>
            <p class="car-price">$${car.price.toLocaleString()}</p>
            <div class="car-details">
                <span>📍 ${car.location || 'N/A'}</span>
                <span>⛽ ${car.fuel_type}</span>
                <span>🔧 ${car.transmission}</span>
                <span>📊 ${car.mileage ? car.mileage.toLocaleString() : 'N/A'} mi</span>
            </div>
            <p class="car-condition">Used${car.engine_condition ? ` • Engine: ${car.engine_condition.charAt(0).toUpperCase() + car.engine_condition.slice(1)}` : ''}</p>
            <div id="reviewSummary-${car.id}" class="car-reviews-summary" style="margin-top: 0.5rem; color: #6b7280; font-size: 0.875rem;">
                <span>💬 Reviews</span>
            </div>
        </div>
    `;
    
    // Update favorite button state
    const favoriteBtn = card.querySelector('.favorite-btn');
    if (favoriteBtn && typeof updateFavoriteButton !== 'undefined') {
        setTimeout(() => {
            updateFavoriteButton(car.id, favoriteBtn);
        }, 500);
    }
    
    // Add compare button to car info
    const carInfo = card.querySelector('.car-info');
    const titleDiv = carInfo.querySelector('div');
    
    // Compare button
    const compareBtn = document.createElement('button');
    compareBtn.className = 'compare-btn';
    compareBtn.textContent = isInCompare(car.id) ? 'Remove from Compare' : 'Compare';
    compareBtn.dataset.carId = car.id;
    if (isInCompare(car.id)) {
        compareBtn.classList.add('in-compare');
    }
    compareBtn.onclick = (e) => {
        e.stopPropagation();
        if (isInCompare(car.id)) {
            removeFromCompare(car.id);
            compareBtn.textContent = 'Compare';
            compareBtn.classList.remove('in-compare');
        } else {
            if (addToCompare(car.id)) {
                compareBtn.textContent = 'Remove from Compare';
                compareBtn.classList.add('in-compare');
            }
        }
    };
    
    // Add buttons container
    const buttonsContainer = document.createElement('div');
    buttonsContainer.style.cssText = 'display: flex; gap: 0.5rem; margin-top: 0.5rem;';
    buttonsContainer.appendChild(compareBtn);
    carInfo.appendChild(buttonsContainer);
    
    // Load review summary
    loadReviewSummary(car.id);
    
    return card;
}

/**
 * Display pagination controls
 */
function displayPagination(currentPage, totalPages) {
    const pagination = document.getElementById('pagination');
    pagination.style.display = 'flex';
    pagination.innerHTML = '';
    
    // Previous button
    const prevBtn = document.createElement('button');
    prevBtn.textContent = 'Previous';
    prevBtn.className = 'btn btn-secondary';
    prevBtn.disabled = currentPage === 1;
    prevBtn.onclick = () => loadCars(currentPage - 1);
    pagination.appendChild(prevBtn);
    
    // Page numbers
    const pageInfo = document.createElement('span');
    pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
    pageInfo.className = 'page-info';
    pagination.appendChild(pageInfo);
    
    // Next button
    const nextBtn = document.createElement('button');
    nextBtn.textContent = 'Next';
    nextBtn.className = 'btn btn-secondary';
    nextBtn.disabled = currentPage === totalPages;
    nextBtn.onclick = () => loadCars(currentPage + 1);
    pagination.appendChild(nextBtn);
}


/**
 * Apply filters
 */
function applyFilters() {
    console.log('[DEBUG] applyFilters: Applying filters');
    currentFilters = {
        make: document.getElementById('makeFilter').value || null,
        fuel_type: document.getElementById('fuelTypeFilter').value || null,
        transmission: document.getElementById('transmissionFilter').value || null,
        condition: document.getElementById('conditionFilter').value || null,
        min_price: document.getElementById('minPriceFilter').value || null,
        max_price: document.getElementById('maxPriceFilter').value || null,
        min_year: document.getElementById('minYearFilter').value || null,
        max_year: document.getElementById('maxYearFilter').value || null,
        sort_by: document.getElementById('sortByFilter').value || 'created_at',
        sort_order: document.getElementById('sortOrderFilter').value || 'desc',
        search: document.getElementById('searchInput').value.trim() || null
    };
    console.log('[DEBUG] applyFilters: Filters applied:', currentFilters);
    currentPage = 1;
    window.currentPage = currentPage;
    window.currentFilters = currentFilters;
    if (typeof loadCars === 'function') {
        loadCars(currentPage);
    } else if (typeof window.loadCars === 'function') {
        window.loadCars(currentPage);
    } else {
        console.error('loadCars function not available');
    }
}

// Make functions globally available
window.applyFilters = applyFilters;

/**
 * Clear all filters
 */
function clearFilters() {
    console.log('[DEBUG] clearFilters: Clearing all filters');
    document.getElementById('searchInput').value = '';
    document.getElementById('makeFilter').value = '';
    document.getElementById('fuelTypeFilter').value = '';
    document.getElementById('transmissionFilter').value = '';
    document.getElementById('conditionFilter').value = '';
    document.getElementById('minPriceFilter').value = '';
    document.getElementById('maxPriceFilter').value = '';
    document.getElementById('minYearFilter').value = '';
    document.getElementById('maxYearFilter').value = '';
    document.getElementById('sortByFilter').value = 'created_at';
    document.getElementById('sortOrderFilter').value = 'desc';
    
    currentFilters = {};
    window.currentFilters = {};
    currentPage = 1;
    window.currentPage = 1;
    console.log('[DEBUG] clearFilters: Filters cleared, reloading cars');
    if (typeof loadCars === 'function') {
        loadCars(currentPage);
    } else if (typeof window.loadCars === 'function') {
        window.loadCars(currentPage);
    } else {
        console.error('loadCars function not available');
    }
}

// Make functions globally available
window.clearFilters = clearFilters;

/**
 * Load review summary for a car (for listings page)
 */
async function loadReviewSummary(carId) {
    try {
        const url = `${API_BASE_URL}/api/v1/reviews/car/${carId}`;
        const response = await fetch(url);
        
        if (response.ok) {
            const data = await response.json();
            const reviewSummaryEl = document.getElementById(`reviewSummary-${carId}`);
            
            if (reviewSummaryEl) {
                const total = data.total || 0;
                const avgRating = data.average_rating;
                
                if (total === 0) {
                    reviewSummaryEl.innerHTML = '<span>💬 No reviews yet</span>';
                } else if (avgRating !== null && avgRating !== undefined) {
                    const stars = '⭐'.repeat(Math.round(avgRating));
                    reviewSummaryEl.innerHTML = `<span>💬 ${total} review${total !== 1 ? 's' : ''} • ${stars} ${avgRating.toFixed(1)}/5</span>`;
                } else {
                    reviewSummaryEl.innerHTML = `<span>💬 ${total} review${total !== 1 ? 's' : ''}</span>`;
                }
            }
        } else {
            const reviewSummaryEl = document.getElementById(`reviewSummary-${carId}`);
            if (reviewSummaryEl) {
                reviewSummaryEl.innerHTML = '<span>💬 No reviews</span>';
            }
        }
    } catch (error) {
        console.error('[DEBUG] loadReviewSummary: Error loading reviews for car', carId, error);
        const reviewSummaryEl = document.getElementById(`reviewSummary-${carId}`);
        if (reviewSummaryEl) {
            reviewSummaryEl.innerHTML = '<span>💬 No reviews</span>';
        }
    }
}


