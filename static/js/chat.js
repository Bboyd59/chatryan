document.addEventListener('DOMContentLoaded', () => {
    const messageContainer = document.querySelector('.messages');
    const chatForm = document.querySelector('.chat-form');
    const chatInput = document.querySelector('.chat-input');

    // Auto-resize textarea
    function adjustTextareaHeight() {
        chatInput.style.height = 'auto';
        const newHeight = Math.min(chatInput.scrollHeight, 200);
        chatInput.style.height = `${Math.max(45, newHeight)}px`; // Minimum height of 45px
    }

    chatInput.addEventListener('input', adjustTextareaHeight);

    // Handle Enter key
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (chatInput.value.trim()) {
                chatForm.dispatchEvent(new Event('submit'));
            }
        }
    });

    function createTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'typing-indicator';
        indicator.innerHTML = `
            <span></span>
            <span></span>
            <span></span>
        `;
        return indicator;
    }

    function appendMessage(content, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
        
        if (isUser) {
            messageDiv.textContent = content;
        } else {
            // Parse markdown for AI responses
            try {
                messageDiv.innerHTML = marked.parse(content, {
                    breaks: true,
                    gfm: true,
                    sanitize: false
                });
            } catch (error) {
                console.error('Markdown parsing error:', error);
                messageDiv.textContent = content;
            }
        }
        
        messageContainer.appendChild(messageDiv);
        messageContainer.scrollTop = messageContainer.scrollHeight;
        
        // Reset input height after sending
        if (isUser) {
            chatInput.style.height = '45px';
            adjustTextareaHeight();
        }
    }

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const message = chatInput.value.trim();
        if (!message) return;

        // Clear input and reset height
        chatInput.value = '';
        chatInput.style.height = '45px';
        
        // Add user message
        appendMessage(message, true);

        // Add typing indicator
        const typingIndicator = createTypingIndicator();
        messageContainer.appendChild(typingIndicator);
        messageContainer.scrollTop = messageContainer.scrollHeight;

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            // Remove typing indicator
            typingIndicator.remove();

            const data = await response.json();
            appendMessage(data.response, false);
        } catch (error) {
            console.error('Error:', error);
            // Remove typing indicator
            typingIndicator.remove();
            appendMessage('Sorry, there was an error processing your message.', false);
        }
    });

    // Initial height adjustment
    adjustTextareaHeight();
});
