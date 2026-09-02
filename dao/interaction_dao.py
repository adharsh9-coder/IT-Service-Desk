from config.database import db
from model.interactions import TicketComment, TicketHistory, TicketAttachment, TicketAssignment, Feedback

class InteractionDAO:
    def add_comment(self, comment_object):
        db.session.add(comment_object)
        db.session.commit()
        return comment_object

    def add_history_record(self, history_object):
        db.session.add(history_object)
        db.session.commit()
        return history_object

    def assign_ticket(self, assignment_object):
        db.session.add(assignment_object)
        db.session.commit()
        return assignment_object

    def add_attachment(self, attachment_object):
        db.session.add(attachment_object)
        db.session.commit()
        return attachment_object

    def add_feedback(self, feedback_object):
        db.session.add(feedback_object)
        db.session.commit()
        return feedback_object

    def get_global_audit_trail(self, start_date=None, end_date=None):
        from model.interactions import TicketHistory
        from datetime import datetime, timedelta
        
        query = TicketHistory.query
    
        if start_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(TicketHistory.changed_at >= start_dt)
            
        if end_date:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(TicketHistory.changed_at < end_dt)
            
        return query.order_by(TicketHistory.changed_at.desc()).all()