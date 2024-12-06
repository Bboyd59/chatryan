from flask import Blueprint, render_template, jsonify, request, send_file
import io
import PyPDF2
from flask_login import login_required, current_user
from models import Chat, Message, User, KnowledgeBase, db
from claude_api import get_claude_response
from voice_chat import start_voice_session, end_voice_session, create_voice_response

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def chat():
    return render_template('chat.html')
@main_bp.route('/voice')
@login_required
def voice_chat():
    agent_id = os.environ.get('AGENT_ID')
    return render_template('voice_chat.html', agent_id=agent_id)


@main_bp.route('/api/chat', methods=['POST'])
@login_required
def process_message():
    data = request.json
    message = data.get('message')
    
    # Create new chat if needed
    chat = Chat.query.filter_by(user_id=current_user.id).order_by(Chat.created_at.desc()).first()
    if not chat:
        chat = Chat(user_id=current_user.id)
        db.session.add(chat)
        db.session.commit()
    
    # Save user message
    user_message = Message(chat_id=chat.id, content=message, is_user=True)
    db.session.add(user_message)
    
    # Search knowledge base first
    kb_entries = KnowledgeBase.query.all()
    relevant_info = ""
    
    for entry in kb_entries:
        if any(keyword.lower() in entry.content.lower() for keyword in message.split()):
            relevant_info += f"\n\nRelevant information from knowledge base: {entry.content}"
    
    # Get Claude's response with context from knowledge base
    if relevant_info:
        context = f"Please use this additional context while answering: {relevant_info}\n\nUser question: {message}"
        claude_response = get_claude_response(context)
    else:
        claude_response = get_claude_response(message)
    
    ai_message = Message(chat_id=chat.id, content=claude_response, is_user=False)
    db.session.add(ai_message)
    
    db.session.commit()
    
    return jsonify({
        'response': claude_response
    })

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

@main_bp.route('/api/voice/start', methods=['POST'])
@login_required
def start_voice():
    try:
        # Create a new chat session
        chat = Chat(user_id=current_user.id)
        db.session.add(chat)
        db.session.commit()
        
        def on_agent_response(response):
            message = Message(
                chat_id=chat.id,
                content=response,
                is_user=False
            )
            db.session.add(message)
            db.session.commit()
            logger.info(f"Agent response saved: {response}")
        
        def on_user_transcript(transcript):
            message = Message(
                chat_id=chat.id,
                content=transcript,
                is_user=True
            )
            db.session.add(message)
            db.session.commit()
            logger.info(f"User transcript saved: {transcript}")
        
        # Start conversation with callbacks
        from voice_conversation import voice_manager
        conversation_id = voice_manager.create_conversation(
            on_response=on_agent_response,
            on_transcript=on_user_transcript
        )
        
        if conversation_id:
            return jsonify({'status': 'success', 'message': 'Voice session started'})
        return jsonify({'error': 'Failed to start voice session'}), 500
        
    except Exception as e:
        logger.error(f"Error in start_voice: {str(e)}")
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/voice/end', methods=['POST'])
@login_required
def end_voice():
    try:
        from voice_conversation import voice_manager
        if voice_manager.end_conversation():
            return jsonify({
                'status': 'success',
                'message': 'Voice session ended'
            })
        return jsonify({'error': 'Failed to end voice session'}), 500
    except Exception as e:
        logger.error(f"Error in end_voice: {str(e)}")
        return jsonify({'error': str(e)}), 500
