import os
from openai import OpenAI

# The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# Do not change this unless explicitly requested by the user
def get_openai_response(message, stream=False):
    """
    Get response from OpenAI API with optional streaming support
    """
    try:
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are Aron Home Loans' AI mortgage assistant, powered by advanced technology to help clients navigate the home loan process. Your expertise covers all aspects of mortgages, including conventional loans, FHA, VA, refinancing, and current market rates. Your communication style is professional yet approachable, making complex mortgage concepts easy to understand. You provide accurate, up-to-date information about Aron Home Loans' services while maintaining a helpful and patient demeanor. For specific rate quotes or personal financial advice, you appropriately direct clients to contact Aron Jimenez directly at 951-420-6511. You're knowledgeable about the California housing market and Aron Home Loans' specialty areas."
                },
                {
                    "role": "user", 
                    "content": message
                }
            ],
            stream=stream,
            temperature=0.7,
        )
        
        return response

    except Exception as e:
        print(f"Error calling OpenAI API: {str(e)}")
        return None
