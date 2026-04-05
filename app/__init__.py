from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
limiter = Limiter(key_func=get_remote_address)

log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f'app_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    database_dir = Path('database')
    database_dir.mkdir(exist_ok=True)
    
    # --- VULN: FLAW 5 - Security Misconfiguration, weak SECRET_KEY ---
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'TEST_SECRET_KEY')
    # --- END VULN: FLAW 5 (SECRET_KEY) ---

    # --- FIX: FLAW 5 - Security Misconfiguration, strong SECRET_KEY ---
    # app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(32).hex()
    # --- END FIX: FLAW 5 (SECRET_KEY) ---

    db_path = database_dir / 'app.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f'sqlite:///{db_path.absolute()}')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'True') == 'True'
    
    db.init_app(app)
    limiter.init_app(app)
    
    # --- VULN: FLAW 5 - Security Misconfiguration, open CORS ---
    CORS(app)
    # --- END VULN: FLAW 5 (CORS) ---

    # --- FIX: FLAW 5 - Security Misconfiguration, restricted CORS ---
    # CORS(app, origins=['https://something.com'], supports_credentials=True)
    # --- END FIX: FLAW 5 (CORS) ---
    
    from app.routes import auth_routes, team_routes, task_routes, comment_routes, user_routes, log_routes
    
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(team_routes.bp)
    app.register_blueprint(task_routes.bp)
    app.register_blueprint(comment_routes.bp)
    app.register_blueprint(user_routes.bp)
    app.register_blueprint(log_routes.bp)
    
    @app.route('/')
    def index():
        from flask import redirect, request, g
        from app.auth import verify_jwt
        from app.models import User
        
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.split(' ')[1]
            except:
                pass
        
        if not token:
            token = request.cookies.get('token')
        
        if token:
            payload = verify_jwt(token)
            if payload:
                user = User.query.get(payload['user_id'])
                if user and user.is_active:
                    return redirect('/teams')
        
        return redirect('/login')
    
    @app.route('/favicon.ico')
    def favicon():
        from flask import abort
        abort(404)
    
    @app.after_request
    def set_security_headers(response):
        # --- VULN: FLAW 5 - Security Misconfiguration, headers only in prod ---
        if not app.config.get('DEBUG'):
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
        # --- END VULN: FLAW 5 (security headers) ---
        # --- FIX: FLAW 5 - Security Misconfiguration, always set headers ---
        # response.headers['X-Content-Type-Options'] = 'nosniff'
        # response.headers['X-Frame-Options'] = 'DENY'
        # response.headers['X-XSS-Protection'] = '1; mode=block'
        # response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        # --- END FIX: FLAW 5 (security headers) ---
        return response
    
    @app.errorhandler(Exception)
    def handle_error(e):
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return {'error': 'Internal server error'}, 500
    
    return app

