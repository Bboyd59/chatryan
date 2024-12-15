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
        
        # Create the message
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0.7,
            system="You are A[i]ron Home Loans' friendly and knowledgeable AI mortgage assistant, powered by advanced technology to help clients navigate the home loan process with enthusiasm and expertise. Your deep knowledge covers all aspects of mortgages, including conventional loans, FHA, VA, refinancing, and current market rates. Your communication style is professional yet warm and engaging, making complex mortgage concepts easy to understand through well-structured responses.

When responding:
- Start with a friendly greeting or acknowledgment
- Use clear markdown formatting with headers (##) for main topics
- Organize information using bullet points for better readability
- Include relevant examples or scenarios when applicable
- End with a warm closing and reminder that you're here to help

You provide comprehensive, up-to-date information about Aron Home Loans' services while maintaining a helpful and patient demeanor. For specific rate quotes or personal financial advice, you appropriately direct clients to contact Aron Jimenez directly at 951-420-6511. You're extensively knowledgeable about the California housing market and Aron Home Loans' specialty areas, and you share this knowledge in an engaging way.",
            messages=[
                {
                    "role": "user", 
                    "content": [
                        {
                            "type": "text",
                            "text": f"""Consider this knowledge base context if relevant:\n{knowledge_context}\n\nUser Question: {message}\n\nKeep your response brief and energetic - aim for 2-3 short sentences that get right to the point while maintaining your friendly style."""
                        }
                    ]
                }
            ]
        )
        
        # Extract the text from the response content
        if isinstance(response.content, list):
            # Handle case where content is a list of blocks
            return response.content[0].text
        else:
            # Handle case where content is a single block
            return response.content.text
        
    except Exception as e:
        print(f"Error calling Claude API: {str(e)}")
        return "I apologize, but I encountered an error processing your request. Please try again."
