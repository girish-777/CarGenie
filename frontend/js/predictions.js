/**
 * Predictions JavaScript for ownership cost and future value
 */

var API_BASE_URL = 'http://localhost:8000';
if (typeof window.API_BASE_URL !== 'undefined') {
    API_BASE_URL = window.API_BASE_URL;
} else {
    window.API_BASE_URL = API_BASE_URL;
}

/**
 * Load ownership cost prediction
 */
async function loadOwnershipCost(carId, years = 5, annualMileage = 12000) {
    console.log('[DEBUG] loadOwnershipCost: Loading for car', carId);
    
    try {
        const url = `${API_BASE_URL}/api/v1/cars/${carId}/ownership-cost?years=${years}&annual_mileage=${annualMileage}`;
        console.log('[DEBUG] loadOwnershipCost: Fetching from', url);
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error('Failed to load ownership cost');
        }
        
        const data = await response.json();
        console.log('[DEBUG] loadOwnershipCost: Received data', data);
        
        return data;
    } catch (error) {
        console.error('[DEBUG] loadOwnershipCost: Error', error);
        throw error;
    }
}

/**
 * Load future value prediction
 */
async function loadFutureValue(carId, yearsAhead = 5) {
    console.log('[DEBUG] loadFutureValue: Loading for car', carId);
    
    try {
        const url = `${API_BASE_URL}/api/v1/cars/${carId}/future-value?years_ahead=${yearsAhead}`;
        console.log('[DEBUG] loadFutureValue: Fetching from', url);
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error('Failed to load future value');
        }
        
        const data = await response.json();
        console.log('[DEBUG] loadFutureValue: Received data', data);
        
        return data;
    } catch (error) {
        console.error('[DEBUG] loadFutureValue: Error', error);
        throw error;
    }
}

/**
 * Display ownership cost in a container
 */
