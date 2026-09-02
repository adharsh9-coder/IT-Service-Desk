from config.database import db
from datetime import datetime

class TicketCategory(db.Model):
    __tablename__ = 'ticket_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    tickets = db.relationship('Ticket', back_populates='category', lazy=True)

class SLARule(db.Model):
    __tablename__ = 'sla_rules'
    id = db.Column(db.Integer, primary_key=True)
    priority_level = db.Column(db.String(50), unique=True, nullable=False)
    resolve_within_hours = db.Column(db.Integer, nullable=False)

    tickets = db.relationship('Ticket', back_populates='sla', lazy=True)

class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='Open')
    
    category_id = db.Column(db.Integer, db.ForeignKey('ticket_categories.id'), nullable=False)
    sla_id = db.Column(db.Integer, db.ForeignKey('sla_rules.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.now())
    due_date = db.Column(db.DateTime, nullable=True)

    category = db.relationship('TicketCategory', back_populates='tickets')
    sla = db.relationship('SLARule', back_populates='tickets')
    creator = db.relationship('User', foreign_keys=[creator_id], back_populates='tickets_created')

    assignments = db.relationship('TicketAssignment', back_populates='ticket', lazy=True)
    comments = db.relationship('TicketComment', back_populates='ticket', lazy=True)
    attachments = db.relationship('TicketAttachment', back_populates='ticket', lazy=True)
    history = db.relationship('TicketHistory', back_populates='ticket', lazy=True)
    feedback = db.relationship('Feedback', back_populates='ticket', uselist=False)
