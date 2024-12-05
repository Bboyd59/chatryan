import os
import anthropic
from anthropic import Anthropic

def get_claude_response(message):
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    
    try:
        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": message
            }]
        )
        return message.content[0].text
    except Exception as e:
        print(f"Error calling Claude API: {str(e)}")
        return "I apologize, but I encountered an error processing your request. Please try again."
