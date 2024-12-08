import os
import anthropic
from anthropic import Anthropic
from models import KnowledgeBase, db

def search_knowledge_base(query):
    """Search the knowledge base for relevant information"""
    knowledge_entries = KnowledgeBase.query.all()
    relevant_info = []
    
    # Simple keyword matching for now
    query_words = set(query.lower().split())
    for entry in knowledge_entries:
        content_words = set(entry.content.lower().split())
        if query_words & content_words:  # If there's any overlap in words
            relevant_info.append(entry.content)
    
    return "\n".join(relevant_info)

def get_claude_response(message):
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    
    try:
        # Search knowledge base for relevant information
        knowledge_context = search_knowledge_base(message)
        
        # Create a more concise system prompt for iRyan
        system_prompt = """You are iRyan, a fun and energetic fitness instructor who loves helping people get fit and feel amazing! Your style is friendly, encouraging, and down-to-earth. You keep things simple, practical, and engaging. While you know your stuff, you focus more on making fitness enjoyable and accessible to everyone. You mix humor with motivation, but always keep safety in mind. For any medical concerns, you kindly suggest checking with a doctor first."""

        # Construct the prompt with knowledge base context
        full_prompt = f"""Consider this knowledge base context if relevant:
{knowledge_context}

User Question: {message}

Provide a concise, practical response. If using general knowledge, make that clear."""

        # Use streaming for the response
        response_chunks = []
        with client.messages.stream(
            model="claude-3-sonnet-20240229",
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": full_prompt}]
        ) as stream:
            for chunk in stream.text_stream:
                response_chunks.append(chunk)
            
        return "".join(response_chunks)
    except Exception as e:
        print(f"Error calling Claude API: {str(e)}")
        return "I apologize, but I encountered an error processing your request. Please try again."
