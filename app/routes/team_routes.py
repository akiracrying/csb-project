from flask import Blueprint, request, jsonify, render_template, g
from app import db
from app.models import Team, TeamMember, User, ActivityLog
from app.auth import require_auth

bp = Blueprint('teams', __name__)

@bp.route('/teams', methods=['GET'])
@require_auth
def teams_page():
    return render_template('teams.html')

@bp.route('/api/teams', methods=['GET'])
@require_auth
def get_teams():
    user_teams = TeamMember.query.filter_by(user_id=g.current_user.id).all()
    team_ids = [tm.team_id for tm in user_teams]
    
    if g.current_user.role == 'app_admin':
        teams = Team.query.all()
    else:
        teams = Team.query.filter(Team.id.in_(team_ids)).all()
    
    return jsonify([team.to_dict() for team in teams])

@bp.route('/api/teams', methods=['POST'])
@require_auth
def create_team():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    
    if not name:
        return jsonify({'error': 'Team name required'}), 400
    
    team = Team(name=name, description=description, created_by=g.current_user.id)
    db.session.add(team)
    db.session.commit()
    
    member = TeamMember(team_id=team.id, user_id=g.current_user.id, role='admin')
    db.session.add(member)
    db.session.commit()
    
    log = ActivityLog(
        user_id=g.current_user.id,
        action='create_team',
        details=f'Created team {name}',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify(team.to_dict()), 201

@bp.route('/api/teams/<int:team_id>', methods=['GET'])
@require_auth
def get_team(team_id):
    team = Team.query.get(team_id)
    if not team:
        return jsonify({'error': 'Team not found'}), 404
    
    member = TeamMember.query.filter_by(team_id=team_id, user_id=g.current_user.id).first()
    if not member and g.current_user.role != 'app_admin':
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(team.to_dict())

@bp.route('/api/teams/<int:team_id>/members', methods=['POST'])
@require_auth
def add_member(team_id):
    team = Team.query.get(team_id)
    if not team:
        return jsonify({'error': 'Team not found'}), 404
    
    member = TeamMember.query.filter_by(team_id=team_id, user_id=g.current_user.id).first()
    if not member or (member.role != 'admin' and g.current_user.role != 'app_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    username = data.get('username')
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    existing = TeamMember.query.filter_by(team_id=team_id, user_id=user.id).first()
    if existing:
        return jsonify({'error': 'User already in team'}), 400
    
    new_member = TeamMember(team_id=team_id, user_id=user.id, role='member')
    db.session.add(new_member)
    db.session.commit()
    
    return jsonify({'success': True}), 201

