from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from service.ticket_service import TicketService
from service.user_service import UserService
from service.interaction_service import InteractionService
from controller.user_controller import login_required, role_required
import csv
from io import StringIO

admin_bp = Blueprint('admin_bp', __name__)
ticket_service = TicketService()
user_service = UserService()
interaction_service = InteractionService()

@admin_bp.route('/admin/dashboard')
@login_required
@role_required(['Admin'])
def admin_dashboard():
    ticket_service.enforce_sla_escalations()

    metrics = ticket_service.get_admin_metrics()

    categories, slas = ticket_service.get_form_data()

    return render_template(
        'admin_dashboard.html',
        metrics=metrics,
        categories=categories,
        slas=slas
    )

@admin_bp.route('/admin/category/add', methods=['POST'])
@login_required
@role_required(['Admin'])
def add_category():
    category_name = request.form.get('category_name')
    if not category_name:
        flash("Category cannot be empty.", "warning")
        return redirect(url_for('admin_bp.admin_dashboard'))
    try:
        ticket_service.add_new_category(category_name)
        flash(f"Category '{category_name}' added successfully.", "success")
    except Exception as e:
        flash("Failed to add category. It might already exist.", "danger")
        return f"Category creation failed: {str(e)}", 400

    return redirect(url_for('admin_bp.admin_dashboard'))

@admin_bp.route('/admin/tickets', methods=['GET'])
@login_required
@role_required(['Admin'])
def admin_tickets():
    filters = {
        'search': request.args.get('search'),
        'status': request.args.get('status'),
        'priority': request.args.get('priority'),
        'category': request.args.get('category'),
        'sort': request.args.get('sort', 'due_date_asc')
    }

    tickets = ticket_service.get_all_tickets_filtered(filters)
    categories, slas = ticket_service.get_form_data()

    return render_template(
        'admin_tickets.html',
        tickets=tickets,
        categories=categories,
        slas=slas,
        filters=filters
    )

@admin_bp.route('/admin/audit-logs', methods=['GET'])
@login_required
@role_required(['Admin'])
def view_audit_logs():
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    logs = interaction_service.get_audit_trail(start_date, end_date)
    
    return render_template('admin_audit.html', logs=logs, start_date=start_date, end_date=end_date)

@admin_bp.route('/admin/audit-logs/export', methods=['GET'])
@login_required
@role_required(['Admin'])
def export_audit_logs():
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    logs = interaction_service.get_audit_trail(start_date, end_date)
    
    si = StringIO()
    cw = csv.writer(si)
    
    cw.writerow(['Log ID', 'Ticket ID', 'Action', 'Old Value', 'New Value', 'Changed By', 'Timestamp'])
    
    for log in logs:
        username = log.user.username if log.user else f"User {log.changed_by}"
        cw.writerow([
            log.id, 
            log.ticket_id, 
            log.action, 
            log.old_value or 'N/A', 
            log.new_value or 'N/A', 
            username, 
            log.changed_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
        
    output = Response(si.getvalue(), mimetype="text/csv")
    output.headers["Content-Disposition"] = "attachment; filename=system_audit_logs.csv"
    
    return output