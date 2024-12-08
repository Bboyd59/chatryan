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
    try:
        # Search knowledge base for relevant information
        knowledge_context = search_knowledge_base(message)
        
        client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        
        # Create a more concise system prompt for iRyan
        system_prompt = """You are iRyan, a fun and energetic fitness instructor who loves helping people get fit and feel amazing! Your style is friendly, encouraging, and down-to-earth. You keep things simple, practical, and engaging. While you know your stuff, you focus more on making fitness enjoyable and accessible to everyone. You mix humor with motivation, but always keep safety in mind. For any medical concerns, you kindly suggest checking with a doctor first."""

        # Construct the message with knowledge base context
        full_prompt = f"""Consider this knowledge base context if relevant:
{knowledge_context}

User Question: {message}

Keep your response brief and energetic - aim for 2-3 short sentences that get right to the point while maintaining your friendly style."""

        with client.messages.stream(
            max_tokens=1024,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_prompt}
            ],
            model="claude-3-sonnet-20240229"
        ) as stream:
            for text in stream.text_stream:
                yield text
    except Exception as e:
        print(f"Error calling Claude API: {str(e)}")
        yield "I apologize, but I encountered an error processing your request. Please try again."
