from flask import Blueprint, request, jsonify, g
from app import db
from app.models import Comment, Task, TeamMember, ActivityLog
from app.auth import require_auth

bp = Blueprint('comments', __name__)

@bp.route('/api/tasks/<int:task_id>/comments', methods=['GET'])
@require_auth
def get_comments(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    member = TeamMember.query.filter_by(team_id=task.team_id, user_id=g.current_user.id).first()
    if not member and g.current_user.role != 'app_admin':
        return jsonify({'error': 'Access denied'}), 403
    
    comments = Comment.query.filter_by(task_id=task_id).all()
    return jsonify([c.to_dict() for c in comments])

@bp.route('/api/tasks/<int:task_id>/comments', methods=['POST'])
@require_auth
def create_comment(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    member = TeamMember.query.filter_by(team_id=task.team_id, user_id=g.current_user.id).first()
    if not member and g.current_user.role != 'app_admin':
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    content = data.get('content')
    
    if not content:
        return jsonify({'error': 'Content required'}), 400
    
    comment = Comment(task_id=task_id, user_id=g.current_user.id, content=content)
    db.session.add(comment)
    db.session.commit()
    
    return jsonify(comment.to_dict()), 201

@bp.route('/api/comments/<int:comment_id>', methods=['DELETE'])
@require_auth
def delete_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404
    
    task = Task.query.get(comment.task_id)
    member = TeamMember.query.filter_by(team_id=task.team_id, user_id=g.current_user.id).first()
    
    if comment.user_id != g.current_user.id:
        if member and member.role == 'admin':
            pass
        elif g.current_user.role == 'app_admin':
            pass
        else:
            return jsonify({'error': 'Access denied'}), 403
    
    db.session.delete(comment)
    db.session.commit()
    
    return jsonify({'success': True})

