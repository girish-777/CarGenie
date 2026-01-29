/**
 * Global AI Chatbot Widget (RAG - Retrieval Augmented Generation)
 * Floating widget available on all pages
 */

var API_BASE_URL = 'http://localhost:8000';
if (typeof window.API_BASE_URL !== 'undefined') {
    API_BASE_URL = window.API_BASE_URL;
} else {
    window.API_BASE_URL = API_BASE_URL;
}

// Store conversation history
let conversationHistory = [];

// Chatbot state
let chatbotOpen = false;
let currentCarId = null;
let lastUserQuestion = '';

// Suggestion history (last N user searches/questions)
const RECENT_SUGGESTIONS_KEY = 'cargenie_chatbot_recent_searches';
const MAX_RECENT_SUGGESTIONS = 5;

function loadRecentSuggestions() {
    try {
        const raw = localStorage.getItem(RECENT_SUGGESTIONS_KEY);
        const parsed = raw ? JSON.parse(raw) : [];
        if (!Array.isArray(parsed)) return [];
        return parsed
            .filter(s => typeof s === 'string')
            .map(s => s.trim())
            .filter(Boolean);
    } catch {
        return [];
    }
}

function saveRecentSuggestions(items) {
    try {
        localStorage.setItem(RECENT_SUGGESTIONS_KEY, JSON.stringify(items));
    } catch {
        // ignore storage errors (private mode etc.)
    }
}

function addRecentSuggestion(query) {
    const q = (query || '').trim();
    if (!q) return;

    const recent = loadRecentSuggestions();
    const normalized = q.toLowerCase();
    const deduped = recent.filter(x => x.toLowerCase() !== normalized);
    deduped.unshift(q);
    saveRecentSuggestions(deduped.slice(0, MAX_RECENT_SUGGESTIONS));
}

function getBaseSuggestions() {
    if (currentCarId) {
        return [
            'What are the key features of this car?',
            'What is the fuel economy?',
            'What do reviews say?',
        ];
    }
    return [
        'What should I look for when buying a car?',
        'What is the difference between electric and gasoline cars?',
        'How do I compare cars?',
    ];
}

function generateFollowUpSuggestions(question) {
    const q = (question || '').toLowerCase();
    if (!q.trim()) return [];

    // Car-specific vs general phrasing
    const aboutThisCar = currentCarId ? 'this car' : 'a car';

    // Helper to build unique suggestions
    const suggestions = [];
    const add = (s) => {
        const t = (s || '').trim();
        if (!t) return;
        const norm = t.toLowerCase();
        if (!suggestions.some(x => x.toLowerCase() === norm)) suggestions.push(t);
    };

    // Keyword-driven follow-ups
    if (q.includes('buy') || q.includes('purchase') || q.includes('what should i look for')) {
        add('What are the most important things to check before buying?');
        add('How can I spot a good deal vs overpriced listings?');
        add('What mileage/year range is safest for my budget?');
        add('What questions should I ask the seller/dealer?');
        add('What paperwork should I verify before purchase?');
    } else if (q.includes('compare') || q.includes('difference') || q.includes('vs')) {
        add('Can you compare reliability and maintenance costs?');
        add('Which option is better for city driving?');
        add('Which option holds value better (resale)?');
        add('How do running costs differ over 5 years?');
        add('What are common issues to watch out for?');
    } else if (q.includes('electric') || q.includes('ev') || q.includes('battery')) {
        add('How far does an EV typically go on a full charge?');
        add('What should I check about battery health when buying used?');
        add('How much does charging cost vs gas per month?');
        add('What charging options do I need at home?');
        add('Are EV maintenance costs lower than gas cars?');
    } else if (q.includes('price') || q.includes('budget') || q.includes('cost') || q.includes('afford')) {
        add(`What affects the price of ${aboutThisCar} the most?`);
        add('What is a fair price range for this type of car?');
        add('How can I negotiate the price effectively?');
        add('What ownership costs should I budget for (insurance, maintenance)?');
        add('Should I prioritize lower price or lower mileage?');
    } else if (q.includes('mileage') || q.includes('odometer')) {
        add('What mileage is considered “high” for this model/year?');
        add('How does mileage impact expected maintenance?');
        add('Is a newer car with higher mileage better than an older low‑mileage car?');
        add('What components wear out first at this mileage?');
        add('What service history should I look for?');
    } else if (q.includes('reliab') || q.includes('problem') || q.includes('issue')) {
        add('What are the most common problems for this model?');
        add('What maintenance schedule should I follow?');
        add('How can I check for past accident or flood damage?');
        add('What should a mechanic inspect in a pre‑purchase inspection?');
        add('What warranty options are worth it?');
    } else if (q.includes('fuel') || q.includes('mpg') || q.includes('economy')) {
        add(`What is the real‑world fuel economy for ${aboutThisCar}?`);
        add('How can I improve fuel economy with driving habits?');
        add('Does fuel type (gas/hybrid/diesel) change maintenance costs?');
        add('Is hybrid worth it for my driving pattern?');
        add('How do fuel costs compare monthly for my mileage?');
    } else if (q.includes('feature') || q.includes('tech') || q.includes('interior') || q.includes('safety')) {
        add('Which safety features matter most for daily driving?');
        add('What trim level gives best value for features?');
        add('What should I check during a test drive for comfort/noise?');
        add('Are there any missing features I should avoid?');
        add('How do crash test ratings compare for similar cars?');
    } else {
        // Generic follow-ups when we can't classify the question well
        add(`What are the pros and cons of ${aboutThisCar}?`);
        add('What similar cars should I also consider?');
        add('What should I check during a test drive?');
        add('How reliable is this type of car long term?');
        add('What are typical maintenance and running costs?');
    }

    // Ensure we return at most 5, but always try to return 5
    return suggestions.slice(0, 5);
}

