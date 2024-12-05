import os
import json
import httpx
from sseclient import SSEClient

def get_claude_response(message, stream=True):
    api_key = os.environ["ANTHROPIC_API_KEY"]
    headers = {
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
        "x-api-key": api_key
    }
    
    data = {
        "model": "claude-3-sonnet-20241022",
        "messages": [{"role": "user", "content": message}],
        "max_tokens": 1024,
        "stream": stream
    }

    try:
        if stream:
            response = httpx.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                stream=True
            )
            response.raise_for_status()
            
            client = SSEClient(response)
            full_response = ""
            
            for event in client.events():
                if event.data != "[DONE]":
                    try:
                        data = json.loads(event.data)
                        if "text" in data.get("delta", {}):
                            text_chunk = data["delta"]["text"]
                            full_response += text_chunk
                            yield text_chunk
                    except json.JSONDecodeError:
                        continue
            
            return full_response
        else:
            # Non-streaming response
            response = httpx.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json={**data, "stream": False}
            )
            response.raise_for_status()
            return response.json()["content"][0]["text"]
            
    except Exception as e:
        error_msg = "I apologize, but I encountered an error processing your request. Please try again."
        if stream:
            yield error_msg
        return error_msg
