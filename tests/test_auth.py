def test_user_registration(client):
    """Verifies a new employee can register successfully."""
    response = client.post('/register', data={
        'username': 'new_tester',
        'email': 'tester@company.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Registration successful" in response.data

def test_login_and_jwt_generation(client):
    """Verifies login generates a JWT cookie and redirects to dashboard."""
    # Register first
    client.post('/register', data={'username': 'bob', 'email': 'b@b.com', 'password': '123'})
    
    # Attempt login
    response = client.post('/login', data={
        'username': 'bob',
        'password': '123'
    })
    
    # Assert JWT cookie is set and user is redirected (302)
    assert response.status_code == 302
    assert 'auth_token' in response.headers.get('Set-Cookie', '')

def test_admin_route_protection(client):
    """Verifies unauthenticated users cannot access the admin command center."""
    response = client.get('/admin/dashboard', follow_redirects=True)
    assert b"Please log in to access this page" in response.data

def test_login_invalid_credentials(client):
    """1. Verifies that entering a wrong password blocks access and shows an error."""
    response = client.post('/login', data={'username': 'fake_user', 'password': 'wrong_password'}, follow_redirects=True)
    assert b"Invalid username or password" in response.data

def test_user_logout(client):
    """2. Verifies that logging out successfully deletes the JWT cookie."""
    client.post('/register', data={'username': 'logout_tester', 'email': 'l@l.com', 'password': '123'})
    client.post('/login', data={'username': 'logout_tester', 'password': '123'})
    
    response = client.get('/logout', follow_redirects=False)
    assert response.status_code == 302
    assert 'auth_token=;' in response.headers.get('Set-Cookie', '') # Cookie cleared

def test_dashboard_redirect_employee(client):
    """3. Verifies the smart dashboard router sends Employees to the correct URL."""
    client.post('/register', data={'username': 'emp_router', 'email': 'er@er.com', 'password': '123'})
    client.post('/login', data={'username': 'emp_router', 'password': '123'})
    
    response = client.get('/dashboard', follow_redirects=False)
    assert response.status_code == 302
    assert '/employee/dashboard' in response.location