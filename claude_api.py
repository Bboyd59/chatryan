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
        system_prompt = """You are iRyan, a fitness instructor focused on practical, evidence-based advice. Be concise, clear, and motivating. Prioritize safety and proper form. For medical questions, advise consulting healthcare professionals."""

        # Construct the prompt with knowledge base context
        full_prompt = f"""Consider this knowledge base context if relevant:
{knowledge_context}

User Question: {message}

Provide a concise, practical response. If using general knowledge, make that clear."""

        # Use streaming for the response
        stream = client.messages.stream(
            model="claude-3-sonnet-20240229",
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": full_prompt}]
        )
        
        response_chunks = []
        for chunk in stream:
            if chunk.type == "content_block_delta":
                response_chunks.append(chunk.text)
            
        return "".join(response_chunks)
    except Exception as e:
        print(f"Error calling Claude API: {str(e)}")
        return "I apologize, but I encountered an error processing your request. Please try again."
