from flask import Blueprint, request, jsonify, render_template, g
from app import db
from app.models import User, ActivityLog
from app.auth import require_auth, require_admin
from sqlalchemy import text, or_

bp = Blueprint('users', __name__)

@bp.route('/admin/users', methods=['GET'])
@require_auth
def users_page():
    if g.current_user.role != 'app_admin':
        return jsonify({'error': 'Access denied'}), 403
    return render_template('admin/users.html')

@bp.route('/api/users', methods=['GET'])
@require_auth
@require_admin
def get_users():
    search = request.args.get('search', '')
    
    if search:
        query = f"SELECT * FROM users WHERE username LIKE '%{search}%' OR email LIKE '%{search}%'"
        # fix: use parameterized queries to prevent SQL injection
        # from sqlalchemy import or_
        # users = User.query.filter(
        #     or_(
        #         User.username.like(f'%{search}%'),
        #         User.email.like(f'%{search}%')
        #     )
        # ).all()
        # return jsonify([user.to_dict() for user in users])
        result = db.session.execute(text(query))
        users = []
        for row in result:
            user = User.query.get(row[0])
            if user:
                users.append(user.to_dict())
        return jsonify(users)
    
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@bp.route('/api/users/<int:user_id>/role', methods=['PUT'])
@require_auth
@require_admin
def update_user_role(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    role = data.get('role')
    
    if role not in ['user', 'team_admin', 'app_admin']:
        return jsonify({'error': 'Invalid role'}), 400
    
    user.role = role
    db.session.commit()
    
    log = ActivityLog(
        user_id=g.current_user.id,
        action='update_user_role',
        details=f'Changed role of user {user_id} to {role}',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'success': True})

@bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@require_auth
@require_admin
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.id == g.current_user.id:
        return jsonify({'error': 'Cannot delete yourself'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    log = ActivityLog(
        user_id=g.current_user.id,
        action='delete_user',
        details=f'Deleted user {user_id}',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'success': True})

