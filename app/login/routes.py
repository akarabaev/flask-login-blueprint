import requests

from flask import render_template, request, url_for, jsonify
from flask_login import current_user, login_user, logout_user
from werkzeug.utils import redirect

from .. import db
from ..login import bp
from ..models import User


def send_email(recipient_email, email_subject, email_text):
    response = requests.post(
        'http://localhost:5465',
        json={
            'recipient_email': recipient_email,
            'email_subject': email_subject,
            'email_text': email_text
        }
    )
    if response.status_code != 200:
        raise Exception(response.text)



@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main_page_bp.index'))
    
    if request.method == 'POST':
        payload = request.get_json()
        email = payload.get('email')
        if User.query.filter_by(email=email).first():
            return jsonify({'formErrorMessage': 'Пользователь с таким email уже существует'})
        
        password = payload.get('password')
        user = User(email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        return jsonify({'redirect_url': '/login?flash=successfulRegistration'})
    return render_template('register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        payload = request.get_json()
        email = payload.get('email')
        password = payload.get('password')
        remember_me = bool(payload.get('remember_me'))

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'formErrorMessage': 'Неправильный логин или пароль'})
        
        is_password_correct = user.check_password(password)
        if not is_password_correct:
            return jsonify({'formErrorMessage': 'Неправильный логин или пароль'})
        
        login_user(user, remember=remember_me)
        return jsonify({'redirect_url': '/'})
    return render_template('login.html')


@bp.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({'redirect_url': '/login'})


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main_page_bp.index'))
    if request.method == 'POST':
        payload = request.get_json()
        email = payload.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            token = user.get_reset_password_token()
            reset_link = url_for('login_bp.reset_password', token=token, _external=True)
            send_email(
                recipient_email=user.email, 
                email_subject='Сброс пароля', 
                email_text=f"Чтобы сбросить пароль, перейдите по ссылке: {reset_link}"
            )
        
        return jsonify({'outputMessage': 'Ссылка для сброса пароля отправлена на вашу почту'})
    return render_template('reset_password_request.html')
            

@bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if current_user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        payload = request.get_json()
        token = payload.get('token')
        password = payload.get('password')
        user = User.verify_reset_password_token(token)
        if not user:
            return jsonify({'formErrorMessage': 'Вы перешли по некорректной ссылке для сброса пароля'})
        
        user.set_password(password)
        db.session.commit()
        return jsonify({'redirect_url': url_for('login_bp.login', flash='successfulResetPassword')})
    
    return render_template('reset_password.html')

