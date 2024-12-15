from flask import Blueprint, render_template, jsonify, request, send_file, session, Response
import PyPDF2
from flask_login import login_required, current_user
from models import Chat, Message, User, KnowledgeBase, db
from openai_api import get_openai_response
import elevenlabs_api
import io
import os
import json

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def chat():
    return render_template('chat.html')

@main_bp.route('/api/chat', methods=['POST', 'GET'])
@login_required
def process_message():
    try:
        if request.method == 'POST':
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
            db.session.commit()

            def generate():
                try:
                    stream = get_openai_response(message, stream=True)
                    if not stream:
                        yield f'data: {json.dumps({"error": "Failed to get response from AI"})}\n\n'
                        return

                    full_response = ""
                    for chunk in stream:
                        if chunk.choices[0].delta.content is not None:
                            content = chunk.choices[0].delta.content
                            full_response += content
                            yield f'data: {json.dumps({"chunk": content})}\n\n'
                    
                    if full_response:
                        # Save the complete message to database
                        ai_message = Message(chat_id=chat.id, content=full_response, is_user=False)
                        db.session.add(ai_message)
                        db.session.commit()
                        yield f'data: {json.dumps({"message_id": ai_message.id})}\n\n'
                    else:
                        yield f'data: {json.dumps({"error": "No response content received"})}\n\n'
                except Exception as e:
                    print(f"Streaming error: {str(e)}")
                    yield f'data: {json.dumps({"error": str(e)})}\n\n'

            return Response(
                generate(),
                mimetype='text/event-stream'
            )
            
        elif request.method == 'GET':
            return jsonify({'error': 'Please send a POST request with your message'}), 405
            
    except Exception as e:
        print(f"Error processing message: {str(e)}")
        return jsonify({
            'error': 'Error processing your message. Please try again.'
        }), 500

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