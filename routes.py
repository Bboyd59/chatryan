from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from models import Chat, Message, User, db
from claude_api import get_claude_response

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
    
    # Get Claude's response
    claude_response = get_claude_response(message)
    ai_message = Message(chat_id=chat.id, content=claude_response, is_user=False)
    db.session.add(ai_message)
    
    db.session.commit()
    
    return jsonify({
        'response': claude_response
    })

@main_bp.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        return render_template('error.html', message="Access denied"), 403
    
    users = User.query.all()
    chats = Chat.query.all()
    return render_template('admin.html', users=users, chats=chats)
