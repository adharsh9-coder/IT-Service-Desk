from config.database import db
from model.user import User, Role
from model.ticket import Ticket, TicketCategory, SLARule

def test_create_ticket(client):
    """Verifies an authenticated employee can raise a new ticket."""
    # Register and login to set the JWT cookie
    client.post('/register', data={'username': 'alice', 'email': 'a@a.com', 'password': '123'})
    client.post('/login', data={'username': 'alice', 'password': '123'})
    
    # We must seed a category and SLA for the form to accept the POST
    from config.database import db
    from model.ticket import TicketCategory, SLARule
    db.session.add(TicketCategory(name='Hardware'))
    db.session.add(SLARule(priority_level='Low', resolve_within_hours=48))
    db.session.commit()

    # Submit the ticket
    response = client.post('/ticket/create', data={
        'title': 'Broken Mouse',
        'description': 'The scroll wheel is stuck.',
        'category_id': 1,
        'sla_id': 1
    }, follow_redirects=True)

    assert b"Support ticket created successfully" in response.data

def test_employee_dashboard_access(client):
    """4. Verifies an authenticated employee can load their specific dashboard."""
    client.post('/register', data={'username': 'emp_dash', 'email': 'ed@ed.com', 'password': '123'})
    client.post('/login', data={'username': 'emp_dash', 'password': '123'})
    
    response = client.get('/employee/dashboard')
    assert response.status_code == 200
    assert b"IT Service Desk" in response.data

def test_add_comment_to_ticket(client):
    """5. Verifies a user can add a text comment to an active ticket."""
    client.post('/register', data={'username': 'commenter', 'email': 'c@c.com', 'password': '123'})
    client.post('/login', data={'username': 'commenter', 'password': '123'})
    
    # Setup dummy data
    db.session.add(TicketCategory(name='Software'))
    db.session.add(SLARule(priority_level='High', resolve_within_hours=4))
    db.session.commit()
    
    client.post('/ticket/create', data={'title': 'App Crash', 'description': 'Fails on startup', 'category_id': 1, 'sla_id': 1})
    
    # Add comment (assuming ticket ID is 1 in this isolated test DB)
    response = client.post('/ticket/1/comment', data={'comment_text': 'I also tried rebooting.'}, follow_redirects=True)
    assert b"Reply posted successfully" in response.data or b"Comment added" in response.data

def test_employee_cannot_access_agent_dashboard(client):
    """6. Verifies the RBAC (Role-Based Access Control) blocks employees from agent views."""
    client.post('/register', data={'username': 'sneaky_emp', 'email': 'se@se.com', 'password': '123'})
    client.post('/login', data={'username': 'sneaky_emp', 'password': '123'})
    
    response = client.get('/agent/dashboard', follow_redirects=True)
    assert b"Access Denied" in response.data

def test_dynamic_sla_escalator_no_crash(client):
    """7. Verifies the SLA enforcement method can execute safely without throwing errors."""
    from service.ticket_service import TicketService
    service = TicketService()
    try:
        service.enforce_sla_escalations()
        passed = True
    except Exception:
        passed = False
    assert passed == True