function _escapeHtml(text) {
    return String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function _attachSuggestionHandlers(container) {
    const buttons = container.querySelectorAll('button.suggestion-chip[data-suggestion]');
    buttons.forEach((btn) => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const value = btn.getAttribute('data-suggestion') || '';
            if (value) {
                window.sendSuggestion(value);
            }
        });
    });
}

function renderChatbotSuggestions() {
    const suggestionsContainer = document.getElementById('chatbotSuggestions');
    if (!suggestionsContainer) return;

    const base = getBaseSuggestions();
    const followUps = generateFollowUpSuggestions(lastUserQuestion);

    // Do NOT create separate boxes/sections. Show a single suggestions row.
    // Prefer follow-ups based on the previous question; fallback to base suggestions.
    const suggestionsToShow =
        followUps && followUps.length >= 3
            ? followUps.slice(0, 5)
            : base.slice(0, 3);

    suggestionsContainer.innerHTML = `
        <div class="suggestion-chips">
            <span class="suggestions-label">Try asking:</span>
            ${suggestionsToShow
                .map(
                    (q) =>
                        `<button type="button" class="suggestion-chip" data-suggestion="${_escapeHtml(q)}">${_escapeHtml(q)}</button>`
                )
                .join('')}
        </div>
    `;
    suggestionsContainer.style.display = 'block';
    _attachSuggestionHandlers(suggestionsContainer);
}

/**
 * Initialize global chatbot widget
 */
