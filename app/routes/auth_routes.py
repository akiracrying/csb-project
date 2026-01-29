from flask import Blueprint, request, jsonify, render_template
from app import db, limiter
from app.models import User, ActivityLog
from app.auth import generate_jwt, require_auth
from datetime import datetime

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

@bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({'error': 'Missing required fields'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    token = generate_jwt(user)
    
    log = ActivityLog(
        user_id=user.id,
        action='register',
        details=f'User {username} registered',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    response = jsonify({'token': token, 'user': user.to_dict()})
    response.set_cookie('token', token, httponly=False, samesite='Lax')
    return response, 201

@bp.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@bp.route('/api/login', methods=['POST'])
# fix: add rate limiting to prevent bruteforce attacks
# @limiter.limit("5 per minute")
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400
    
    user = User.query.filter_by(username=username).first()
    # fix: use generic error message to prevent user enumeration
    # if not user or not user.check_password(password):
    #     return jsonify({'error': 'Invalid username or password'}), 401
    if not user:
        return jsonify({'error': 'User not found'}), 401
    
    if not user.check_password(password):
        return jsonify({'error': 'Invalid password'}), 401
    
    token = generate_jwt(user)
    
    log = ActivityLog(
        user_id=user.id,
        action='login',
        details=f'User {username} logged in',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    response = jsonify({'token': token, 'user': user.to_dict()})
    response.set_cookie('token', token, httponly=False, samesite='Lax')
    return response, 200

@bp.route('/api/me', methods=['GET'])
@require_auth
def get_current_user():
    from flask import g
    try:
        user_dict = g.current_user.to_dict()
        return jsonify(user_dict)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in get_current_user: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to get user info'}), 500

