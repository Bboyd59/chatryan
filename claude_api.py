import os
from openai import OpenAI
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
        
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        
        # Create the message with streaming
        stream = client.chat.completions.create(
            model="gpt-4",
            max_tokens=1000,
            temperature=0.7,
            stream=True,
            messages=[
                {
                    "role": "system",
                    "content": "You are Aron Home Loans' AI mortgage assistant, powered by advanced technology to help clients navigate the home loan process. Your expertise covers all aspects of mortgages, including conventional loans, FHA, VA, refinancing, and current market rates. Your communication style is professional yet approachable, making complex mortgage concepts easy to understand. You provide accurate, up-to-date information about Aron Home Loans' services while maintaining a helpful and patient demeanor. For specific rate quotes or personal financial advice, you appropriately direct clients to contact Aron Jimenez directly at 951-420-6511. You're knowledgeable about the California housing market and Aron Home Loans' specialty areas."
                },
                {
                    "role": "user",
                    "content": f"Consider this knowledge base context if relevant:\n{knowledge_context}\n\nUser Question: {message}\n\nKeep your response brief and energetic - aim for 2-3 short sentences that get right to the point while maintaining your friendly style."
                }
            ]
        )
        
        # Collect the streamed response
        response_text = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                response_text += chunk.choices[0].delta.content
        
        return response_text
        
    except Exception as e:
        print(f"Error calling Claude API: {str(e)}")
        return "I apologize, but I encountered an error processing your request. Please try again."
