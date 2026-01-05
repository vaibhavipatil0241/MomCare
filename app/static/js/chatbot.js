/**
 * AI Chatbot for Baby Care
 * Provides intelligent responses using backend API
 */

let isTyping = false;

// Quick question handler
function askQuestion(question) {
    document.getElementById('user-input').value = question;
    sendMessage();
}

// Handle Enter key press
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Main send message function
async function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();

    if (!message || isTyping) return;

    // Add user message
    addMessage(message, 'user');

    // Clear input
    input.value = '';

    // Show typing indicator
    showTypingIndicator();

    try {
        // Call backend API
        const response = await fetch('/babycare/api/chatbot/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: message })
        });

        const data = await response.json();

        // Remove typing indicator
        hideTypingIndicator();

        if (data.success) {
            // Add bot response with markdown formatting
            addMessage(data.response, 'bot', true);
        } else {
            addMessage('Sorry, I encountered an error. Please try again.', 'bot');
        }
    } catch (error) {
        console.error('Error:', error);
        hideTypingIndicator();
        addMessage('Sorry, I\'m having trouble connecting. Please try again later.', 'bot');
    }
}

// Add message to chat
function addMessage(text, sender, isMarkdown = false) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = sender === 'bot' 
        ? '<i class="fas fa-robot"></i>' 
        : '<i class="fas fa-user"></i>';

    const content = document.createElement('div');
    content.className = 'message-content';
    
    if (isMarkdown && sender === 'bot') {
        // Convert markdown-style formatting to HTML
        content.innerHTML = formatBotResponse(text);
    } else {
        content.innerHTML = `<p>${escapeHtml(text)}</p>`;
    }

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    messagesContainer.appendChild(messageDiv);

    // Scroll to bottom with smooth animation
    scrollToBottom();
}

// Format bot response with markdown-like syntax
function formatBotResponse(text) {
    // Convert markdown to HTML
    let formatted = text;
    
    // Headers (e.g., **Bold Text:**)
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Bullet points
    formatted = formatted.replace(/^• (.+)$/gm, '<li>$1</li>');
    
    // Wrap consecutive list items in ul
    formatted = formatted.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');
    
    // Line breaks
    formatted = formatted.replace(/\n\n/g, '</p><p>');
    formatted = formatted.replace(/\n/g, '<br>');
    
    // Emojis - ensure they display properly
    formatted = `<p>${formatted}</p>`;
    
    return formatted;
}

// Show typing indicator
function showTypingIndicator() {
    isTyping = true;
    const messagesContainer = document.getElementById('chat-messages');
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot typing-indicator';
    typingDiv.id = 'typing-indicator';
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = '<i class="fas fa-robot"></i>';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    content.innerHTML = `
        <div class="typing-animation">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
    
    typingDiv.appendChild(avatar);
    typingDiv.appendChild(content);
    messagesContainer.appendChild(typingDiv);
    
    scrollToBottom();
}

// Hide typing indicator
function hideTypingIndicator() {
    isTyping = false;
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// Smooth scroll to bottom
function scrollToBottom() {
    const messagesContainer = document.getElementById('chat-messages');
    messagesContainer.scrollTo({
        top: messagesContainer.scrollHeight,
        behavior: 'smooth'
    });
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Add CSS for typing animation dynamically
const style = document.createElement('style');
style.textContent = `
    .typing-indicator {
        opacity: 0.7;
    }
    
    .typing-animation {
        display: flex;
        gap: 5px;
        padding: 10px 0;
    }
    
    .typing-animation span {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #8b5cf6;
        animation: typing 1.4s infinite;
    }
    
    .typing-animation span:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .typing-animation span:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    @keyframes typing {
        0%, 60%, 100% {
            transform: translateY(0);
            opacity: 0.7;
        }
        30% {
            transform: translateY(-10px);
            opacity: 1;
        }
    }
    
    .message-content ul {
        margin: 0.5rem 0;
        padding-left: 1.5rem;
    }
    
    .message-content li {
        margin: 0.3rem 0;
        line-height: 1.6;
    }
    
    .message-content strong {
        color: #8b5cf6;
        font-weight: 600;
    }
    
    .message-content p {
        margin: 0.5rem 0;
    }
    
    .message-content p:first-child {
        margin-top: 0;
    }
    
    .message-content p:last-child {
        margin-bottom: 0;
    }
`;
document.head.appendChild(style);

console.log('AI Chatbot script loaded successfully');
