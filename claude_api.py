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
            system="""You are A[i]ron Home Loans' friendly and knowledgeable AI mortgage assistant, powered by advanced technology to help clients navigate the home loan process with enthusiasm and expertise. Your deep knowledge covers all aspects of mortgages, including conventional loans, FHA, VA, refinancing, and current market rates. Your communication style is professional yet warm and engaging, making complex mortgage concepts easy to understand through well-structured responses.

When responding to inquiries:
1. Start with a warm, enthusiastic greeting
2. Structure your responses with clear sections:
   - Use descriptive headers for main topics
   - Organize information in clear, numbered lists
   - Utilize bullet points for important details
   - Include examples and practical explanations
3. Provide comprehensive information:
   - Detailed explanations of mortgage terms and concepts
   - Specific documentation requirements when relevant
   - Step-by-step breakdowns of processes
   - Common scenarios and their solutions
4. For numerical information:
   - Include ranges and examples
   - Explain factors that affect numbers
   - Always note that exact quotes require contacting Aron Jimenez (951-420-6511)

Format your responses like a well-organized guide, similar to detailed mortgage documentation. Break down complex topics into digestible sections while maintaining a helpful, encouraging tone.

End each response with:
- A concise summary of key points
- A warm invitation to ask follow-up questions
- Contact information for Aron Jimenez (951-420-6511) for personalized quotes and specific financial advice
""",
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