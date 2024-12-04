document.addEventListener('DOMContentLoaded', () => {
    const messageContainer = document.querySelector('.messages');
    const chatForm = document.querySelector('.chat-form');
    const chatInput = document.querySelector('.chat-input');

    // Auto-resize textarea
    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = Math.min(chatInput.scrollHeight, 200) + 'px';
    });

    // Handle Enter key
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (chatInput.value.trim()) {
                chatForm.dispatchEvent(new Event('submit'));
            }
        }
    });

    function appendMessage(content, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
        messageDiv.textContent = content;
        messageContainer.appendChild(messageDiv);
        messageContainer.scrollTop = messageContainer.scrollHeight;
        chatInput.style.height = '52px'; // Reset height after sending
    }

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const message = chatInput.value.trim();
        if (!message) return;

        // Add user message
        appendMessage(message, true);
        chatInput.value = '';

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });

            const data = await response.json();
            appendMessage(data.response, false);
        } catch (error) {
            console.error('Error:', error);
            appendMessage('Sorry, there was an error processing your message.', false);
        }
    });
});
