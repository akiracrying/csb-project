from flask import Blueprint, request, jsonify, render_template, g
from app import db
from app.models import Task, TeamMember, Comment, ActivityLog
from app.auth import require_auth
from sqlalchemy import text

bp = Blueprint('tasks', __name__)

@bp.route('/tasks', methods=['GET'])
@require_auth
def tasks_page():
    return render_template('tasks.html')

@bp.route('/api/tasks', methods=['GET'])
@require_auth
def get_tasks():
    team_id = request.args.get('team_id', type=int)
    status = request.args.get('status')
    search = request.args.get('search', '')
    
    user_teams = TeamMember.query.filter_by(user_id=g.current_user.id).all()
    team_ids = [tm.team_id for tm in user_teams]
    
    if search:
        query = f"SELECT * FROM tasks WHERE (title LIKE '%{search}%' OR description LIKE '%{search}%')"
    else:
        if g.current_user.role == 'app_admin':
            query = "SELECT * FROM tasks WHERE 1=1"
        else:
            if not team_ids:
                query = "SELECT * FROM tasks WHERE 1=0"
            else:
                query = f"SELECT * FROM tasks WHERE team_id IN ({','.join(map(str, team_ids))})"
    
    if team_id and not search:
        query += f" AND team_id = {team_id}"
    
    if status and not search:
        query += f" AND status = '{status}'"
    
    # fix: use parameterized queries to prevent SQL injection
    # from sqlalchemy import or_
    # if search:
    #     tasks_query = Task.query.filter(
    #         or_(
    #             Task.title.like(f'%{search}%'),
    #             Task.description.like(f'%{search}%')
    #         )
    #     )
    # else:
    #     tasks_query = Task.query
    # 
    # if team_id:
    #     tasks_query = tasks_query.filter_by(team_id=team_id)
    # if status:
    #     tasks_query = tasks_query.filter_by(status=status)
    # 
    # if g.current_user.role != 'app_admin':
    #     tasks_query = tasks_query.filter(Task.team_id.in_(team_ids))
    # 
    # tasks = tasks_query.all()
    # return jsonify([task.to_dict() for task in tasks])
    
    # fix: use parameterized queries to prevent SQL injection
    # from sqlalchemy import or_
    # if search:
    #     tasks_query = Task.query.filter(
    #         or_(
    #             Task.title.like(f'%{search}%'),
    #             Task.description.like(f'%{search}%')
    #         )
    #     )
    # else:
    #     tasks_query = Task.query
    # 
    # if team_id:
    #     tasks_query = tasks_query.filter_by(team_id=team_id)
    # if status:
    #     tasks_query = tasks_query.filter_by(status=status)
    # 
    # if g.current_user.role != 'app_admin':
    #     tasks_query = tasks_query.filter(Task.team_id.in_(team_ids))
    # 
    # tasks = tasks_query.all()
    # return jsonify([task.to_dict() for task in tasks])
    
    # fix: use parameterized queries to prevent SQL injection
    # from sqlalchemy import or_
    # if search:
    #     tasks_query = Task.query.filter(
    #         or_(
    #             Task.title.like(f'%{search}%'),
    #             Task.description.like(f'%{search}%')
    #         )
    #     )
    # else:
    #     tasks_query = Task.query
    # 
    # if team_id:
    #     tasks_query = tasks_query.filter_by(team_id=team_id)
    # if status:
    #     tasks_query = tasks_query.filter_by(status=status)
    # 
    # if g.current_user.role != 'app_admin':
    #     tasks_query = tasks_query.filter(Task.team_id.in_(team_ids))
    # 
    # tasks = tasks_query.all()
    # return jsonify([task.to_dict() for task in tasks])
    
    result = db.session.execute(text(query))
    tasks = []
    for row in result:
        task = Task.query.get(row[0])
        if task:
            tasks.append(task.to_dict())
    
    return jsonify(tasks)

@bp.route('/api/tasks', methods=['POST'])
@require_auth
def create_task():
    data = request.get_json()
    team_id = data.get('team_id')
    title = data.get('title')
    description = data.get('description', '')
    status = data.get('status', 'todo')
    priority = data.get('priority', 'medium')
    assigned_to = data.get('assigned_to')
    
    if not team_id or not title:
        return jsonify({'error': 'Team ID and title required'}), 400
    
    member = TeamMember.query.filter_by(team_id=team_id, user_id=g.current_user.id).first()
    if not member and g.current_user.role != 'app_admin':
        return jsonify({'error': 'Access denied'}), 403
    
    task = Task(
        team_id=team_id,
        title=title,
        description=description,
        status=status,
        priority=priority,
        created_by=g.current_user.id,
        assigned_to=assigned_to
    )
    db.session.add(task)
    db.session.commit()
    
    log = ActivityLog(
        user_id=g.current_user.id,
        action='create_task',
        details=f'Created task {title}',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify(task.to_dict()), 201

@bp.route('/api/tasks/<int:task_id>', methods=['GET'])
@require_auth
def get_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    # fix: check if user has access to the team that owns this task
    # member = TeamMember.query.filter_by(team_id=task.team_id, user_id=g.current_user.id).first()
    # if not member and g.current_user.role != 'app_admin':
    #     return jsonify({'error': 'Access denied'}), 403
    
    comments = Comment.query.filter_by(task_id=task_id).all()
    task_dict = task.to_dict()
    task_dict['comments'] = [c.to_dict() for c in comments]
    
    return jsonify(task_dict)

@bp.route('/api/tasks/<int:task_id>', methods=['PUT'])
@require_auth
def update_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    member = TeamMember.query.filter_by(team_id=task.team_id, user_id=g.current_user.id).first()
    if not member and g.current_user.role != 'app_admin':
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'status' in data:
        task.status = data['status']
    if 'priority' in data:
        task.priority = data['priority']
    if 'assigned_to' in data:
        task.assigned_to = data['assigned_to']
    
    db.session.commit()
    
    return jsonify(task.to_dict())

@bp.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@require_auth
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    member = TeamMember.query.filter_by(team_id=task.team_id, user_id=g.current_user.id).first()
    if member and member.role == 'admin':
        pass
    elif g.current_user.role == 'app_admin':
        pass
    else:
        return jsonify({'error': 'Access denied'}), 403
    
    db.session.delete(task)
    db.session.commit()
    
    log = ActivityLog(
        user_id=g.current_user.id,
        action='delete_task',
        details=f'Deleted task {task_id}',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'success': True})

