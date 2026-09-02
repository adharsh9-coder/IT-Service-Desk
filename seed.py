from app import create_app
from config.database import db
from model.user import Role, User
from model.ticket import TicketCategory, SLARule
from config.database import bcrypt

def seed_database():
    app = create_app()
    with app.app_context():
        # 1. Seed Roles
        roles = ['Employee', 'Support Agent', 'Admin']
        for role_name in roles:
            existing_role = Role.query.filter_by(role_name=role_name).first()
            if not existing_role:
                new_role = Role(role_name=role_name)
                db.session.add(new_role)
                print(f"Added Role: {role_name}")

        db.session.commit() # Commit roles first so we can use the Admin ID

        # 2. Seed Ticket Categories
        categories = ['Hardware', 'Software', 'Network', 'Access & Passwords', 'Other']
        for cat_name in categories:
            existing_cat = TicketCategory.query.filter_by(name=cat_name).first()
            if not existing_cat:
                new_cat = TicketCategory(name=cat_name)
                db.session.add(new_cat)
                print(f"Added Category: {cat_name}")

        # 3. Seed SLA Rules
        # priority_level : resolve_within_hours
        sla_rules = {
            'Low': 48,
            'Medium': 24,
            'High': 8,
            'Critical': 2
        }
        
        for priority, hours in sla_rules.items():
            existing_sla = SLARule.query.filter_by(priority_level=priority).first()
            if not existing_sla:
                new_sla = SLARule(priority_level=priority, resolve_within_hours=hours)
                db.session.add(new_sla)
                print(f"Added SLA Rule: {priority} ({hours} hours)")

        db.session.commit()

        # 4. Seed a Default Admin User
        admin_role = Role.query.filter_by(role_name='Admin').first()
        existing_admin = User.query.filter_by(username='admin').first()
        
        if not existing_admin and admin_role:
            # Bcrypt generates a byte-string, so we decode it to 'utf-8' to store as a normal string in MySQL
            hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
            
            admin_user = User(
                username='admin',
                email='admin@servicedesk.com',
                password_hash=hashed_pw,
                role_id=admin_role.id
            )
            db.session.add(admin_user)
            print("Added Default Admin User (username: admin, password: admin123)")

        db.session.commit()
        print("✅ Database seeding complete!")

if __name__ == '__main__':
    seed_database()