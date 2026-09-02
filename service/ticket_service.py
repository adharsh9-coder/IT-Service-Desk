from dao.ticket_dao import TicketDAO
from dao.interaction_dao import InteractionDAO
from model.ticket import Ticket, TicketCategory
from model.interactions import TicketHistory, TicketAssignment
from datetime import datetime, timedelta
import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app


ticket_dao = TicketDAO()
interaction_dao = InteractionDAO()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'txt'}


class TicketService:
    def create_new_ticket(self, title, description, category_id, sla_id, creator_id):
        sla_rule = ticket_dao.get_sla_by_id(sla_id)

        due_date = datetime.now() + timedelta(hours=sla_rule.resolve_within_hours)

        new_ticket = Ticket(
            title=title,
            description=description,
            category_id=category_id,
            sla_id=sla_id,
            creator_id=creator_id,
            due_date=due_date
        )

        saved_ticket = ticket_dao.create_ticket(new_ticket)

        self._record_history(saved_ticket.id, creator_id, "Ticket Created", None, "Open")
        return saved_ticket

    def assign_ticket(self, ticket_id, agent_id, assigner_id):
        assignment = TicketAssignment(ticket_id=ticket_id, agent_id=agent_id)
        interaction_dao.assign_ticket(assignment)

        ticket = ticket_dao.get_ticket_by_id(ticket_id)
        old_status = ticket.status
        ticket.status = "Assigned"
        ticket_dao.update_ticket_status(ticket)
        
        self._record_history(ticket_id, assigner_id, "Ticket Assigned", old_status, "Assigned")
        return ticket

    def update_status(self, ticket_id, new_status, user_id):
        ticket = ticket_dao.get_ticket_by_id(ticket_id)
        old_status = ticket.status
        ticket.status = new_status
        updated_ticket = ticket_dao.update_ticket_status(ticket)
        
        self._record_history(ticket_id, user_id, "Status Update", old_status, new_status)
        return updated_ticket

    def escalate_ticket(self, ticket_id, admin_id):
        return self.update_status(ticket_id, "Escalated", admin_id)

    def _record_history(self, ticket_id, user_id, action, old_val, new_val):
        history = TicketHistory(
            ticket_id=ticket_id,
            changed_by=user_id,
            action=action,
            old_value=old_val,
            new_value=new_val
        )
        interaction_dao.add_history_record(history)

    def get_user_tickets(self, user_id):
        return ticket_dao.get_tickets_by_creator(user_id)

    def get_all_tickets(self):
        return ticket_dao.get_all_tickets()
        
    def get_ticket_details(self, ticket_id):
        return ticket_dao.get_ticket_by_id(ticket_id)

    def get_form_data(self):
        categories = ticket_dao.get_all_categories()
        slas = ticket_dao.get_all_slas()
        return categories, slas

    def get_unassigned_queue(self, filters=None):
        filters = filters or {}
        return ticket_dao.get_filtered_unassigned_tickets(filters)

    def get_agent_queue(self, agent_id, filters=None):
        filters = filters or {}
        return ticket_dao.get_filtered_agent_tickets(agent_id, filters)

    def is_agent_assigned(self, ticket_id, agent_id):
        ticket = ticket_dao.get_ticket_by_id(ticket_id)
        
        if not ticket or not ticket.assignments:
            return False
            
        latest_assignment = sorted(ticket.assignments, key=lambda x: x.assigned_at, reverse=True)[0]
        
        return latest_assignment.agent_id == agent_id

    def get_admin_metrics(self):
        return ticket_dao.get_ticket_metrics()

    def add_new_category(self, category_name):
        new_category = TicketCategory(name=category_name)
        return ticket_dao.add_category(new_category)

    def enforce_sla_escalations(self):
        overdue_tickets = ticket_dao.get_overdue_tickets()
        
        if not overdue_tickets:
            return # No action needed
            
        for ticket in overdue_tickets:
            old_status = ticket.status
            ticket.status = 'Escalated'

            ticket_dao.update_ticket_status(ticket)

            self._record_history(
                ticket_id=ticket.id, 
                user_id=1, 
                action="Automated SLA Escalation", 
                old_val=old_status, 
                new_val="Escalated"
            )

    def get_all_tickets_filtered(self, filters=None):
        filters = filters or {}
        return ticket_dao.get_filtered_all_tickets(filters)
    