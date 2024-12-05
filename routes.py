from flask import Blueprint, render_template, jsonify, request, Response, stream_with_context
import PyPDF2
import os
import json
from flask_login import login_required, current_user
from models import Chat, Message, User, KnowledgeBase, db
from claude_api import get_claude_response
import asyncio
from flask import current_app
import httpx

def process_stream(message):
    # Create new chat if needed
    chat = Chat.query.filter_by(user_id=current_user.id).order_by(Chat.created_at.desc()).first()
    if not chat:
        chat = Chat(user_id=current_user.id)
        db.session.add(chat)
        db.session.commit()
    
    # Save user message
    user_message = Message(chat_id=chat.id, content=message, is_user=True)
    db.session.add(user_message)
    db.session.commit()
    
    # Search knowledge base
    kb_entries = KnowledgeBase.query.all()
    relevant_info = ""
    
    for entry in kb_entries:
        if any(keyword.lower() in entry.content.lower() for keyword in message.split()):
            relevant_info += f"\n\nRelevant information from knowledge base: {entry.content}"
    
    # Get Claude's streaming response
    response_text = ""
    if relevant_info:
        context = f"Please use this additional context while answering: {relevant_info}\n\nUser question: {message}"
        for chunk in get_claude_response(context, stream=True):
            response_text += chunk
            yield f"data: {json.dumps({'response': chunk})}\n\n"
    else:
        for chunk in get_claude_response(message, stream=True):
            response_text += chunk
            yield f"data: {json.dumps({'response': chunk})}\n\n"
    
    # Save AI response
    ai_message = Message(chat_id=chat.id, content=response_text, is_user=False)
    db.session.add(ai_message)
    db.session.commit()
    
    yield "data: [DONE]\n\n"

# Initialize fal.ai configuration
FAL_KEY = os.getenv('FAL_KEY')

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def chat():
    return render_template('chat.html')

@main_bp.route('/api/chat', methods=['POST'])
@login_required
async def process_message():
    data = request.json
    message = data.get('message')
    is_image_mode = data.get('isImageMode', False)
    
    # Create new chat if needed
    chat = Chat.query.filter_by(user_id=current_user.id).order_by(Chat.created_at.desc()).first()
    if not chat:
        chat = Chat(user_id=current_user.id)
        db.session.add(chat)
        db.session.commit()
    
    # Save user message
    user_message = Message(chat_id=chat.id, content=message, is_user=True)
    db.session.add(user_message)
    db.session.commit()
    
    if is_image_mode:
        error_msg = None
        try:
            # Call fal.ai API for image generation
            if not FAL_KEY:
                raise ValueError("FAL_KEY environment variable is not configured")
            
            from fal import FalClient
            fal = FalClient(FAL_KEY)
            
            @retry_with_exponential_backoff(max_retries=3, initial_delay=1, max_delay=10)
            async def generate_image(prompt):
                try:
                    # Use the fal.ai client to generate image with better error handling
                    result = await fal.submit(
                        model="fal-ai/flux-pro/v1.1-ultra",
                        input_data={
                            "prompt": prompt,
                            "num_images": 1,
                            "enable_safety_checker": True,
                            "safety_tolerance": "2",
                            "aspect_ratio": "16:9"
                        }
                    )
                    
                    if not result or not result.data or 'images' not in result.data:
                        raise ValueError("Invalid response format from image generation API")
                    
                    return result.data['images'][0]['url']
                except Exception as e:
                    current_app.logger.error(f"Error generating image: {str(e)}")
                    raise
            
            # Generate image with retry mechanism
            image_url = await generate_image(message)
            response = f"![Generated Image]({image_url})"
            
            # Save AI response
            ai_message = Message(chat_id=chat.id, content=response, is_user=False)
            db.session.add(ai_message)
            db.session.commit()
            
            return jsonify({
                'response': response,
                'success': True
            })
            
        except ValueError as ve:
            error_msg = f"Configuration error: {str(ve)}"
            current_app.logger.error(f"Configuration error in image generation: {str(ve)}")
        except fal.exceptions.AuthenticationError:
            error_msg = "Authentication failed. Please check your FAL API key."
            current_app.logger.error("FAL API authentication failed")
        except fal.exceptions.RateLimitError:
            error_msg = "Rate limit exceeded. Please try again later."
            current_app.logger.error("FAL API rate limit exceeded")
        except fal.exceptions.ServerError:
            error_msg = "The image generation service is temporarily unavailable. Please try again later."
            current_app.logger.error("FAL API server error")
        except Exception as e:
            error_msg = "An unexpected error occurred while generating the image. Please try again."
            current_app.logger.error(f"Unexpected error in image generation: {str(e)}")
        
        if error_msg:
            # Save error message
            ai_message = Message(chat_id=chat.id, content=error_msg, is_user=False)
            db.session.add(ai_message)
            db.session.commit()
            
            return jsonify({
                'response': error_msg,
                'success': False,
                'error': str(error_msg)
            }), 500
    else:
        # For text chat, return a streaming response
        def generate():
            # Search knowledge base
            kb_entries = KnowledgeBase.query.all()
            relevant_info = ""
            
            for entry in kb_entries:
                if any(keyword.lower() in entry.content.lower() for keyword in message.split()):
                    relevant_info += f"\n\nRelevant information from knowledge base: {entry.content}"
            
            # Get Claude's streaming response
            response_text = ""
            if relevant_info:
                context = f"Please use this additional context while answering: {relevant_info}\n\nUser question: {message}"
                for chunk in get_claude_response(context, stream=True):
                    response_text += chunk
                    yield f"data: {json.dumps({'response': chunk})}\n\n"
            else:
                for chunk in get_claude_response(message, stream=True):
                    response_text += chunk
                    yield f"data: {json.dumps({'response': chunk})}\n\n"
            
            # Save AI response
            ai_message = Message(chat_id=chat.id, content=response_text, is_user=False)
            db.session.add(ai_message)
            db.session.commit()
            
            yield "data: [DONE]\n\n"
        
        return Response(stream_with_context(generate()), mimetype='text/event-stream')

@main_bp.route('/admin/upload-knowledge', methods=['POST'])
@login_required
def upload_knowledge():
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
        
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    if not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are supported'}), 400
    
    try:
        # Read PDF content
        pdf_reader = PyPDF2.PdfReader(file)
        content = ""
        for page in pdf_reader.pages:
            content += page.extract_text() + "\n"
        
        # Create knowledge base entry
        kb_entry = KnowledgeBase(
            title=file.filename,
            content=content,
            source_file=file.filename,
            content_type='pdf'
        )
        
        db.session.add(kb_entry)
        db.session.commit()
        
        return jsonify({
            'message': 'PDF uploaded and processed successfully',
            'entry': kb_entry.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        return render_template('error.html', message="Access denied"), 403
    
    users = User.query.all()
    chats = Chat.query.all()
    knowledge_base = KnowledgeBase.query.order_by(KnowledgeBase.updated_at.desc()).all()
    return render_template('admin.html', users=users, chats=chats, knowledge_base=knowledge_base)
