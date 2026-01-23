/**
 * Reviews JavaScript for managing car reviews
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
 * Load reviews for a car
 */
async function loadCarReviews(carId) {
    console.log('[DEBUG] loadCarReviews: Loading reviews for car', carId);
    
    try {
        const url = `${API_BASE_URL}/api/v1/reviews/car/${carId}`;
        const response = await fetch(url);
        
        if (!response.ok) {
            console.error('[DEBUG] loadCarReviews: Error loading reviews', response.status);
            return { reviews: [], total: 0, average_rating: null };
        }
        
        const data = await response.json();
        console.log('[DEBUG] loadCarReviews: Reviews loaded', data.total, 'reviews');
        return data;
    } catch (error) {
        console.error('[DEBUG] loadCarReviews: Error', error);
        return { reviews: [], total: 0, average_rating: null };
    }
}

/**
 * Create a review
 */
async function createReview(carId, rating, title, content) {
    console.log('[DEBUG] createReview: Creating review for car', carId);
    
    if (!isLoggedIn()) {
        alert('Please login to write a review');
        window.location.href = 'login.html';
        return null;
    }
    
    try {
        const url = `${API_BASE_URL}/api/v1/reviews/`;
        const token = getAuthToken();
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                car_id: carId,
                rating: rating,
                title: title,
                content: content
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to create review');
        }
        
        const data = await response.json();
        console.log('[DEBUG] createReview: Review created', data.id);
        return data;
    } catch (error) {
        console.error('[DEBUG] createReview: Error', error);
        alert('Error creating review: ' + error.message);
        return null;
    }
}

/**
 * Get current user ID from token (if available)
 */
function getCurrentUserId() {
    // Try to get user info from token or localStorage
    const token = localStorage.getItem('auth_token');
    if (!token) return null;
    
    // Decode JWT token to get user info (simple base64 decode)
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        // Note: This is a simplified approach. In production, you might want to call /api/v1/auth/me
        return payload.sub; // email from token
    } catch (e) {
        return null;
    }
}

/**
 * Get current user's review for a car
 */
async function getUserReview(carId) {
    if (!isLoggedIn()) return null;
    
    try {
        const reviewsData = await loadCarReviews(carId);
        const reviews = reviewsData.reviews || [];
        const token = getAuthToken();
        
        // We need to get current user ID - let's fetch from /api/v1/auth/me
        try {
            const userResponse = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (userResponse.ok) {
                const user = await userResponse.json();
                // Find user's review
                return reviews.find(r => r.user_id === user.id);
            }
        } catch (e) {
            console.error('[DEBUG] getUserReview: Error fetching user info', e);
        }
    } catch (e) {
        console.error('[DEBUG] getUserReview: Error', e);
    }
    return null;
}

/**
 * Display reviews on the page
 */
