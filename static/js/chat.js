document.addEventListener('DOMContentLoaded', () => {
    // Only initialize chat functionality if we're on the chat page
    const messageContainer = document.querySelector('.messages');
    if (!messageContainer) return; // Exit if not on chat page
    
    const chatForm = document.querySelector('.chat-form');
    const chatInput = document.querySelector('.chat-input');
    const voiceToggle = document.querySelector('.voice-toggle');
    let voiceEnabled = false;

    // Speech recognition setup
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    let isRecording = false;

    // Voice toggle functionality
    voiceToggle.addEventListener('click', () => {
        if (!isRecording) {
            // Start recording
            recognition.start();
            isRecording = true;
            voiceToggle.classList.add('recording');
            chatInput.placeholder = "Listening...";
        } else {
            // Stop recording
            recognition.stop();
            isRecording = false;
            voiceToggle.classList.remove('recording');
            chatInput.placeholder = "Message iRyan...";
        }
    });

    // Handle speech recognition results
    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        chatInput.value = transcript;
        adjustTextareaHeight();
        isRecording = false;
        voiceToggle.classList.remove('recording');
        chatInput.placeholder = "Message iRyan...";
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        isRecording = false;
        voiceToggle.classList.remove('recording');
        chatInput.placeholder = "Message iRyan...";
    };

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
            // Create EventSource for streaming response
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    voice_enabled: voiceEnabled
                })
            });

            // Create EventSource for streaming response
            const eventSource = new EventSource(`/api/chat`);
            let currentMessageDiv;

            eventSource.onmessage = (event) => {
                const data = JSON.parse(event.data);
                
                if (data.error) {
                    console.error('Server error:', data.error);
                    appendMessage('Error: ' + data.error, false);
                    eventSource.close();
                    return;
                }

                if (data.chunk) {
                    if (!currentMessageDiv) {
                        currentMessageDiv = document.createElement('div');
                        currentMessageDiv.className = 'message ai-message';
                        messageContainer.appendChild(currentMessageDiv);
                    }
                    currentMessageDiv.textContent += data.chunk;
                    messageContainer.scrollTop = messageContainer.scrollHeight;
                }

                if (data.message_id) {
                    // Final message received, close the connection
                    eventSource.close();
                }
            };

            eventSource.onerror = (error) => {
                console.error('EventSource error:', error);
                eventSource.close();
                appendMessage('Error: Connection lost. Please try again.', false);
            };

            // Remove typing indicator
            typingIndicator.remove();
            
            // Handle audio response if voice is enabled
            if (voiceEnabled) {
                if (data.has_audio && data.audio) {
                    console.log('Playing audio response...');
                    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                    const audioElement = new Audio('data:audio/mpeg;base64,' + data.audio);
                    
                    // Create source node
                    const source = audioContext.createMediaElementSource(audioElement);
                    
                    // Create gain node for volume control
                    const gainNode = audioContext.createGain();
                    gainNode.gain.value = 1.0; // Set initial volume
                    
                    // Connect nodes
                    source.connect(gainNode);
                    gainNode.connect(audioContext.destination);
                    
                    // Play audio
                    audioElement.play().catch(error => {
                        console.error('Error playing audio:', error);
                        appendMessage('Error playing audio response. Please try again.', false);
                    });
                    
                    // Update UI to show audio is playing
                    voiceToggle.classList.add('playing');
                    
                    // Remove playing class when audio ends
                    audioElement.addEventListener('ended', () => {
                        voiceToggle.classList.remove('playing');
                    });
                } else {
                    console.log('No audio response available');
                    appendMessage('Voice response not available. Please try again.', false);
                }
            }
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
