import pytest
from app import create_app
from config.database import db
from model.user import Role


@pytest.fixture
def client():
    # Inject the SQLite config directly into the app factory
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False
    })

    with app.test_client() as client:
        with app.app_context():
            # This now safely executes against the temporary SQLite memory!
            db.create_all()
            
            emp_role = Role(role_name='Employee')
            admin_role = Role(role_name='Admin')
            db.session.add_all([emp_role, admin_role])
            db.session.commit()
            
            yield client
            
            db.drop_all()