async function displayReviews(carId, containerId) {
    console.log('[DEBUG] displayReviews: Displaying reviews for car', carId);
    
    const container = document.getElementById(containerId);
    if (!container) {
        console.error('[DEBUG] displayReviews: Container not found', containerId);
        return;
    }
    
    // Show loading
    container.innerHTML = '<p>Loading reviews...</p>';
    
    const reviewsData = await loadCarReviews(carId);
    const reviews = reviewsData.reviews || [];
    const averageRating = reviewsData.average_rating;
    const total = reviewsData.total || 0;
    
    // Check if user has already reviewed this car
    let userReview = null;
    if (isLoggedIn()) {
        userReview = await getUserReview(carId);
    }
    
    // Build reviews HTML
    let reviewsHTML = '<div class="reviews-section">';
    
    // Average rating header
    if (averageRating !== null) {
        reviewsHTML += `
            <div class="reviews-header">
                <h2>Reviews (${total})</h2>
                <div class="average-rating">
                    <span class="rating-stars">${'⭐'.repeat(Math.round(averageRating))}</span>
                    <span class="rating-value">${averageRating.toFixed(1)}/5</span>
                </div>
            </div>
        `;
    } else {
        reviewsHTML += `<h2>Reviews (${total})</h2>`;
    }
    
    // AI Summary section (if available)
    const aiSummaryReview = reviews.find(r => r.ai_summary);
    if (aiSummaryReview && aiSummaryReview.ai_summary) {
        reviewsHTML += `
            <div class="ai-summary-container">
                <h3>🤖 AI-Powered Summary</h3>
                <div class="ai-summary-content">
                    <p>${aiSummaryReview.ai_summary}</p>
                </div>
            </div>
        `;
    } else if (total >= 2) {
        // Show button to generate summary if we have enough reviews
        reviewsHTML += `
            <div class="ai-summary-container">
                <button id="generateSummaryBtn" class="btn btn-secondary" onclick="generateReviewSummary(${carId})">
                    🤖 Generate AI Summary
                </button>
            </div>
        `;
    }
    
    // Review form (if logged in)
    if (isLoggedIn()) {
        if (userReview) {
            // User already reviewed - show edit form
            reviewsHTML += `
                <div class="review-form-container">
                    <h3>Edit Your Review</h3>
                    <p style="color: #6b7280; margin-bottom: 1rem;">You've already reviewed this car. You can update your review below.</p>
                    <form id="reviewForm" onsubmit="handleReviewUpdate(event, ${carId}, ${userReview.id}); return false;">
                        <div class="form-group">
                            <label>Rating</label>
                            <select id="reviewRating" required>
                                <option value="">Select rating</option>
                                <option value="5" ${userReview.rating === 5 ? 'selected' : ''}>5 ⭐⭐⭐⭐⭐</option>
                                <option value="4" ${userReview.rating === 4 ? 'selected' : ''}>4 ⭐⭐⭐⭐</option>
                                <option value="3" ${userReview.rating === 3 ? 'selected' : ''}>3 ⭐⭐⭐</option>
                                <option value="2" ${userReview.rating === 2 ? 'selected' : ''}>2 ⭐⭐</option>
                                <option value="1" ${userReview.rating === 1 ? 'selected' : ''}>1 ⭐</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Title (optional)</label>
                            <input type="text" id="reviewTitle" placeholder="Review title" value="${userReview.title || ''}">
                        </div>
                        <div class="form-group">
                            <label>Your Review</label>
                            <textarea id="reviewContent" required placeholder="Write your review here (minimum 10 characters)" minlength="10">${userReview.content || ''}</textarea>
                        </div>
                        <div style="display: flex; gap: 1rem;">
                            <button type="submit" class="btn btn-primary">Update Review</button>
                            <button type="button" class="btn btn-secondary" onclick="handleReviewDelete(${carId}, ${userReview.id})">Delete Review</button>
                        </div>
                    </form>
                </div>
            `;
        } else {
            // User hasn't reviewed yet - show create form
            reviewsHTML += `
                <div class="review-form-container">
                    <h3>Write a Review</h3>
                    <form id="reviewForm" onsubmit="handleReviewSubmit(event, ${carId}); return false;">
                        <div class="form-group">
                            <label>Rating</label>
                            <select id="reviewRating" required>
                                <option value="">Select rating</option>
                                <option value="5">5 ⭐⭐⭐⭐⭐</option>
                                <option value="4">4 ⭐⭐⭐⭐</option>
                                <option value="3">3 ⭐⭐⭐</option>
                                <option value="2">2 ⭐⭐</option>
                                <option value="1">1 ⭐</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Title (optional)</label>
                            <input type="text" id="reviewTitle" placeholder="Review title">
                        </div>
                        <div class="form-group">
                            <label>Your Review</label>
                            <textarea id="reviewContent" required placeholder="Write your review here (minimum 10 characters)" minlength="10"></textarea>
                        </div>
                        <button type="submit" class="btn btn-primary">Submit Review</button>
                    </form>
                </div>
            `;
        }
    } else {
        reviewsHTML += `
            <div class="review-form-container">
                <p><a href="login.html">Login</a> to write a review</p>
            </div>
        `;
    }
    
    // Reviews list
    reviewsHTML += '<div class="reviews-list">';
    
    if (reviews.length === 0) {
        reviewsHTML += '<p class="no-reviews">No reviews yet. Be the first to review this car!</p>';
    } else {
        reviews.forEach(review => {
            const stars = '⭐'.repeat(review.rating);
            const isUserReview = userReview && review.id === userReview.id;
            reviewsHTML += `
                <div class="review-item ${isUserReview ? 'user-review' : ''}">
                    <div class="review-header">
                        <div class="review-rating">${stars} (${review.rating}/5)</div>
                        <div class="review-date">${new Date(review.created_at).toLocaleDateString()}${review.updated_at && review.updated_at !== review.created_at ? ' (updated)' : ''}</div>
                        ${isUserReview ? '<span style="color: #2563eb; font-size: 0.875rem;">Your review</span>' : ''}
                    </div>
                    ${review.title ? `<h4 class="review-title">${review.title}</h4>` : ''}
                    <p class="review-content">${review.content}</p>
                </div>
            `;
        });
    }
    
    reviewsHTML += '</div></div>';
    
    container.innerHTML = reviewsHTML;
    console.log('[DEBUG] displayReviews: Reviews displayed');
}

/**
 * Handle review form submission
 */
