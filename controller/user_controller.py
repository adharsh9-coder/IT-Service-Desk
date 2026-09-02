from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, make_response, g
from service.user_service import UserService
from functools import wraps
import jwt
from datetime import datetime, timedelta, timezone

user_bp = Blueprint('user_bp', __name__)

user_service = UserService()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('auth_token')
        if not token:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('user_bp.login'))
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            
            g.user_id = data['user_id']
            g.username = data['username']
            g.role = data['role']

        # except jwt.ExpiredSignatureError:
        #     flash("Session expired. Please log in again.", "warning")
        #     return redirect(url_for('user_bp.login'))
        
        except jwt.ExpiredSignatureError:
            flash("Session expired. Please log in again.", "warning")
            # Delete the expired cookie so the /login route doesn't redirect them again
            response = make_response(redirect(url_for('user_bp.login')))
            response.set_cookie('auth_token', '', expires=0)
            return response
        except jwt.InvalidTokenError:
            flash("Invalid authentication. Please log in again.", "danger")
            return redirect(url_for('user_bp.login'))
            
        return f(*args, **kwargs)
    return decorated_function

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'role') or g.role not in allowed_roles:
                flash("Access Denied: You do not have permission to view this page.", "danger")
                return redirect(url_for('user_bp.dashboard_redirect'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.cookies.get('auth_token'):
        return redirect(url_for('user_bp.dashboard_redirect'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = user_service.authenticate_user(username, password)

        if user:
            token = jwt.encode({
                'user_id': user.id,
                'username': user.username,
                'role': user.role.role_name,
                'exp': datetime.now(timezone.utc) + timedelta(hours=2)
            }, current_app.config['SECRET_KEY'], algorithm="HS256")

            flash(f"Welcome back, {user.username}!", "success")
            resp = make_response(redirect(url_for('user_bp.dashboard_redirect')))
            resp.set_cookie(
                'auth_token', token, 
                httponly=True, 
                secure=False,
                samesite='Strict'
            )
            return resp
        else:
            flash("Invalid username or password.", "danger")

    return render_template('login.html')

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            user_service.register_user(username, email, password)
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for('user_bp.login'))
        except Exception as e:
            flash(f"Registration failed: {str(e)}", "danger")
            return f"Registration failed: {str(e)}", 400

    return render_template('register.html')

@user_bp.route('/logout')
def logout():
    resp = make_response(redirect(url_for('user_bp.login')))
    resp.set_cookie('auth_token', '', expires=0)
    flash("You have been successfully logged out.", "info")
    return resp

@user_bp.route('/dashboard')
@login_required
def dashboard_redirect():
    if g.role == 'Admin':
        return redirect(url_for('admin_bp.admin_dashboard'))
    elif g.role == 'Support Agent':
        return redirect(url_for('ticket_bp.agent_dashboard'))
    else:
        return redirect(url_for('ticket_bp.employee_dashboard'))

@user_bp.route('/admin/create-staff', methods=['POST'])
@login_required
@role_required(['Admin'])
def create_staff():
    new_username = request.form.get('username')
    new_email = request.form.get('email')
    password = request.form.get('password')
    target_role = request.form.get('role')

    admin_user = user_service.get_user_info(g.user_id)
    
    try:
        user_service.create_previleged_account(
            admin_user, new_username, new_email, password, target_role
        )
        flash(f"Successfully provisioned {target_role}: {new_username}", "success")
    except Exception as e:
        flash(f"Error provisioning user: {str(e)}", "danger")
        return f"Registration failed: {str(e)}", 400

        
    return redirect(url_for('admin_bp.admin_dashboard'))