window.initGlobalChatbot = function() {
    console.log('[DEBUG] initGlobalChatbot: Initializing global chatbot widget');
    
    // Check if chatbot already exists
    if (document.getElementById('globalChatbotWidget')) {
        return;
    }
    
    // Detect if we're on a car detail page
    const urlParams = new URLSearchParams(window.location.search);
    const carIdParam = urlParams.get('id');
    if (carIdParam && window.location.pathname.includes('car-detail.html')) {
        currentCarId = parseInt(carIdParam);
    }
    
    // Create chatbot widget HTML
    const chatbotHTML = `
        <div id="globalChatbotWidget" class="global-chatbot-widget">
            <!-- Chatbot Toggle Button -->
            <button id="chatbotToggleBtn" class="chatbot-toggle-btn" onclick="toggleChatbot()">
                <span class="chatbot-text">Assistant</span>
                <span class="chatbot-icon">💬</span>
            </button>
            
            <!-- Chatbot Panel -->
            <div id="chatbotPanel" class="chatbot-panel" style="display: none;">
                <div class="chatbot-panel-header">
                    <div>
                        <h3>🤖 AI Car Advisor</h3>
                        <p class="chatbot-subtitle">${currentCarId ? 'Ask about this car' : 'Ask me anything about cars'}</p>
                    </div>
                    <button class="chatbot-close-btn" onclick="toggleChatbot()">×</button>
                </div>
                
                <div class="chatbot-panel-messages" id="chatbotMessages">
                    <div class="chatbot-message bot-message">
                        <div class="message-content">
                            👋 Hi! I'm your AI car advisor. ${currentCarId ? `I can answer questions about this car, or help you with general car questions.` : 'Ask me anything about cars, features, specifications, or car buying advice!'}
                        </div>
                    </div>
                </div>
                
                <div class="chatbot-panel-suggestions" id="chatbotSuggestions">
                    <!-- Filled by renderChatbotSuggestions() -->
                </div>
                
                <div class="chatbot-panel-input">
                    <input 
                        type="text" 
                        id="chatbotInput" 
                        class="chatbot-input" 
                        placeholder="${currentCarId ? 'Ask about this car...' : 'Ask me anything about cars...'}"
                        onkeypress="handleChatbotKeyPress(event)"
                    >
                    <button class="chatbot-send-btn" onclick="sendChatbotMessage()" id="chatbotSendBtn">
                        Send
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Add to body
    document.body.insertAdjacentHTML('beforeend', chatbotHTML);
    
    console.log('[DEBUG] initGlobalChatbot: Global chatbot widget created');

    // Render suggestions (base + recent)
    renderChatbotSuggestions();
}

/**
 * Toggle chatbot open/close
 */
window.toggleChatbot = function() {
    const panel = document.getElementById('chatbotPanel');
    const toggleBtn = document.getElementById('chatbotToggleBtn');
    
    if (!panel || !toggleBtn) return;
    
    chatbotOpen = !chatbotOpen;
    
    if (chatbotOpen) {
        panel.style.display = 'flex';
        toggleBtn.classList.add('active');
        // Refresh suggestions each time we open
        renderChatbotSuggestions();
        // Focus input
        setTimeout(() => {
            const input = document.getElementById('chatbotInput');
            if (input) input.focus();
        }, 100);
    } else {
        panel.style.display = 'none';
        toggleBtn.classList.remove('active');
    }
};

/**
 * Handle Enter key press
 */
window.handleChatbotKeyPress = function(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendChatbotMessage();
    }
};

/**
 * Send a suggestion as a message
 */
window.sendSuggestion = function(message) {
    const input = document.getElementById('chatbotInput');
    if (input) {
        input.value = message;
        sendChatbotMessage();
    }
};

/**
 * Send chatbot message
 */
window.sendChatbotMessage = async function() {
    const input = document.getElementById('chatbotInput');
    const sendBtn = document.getElementById('chatbotSendBtn');
    const messagesContainer = document.getElementById('chatbotMessages');
    const suggestionsContainer = document.getElementById('chatbotSuggestions');
    
    if (!input || !messagesContainer) {
        console.error('[DEBUG] sendChatbotMessage: Required elements not found');
        return;
    }
    
    const message = input.value.trim();
    if (!message) {
        return;
    }

    // Track the latest question to generate follow-up suggestions
    lastUserQuestion = message;
    
    // Clear input
    input.value = '';
    
    // Disable input and button
    input.disabled = true;
    if (sendBtn) sendBtn.disabled = true;
    
    // Track last 5 searches/questions for suggestion chips
    addRecentSuggestion(message);
    // Keep suggestions visible and updated (show at least last 5 searches)
    if (suggestionsContainer) {
        renderChatbotSuggestions();
    }
    
    // Add user message to UI
    addMessageToChat(messagesContainer, message, 'user');
    
    // Add typing indicator
    const typingId = addTypingIndicator(messagesContainer);
    
    try {
        // Add current message to history
        conversationHistory.push({
            role: 'user',
            content: message
        });
        
        let response;
        
        // If on car detail page, use car-specific endpoint
        if (currentCarId) {
            const url = `${API_BASE_URL}/api/v1/ai/chat/${currentCarId}`;
            console.log('[DEBUG] sendChatbotMessage: Sending to car-specific endpoint', url);
            
            const apiResponse = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    conversation_history: conversationHistory.slice(-5) // Last 5 messages
                })
            });
            
            if (!apiResponse.ok) {
                const errorData = await apiResponse.json();
                throw new Error(errorData.detail || 'Failed to get response');
            }
            
            response = await apiResponse.json();
        } else {
            // General car questions - use general endpoint
            const url = `${API_BASE_URL}/api/v1/ai/chat/general`;
            console.log('[DEBUG] sendChatbotMessage: Sending to general endpoint', url);
            
            const apiResponse = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    conversation_history: conversationHistory.slice(-5)
                })
            });
            
            if (!apiResponse.ok) {
                const errorData = await apiResponse.json();
                throw new Error(errorData.detail || 'Failed to get response');
            }
            
            response = await apiResponse.json();
        }
        
        // Remove typing indicator
        removeTypingIndicator(messagesContainer, typingId);
        
        const aiResponse = response.response;
        
        // Add bot response to UI
        addMessageToChat(messagesContainer, aiResponse, 'bot');

        // After receiving the answer, re-render suggestions so user always sees follow-ups
        renderChatbotSuggestions();
        
        // Add bot response to history
        conversationHistory.push({
            role: 'assistant',
            content: aiResponse
        });
        
        // Keep history limited to last 10 messages
        if (conversationHistory.length > 10) {
            conversationHistory = conversationHistory.slice(-10);
        }
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
    } catch (error) {
        console.error('[DEBUG] sendChatbotMessage: Error', error);
        
        // Remove typing indicator
        removeTypingIndicator(messagesContainer, typingId);
        
        // Show error message
        addMessageToChat(messagesContainer, 
            `Sorry, I encountered an error: ${error.message}. Please try again or visit a car's detail page for specific information.`, 
            'bot', 
            true
        );
    } finally {
        // Re-enable input and button
        input.disabled = false;
        if (sendBtn) sendBtn.disabled = false;
        input.focus();
    }
};

