/**
 * Car comparison JavaScript
 */

var API_BASE_URL = 'http://localhost:8000';
if (typeof window.API_BASE_URL !== 'undefined') {
    API_BASE_URL = window.API_BASE_URL;
} else {
    window.API_BASE_URL = API_BASE_URL;
}
const MAX_COMPARE_CARS = 3;
const COMPARE_STORAGE_KEY = 'compare_cars';

/**
 * Get cars from localStorage
 */
function getCompareCars() {
    const stored = localStorage.getItem(COMPARE_STORAGE_KEY);
    const cars = stored ? JSON.parse(stored) : [];
    console.log('[DEBUG] getCompareCars: Retrieved', cars.length, 'cars from localStorage:', cars);
    return cars;
}

/**
 * Save cars to localStorage
 */
function saveCompareCars(carIds) {
    console.log('[DEBUG] saveCompareCars: Saving', carIds.length, 'cars to localStorage:', carIds);
    localStorage.setItem(COMPARE_STORAGE_KEY, JSON.stringify(carIds));
    console.log('[DEBUG] saveCompareCars: Cars saved successfully');
}

/**
 * Check if user is logged in
 */
function isLoggedIn() {
    return !!localStorage.getItem('auth_token');
}

/**
 * Add car to comparison
 */
function addToCompare(carId) {
    console.log('[DEBUG] addToCompare: Attempting to add car ID', carId, 'to comparison');
    
    // Check if user is logged in
    if (!isLoggedIn()) {
        if (confirm('Please login to compare cars. Go to login page?')) {
            window.location.href = 'login.html';
        }
        return false;
    }
    
    const compareCars = getCompareCars();
    
    if (compareCars.includes(carId)) {
        console.warn('[DEBUG] addToCompare: Car already in comparison');
        alert('This car is already in comparison');
        return false;
    }
    
    if (compareCars.length >= MAX_COMPARE_CARS) {
        console.warn('[DEBUG] addToCompare: Maximum comparison limit reached');
        alert(`You can only compare up to ${MAX_COMPARE_CARS} cars at a time. Please remove one first.`);
        return false;
    }
    
    compareCars.push(carId);
    saveCompareCars(compareCars);
    console.log('[DEBUG] addToCompare: Car added successfully, total cars:', compareCars.length);
    
    // Show notification
    showNotification('Car added to comparison');
    
    // Update compare button if on listings page
    updateCompareButtons();
    
    return true;
}

/**
 * Remove car from comparison
 */
function removeFromCompare(carId) {
    console.log('[DEBUG] removeFromCompare: Attempting to remove car ID', carId, 'from comparison');
    const compareCars = getCompareCars();
    const index = compareCars.indexOf(carId);
    
    if (index > -1) {
        console.log('[DEBUG] removeFromCompare: Car found at index', index);
        compareCars.splice(index, 1);
        saveCompareCars(compareCars);
        console.log('[DEBUG] removeFromCompare: Car removed, remaining cars:', compareCars.length);
        updateCompareButtons();
        
        // Reload comparison if on compare page
        if (window.location.pathname.includes('compare.html')) {
            console.log('[DEBUG] removeFromCompare: On compare page, reloading comparison');
            loadComparison();
        }
        
        return true;
    }
    
    console.warn('[DEBUG] removeFromCompare: Car not found in comparison');
    return false;
}

/**
 * Check if car is in comparison
 */
function isInCompare(carId) {
    const compareCars = getCompareCars();
    const result = compareCars.includes(carId);
    console.log('[DEBUG] isInCompare: Car ID', carId, 'is in compare?', result);
    return result;
}

/**
 * Clear all comparisons
 */
function clearComparison() {
    if (confirm('Clear all cars from comparison?')) {
        localStorage.removeItem(COMPARE_STORAGE_KEY);
        updateCompareButtons();
        
        if (window.location.pathname.includes('compare.html')) {
            loadComparison();
        }
    }
}

/**
 * Load and display comparison
 */
async function loadComparison() {
    console.log('[DEBUG] loadComparison: Starting to load comparison');
    const compareCars = getCompareCars();
    console.log('[DEBUG] loadComparison: Cars to compare:', compareCars);
    
    const container = document.getElementById('comparisonContainer');
    const emptyState = document.getElementById('emptyState');
    const grid = document.getElementById('comparisonGrid');
    
    if (!container || !grid) {
        console.error('[DEBUG] loadComparison: Required DOM elements not found');
        return;
    }
    
    if (compareCars.length === 0) {
        console.log('[DEBUG] loadComparison: No cars to compare, showing empty state');
        container.style.display = 'none';
        if (emptyState) emptyState.style.display = 'block';
        return;
    }
    
    console.log('[DEBUG] loadComparison: Loading', compareCars.length, 'cars for comparison');
    container.style.display = 'block';
    if (emptyState) emptyState.style.display = 'none';
    grid.innerHTML = '';
    
    // Load each car
    for (const carId of compareCars) {
        try {
            console.log('[DEBUG] loadComparison: Loading car ID', carId);
            const url = `${API_BASE_URL}/api/v1/cars/${carId}`;
            const response = await fetch(url);
            console.log('[DEBUG] loadComparison: Response for car', carId, 'status:', response.status);
            
            if (!response.ok) {
                console.warn('[DEBUG] loadComparison: Failed to load car', carId);
                continue;
            }
            
            const car = await response.json();
            console.log('[DEBUG] loadComparison: Car loaded:', car.make, car.model);
            const card = createComparisonCard(car);
            grid.appendChild(card);
            console.log('[DEBUG] loadComparison: Card added for car', carId);
        } catch (error) {
            console.error(`[DEBUG] loadComparison: Error loading car ${carId}:`, error);
        }
    }
    
    console.log('[DEBUG] loadComparison: Comparison loaded successfully');
}

