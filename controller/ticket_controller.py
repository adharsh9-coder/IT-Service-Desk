from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory, g
from service.ticket_service import TicketService
from service.interaction_service import InteractionService
from controller.user_controller import login_required, role_required

ticket_bp = Blueprint('ticket_bp', __name__)
ticket_service = TicketService()
interaction_service = InteractionService()

@ticket_bp.route('/employee/dashboard')
@login_required
@role_required(['Employee'])
def employee_dashboard():
    ticket_service.enforce_sla_escalations()

    tickets = ticket_service.get_user_tickets(g.user_id)
    return render_template('employee_dashboard.html', tickets=tickets)

@ticket_bp.route('/agent/dashboard')
@login_required
@role_required(['Support Agent', 'Admin'])
def agent_dashboard():
    ticket_service.enforce_sla_escalations()

    unassigned_filters = {
        'search': request.args.get('unassigned_search'),
        'priority': request.args.get('unassigned_priority'),
        'category': request.args.get('unassigned_category'),
        'sort': request.args.get('unassigned_sort', 'due_date_asc')
    }

    active_filters = {
        'search': request.args.get('active_search'),
        'status': request.args.get('active_status'),
        'priority': request.args.get('active_priority'),
        'category': request.args.get('active_category'),
        'sort': request.args.get('active_sort', 'due_date_asc')
    }

    unassigned_tickets = ticket_service.get_unassigned_queue(unassigned_filters)
    my_tickets = ticket_service.get_agent_queue(g.user_id, active_filters)

    categories, slas = ticket_service.get_form_data()
    
    return render_template(
        'agent_dashboard.html', 
        unassigned_tickets=unassigned_tickets, 
        my_tickets=my_tickets,
        categories=categories,
        slas=slas,
        unassigned_filters=unassigned_filters,
        active_filters=active_filters
    )

@ticket_bp.route('/ticket/create', methods=['GET', 'POST'])
@login_required
def create_ticket():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category_id = request.form.get('category_id')
        sla_id = request.form.get('sla_id')

        file_obj = request.files.get('attachment')
        
        try:
            ticket = ticket_service.create_new_ticket(
                title=title, 
                description=description, 
                category_id=category_id, 
                sla_id=sla_id, 
                creator_id=g.user_id
            )

            if file_obj:
                interaction_service.process_attachment(
                    file_object=file_obj, 
                    ticket_id=ticket.id, 
                    uploader_id=g.user_id, 
                    upload_folder=current_app.config['UPLOAD_FOLDER']
                )

            flash("Support ticket created successfully!", "success")
            return redirect(url_for('ticket_bp.employee_dashboard'))
        except Exception as e:
            flash(f"Error creating ticket: {str(e)}", "danger")
            return f"Ticket creation failed: {str(e)}", 400

    categories, slas = ticket_service.get_form_data()
    return render_template('create_ticket.html', categories=categories, slas=slas)

@ticket_bp.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@ticket_bp.route('/ticket/<int:ticket_id>', methods=['GET'])
@login_required
def ticket_details(ticket_id):
    ticket = ticket_service.get_ticket_details(ticket_id)
    if not ticket:
        flash("Ticket not found.", "warning")
        return redirect(url_for('ticket_bp.employee_dashboard'))
        
    return render_template('ticket_details.html', ticket=ticket)

@ticket_bp.route('/ticket/<int:ticket_id>/comment', methods=['POST'])
@login_required
def add_comment(ticket_id):
    text = request.form.get('comment_text')
    file_obj = request.files.get('attachment')

    try:
        if text and text.strip():
            interaction_service.add_comment(ticket_id, g.user_id, text)
        if file_obj:
            interaction_service.process_attachment(
                file_object=file_obj, 
                ticket_id=ticket_id, 
                uploader_id=g.user_id, 
                upload_folder=current_app.config['UPLOAD_FOLDER']
            )
        flash("Comment added.", "success")
    except Exception as e:
        flash(f"Failed to add comment: {str(e)}", "danger")
        return f"Failed to add commen: {str(e)}", 400
        
    return redirect(url_for('ticket_bp.ticket_details', ticket_id=ticket_id))

@ticket_bp.route('/ticket/<int:ticket_id>/update-status', methods=['POST'])
@login_required
@role_required(['Support Agent', 'Admin'])
def update_status(ticket_id):
    new_status = request.form.get('status')

    if g.user_id == 'Support Agent':
        is_assigned = ticket_service.is_agent_assigned(ticket_id, g.user_id)
        if not is_assigned:
            flash("Access Denied: You can only update tickets that are assigned to you.", "danger")
            return redirect(url_for('ticket_bp.ticket_details', ticket_id=ticket_id))

    try:
        ticket_service.update_status(ticket_id, new_status, g.user_id)
        flash(f"Ticket status updated to {new_status}.", "success")
    except Exception as e:
        flash("Failed to update status.", "danger")
        
    return redirect(url_for('ticket_bp.ticket_details', ticket_id=ticket_id))

@ticket_bp.route('/ticket/<int:ticket_id>/assign', methods=['POST'])
@login_required
@role_required(['Support Agent', 'Admin'])
def assign_ticket(ticket_id):
    target_agent_id = request.form.get('agent_id', g.user_id)
    
    try:
        ticket_service.assign_ticket(ticket_id, target_agent_id, g.user_id)
        flash("Ticket successfully assigned!", "success")
    except Exception as e:
        flash(f"Error assigning ticket: {str(e)}", "danger")
        
    return redirect(url_for('ticket_bp.agent_dashboard'))

@ticket_bp.route('/ticket/<int:ticket_id>/feedback', methods=['POST'])
@login_required
@role_required(['Employee'])
def submit_feedback(ticket_id):
    try:
        rating = int(request.form.get('rating', 0))
        comments = request.form.get('comments', '')
        
        interaction_service.submit_feedback(ticket_id, g.user_id, rating, comments)
        flash("Thank you! Your feedback has been recorded.", "success")
    except Exception as e:
        flash(f"Failed to submit feedback: {str(e)}", "danger")
        
    return redirect(url_for('ticket_bp.ticket_details', ticket_id=ticket_id))