/**
 * Add message to chat UI
 */
function addMessageToChat(container, message, role, isError = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chatbot-message ${role}-message ${isError ? 'error-message' : ''}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = message;
    
    messageDiv.appendChild(contentDiv);
    container.appendChild(messageDiv);
    
    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

/**
 * Add typing indicator
 */
function addTypingIndicator(container) {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chatbot-message bot-message';
    typingDiv.id = 'typing-indicator';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content typing-indicator';
    contentDiv.innerHTML = '<span></span><span></span><span></span>';
    
    typingDiv.appendChild(contentDiv);
    container.appendChild(typingDiv);
    
    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
    
    return 'typing-indicator';
}

/**
 * Remove typing indicator
 */
function removeTypingIndicator(container, indicatorId) {
    const indicator = document.getElementById(indicatorId);
    if (indicator) {
        indicator.remove();
    }
}

/**
 * Update chatbot context when navigating to car detail page
 */
window.updateChatbotContext = function(carId) {
    currentCarId = carId;
    conversationHistory = []; // Reset conversation when changing cars
    
    const subtitle = document.querySelector('.chatbot-subtitle');
    const input = document.getElementById('chatbotInput');
    const suggestions = document.getElementById('chatbotSuggestions');
    
    if (subtitle) {
        subtitle.textContent = 'Ask about this car';
    }
    
    if (input) {
        input.placeholder = 'Ask about this car...';
    }
    
    if (suggestions) {
        renderChatbotSuggestions();
    }
    
    // Update welcome message
    const messagesContainer = document.getElementById('chatbotMessages');
    if (messagesContainer) {
        messagesContainer.innerHTML = `
            <div class="chatbot-message bot-message">
                <div class="message-content">
                    👋 Hi! I can now answer questions about this car, or help you with general car questions.
                </div>
            </div>
        `;
    }
};

// Initialize chatbot when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        initGlobalChatbot();
        
        // Update context if on car detail page
        const urlParams = new URLSearchParams(window.location.search);
        const carIdParam = urlParams.get('id');
        if (carIdParam && window.location.pathname.includes('car-detail.html')) {
            currentCarId = parseInt(carIdParam);
        }
    });
} else {
    // DOM already loaded
    initGlobalChatbot();
    
    // Update context if on car detail page
    const urlParams = new URLSearchParams(window.location.search);
    const carIdParam = urlParams.get('id');
    if (carIdParam && window.location.pathname.includes('car-detail.html')) {
        currentCarId = parseInt(carIdParam);
    }
}
