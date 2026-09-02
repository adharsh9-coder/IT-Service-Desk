from config.database import db
from model.user import User, Role

class UserDAO:
    def create_user(self, user_object):
        db.session.add(user_object)
        db.session.commit()
        return user_object

    def get_user_by_id(self, user_id):
        return User.query.get(user_id)

    def get_user_by_username(self, username):
        return User.query.filter_by(username=username).first()

    def get_user_by_email(self, email):
        return User.query.filter_by(email=email).first()

    def get_role_by_name(self, role_name):
        return Role.query.filter_by(role_name=role_name).first()