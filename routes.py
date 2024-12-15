from flask import Blueprint, render_template, jsonify, request, send_file, session, Response
import PyPDF2
from flask_login import login_required, current_user
from models import Chat, Message, User, KnowledgeBase, db
from claude_api import get_claude_response
import elevenlabs_api
import io
import os

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
    voice_enabled = request.json.get('voice_enabled', False)
    
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
    
    # Create AI message placeholder
    ai_message = Message(chat_id=chat.id, content="", is_user=False)
    db.session.add(ai_message)
    db.session.commit()
    
    def generate_streaming_response():
        full_response = ""
        try:
            for chunk in get_claude_response(message):
                full_response += chunk
                yield f"data: {json.dumps({'chunk': chunk, 'message_id': ai_message.id})}\n\n"
            
            # Update the complete message in database
            ai_message.content = full_response
            db.session.commit()
            
            # Handle voice response if enabled
            if voice_enabled:
                try:
                    print("Voice mode enabled, processing with ElevenLabs...")
                    conversation = elevenlabs_api.create_conversation()
                    if conversation:
                        response = elevenlabs_api.send_message(conversation, full_response)
                        if response and response.get('audio'):
                            audio = response['audio']
                            audio_b64 = base64.b64encode(audio).decode('utf-8')
                            yield f"data: {json.dumps({'audio': audio_b64, 'message_id': ai_message.id})}\n\n"
                except Exception as e:
                    print(f"Error in voice processing: {str(e)}")
                    
        except Exception as e:
            print(f"Error in streaming response: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
        yield "data: [DONE]\n\n"
    
    return Response(
        generate_streaming_response(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )

@main_bp.route('/admin/knowledge/<int:entry_id>', methods=['DELETE'])
@login_required
def delete_knowledge(entry_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
        
    entry = KnowledgeBase.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    
    return jsonify({'message': 'Entry deleted successfully'})

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