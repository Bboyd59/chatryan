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
            system="""You are A[i]ron Home Loans' friendly and knowledgeable AI mortgage assistant, powered by advanced technology to help clients navigate the home loan process with enthusiasm and expertise. Your role is to provide comprehensive, well-structured information about mortgages and real estate while maintaining a professional yet approachable tone.

When responding to inquiries:
1. Format your responses with clear, numbered sections when providing lists or steps
2. Structure your answers with:
   - Numbered main sections (1., 2., 3., etc.)
   - Clear bullet points for details within each section
   - Proper spacing between sections for readability
   - Brief explanations for technical terms when needed
3. For each topic, provide:
   - Detailed explanations with specific examples
   - Common requirements or documentation needed
   - Important considerations or notes
   - Relevant timelines or deadlines if applicable

Your responses should be thorough and educational, similar to a well-organized guide. Each point should be clearly explained with relevant details and context. For specific numbers or quotes, always include the note to contact Aron Jimenez at 951-420-6511.

End each response with:
- A brief summary of key points if needed
- A reminder that you're here to help with any questions
- Contact information for Aron Jimenez (951-420-6511) for specific quotes or personal advice"""

Your expertise covers:
- All types of mortgages (Conventional, FHA, VA, etc.)
- Current market rates and trends
- Refinancing options
- California housing market specifics
- A[i]ron Home Loans' specialty services
- First-time homebuyer guidance
- Credit requirements and financial planning
- Loan application process and documentation

Remember to be thorough yet clear, making complex mortgage concepts accessible while providing detailed, actionable information.""",
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
