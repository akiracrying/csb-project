from app import create_app, db
from app.models import User, Team, TeamMember, Task, Comment, ActivityLog

app = create_app()

with app.app_context():
    print('Dropping all tables...')
    db.drop_all()
    print('Creating tables...')
    db.create_all()
    
    print('Creating users...')
    alice = User(username='alice', email='alice@company.com')
    alice.set_password('alice')
    alice.role = 'user'
    db.session.add(alice)
    
    bob = User(username='bob', email='bob@company.com')
    bob.set_password('bob')
    bob.role = 'user'
    db.session.add(bob)
    
    charlie = User(username='charlie', email='charlie@company.com')
    charlie.set_password('charlie')
    charlie.role = 'user'
    db.session.add(charlie)
    
    admin = User(username='admin', email='admin@company.com')
    admin.set_password('admin')
    admin.role = 'app_admin'
    db.session.add(admin)
    
    testuser = User(username='testuser', email='testuser@company.com')
    testuser.set_password('testuser')
    testuser.role = 'user'
    db.session.add(testuser)
    
    db.session.commit()
    print(f'Created users: alice (id={alice.id}), bob (id={bob.id}), charlie (id={charlie.id}), admin (id={admin.id}), testuser (id={testuser.id})')
    
    print('Creating teams...')
    dev_team = Team(name='Development Team', description='Main development team working on the product', created_by=alice.id)
    db.session.add(dev_team)
    
    qa_team = Team(name='QA Team', description='Quality assurance and testing team', created_by=bob.id)
    db.session.add(qa_team)
    
    ops_team = Team(name='Operations Team', description='DevOps and infrastructure management', created_by=charlie.id)
    db.session.add(ops_team)
    
    db.session.commit()
    print(f'Created teams: Development (id={dev_team.id}), QA (id={qa_team.id}), Operations (id={ops_team.id})')
    
    print('Adding team members...')
    member1 = TeamMember(team_id=dev_team.id, user_id=alice.id, role='admin')
    db.session.add(member1)
    
    member2 = TeamMember(team_id=dev_team.id, user_id=bob.id, role='member')
    db.session.add(member2)
    
    member3 = TeamMember(team_id=qa_team.id, user_id=bob.id, role='admin')
    db.session.add(member3)
    
    member4 = TeamMember(team_id=qa_team.id, user_id=charlie.id, role='member')
    db.session.add(member4)
    
    member5 = TeamMember(team_id=ops_team.id, user_id=charlie.id, role='admin')
    db.session.add(member5)
    
    member6 = TeamMember(team_id=ops_team.id, user_id=alice.id, role='member')
    db.session.add(member6)
    
    member7 = TeamMember(team_id=dev_team.id, user_id=testuser.id, role='member')
    db.session.add(member7)
    
    db.session.commit()
    print('Team members assigned')
    print(f'  testuser is ONLY in Development Team (ID: {dev_team.id})')
    
    print('Creating tasks...')
    task1 = Task(
        team_id=dev_team.id,
        title='Implement user authentication',
        description='Add JWT-based authentication system with login and registration endpoints',
        status='in_progress',
        priority='high',
        created_by=alice.id,
        assigned_to=bob.id
    )
    db.session.add(task1)
    
    task2 = Task(
        team_id=dev_team.id,
        title='Create database schema',
        description='Design and implement database models for users, teams, and tasks',
        status='done',
        priority='high',
        created_by=alice.id,
        assigned_to=alice.id
    )
    db.session.add(task2)
    
    task3 = Task(
        team_id=dev_team.id,
        title='Add API documentation',
        description='Write comprehensive API documentation using OpenAPI/Swagger',
        status='todo',
        priority='medium',
        created_by=bob.id
    )
    db.session.add(task3)
    
    task4 = Task(
        team_id=qa_team.id,
        title='Test authentication flow',
        description='Write integration tests for login, registration, and token validation',
        status='in_progress',
        priority='high',
        created_by=bob.id,
        assigned_to=charlie.id
    )
    db.session.add(task4)
    
    task5 = Task(
        team_id=qa_team.id,
        title='Security audit',
        description='Perform security review of all API endpoints and identify potential vulnerabilities',
        status='todo',
        priority='high',
        created_by=bob.id
    )
    db.session.add(task5)
    
    task6 = Task(
        team_id=qa_team.id,
        title='Performance testing',
        description='Load testing for concurrent user scenarios',
        status='todo',
        priority='medium',
        created_by=charlie.id
    )
    db.session.add(task6)
    
    task7 = Task(
        team_id=ops_team.id,
        title='Setup production environment',
        description='Configure production server with proper security settings and monitoring',
        status='in_progress',
        priority='high',
        created_by=charlie.id,
        assigned_to=alice.id
    )
    db.session.add(task7)
    
    task8 = Task(
        team_id=ops_team.id,
        title='Configure CI/CD pipeline',
        description='Set up automated testing and deployment pipeline',
        status='done',
        priority='medium',
        created_by=charlie.id
    )
    db.session.add(task8)
    
    task9 = Task(
        team_id=ops_team.id,
        title='Backup strategy',
        description='Implement automated database backups with retention policy',
        status='todo',
        priority='low',
        created_by=alice.id
    )
    db.session.add(task9)
    
    db.session.commit()
    print(f'Created {9} tasks across all teams')
    
    print('Adding comments...')
    comment1 = Comment(task_id=task1.id, user_id=alice.id, content='Started working on JWT implementation. Need to add refresh token mechanism.')
    db.session.add(comment1)
    
    comment2 = Comment(task_id=task1.id, user_id=bob.id, content='Reviewing the code. Looks good so far, but we should add rate limiting.')
    db.session.add(comment2)
    
    comment3 = Comment(task_id=task4.id, user_id=charlie.id, content='Tests are passing. Found one edge case with token expiration that needs fixing.')
    db.session.add(comment3)
    
    comment4 = Comment(task_id=task7.id, user_id=alice.id, content='Server is configured. Waiting for SSL certificate to complete setup.')
    db.session.add(comment4)
    
    comment5 = Comment(task_id=task5.id, user_id=bob.id, content='Identified several security issues. Creating detailed report.')
    db.session.add(comment5)
    
    db.session.commit()
    print(f'Created {5} comments')
    
    print('Creating activity logs...')
    log1 = ActivityLog(user_id=alice.id, action='register', details='User alice registered', ip_address='192.168.1.10')
    db.session.add(log1)
    
    log2 = ActivityLog(user_id=bob.id, action='register', details='User bob registered', ip_address='192.168.1.11')
    db.session.add(log2)
    
    log3 = ActivityLog(user_id=alice.id, action='login', details='User alice logged in', ip_address='192.168.1.10')
    db.session.add(log3)
    
    log4 = ActivityLog(user_id=alice.id, action='create_team', details='Created team Development Team', ip_address='192.168.1.10')
    db.session.add(log4)
    
    log5 = ActivityLog(user_id=alice.id, action='create_task', details='Created task: Implement user authentication', ip_address='192.168.1.10')
    db.session.add(log5)
    
    log6 = ActivityLog(user_id=bob.id, action='login', details='User bob logged in', ip_address='192.168.1.11')
    db.session.add(log6)
    
    log7 = ActivityLog(user_id=bob.id, action='create_team', details='Created team QA Team', ip_address='192.168.1.11')
    db.session.add(log7)
    
    log8 = ActivityLog(user_id=admin.id, action='login', details='Admin logged in', ip_address='10.0.0.1')
    db.session.add(log8)
    
    db.session.commit()
    print(f'Created {8} activity logs')
    
    print('\n' + '='*60)
    print('Database seeded successfully!')
    print('='*60)
    print('\nTest Users (password = username):')
    print('  alice    / alice        (user) - Member of Development & Operations')
    print('  bob      / bob          (user) - Member of Development & QA')
    print('  charlie  / charlie      (user) - Member of QA & Operations')
    print('  testuser / testuser     (user) - Member of Development ONLY (for testing SQL Injection)')
    print('  admin    / admin        (app_admin) - Full system access')
    print('\nTeams:')
    print(f'  Development Team (ID: {dev_team.id}) - {alice.username} (admin), {bob.username} (member)')
    print(f'  QA Team (ID: {qa_team.id}) - {bob.username} (admin), {charlie.username} (member)')
    print(f'  Operations Team (ID: {ops_team.id}) - {charlie.username} (admin), {alice.username} (member)')
    print('\nTasks created:')
    print(f'  Development Team: {task1.title}, {task2.title}, {task3.title}')
    print(f'  QA Team: {task4.title}, {task5.title}, {task6.title}')
    print(f'  Operations Team: {task7.title}, {task8.title}, {task9.title}')
    print('\nReady for vulnerability testing!')
    print('='*60)