function displayOwnershipCost(container, costData) {
    console.log('[DEBUG] displayOwnershipCost: Displaying cost data');
    
    const html = `
        <div class="prediction-card">
            <h3>💰 Total Ownership Cost</h3>
            <div class="prediction-summary">
                <div class="prediction-item">
                    <span class="prediction-label">Total Cost:</span>
                    <span class="prediction-value">$${costData.total_cost.toLocaleString()}</span>
                </div>
                <div class="prediction-item">
                    <span class="prediction-label">Monthly Cost:</span>
                    <span class="prediction-value">$${costData.monthly_cost.toLocaleString()}</span>
                </div>
                <div class="prediction-item">
                    <span class="prediction-label">Cost per Mile:</span>
                    <span class="prediction-value">$${costData.cost_per_mile.toFixed(2)}</span>
                </div>
            </div>
            
            <h4 style="margin-top: 1.5rem; margin-bottom: 1rem;">Cost Breakdown</h4>
            <div class="cost-breakdown">
                <div class="breakdown-item">
                    <span>Depreciation:</span>
                    <span>$${costData.depreciation.toLocaleString()}</span>
                </div>
                <div class="breakdown-item">
                    <span>Fuel:</span>
                    <span>$${costData.fuel_cost.toLocaleString()}</span>
                </div>
                <div class="breakdown-item">
                    <span>Insurance:</span>
                    <span>$${costData.insurance.toLocaleString()}</span>
                </div>
                <div class="breakdown-item">
                    <span>Maintenance:</span>
                    <span>$${costData.maintenance.toLocaleString()}</span>
                </div>
                <div class="breakdown-item">
                    <span>Repairs:</span>
                    <span>$${costData.repairs.toLocaleString()}</span>
                </div>
                <div class="breakdown-item">
                    <span>Registration & Taxes:</span>
                    <span>$${costData.registration_taxes.toLocaleString()}</span>
                </div>
            </div>
            
            <details style="margin-top: 1rem;">
                <summary style="cursor: pointer; color: #2563eb; font-weight: 600;">View Yearly Breakdown</summary>
                <div style="margin-top: 1rem;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background-color: #f3f4f6;">
                                <th style="padding: 0.5rem; text-align: left; border: 1px solid #e5e7eb;">Year</th>
                                <th style="padding: 0.5rem; text-align: right; border: 1px solid #e5e7eb;">Depreciation</th>
                                <th style="padding: 0.5rem; text-align: right; border: 1px solid #e5e7eb;">Fuel</th>
                                <th style="padding: 0.5rem; text-align: right; border: 1px solid #e5e7eb;">Insurance</th>
                                <th style="padding: 0.5rem; text-align: right; border: 1px solid #e5e7eb;">Maintenance</th>
                                <th style="padding: 0.5rem; text-align: right; border: 1px solid #e5e7eb;">Total</th>
                                <th style="padding: 0.5rem; text-align: right; border: 1px solid #e5e7eb;">Remaining Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${costData.yearly_breakdown.map(year => `
                                <tr>
                                    <td style="padding: 0.5rem; border: 1px solid #e5e7eb;">Year ${year.year}</td>
                                    <td style="padding: 0.5rem; text-align: right; border: 1px solid #e5e7eb;">$${year.depreciation.toLocaleString()}</td>
                                    <td style="padding: 0.5rem; text-align: right; border: 1px solid #e5e7eb;">$${year.fuel.toLocaleString()}</td>
                                    <td style="padding: 0.5rem; text-align: right; border: 1px solid #e5e7eb;">$${year.insurance.toLocaleString()}</td>
                                    <td style="padding: 0.5rem; text-align: right; border: 1px solid #e5e7eb;">$${year.maintenance.toLocaleString()}</td>
                                    <td style="padding: 0.5rem; text-align: right; border: 1px solid #e5e7eb; font-weight: 600;">$${year.total.toLocaleString()}</td>
                                    <td style="padding: 0.5rem; text-align: right; border: 1px solid #e5e7eb; color: #059669;">$${year.remaining_value.toLocaleString()}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </details>
        </div>
    `;
    
    container.innerHTML = html;
}

/**
 * Display future value prediction
 */
function displayFutureValue(container, valueData) {
    console.log('[DEBUG] displayFutureValue: Displaying value data');
    
    const html = `
        <div class="prediction-card">
            <h3>📈 Future Value Prediction</h3>
            <div class="prediction-summary">
                <div class="prediction-item">
                    <span class="prediction-label">Current Value:</span>
                    <span class="prediction-value">$${valueData.current_price.toLocaleString()}</span>
                </div>
                <div class="prediction-item">
                    <span class="prediction-label">Current Mileage:</span>
                    <span class="prediction-value">${valueData.current_mileage.toLocaleString()} mi</span>
                </div>
            </div>
            
            <h4 style="margin-top: 1.5rem; margin-bottom: 1rem;">Value Projection</h4>
            <div class="value-projection">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background-color: #f3f4f6;">
                            <th style="padding: 0.5rem; text-align: left; border: 1px solid #e5e7eb;">Year</th>
                            <th style="padding: 0.5rem; text-align: right; border: 1px solid #e5e7eb;">Predicted Value</th>
                            <th style="padding: 0.5rem; text-align: right; border: 1px solid #e5e7eb;">Mileage</th>
                            <th style="padding: 0.5rem; text-align: right; border: 1px solid #e5e7eb;">Depreciation</th>
                            <th style="padding: 0.5rem; text-align: right; border: 1px solid #e5e7eb;">% Lost</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${valueData.predictions.map(pred => `
                            <tr>
                                <td style="padding: 0.5rem; border: 1px solid #e5e7eb; font-weight: 600;">${pred.year}</td>
                                <td style="padding: 0.5rem; text-align: right; border: 1px solid #e5e7eb; color: #059669; font-weight: 600;">$${pred.value.toLocaleString()}</td>
                                <td style="padding: 0.5rem; text-align: right; border: 1px solid #e5e7eb;">${pred.mileage.toLocaleString()} mi</td>
                                <td style="padding: 0.5rem; text-align: right; border: 1px solid #e5e7eb; color: #dc2626;">-$${pred.total_depreciation.toLocaleString()}</td>
                                <td style="padding: 0.5rem; text-align: right; border: 1px solid #e5e7eb; color: #dc2626;">${pred.depreciation_percentage}%</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

// Make functions globally available
window.loadOwnershipCost = loadOwnershipCost;
window.loadFutureValue = loadFutureValue;
window.displayOwnershipCost = displayOwnershipCost;
window.displayFutureValue = displayFutureValue;

