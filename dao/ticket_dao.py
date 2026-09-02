from config.database import db
from model.ticket import Ticket, TicketCategory, SLARule

class TicketDAO:
    def create_ticket(self, ticket_object):
        db.session.add(ticket_object)
        db.session.commit()
        return ticket_object

    def get_ticket_by_id(self, ticket_id):
        return Ticket.query.get(ticket_id)

    def get_all_tickets(self):
        return Ticket.query.all()

    def get_tickets_by_creator(self, user_id):
        return Ticket.query.filter_by(creator_id=user_id).all()

    def update_ticket_status(self, ticket):
        db.session.commit()
        return ticket

    def get_category_by_id(self, category_id):
        return TicketCategory.query.get(category_id)

    def get_sla_by_id(self, sla_id):
        return SLARule.query.get(sla_id)
    
    def get_all_categories(self):
        return TicketCategory.query.all()

    def get_all_slas(self):
        return SLARule.query.all()

    def get_unassigned_tickets(self):
        from model.ticket import Ticket
        from model.interactions import TicketAssignment
        
        return Ticket.query.outerjoin(TicketAssignment).filter(
            TicketAssignment.id.is_(None),
            Ticket.status.in_(['Open', 'Escalated'])
        ).all()

    def get_agent_tickets(self, agent_id):
        from model.interactions import TicketAssignment
        return Ticket.query.join(TicketAssignment).filter(TicketAssignment.agent_id == agent_id).all()

    def get_ticket_metrics(self):
        total = Ticket.query.count()
        open_count = Ticket.query.filter_by(status='Open').count()
        in_progress = Ticket.query.filter_by(status='In Progress').count()
        resolved = Ticket.query.filter_by(status='Resolved').count()
        escalated = Ticket.query.filter_by(status='Escalated').count()

        return {
            'total': total,
            'open': open_count,
            'in_progress': in_progress,
            'resolved': resolved,
            'escalated': escalated
        }

    def add_category(self, category_object):
        db.session.add(category_object)
        db.session.commit()
        return category_object

    def _apply_filters(self, query, filters):
        from model.ticket import Ticket
        
        if filters.get('search'):
            search_term = f"%{filters['search']}%"
            query = query.filter(Ticket.title.ilike(search_term) | Ticket.description.ilike(search_term))
            
        if filters.get('status'):
            query = query.filter(Ticket.status == filters['status'])
            
        if filters.get('priority'):
            query = query.filter(Ticket.sla_id == filters['priority'])
            
        if filters.get('category'):
            query = query.filter(Ticket.category_id == filters['category'])
            
        if filters.get('sort') == 'due_date_desc':
            query = query.order_by(Ticket.due_date.desc())
        else: 
            query = query.order_by(Ticket.due_date.asc())
            
        return query.all()

    def get_filtered_unassigned_tickets(self, filters):
        from model.ticket import Ticket
        from model.interactions import TicketAssignment
        
        query = Ticket.query.outerjoin(TicketAssignment).filter(
            TicketAssignment.id.is_(None),
            Ticket.status.in_(['Open', 'Escalated'])
        )
        return self._apply_filters(query, filters)

    def get_filtered_agent_tickets(self, agent_id, filters):
        from model.ticket import Ticket
        from model.interactions import TicketAssignment
        query = Ticket.query.join(TicketAssignment).filter(TicketAssignment.agent_id == agent_id)
        return self._apply_filters(query, filters)

    def get_overdue_tickets(self):
        from model.ticket import Ticket
        from datetime import datetime
        
        return Ticket.query.filter(
            Ticket.status.notin_(['Resolved', 'Escalated']),
            Ticket.due_date < datetime.now()
        ).all()

    def get_filtered_all_tickets(self, filters):
        from model.ticket import Ticket
        query = Ticket.query
        return self._apply_filters(query, filters)