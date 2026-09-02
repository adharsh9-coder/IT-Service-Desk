from config.database import db
from datetime import datetime

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)

    users = db.relationship('User', back_populates='role', lazy=True)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())

    role = db.relationship('Role', back_populates='users')
    tickets_created = db.relationship('Ticket', foreign_keys='Ticket.creator_id', back_populates='creator', lazy=True)
    comments = db.relationship('TicketComment', foreign_keys='TicketComment.user_id', back_populates='author', lazy=True)
