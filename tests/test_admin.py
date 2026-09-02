from config.database import db
from model.user import User, Role
from service.user_service import bcrypt

def _setup_admin_login(client):
    """Helper method to bypass registration and force an Admin account."""
    admin_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
    admin_user = User(username='boss_admin', email='boss@admin.com', password_hash=admin_pw, role_id=2)
    db.session.add(admin_user)
    
    # Also create the Support Agent role for provisioning tests
    db.session.add(Role(role_name='Support Agent'))
    db.session.commit()
    
    client.post('/login', data={'username': 'boss_admin', 'password': 'admin123'})
    return admin_user

def test_admin_dashboard_loads(client):
    """8. Verifies the Admin Command Center loads with all metric cards."""
    _setup_admin_login(client)
    response = client.get('/admin/dashboard')
    assert response.status_code == 200
    assert b"Admin Command Center" in response.data

def test_admin_add_ticket_category(client):
    """9. Verifies an Admin can add a new ticket category to the system."""
    _setup_admin_login(client)
    response = client.post('/admin/category/add', data={'category_name': 'Cloud Servers'}, follow_redirects=True)
    assert b"added successfully" in response.data

def test_admin_add_empty_category_fails(client):
    """10. Verifies form validation stops Admins from adding blank categories."""
    _setup_admin_login(client)
    response = client.post('/admin/category/add', data={'category_name': ''}, follow_redirects=True)
    assert b"Category cannot be empty" in response.data

def test_admin_provision_staff(client):
    """11. Verifies an Admin can successfully create a Support Agent account."""
    _setup_admin_login(client)
    response = client.post('/admin/create-staff', data={
        'username': 'new_agent',
        'email': 'agent@desk.com',
        'password': 'secure123',
        'role': 'Support Agent'
    }, follow_redirects=True)
    assert b"Successfully provisioned" in response.data

def test_admin_global_ticket_explorer(client):
    """12. Verifies the global ticket explorer page loads successfully."""
    _setup_admin_login(client)
    response = client.get('/admin/tickets')
    assert response.status_code == 200
    assert b"Global Ticket Explorer" in response.data

def test_admin_audit_log_view(client):
    """13. Verifies the chronological system audit log page loads correctly."""
    _setup_admin_login(client)
    response = client.get('/admin/audit-logs')
    assert response.status_code == 200
    assert b"System Audit Trail" in response.data

def test_admin_audit_log_export_csv(client):
    """14. Verifies the CSV export route generates a file attachment."""
    _setup_admin_login(client)
    response = client.get('/admin/audit-logs/export')
    assert response.status_code == 200
    assert response.mimetype == 'text/csv'
    assert 'attachment; filename=system_audit_logs.csv' in response.headers['Content-Disposition']

def test_agent_dashboard_loads(client):
    """15. Verifies that a provisioned Support Agent can view their work queues."""
    _setup_admin_login(client) # Run this to seed the Support Agent role
    
    agent_pw = bcrypt.generate_password_hash('agent123').decode('utf-8')
    agent_role = Role.query.filter_by(role_name='Support Agent').first()
    db.session.add(User(username='help_agent', email='help@desk.com', password_hash=agent_pw, role_id=agent_role.id))
    db.session.commit()
    
    # Login as the new agent
    client.post('/logout')
    client.post('/login', data={'username': 'help_agent', 'password': 'agent123'})
    
    response = client.get('/agent/dashboard')
    assert response.status_code == 200
    assert b"Open Queue (Unassigned)" in response.data

def test_agent_claim_ticket_fails_unauthorized(client):
    """16. Verifies an employee attempting to force-claim a ticket via URL is blocked."""
    client.post('/register', data={'username': 'emp_claim', 'email': 'ec@ec.com', 'password': '123'})
    client.post('/login', data={'username': 'emp_claim', 'password': '123'})
    
    response = client.post('/ticket/1/assign', follow_redirects=True)
    assert b"Access Denied" in response.data