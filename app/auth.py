from functools import wraps
from flask import request, g, jsonify
import jwt
from datetime import datetime, timedelta
from app import db
from app.models import User
import os

def generate_jwt(user):
    # fix: use shorter token expiration (e.g., 1 hour) and implement refresh tokens
    # payload = {
    #     'user_id': user.id,
    #     'username': user.username,
    #     'role': user.role,
    #     'exp': datetime.utcnow() + timedelta(hours=1)
    # }
    payload = {
        'user_id': user.id,
        'username': user.username,
        'role': user.role,
        'exp': datetime.utcnow() + timedelta(days=365)
    }
    secret = os.environ.get('SECRET_KEY', 'TEST_SECRET_KEY')
    token = jwt.encode(payload, secret, algorithm='HS256')
    return token

def verify_jwt(token):
    try:
        secret = os.environ.get('SECRET_KEY', 'TEST_SECRET_KEY')
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        import logging
        logger = logging.getLogger(__name__)
        
        token = None
        auth_header = request.headers.get('Authorization')
        
        logger.info(f"Auth check for {request.path} - Auth header: {auth_header is not None}")
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]
                logger.info(f"Token extracted from header: {token[:20]}...")
            except IndexError:
                logger.warning("Invalid token format in Authorization header")
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            token = request.cookies.get('token')
            if token:
                logger.info(f"Token found in cookies: {token[:20]}...")
        
        if not token:
            logger.warning(f"No token found for {request.path}")
            return jsonify({'error': 'Authentication required'}), 401
        
        payload = verify_jwt(token)
        if not payload:
            logger.warning(f"Invalid or expired token for {request.path}")
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        user = User.query.get(payload['user_id'])
        if not user or not user.is_active:
            logger.warning(f"User not found or inactive: {payload.get('user_id')}")
            return jsonify({'error': 'User not found or inactive'}), 401
        
        logger.info(f"User authenticated: {user.username} for {request.path}")
        g.current_user = user
        g.token_payload = payload
        return f(*args, **kwargs)
    
    return decorated_function

def require_admin(f):
    @wraps(f)
    @require_auth
    def decorated_function(*args, **kwargs):
        from flask import g
        # fix: check role from database, not from token
        # if g.current_user.role != 'app_admin':
        #     return jsonify({'error': 'Admin access required'}), 403
        token_role = g.token_payload.get('role', 'user')
        if token_role != 'app_admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    
    return decorated_function

