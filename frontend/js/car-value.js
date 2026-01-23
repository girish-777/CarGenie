/**
 * Car Value Estimation JavaScript
 */

var API_BASE_URL = window.BACKEND_URL;
if (typeof window.API_BASE_URL !== 'undefined') {
    API_BASE_URL = window.API_BASE_URL;
} else {
    window.API_BASE_URL = API_BASE_URL;
}

/**
 * Estimate car value
 */
async function estimateCarValue(carData) {
    console.log('[DEBUG] estimateCarValue: Estimating value for', carData);
    
    try {
        const url = `${API_BASE_URL}/api/v1/estimate-value`;
        console.log('[DEBUG] estimateCarValue: Fetching from', url);
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(carData)
        });
        
        console.log('[DEBUG] estimateCarValue: Response status', response.status);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to estimate car value');
        }
        
        const data = await response.json();
        console.log('[DEBUG] estimateCarValue: Received data', data);
        
        return data;
    } catch (error) {
        console.error('[DEBUG] estimateCarValue: Error', error);
        throw error;
    }
}

/**
 * Display value estimation results
 */
function displayValueResult(container, result) {
    console.log('[DEBUG] displayValueResult: Displaying result', result);
    
    const html = `
        <div class="prediction-card" style="max-width: 800px; margin: 0 auto;">
            <h2 style="text-align: center; margin-bottom: 1.5rem; color: #1f2937;">💰 Your Car's Estimated Value</h2>
            
            <div style="text-align: center; margin-bottom: 2rem; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 1rem; color: white;">
                <div style="font-size: 0.9rem; opacity: 0.9; margin-bottom: 0.5rem;">Estimated Market Value</div>
                <div style="font-size: 3rem; font-weight: 700; margin-bottom: 0.5rem;">
                    $${result.estimated_value.toLocaleString()}
                </div>
                <div style="font-size: 0.9rem; opacity: 0.9;">
                    Range: $${result.value_range.min.toLocaleString()} - $${result.value_range.max.toLocaleString()}
                </div>
            </div>
            
            ${result.depreciation_amount ? `
                <div style="margin-bottom: 1.5rem; padding: 1rem; background-color: #f0f9ff; border-radius: 0.5rem; border-left: 4px solid #2563eb;">
                    <h3 style="margin: 0 0 0.5rem 0; color: #1e40af;">Depreciation Analysis</h3>
                    <p style="margin: 0; color: #6b7280;">
                        Your car has depreciated by <strong>$${result.depreciation_amount.toLocaleString()}</strong> 
                        (${result.depreciation_percentage}%) since purchase.
                    </p>
                </div>
            ` : ''}
            
            <div style="margin-bottom: 1.5rem;">
                <h3 style="margin-bottom: 1rem;">Value Factors</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                    <div style="padding: 1rem; background-color: #f9fafb; border-radius: 0.5rem;">
                        <div style="font-size: 0.875rem; color: #6b7280; margin-bottom: 0.25rem;">Car Age</div>
                        <div style="font-size: 1.25rem; font-weight: 600; color: #1f2937;">${result.factors.age_years} years</div>
                    </div>
                    
                    <div style="padding: 1rem; background-color: #f9fafb; border-radius: 0.5rem;">
                        <div style="font-size: 0.875rem; color: #6b7280; margin-bottom: 0.25rem;">Depreciation Rate</div>
                        <div style="font-size: 1.25rem; font-weight: 600; color: #1f2937;">${result.factors.depreciation_rate}% / year</div>
                    </div>
                    
                    <div style="padding: 1rem; background-color: #f9fafb; border-radius: 0.5rem;">
                        <div style="font-size: 0.875rem; color: #6b7280; margin-bottom: 0.25rem;">Mileage Adjustment</div>
                        <div style="font-size: 1.25rem; font-weight: 600; color: ${result.factors.mileage_adjustment >= 0 ? '#dc2626' : '#059669'};">
                            ${result.factors.mileage_adjustment >= 0 ? '+' : ''}${result.factors.mileage_adjustment}%
                        </div>
                        <div style="font-size: 0.75rem; color: #6b7280; margin-top: 0.25rem;">
                            ${result.factors.mileage_difference > 0 ? `${result.factors.mileage_difference.toLocaleString()} mi above average` : 
                              result.factors.mileage_difference < 0 ? `${Math.abs(result.factors.mileage_difference).toLocaleString()} mi below average` : 
                              'Average mileage'}
                        </div>
                    </div>
                    
                    <div style="padding: 1rem; background-color: #f9fafb; border-radius: 0.5rem;">
                        <div style="font-size: 0.875rem; color: #6b7280; margin-bottom: 0.25rem;">Condition Impact</div>
                        <div style="font-size: 1.25rem; font-weight: 600; color: #1f2937;">${result.factors.condition_adjustment}%</div>
                    </div>
                </div>
            </div>
            
            <div style="padding: 1rem; background-color: #fef3c7; border-radius: 0.5rem; border-left: 4px solid #f59e0b;">
                <p style="margin: 0; color: #92400e; font-size: 0.875rem;">
                    <strong>Note:</strong> This is an estimated value based on market data and depreciation models. 
                    Actual market value may vary based on location, demand, and specific features. 
                    For a more accurate valuation, consider getting a professional appraisal.
                </p>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
    container.style.display = 'block';
}

// Handle form submission
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('valueEstimateForm');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorMessage = document.getElementById('errorMessage');
    const valueResult = document.getElementById('valueResult');
    
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Hide previous results
            valueResult.style.display = 'none';
            errorMessage.style.display = 'none';
            
            // Show loading
            loadingIndicator.style.display = 'block';
            
            // Get form data
            const formData = new FormData(e.target);
            const carData = {
                make: formData.get('make'),
                model: formData.get('model'),
                year: parseInt(formData.get('year')),
                mileage: parseInt(formData.get('mileage')),
                condition: formData.get('condition'),
                original_price: formData.get('original_price') ? parseFloat(formData.get('original_price')) : null,
                fuel_type: formData.get('fuel_type') || null,
                transmission: formData.get('transmission') || null
            };
            
            // Remove null values
            Object.keys(carData).forEach(key => {
                if (carData[key] === null || carData[key] === '') {
                    delete carData[key];
                }
            });
            
            try {
                const result = await estimateCarValue(carData);
                loadingIndicator.style.display = 'none';
                displayValueResult(valueResult, result);
            } catch (error) {
                loadingIndicator.style.display = 'none';
                errorMessage.textContent = 'Failed to estimate value: ' + error.message;
                errorMessage.style.display = 'block';
            }
        });
    }
});

// Make functions globally available
window.estimateCarValue = estimateCarValue;
window.displayValueResult = displayValueResult;

