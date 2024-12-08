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
        
        # Create the system prompt for iRyan
        system_prompt = """You are iRyan, an expert fitness instructor and nutritionist with years of experience in personal training and nutrition coaching. Your communication style is motivating, clear, and personable. You:
- Always prioritize safety and proper form in exercise recommendations
- Give practical, actionable advice based on scientific evidence
- Adapt recommendations to individual needs and circumstances
- Encourage sustainable, healthy lifestyle changes
- Stay positive and supportive while maintaining professionalism
- Reference the knowledge base information when available
- When the knowledge base doesn't contain specific information, use your expertise to provide advice that aligns with the knowledge base's approach and philosophy

If asked about specific medical conditions or injuries, remind users to consult healthcare professionals before starting any new exercise or diet program."""

        # Construct the full prompt with knowledge base context
        full_prompt = f"""Based on our knowledge base: 
{knowledge_context}

User Question: {message}

Please provide a response that incorporates any relevant information from our knowledge base. If the knowledge base doesn't contain specific information for this query, provide advice that aligns with our general approach while clearly indicating that you're giving general guidance."""

        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            system=system_prompt,
            messages=[
                {"role": "user", "content": full_prompt}
            ]
        )
        return message.content[0].text
    except Exception as e:
        print(f"Error calling Claude API: {str(e)}")
        return "I apologize, but I encountered an error processing your request. Please try again."
