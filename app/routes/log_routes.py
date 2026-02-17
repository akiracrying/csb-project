from flask import Blueprint, request, jsonify, render_template, g
from app import db
from app.models import ActivityLog
from app.auth import require_auth, require_admin

bp = Blueprint('logs', __name__)

@bp.route('/admin/logs', methods=['GET'])
@require_auth
def logs_page():
    if g.current_user.role != 'app_admin':
        return jsonify({'error': 'Access denied'}), 403
    return render_template('admin/logs.html')

@bp.route('/api/logs', methods=['GET'])
@require_auth
@require_admin
def get_logs():
    user_id = request.args.get('user_id', type=int)
    action = request.args.get('action')
    limit = request.args.get('limit', 100, type=int)
    
    query = ActivityLog.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    if action:
        query = query.filter_by(action=action)
    
    logs = query.order_by(ActivityLog.created_at.desc()).limit(limit).all()
    return jsonify([log.to_dict() for log in logs])

