document.addEventListener('DOMContentLoaded', function() {
    const voiceButton = document.getElementById('voiceButton');
    const statusText = document.getElementById('statusText');
    const messagesContainer = document.getElementById('messages');
    
    let isRecording = false;
    let recognition = null;

    function appendMessage(text, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'ai'}`;
        messageDiv.textContent = text;
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

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
            
            isRecording = true;
            voiceButton.classList.add('recording');
            statusText.textContent = 'Listening... Click again to stop';
            startVoiceRecognition();
            
        } catch (error) {
            console.error('Error starting voice session:', error);
            statusText.textContent = 'Error starting voice session';
        }
    }

    async function endVoiceSession() {
        try {
            stopVoiceRecognition();
            
            const response = await fetch('/api/voice/end', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (!response.ok) {
                throw new Error('Failed to end voice session');
            }
            
            isRecording = false;
            voiceButton.classList.remove('recording');
            statusText.textContent = 'Click the microphone to start speaking';
            
        } catch (error) {
            console.error('Error ending voice session:', error);
            statusText.textContent = 'Error ending voice session';
        }
    }

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
                    
                    try {
                        // Get AI response
                        const chatResponse = await fetch('/api/chat', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ message: transcript })
                        });
                        
                        if (!chatResponse.ok) {
                            throw new Error('Failed to get AI response');
                        }
                        
                        const chatData = await chatResponse.json();
                        appendMessage(chatData.response, false);
                        
                        // Generate and play voice response
                        const audioResponse = await fetch('/api/voice/speak', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ text: chatData.response })
                        });
                        
                        if (audioResponse.ok) {
                            const audioBlob = await audioResponse.blob();
                            const audioUrl = URL.createObjectURL(audioBlob);
                            const audio = new Audio(audioUrl);
                            await audio.play();
                        }
                    } catch (error) {
                        console.error('Error processing voice chat:', error);
                        statusText.textContent = 'Error processing voice chat';
                    }
                }
            };
            
            recognition.onerror = function(event) {
                console.error('Speech recognition error:', event.error);
                statusText.textContent = 'Speech recognition error';
                endVoiceSession();
            };
            
            recognition.start();
        } else {
            statusText.textContent = 'Speech recognition is not supported in your browser';
        }
    }

    function stopVoiceRecognition() {
        if (recognition) {
            recognition.stop();
            recognition = null;
        }
    }

    voiceButton.addEventListener('click', async () => {
        if (!isRecording) {
            await startVoiceSession();
        } else {
            await endVoiceSession();
        }
    });
});