/**
 * Create comparison card
 */
function createComparisonCard(car) {
    const card = document.createElement('div');
    card.className = 'comparison-card';
    
    const imageUrl = car.image_urls && car.image_urls.length > 0 
        ? car.image_urls[0] 
        : 'images/2023-Toyota-Camry.webp';
    
    const processedImageUrl = imageUrl.startsWith('images/') 
        ? imageUrl.replace(/ /g, '%20')
        : imageUrl;
    
    const specs = car.specs || {};
    const scores = car.scores || {};
    
    card.innerHTML = `
        <div class="comparison-card-header">
            <button class="remove-compare-btn" onclick="removeFromCompare(${car.id}); this.closest('.comparison-card').remove(); if(document.getElementById('comparisonGrid').children.length === 0) { document.getElementById('comparisonContainer').style.display='none'; document.getElementById('emptyState').style.display='block'; }">×</button>
            <img src="${processedImageUrl}" alt="${car.make} ${car.model}" class="comparison-image"
                 onerror="this.src='images/2023-Toyota-Camry.webp'">
        </div>
        <div class="comparison-card-body">
            <h3>${car.year} ${car.make} ${car.model}</h3>
            <div class="comparison-price">$${car.price.toLocaleString()}</div>
            
            <div class="comparison-specs">
                <div class="spec-row">
                    <span class="spec-label">Year:</span>
                    <span class="spec-value">${car.year}</span>
                </div>
                <div class="spec-row">
                    <span class="spec-label">Price:</span>
                    <span class="spec-value">$${car.price.toLocaleString()}</span>
                </div>
                <div class="spec-row">
                    <span class="spec-label">Mileage:</span>
                    <span class="spec-value">${car.mileage.toLocaleString()} mi</span>
                </div>
                <div class="spec-row">
                    <span class="spec-label">Fuel Type:</span>
                    <span class="spec-value">${car.fuel_type}</span>
                </div>
                <div class="spec-row">
                    <span class="spec-label">Transmission:</span>
                    <span class="spec-value">${car.transmission}</span>
                </div>
                <div class="spec-row">
                    <span class="spec-label">Condition:</span>
                    <span class="spec-value">${car.condition}${car.engine_condition ? ` • Engine: ${car.engine_condition.charAt(0).toUpperCase() + car.engine_condition.slice(1)}` : ''}</span>
                </div>
                ${specs.horsepower ? `
                <div class="spec-row">
                    <span class="spec-label">Horsepower:</span>
                    <span class="spec-value">${specs.horsepower} HP</span>
                </div>
                ` : ''}
                ${specs.mpg_city && specs.mpg_highway ? `
                <div class="spec-row">
                    <span class="spec-label">MPG:</span>
                    <span class="spec-value">${specs.mpg_city}/${specs.mpg_highway} city/hwy</span>
                </div>
                ` : ''}
                ${scores.overall_score ? `
                <div class="spec-row">
                    <span class="spec-label">Overall Score:</span>
                    <span class="spec-value">${scores.overall_score.toFixed(1)}/10</span>
                </div>
                ` : ''}
            </div>
            
            <div style="margin-top: 1rem;">
                <a href="car-detail.html?id=${car.id}" class="btn btn-primary" style="width: 100%;">View Details</a>
            </div>
        </div>
    `;
    
    return card;
}

/**
 * Update compare buttons on page
 */
function updateCompareButtons() {
    const compareCars = getCompareCars();
    document.querySelectorAll('.compare-btn').forEach(btn => {
        const carId = parseInt(btn.dataset.carId);
        if (isInCompare(carId)) {
            btn.classList.add('in-compare');
            btn.textContent = 'Remove from Compare';
        } else {
            btn.classList.remove('in-compare');
            btn.textContent = 'Compare';
        }
    });
}

/**
 * Show notification
 */
function showNotification(message) {
    // Simple notification - can be enhanced
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #2563eb;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        z-index: 10000;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Load comparison on compare page
if (window.location.pathname.includes('compare.html')) {
// Load comparison on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('[DEBUG] compare.js: DOMContentLoaded - Loading comparison');
    
    // Check if user is logged in
    if (!isLoggedIn()) {
        console.log('[DEBUG] compare.js: User not logged in, showing login prompt');
        const loginPrompt = document.getElementById('loginPrompt');
        const instructionsCard = document.getElementById('instructionsCard');
        const comparisonContainer = document.getElementById('comparisonContainer');
        const emptyState = document.getElementById('emptyState');
        
        if (loginPrompt) loginPrompt.style.display = 'block';
        if (instructionsCard) instructionsCard.style.display = 'none';
        if (comparisonContainer) comparisonContainer.style.display = 'none';
        if (emptyState) emptyState.style.display = 'none';
        return;
    }
    
    // User is logged in, show instructions and load comparison
    const loginPrompt = document.getElementById('loginPrompt');
    const instructionsCard = document.getElementById('instructionsCard');
    
    if (loginPrompt) loginPrompt.style.display = 'none';
    if (instructionsCard) instructionsCard.style.display = 'block';
    
    loadComparison();
});
}

