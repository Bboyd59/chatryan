from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from models import User, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('main.admin'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email, is_admin=True).first()
        
        if user is None:
            flash('Invalid admin credentials')
            return render_template('admin_login.html')
        if not user.check_password(password):
            flash('Invalid password')
            return render_template('admin_login.html')
        
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.admin')
        return redirect(next_page)
    
    return render_template('admin_login.html')

@auth_bp.route('/admin/logout')
@login_required
def admin_logout():
    if current_user.is_admin:
        logout_user()
    return redirect(url_for('main.chat'))
