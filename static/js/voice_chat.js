const { useState, useCallback, useEffect } = React;

function VoiceChat() {
    const [error, setError] = useState(null);
    const [status, setStatus] = useState('disconnected');
    
    const conversation = window.ElevenLabs.useConversation({
        onConnect: () => {
            console.log('Connected');
            setStatus('connected');
            setError(null);
        },
        onDisconnect: () => {
            console.log('Disconnected');
            setStatus('disconnected');
        },
        onMessage: async (message) => {
            console.log('Message:', message);
            try {
                // Display the AI's text response
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message ai';
                messageDiv.textContent = message.text;
                document.querySelector('.messages').appendChild(messageDiv);

                // Get text-to-speech audio for the response
                const audioResponse = await fetch('/api/voice/speak', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ text: message.text })
                });
                
                if (audioResponse.ok) {
                    const audioBlob = await audioResponse.blob();
                    const audioUrl = URL.createObjectURL(audioBlob);
                    const audio = new Audio(audioUrl);
                    await audio.play();
                }
            } catch (error) {
                console.error('Error handling AI response:', error);
                setError('Error playing AI response');
            }
        },
        onError: (error) => {
            console.error('Error:', error);
            setError('Error in voice conversation');
            setStatus('error');
        },
    });

    const startConversation = useCallback(async () => {
        try {
            setError(null);
            // Request microphone permission
            await navigator.mediaDevices.getUserMedia({ audio: true });
            setStatus('connecting');

            // Start the conversation with ElevenLabs agent
            await conversation.startSession({
                agentId: window.AGENT_ID,
                connection: {
                    connectionKey: 'default',
                    resource: 'websocket',
                }
            });

        } catch (error) {
            console.error('Failed to start conversation:', error);
            setError('Failed to start conversation: ' + error.message);
            setStatus('error');
        }
    }, [conversation]);

    const stopConversation = useCallback(async () => {
        try {
            await conversation.endSession();
            setStatus('disconnected');
        } catch (error) {
            console.error('Failed to end conversation:', error);
            setError('Failed to end conversation: ' + error.message);
        }
    }, [conversation]);

    const statusMessage = {
        'disconnected': 'Click the microphone to start speaking',
        'connecting': 'Initializing voice chat...',
        'connected': conversation.isSpeaking ? 'AI is speaking...' : 'Listening...',
        'error': error || 'An error occurred'
    }[status];

    return React.createElement('div', { className: 'voice-chat-container' },
        React.createElement('div', { className: 'voice-interface' },
            React.createElement('div', { 
                className: `voice-status ${status === 'error' ? 'error' : ''}`
            }, statusMessage),
            React.createElement('button', {
                className: `large-voice-button ${status === 'connected' ? 'recording' : ''} ${status === 'error' ? 'error' : ''}`,
                onClick: status === 'connected' ? stopConversation : startConversation,
                disabled: status === 'connecting'
            },
                React.createElement('svg', {
                    xmlns: 'http://www.w3.org/2000/svg',
                    width: 48,
                    height: 48,
                    viewBox: '0 0 24 24',
                    fill: 'none',
                    stroke: 'currentColor',
                    strokeWidth: 2,
                    strokeLinecap: 'round',
                    strokeLinejoin: 'round'
                },
                    React.createElement('path', {
                        d: 'M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z'
                    }),
                    React.createElement('path', {
                        d: 'M19 10v2a7 7 0 0 1-14 0v-2'
                    }),
                    React.createElement('line', {
                        x1: 12,
                        y1: 19,
                        x2: 12,
                        y2: 23
                    }),
                    React.createElement('line', {
                        x1: 8,
                        y1: 23,
                        x2: 16,
                        y2: 23
                    })
                )
            ),
            React.createElement('div', { className: 'messages' })
        )
    );
}

// Initialize React component
document.addEventListener('DOMContentLoaded', function() {
    const root = document.getElementById('voice-chat-root');
    const rootElement = ReactDOM.createRoot(root);
    rootElement.render(React.createElement(VoiceChat));
});