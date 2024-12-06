document.addEventListener('DOMContentLoaded', () => {
    // Only initialize chat functionality if we're on the chat page
    const messageContainer = document.querySelector('.messages');
    if (!messageContainer) return; // Exit if not on chat page
    
    const chatForm = document.querySelector('.chat-form');
    const chatInput = document.querySelector('.chat-input');
    const voiceButton = document.querySelector('#voiceButton');
    
    let isRecording = false;
    let conversation = null;

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

    // Voice conversation handling
    async function startVoiceSession() {
        try {
            const response = await fetch('/api/voice/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (!response.ok) {
                throw new Error('Failed to start voice session');
            }
            
            const data = await response.json();
            isRecording = true;
            voiceButton.classList.add('recording');
            
            // Add a temporary message to show recording status
            appendMessage('Voice conversation started. Click the microphone button again to end.', false);
            
            // Start voice recognition
            startVoiceRecognition();
            
        } catch (error) {
            console.error('Error starting voice session:', error);
            appendMessage('Sorry, there was an error starting the voice conversation.', false);
        }
    }

    async function endVoiceSession() {
        try {
            const response = await fetch('/api/voice/end', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ conversation })
            });
            
            if (!response.ok) {
                throw new Error('Failed to end voice session');
            }
            
            stopVoiceRecognition();
            
            isRecording = false;
            voiceButton.classList.remove('recording');
            conversation = null;
            
            appendMessage('Voice conversation ended.', false);
            
        } catch (error) {
            console.error('Error ending voice session:', error);
            appendMessage('Sorry, there was an error ending the voice conversation.', false);
        }
    }

    let recognition = null;

    function startVoiceRecognition() {
        if ('webkitSpeechRecognition' in window) {
            recognition = new webkitSpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = true;
            
            recognition.onresult = async function(event) {
                const transcript = Array.from(event.results)
                    .map(result => result[0].transcript)
                    .join('');
                
                if (event.results[0].isFinal) {
                    appendMessage(transcript, true);
                    
                    // Get AI response
                    const response = await sendMessage(transcript);
                    
                    // Generate and play voice response
                    try {
                        const audioResponse = await fetch('/api/voice/speak', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ text: response })
                        });
                        
                        if (audioResponse.ok) {
                            const audioBlob = await audioResponse.blob();
                            const audioUrl = URL.createObjectURL(audioBlob);
                            const audio = new Audio(audioUrl);
                            await audio.play();
                        }
                    } catch (error) {
                        console.error('Error playing voice response:', error);
                    }
                }
            };
            
            recognition.start();
        } else {
            appendMessage('Voice recognition is not supported in your browser.', false);
        }
    }

    function stopVoiceRecognition() {
        if (recognition) {
            recognition.stop();
            recognition = null;
        }
    }

    // Voice button click handler
    voiceButton.addEventListener('click', async () => {
        if (!isRecording) {
            await startVoiceSession();
        } else {
            await endVoiceSession();
        }
    });

    // Initial height adjustment
    adjustTextareaHeight();
});
