from app.models.user import User

def test_health_check(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'healthy'
    assert data['database'] == 'healthy'

def test_login_success(client):
    response = client.post('/api/auth/login', json={
        'email': 'admin@test.com',
        'password': 'admin123'
    })
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert 'access_token' in data['data']
    assert data['data']['user']['email'] == 'admin@test.com'
    assert data['data']['user']['role'] == 'admin'

def test_login_invalid_password(client):
    response = client.post('/api/auth/login', json={
        'email': 'admin@test.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    data = response.json()
    assert data['success'] is False

def test_login_nonexistent_user(client):
    response = client.post('/api/auth/login', json={
        'email': 'nonexistent@test.com',
        'password': 'admin123'
    })
    assert response.status_code == 401

def test_login_empty_fields(client):
    response = client.post('/api/auth/login', json={
        'email': '',
        'password': ''
    })
    assert response.status_code in (400, 401, 422)

def test_register_viewer(client):
    response = client.post('/api/auth/register', json={
        'name': 'New Viewer',
        'email': 'newviewer@test.com',
        'password': 'password123',
        'role': 'viewer'
    })
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert data['data']['user']['role'] == 'viewer'

def test_register_duplicate_email(client):
    response = client.post('/api/auth/register', json={
        'name': 'Duplicate Admin',
        'email': 'admin@test.com',
        'password': 'password123',
        'role': 'viewer'
    })
    assert response.status_code == 400

def test_register_admin_without_invite_code(client):
    response = client.post('/api/auth/register', json={
        'name': 'Rogue Admin',
        'email': 'rogue@test.com',
        'password': 'password123',
        'role': 'admin'
    })
    assert response.status_code == 400

def test_get_current_user_profile(client, viewer_headers):
    response = client.get('/api/auth/me', headers=viewer_headers)
    assert response.status_code == 200
    data = response.json()
    assert data['data']['email'] == 'viewer@test.com'

def test_unauthorized_access_protected_page(client):
    response = client.get('/api/auth/me')
    assert response.status_code == 401

def test_role_based_access_admin_only_routes(client, viewer_headers, admin_headers):
    # Viewer cannot list all users
    viewer_res = client.get('/api/users', headers=viewer_headers)
    assert viewer_res.status_code == 403

    # Admin can list all users
    admin_res = client.get('/api/users', headers=admin_headers)
    assert admin_res.status_code == 200
    assert len(admin_res.json()['data']) >= 3
