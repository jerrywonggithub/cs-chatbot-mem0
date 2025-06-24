// Configuration
const API_URL = 'http://localhost:5000/api';

// DOM Elements
const chatMessages = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');

// State
let userId = localStorage.getItem('chatbot_user_id') || null;
let isWaitingForResponse = false;

// Event Listeners
document.addEventListener('DOMContentLoaded', initialize);
sendButton.addEventListener('click', sendMessage);
messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

/**
 * Initialize the chat interface
 */
function initialize() {
    // Focus on input field
    messageInput.focus();
    
    // Check for existing user ID or create new one
    if (!userId) {
        // This will be replaced with the server-generated ID on first message
        // userId = 'temp_' + Date.now().toString();
        // To simulate demo user
        userId = 'customer_bot' 
        localStorage.setItem('chatbot_user_id', userId);
    }
}

/**
 * Send a message to the API
 */
async function sendMessage() {
    const message = messageInput.value.trim();
    
    // Don't send empty messages or if waiting for response
    if (message === '' || isWaitingForResponse) return;
    
    // Clear input field
    messageInput.value = '';
    
    // Add user message to chat
    addMessageToChat(message, 'user');
    
    // Show loading indicator
    showLoadingIndicator();
    
    // Set waiting state
    isWaitingForResponse = true;
    
    try {
        // Send message to API
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message,
                user_id: userId
            })
        });
        
        // Handle API errors
        if (!response.ok) {
            throw new Error(`API returned ${response.status} ${response.statusText}`);
        }
        
        // Parse response
        const data = await response.json();
        
        // Update user ID if needed
        if (data.user_id && data.user_id !== userId) {
            userId = data.user_id;
            localStorage.setItem('chatbot_user_id', userId);
        }
        
        // Remove loading indicator
        removeLoadingIndicator();
        
        // Add bot response to chat
        addMessageToChat(data.response, 'bot');
        
    } catch (error) {
        console.error('Error sending message:', error);
        
        // Remove loading indicator
        removeLoadingIndicator();
        
        // Add error message
        addMessageToChat('Sorry, I encountered an error. Please try again later.', 'bot error');
    } finally {
        // Reset waiting state
        isWaitingForResponse = false;
        
        // Scroll to bottom
        scrollToBottom();
        
        // Focus on input field
        messageInput.focus();
    }
}

/**
 * Add a message to the chat container
 */
function addMessageToChat(content, type) {
    // Create elements
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const paragraph = document.createElement('p');
    paragraph.textContent = content;
    
    // Add time if not a system message
    if (type !== 'system') {
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = getCurrentTime();
        contentDiv.appendChild(timeDiv);
    }
    
    // Assemble message
    contentDiv.prepend(paragraph);
    messageDiv.appendChild(contentDiv);
    
    // Add to chat
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    scrollToBottom();
}

/**
 * Show loading indicator in chat
 */
function showLoadingIndicator() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message bot loading';
    loadingDiv.id = 'loading-indicator';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Add bouncing dots
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('span');
        contentDiv.appendChild(dot);
    }
    
    loadingDiv.appendChild(contentDiv);
    chatMessages.appendChild(loadingDiv);
    
    scrollToBottom();
}

/**
 * Remove loading indicator from chat
 */
function removeLoadingIndicator() {
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.remove();
    }
}

/**
 * Get current formatted time
 */
function getCurrentTime() {
    const now = new Date();
    let hours = now.getHours();
    const minutes = now.getMinutes().toString().padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';
    
    hours = hours % 12;
    hours = hours ? hours : 12; // Convert 0 to 12
    
    return `${hours}:${minutes} ${ampm}`;
}

/**
 * Scroll chat container to bottom
 */
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Retrieve chat history for current user
 * Note: This function is prepared but not used in the initial UI
 */
async function getChatHistory(query = '') {
    try {
        const response = await fetch(`${API_URL}/history?user_id=${userId}&query=${query}`);
        
        if (!response.ok) {
            throw new Error(`API returned ${response.status} ${response.statusText}`);
        }
        
        return await response.json();
        
    } catch (error) {
        console.error('Error fetching chat history:', error);
        return null;
    }
}
