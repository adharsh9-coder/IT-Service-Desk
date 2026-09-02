from flask_sqlalchemy import SQLAlchemy
import urllib.parse
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os

db = SQLAlchemy()

bcrypt = Bcrypt()

load_dotenv()

def init_db(app):
    if os.environ.get('FLASK_TESTING') == 'True':
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        print("🧪 Running in TEST mode with in-memory SQLite")
    else:
        # 1. Try to get the full URL provided by the Docker command
        db_url = os.getenv("MYSQL_DB_URL")

        if db_url:
            app.config["SQLALCHEMY_DATABASE_URI"] = db_url
            print("🚀 Running in DOCKER mode with provided MYSQL_DB_URL")
        else:
            # 2. Otherwise, connect to the live MySQL database
            # 2. Fallback if running locally in VS Code without Docker
            raw_password = os.getenv("raw_password")
            encoded_pass = urllib.parse.quote_plus(raw_password)
            user = os.getenv("db_user")
            db_name = os.getenv("db_name")
            
            app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{user}:{encoded_pass}@localhost/{db_name}"
            print("🚀 Running in DEV/PROD mode with MySQL")

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    db.init_app(app)

    bcrypt.init_app(app)