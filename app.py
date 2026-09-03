# from flask import Flask
# from config.database import init_db, db
# import model
# from controller.user_controller import user_bp
# from controller.ticket_controller import ticket_bp
# from controller.admin_controller import admin_bp
# import os

# app = Flask(__name__)

# app.config['SECRET_KEY'] = 'your-strong-secret'

# init_db(app)

# app.register_blueprint(user_bp)
# app.register_blueprint(ticket_bp)
# app.register_blueprint(admin_bp)

# app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024


# if not os.path.exists(app.config['UPLOAD_FOLDER']):
#     os.makedirs(app.config['UPLOAD_FOLDER'])

# with app.app_context():
#     try:
#         db.create_all()
#         print("Successfully connected to the database and created tables")
#     except Exception as e:
#         print(f"Error connecting to the database: {e}")

# @app.route('/')
# def home():
#     return "IT Service Desk backend is running"

# if __name__ == '__main__':
#     app.run(debug=True)


import os
from flask import Flask
from config.database import init_db, db, bcrypt
from controller.user_controller import user_bp
from controller.ticket_controller import ticket_bp
from controller.admin_controller import admin_bp

def create_app(test_config=None):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-strong-secret'
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    if test_config is None:
        # Normal production/dev mode (Connects to MySQL)
        init_db(app)
    else:
        # Test mode (Bypasses init_db and safely injects SQLite)
        app.config.update(test_config)
        db.init_app(app)
        bcrypt.init_app(app)

    app.register_blueprint(user_bp)
    app.register_blueprint(ticket_bp)
    app.register_blueprint(admin_bp)

    # Health check route for Kubernetes probes
    @app.route('/health')
    def health_check():
        return "App is healthy and jenkins is building", 200

    return app

# Only run the server if executed directly via the terminal
if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=3000)