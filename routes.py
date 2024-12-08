from flask import Blueprint, render_template, jsonify, request, send_file, session
import PyPDF2
from flask_login import login_required, current_user
from models import Chat, Message, User, KnowledgeBase, db
from claude_api import get_claude_response
from elevenlabs_api import start_conversation, send_message, end_conversation
import io

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def chat():
    return render_template('chat.html')

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
    
    # Check if voice mode is enabled
    voice_enabled = request.json.get('voice_enabled', False)
    
    if voice_enabled:
        # Initialize or get existing conversation
        conversation = session.get('eleven_conversation')
        if not conversation:
            conversation = start_conversation()
            if not conversation:
                return jsonify({'error': 'Failed to start ElevenLabs conversation'}), 500
            session['eleven_conversation'] = conversation
        
        # Get ElevenLabs conversational response
        response = send_message(conversation, message)
        
        if response and response.get('text'):
            ai_message = Message(chat_id=chat.id, content=response['text'], is_user=False)
            db.session.add(ai_message)
            db.session.commit()
            
            return jsonify({
                'response': response['text'],
                'has_audio': bool(response.get('audio')),
                'message_id': ai_message.id,
                'audio': response.get('audio'),
                'conversation_id': response.get('conversation_id')
            })
    
    # Fallback to Claude or if voice is not enabled
    claude_response = get_claude_response(message)
    ai_message = Message(chat_id=chat.id, content=claude_response, is_user=False)
    db.session.add(ai_message)
    db.session.commit()
    
    return jsonify({
        'response': claude_response,
        'has_audio': False,
        'message_id': ai_message.id
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
    return render_template('admin.html', users=users, chats=chats, knowledge_base=knowledge_base)

@main_bp.route('/api/audio-response/<int:message_id>')
@login_required
def get_audio_response(message_id):
    message = Message.query.get_or_404(message_id)
    if message.chat.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    audio_data = text_to_speech(message.content)
    if audio_data:
        return send_file(
            io.BytesIO(audio_data),
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name='response.mp3'
        )
    return jsonify({'error': 'Failed to generate audio'}), 500