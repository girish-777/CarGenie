/**
 * Global AI Chatbot Widget (RAG - Retrieval Augmented Generation)
 * Floating widget available on all pages
 */

var API_BASE_URL = window.BACKEND_URL;
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
                    <p class="suggestions-label">Try asking:</p>
                    <div class="suggestion-chips">
                        ${currentCarId ? `
                            <button class="suggestion-chip" onclick="sendSuggestion('What are the key features of this car?')">Key features?</button>
                            <button class="suggestion-chip" onclick="sendSuggestion('What is the fuel economy?')">Fuel economy?</button>
                            <button class="suggestion-chip" onclick="sendSuggestion('What do reviews say?')">Reviews?</button>
                        ` : `
                            <button class="suggestion-chip" onclick="sendSuggestion('What should I look for when buying a car?')">Buying tips?</button>
                            <button class="suggestion-chip" onclick="sendSuggestion('What is the difference between electric and gasoline cars?')">Electric vs Gas?</button>
                            <button class="suggestion-chip" onclick="sendSuggestion('How do I compare cars?')">Compare cars?</button>
                        `}
                    </div>
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
    
    // Clear input
    input.value = '';
    
    // Disable input and button
    input.disabled = true;
    if (sendBtn) sendBtn.disabled = true;
    
    // Hide suggestions after first message
    if (suggestionsContainer) {
        suggestionsContainer.style.display = 'none';
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
        suggestions.innerHTML = `
            <p class="suggestions-label">Try asking:</p>
            <div class="suggestion-chips">
                <button class="suggestion-chip" onclick="sendSuggestion('What are the key features of this car?')">Key features?</button>
                <button class="suggestion-chip" onclick="sendSuggestion('What is the fuel economy?')">Fuel economy?</button>
                <button class="suggestion-chip" onclick="sendSuggestion('What do reviews say?')">Reviews?</button>
            </div>
        `;
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
