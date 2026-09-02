from dao.user_dao import UserDAO
from model.user import User
from config.database import bcrypt

user_dao = UserDAO()

class UserService:
    def authenticate_user(self, username, password):
        user = user_dao.get_user_by_username(username)

        if user and bcrypt.check_password_hash(user.password_hash, password):
            return user
        return None

    def register_user(self, username, email, raw_password):
        role = user_dao.get_role_by_name('Employee')
        if not role:
            raise ValueError("System error: Default role missing")

        hashed_pw = bcrypt.generate_password_hash(raw_password).decode('utf-8')

        new_user = User(
            username = username,
            email=email,
            password_hash=hashed_pw,
            role_id=role.id
        )
        return user_dao.create_user(new_user)

    def create_previleged_account(self, admin_user, new_username, new_email, raw_password, target_role_name):
        if admin_user.role.role_name != 'Admin':
            raise PermissionError("Access Denied: Only Admins can provision staff accounts")

        if target_role_name not in ['Support Agent', 'Admin']:
           raise ValueError("This function is only for creating privileged accounts.")

        role = user_dao.get_role_by_name(target_role_name)
        hashed_pw = bcrypt.generate_password_hash(raw_password).decode('utf-8')

        new_staff = User(
            username=new_username,
            email=new_email,
            password_hash=hashed_pw,
            role_id=role.id
        )
        return user_dao.create_user(new_staff)

    def get_user_info(self, user_id):
        return user_dao.get_user_by_id(user_id)