window.handleReviewSubmit = async function(event, carId) {
    event.preventDefault();
    console.log('[DEBUG] handleReviewSubmit: Submitting review for car', carId);
    
    const rating = parseInt(document.getElementById('reviewRating').value);
    const title = document.getElementById('reviewTitle').value.trim();
    const content = document.getElementById('reviewContent').value.trim();
    
    if (!rating || !content) {
        alert('Please fill in rating and review content');
        return;
    }
    
    if (content.length < 10) {
        alert('Review content must be at least 10 characters');
        return;
    }
    
    const review = await createReview(carId, rating, title || null, content);
    
    if (review) {
        alert('✅ Review submitted successfully! AI summary will be generated automatically if there are enough reviews.');
        // Reload reviews
        displayReviews(carId, 'reviewsContainer');
        // Clear form
        document.getElementById('reviewForm').reset();
    }
};

/**
 * Update an existing review
 */
async function updateReview(reviewId, rating, title, content) {
    console.log('[DEBUG] updateReview: Updating review', reviewId);
    
    if (!isLoggedIn()) {
        alert('Please login to update a review');
        window.location.href = 'login.html';
        return null;
    }
    
    try {
        const url = `${API_BASE_URL}/api/v1/reviews/${reviewId}`;
        const token = getAuthToken();
        
        const response = await fetch(url, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                rating: rating,
                title: title || null,
                content: content
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to update review');
        }
        
        const data = await response.json();
        console.log('[DEBUG] updateReview: Review updated', data.id);
        return data;
    } catch (error) {
        console.error('[DEBUG] updateReview: Error', error);
        alert('Error updating review: ' + error.message);
        return null;
    }
}

/**
 * Delete a review
 */
async function deleteReview(reviewId) {
    console.log('[DEBUG] deleteReview: Deleting review', reviewId);
    
    if (!isLoggedIn()) {
        alert('Please login to delete a review');
        return false;
    }
    
    if (!confirm('Are you sure you want to delete this review?')) {
        return false;
    }
    
    try {
        const url = `${API_BASE_URL}/api/v1/reviews/${reviewId}`;
        const token = getAuthToken();
        
        const response = await fetch(url, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to delete review');
        }
        
        console.log('[DEBUG] deleteReview: Review deleted');
        return true;
    } catch (error) {
        console.error('[DEBUG] deleteReview: Error', error);
        alert('Error deleting review: ' + error.message);
        return false;
    }
}

/**
 * Handle review update
 */
window.handleReviewUpdate = async function(event, carId, reviewId) {
    event.preventDefault();
    console.log('[DEBUG] handleReviewUpdate: Updating review', reviewId, 'for car', carId);
    
    const rating = parseInt(document.getElementById('reviewRating').value);
    const title = document.getElementById('reviewTitle').value.trim();
    const content = document.getElementById('reviewContent').value.trim();
    
    if (!rating || !content) {
        alert('Please fill in rating and review content');
        return;
    }
    
    if (content.length < 10) {
        alert('Review content must be at least 10 characters');
        return;
    }
    
    const review = await updateReview(reviewId, rating, title || null, content);
    
    if (review) {
        alert('✅ Review updated successfully!');
        // Reload reviews
        displayReviews(carId, 'reviewsContainer');
    }
};

/**
 * Handle review deletion
 */
window.handleReviewDelete = async function(carId, reviewId) {
    console.log('[DEBUG] handleReviewDelete: Deleting review', reviewId);
    
    const success = await deleteReview(reviewId);
    
    if (success) {
        alert('✅ Review deleted successfully!');
        // Reload reviews
        displayReviews(carId, 'reviewsContainer');
    }
};

/**
 * Generate AI summary for car reviews
 */
window.generateReviewSummary = async function(carId) {
    console.log('[DEBUG] generateReviewSummary: Generating summary for car', carId);
    
    const btn = document.getElementById('generateSummaryBtn');
    if (btn) {
        btn.disabled = true;
        btn.textContent = '🤖 Generating...';
    }
    
    try {
        const url = `${API_BASE_URL}/api/v1/ai/reviews/${carId}/summarize`;
        const response = await fetch(url, {
            method: 'POST'
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to generate summary');
        }
        
        const data = await response.json();
        console.log('[DEBUG] generateReviewSummary: Summary generated');
        
        // Reload reviews to show the summary
        displayReviews(carId, 'reviewsContainer');
        alert('✅ AI summary generated successfully!');
    } catch (error) {
        console.error('[DEBUG] generateReviewSummary: Error', error);
        alert('Error generating summary: ' + error.message);
        if (btn) {
            btn.disabled = false;
            btn.textContent = '🤖 Generate AI Summary';
        }
    }
};

