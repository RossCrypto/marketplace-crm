from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models import db, Contact, Lead, Task, Note, Interaction, User, Order, Product
from datetime import datetime, timedelta
from functools import wraps

crm_bp = Blueprint('crm', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

# ââ Dashboard ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
@crm_bp.route('/')
@admin_required
def dashboard():
    total_contacts = Contact.query.count()
    total_leads = Lead.query.count()
    open_leads = Lead.query.filter(Lead.stage.notin_(['won', 'lost'])).count()
    won_leads = Lead.query.filter_by(stage='won').count()
    pipeline_value = db.session.query(db.func.sum(Lead.value)).filter(Lead.stage.notin_(['won', 'lost'])).scalar() or 0
    total_revenue = db.session.query(db.func.sum(Order.total)).scalar() or 0
    total_orders = Order.query.count()
    pending_tasks = Task.query.filter(Task.status.in_(['pending', 'in_progress'])).count()

    recent_leads = Lead.query.order_by(Lead.created_at.desc()).limit(5).all()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    upcoming_tasks = Task.query.filter(Task.status != 'completed').order_by(Task.due_date.asc()).limit(5).all()

    # Pipeline stages data
    stages = ['new', 'qualified', 'proposal', 'negotiation', 'won', 'lost']
    pipeline_data = {}
    for stage in stages:
        count = Lead.query.filter_by(stage=stage).count()
        value = db.session.query(db.func.sum(Lead.value)).filter_by(stage=stage).scalar() or 0
        pipeline_data[stage] = {'count': count, 'value': value}

    return render_template('crm/dashboard.html',
        total_contacts=total_contacts, total_leads=total_leads,
        open_leads=open_leads, won_leads=won_leads,
        pipeline_value=pipeline_value, total_revenue=total_revenue,
        total_orders=total_orders, pending_tasks=pending_tasks,
        recent_leads=recent_leads, recent_orders=recent_orders,
        upcoming_tasks=upcoming_tasks, pipeline_data=pipeline_data)

# ââ Contacts âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
@crm_bp.route('/contacts')
@admin_required
def contacts():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q')
    query = Contact.query
    if search:
        query = query.filter(
            db.or_(Contact.first_name.ilike(f'%{search}%'),
                   Contact.last_name.ilike(f'%{search}%'),
                   Contact.email.ilike(f'%{search}%'),
                   Contact.company.ilike(f'%{search}%'))
        )
    contacts = query.order_by(Contact.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('crm/contacts.html', contacts=contacts, search=search)

@crm_bp.route('/contacts/new', methods=['GET', 'POST'])
@admin_required
def new_contact():
    if request.method == 'POST':
        contact = Contact(
            first_name=request.form['first_name'],
            last_name=request.form.get('last_name', ''),
            email=request.form.get('email', ''),
            phone=request.form.get('phone', ''),
            company=request.form.get('company', ''),
            job_title=request.form.get('job_title', ''),
            source=request.form.get('source', 'other'),
            notes_text=request.form.get('notes', '')
        )
        db.session.add(contact)
        db.session.commit()
        flash('Contact created.', 'success')
        return redirect(url_for('crm.contact_detail', id=contact.id))
    return render_template('crm/contact_form.html', contact=None)

@crm_bp.route('/contacts/<int:id>')
@admin_required
def contact_detail(id):
    contact = Contact.query.get_or_404(id)
    notes = Note.query.filter_by(contact_id=id).order_by(Note.created_at.desc()).all()
    tasks = Task.query.filter_by(contact_id=id).order_by(Task.created_at.desc()).all()
    leads = Lead.query.filter_by(contact_id=id).order_by(Lead.created_at.desc()).all()
    interactions = Interaction.query.filter_by(contact_id=id).order_by(Interaction.created_at.desc()).all()
    return render_template('crm/contact_detail.html', contact=contact,
                           notes=notes, tasks=tasks, leads=leads, interactions=interactions)

@crm_bp.route('/contacts/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_contact(id):
    contact = Contact.query.get_or_404(id)
    if request.method == 'POST':
        contact.first_name = request.form['first_name']
        contact.last_name = request.form.get('last_name', '')
        contact.email = request.form.get('email', '')
        contact.phone = request.form.get('phone', '')
        contact.company = request.form.get('company', '')
        contact.job_title = request.form.get('job_title', '')
        contact.source = request.form.get('source', 'other')
        contact.notes_text = request.form.get('notes', '')
        db.session.commit()
        flash('Contact updated.', 'success')
        return redirect(url_for('crm.contact_detail', id=contact.id))
    return render_template('crm/contact_form.html', contact=contact)

@crm_bp.route('/contacts/<int:id>/delete', methods=['POST'])
@admin_required
def delete_contact(id):
    contact = Contact.query.get_or_404(id)
    db.session.delete(contact)
    db.session.commit()
    flash('Contact deleted.', 'info')
    return redirect(url_for('crm.contacts'))

# ââ Leads / Pipeline ââââââââââââââââââââââââââââââââââââââââââââââââââ
@crm_bp.route('/leads')
@admin_required
def leads():
    view = request.args.get('view', 'list')
    stage_filter = request.args.get('stage')
    query = Lead.query
    if stage_filter:
        query = query.filter_by(stage=stage_filter)
    leads = query.order_by(Lead.created_at.desc()).all()

    stages = ['new', 'qualified', 'proposal', 'negotiation', 'won', 'lost']
    pipeline = {}
    for s in stages:
        pipeline[s] = Lead.query.filter_by(stage=s).all()

    return render_template('crm/leads.html', leads=leads, pipeline=pipeline,
                           stages=stages, view=view, stage_filter=stage_filter)

@crm_bp.route('/leads/new', methods=['GET', 'POST'])
@admin_required
def new_lead():
    if request.method == 'POST':
        lead = Lead(
            title=request.form['title'],
            contact_id=request.form.get('contact_id', type=int),
            value=request.form.get('value', 0, type=float),
            stage=request.form.get('stage', 'new'),
            probability=request.form.get('probability', 10, type=int),
            description=request.form.get('description', ''),
            expected_close=datetime.strptime(request.form['expected_close'], '%Y-%m-%d').date() if request.form.get('expected_close') else None
        )
        db.session.add(lead)
        db.session.commit()
        flash('Lead created.', 'success')
        return redirect(url_for('crm.leads'))
    contacts = Contact.query.order_by(Contact.first_name).all()
    return render_template('crm/lead_form.html', lead=None, contacts=contacts)

@crm_bp.route('/leads/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_lead(id):
    lead = Lead.query.get_or_404(id)
    if request.method == 'POST':
        lead.title = request.form['title']
        lead.contact_id = request.form.get('contact_id', type=int)
        lead.value = request.form.get('value', 0, type=float)
        lead.stage = request.form.get('stage', 'new')
        lead.probability = request.form.get('probability', 10, type=int)
        lead.description = request.form.get('description', '')
        lead.expected_close = datetime.strptime(request.form['expected_close'], '%Y-%m-%d').date() if request.form.get('expected_close') else None
        db.session.commit()
        flash('Lead updated.', 'success')
        return redirect(url_for('crm.leads'))
    contacts = Contact.query.order_by(Contact.first_name).all()
    return render_template('crm/lead_form.html', lead=lead, contacts=contacts)

@crm_bp.route('/leads/<int:id>/stage', methods=['POST'])
@admin_required
def update_lead_stage(id):
    lead = Lead.query.get_or_404(id)
    lead.stage = request.form.get('stage', lead.stage)
    db.session.commit()
    return jsonify({'success': True})

@crm_bp.route('/leads/<int:id>/delete', methods=['POST'])
@admin_required
def delete_lead(id):
    lead = Lead.query.get_or_404(id)
    db.session.delete(lead)
    db.session.commit()
    flash('Lead deleted.', 'info')
    return redirect(url_for('crm.leads'))

# ââ Tasks ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
@crm_bp.route('/tasks')
@admin_required
def tasks():
    status_filter = request.args.get('status')
    query = Task.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    tasks = query.order_by(Task.due_date.asc().nullslast()).all()
    return render_template('crm/tasks.html', tasks=tasks, status_filter=status_filter)

@crm_bp.route('/tasks/new', methods=['GET', 'POST'])
@admin_required
def new_task():
    if request.method == 'POST':
        task = Task(
            title=request.form['title'],
            description=request.form.get('description', ''),
            contact_id=request.form.get('contact_id', type=int) or None,
            priority=request.form.get('priority', 'medium'),
            status='pending',
            due_date=datetime.strptime(request.form['due_date'], '%Y-%m-%d') if request.form.get('due_date') else None
        )
        db.session.add(task)
        db.session.commit()
        flash('Task created.', 'success')
        return redirect(url_for('crm.tasks'))
    contacts = Contact.query.order_by(Contact.first_name).all()
    return render_template('crm/task_form.html', task=None, contacts=contacts)

@crm_bp.route('/tasks/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_task(id):
    task = Task.query.get_or_404(id)
    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form.get('description', '')
        task.contact_id = request.form.get('contact_id', type=int) or None
        task.priority = request.form.get('priority', 'medium')
        task.status = request.form.get('status', 'pending')
        task.due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d') if request.form.get('due_date') else None
        if task.status == 'completed' and not task.completed_at:
            task.completed_at = datetime.utcnow()
        db.session.commit()
        flash('Task updated.', 'success')
        return redirect(url_for('crm.tasks'))
    contacts = Contact.query.order_by(Contact.first_name).all()
    return render_template('crm/task_form.html', task=task, contacts=contacts)

@crm_bp.route('/tasks/<int:id>/complete', methods=['POST'])
@admin_required
def complete_task(id):
    task = Task.query.get_or_404(id)
    task.status = 'completed'
    task.completed_at = datetime.utcnow()
    db.session.commit()
    flash('Task completed!', 'success')
    return redirect(url_for('crm.tasks'))

# ââ Notes ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
@crm_bp.route('/notes')
@admin_required
def notes():
    notes = Note.query.order_by(Note.created_at.desc()).all()
    return render_template('crm/notes.html', notes=notes)

@crm_bp.route('/notes/new', methods=['POST'])
@admin_required
def new_note():
    note = Note(
        content=request.form['content'],
        contact_id=request.form.get('contact_id', type=int) or None,
        created_by=session.get('user_id')
    )
    db.session.add(note)
    db.session.commit()
    flash('Note added.', 'success')
    return redirect(request.referrer or url_for('crm.notes'))

# ââ Interactions âââââââââââââââââââââââââââââââââââââââââââââââââââââââ
@crm_bp.route('/interactions/new', methods=['POST'])
@admin_required
def new_interaction():
    interaction = Interaction(
        contact_id=request.form.get('contact_id', type=int),
        type=request.form.get('type', 'note'),
        subject=request.form.get('subject', ''),
        body=request.form.get('body', ''),
        direction=request.form.get('direction', 'outbound'),
        created_by=session.get('user_id')
    )
    db.session.add(interaction)
    db.session.commit()
    flash('Interaction logged.', 'success')
    return redirect(request.referrer or url_for('crm.contacts'))

# ââ Analytics ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
@crm_bp.route('/analytics')
@admin_required
def analytics():
    # Revenue by month (last 6 months)
    months = []
    for i in range(5, -1, -1):
        d = datetime.utcnow() - timedelta(days=30 * i)
        start = d.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if i == 0:
            end = datetime.utcnow()
        else:
            next_m = start.replace(month=start.month % 12 + 1) if start.month < 12 else start.replace(year=start.year + 1, month=1)
            end = next_m
        rev = db.session.query(db.func.sum(Order.total)).filter(Order.created_at.between(start, end)).scalar() or 0
        orders = Order.query.filter(Order.created_at.between(start, end)).count()
        months.append({'label': start.strftime('%b %Y'), 'revenue': rev, 'orders': orders})

    # Lead conversion
    total_leads = Lead.query.count()
    won = Lead.query.filter_by(stage='won').count()
    conversion_rate = round((won / total_leads * 100), 1) if total_leads > 0 else 0

    # Top products
    top_products = db.session.query(
        Product.name, db.func.sum(OrderItem.quantity).label('sold'),
        db.func.sum(OrderItem.price * OrderItem.quantity).label('revenue')
    ).join(OrderItem).group_by(Product.id).order_by(db.text('revenue DESC')).limit(5).all()

    return render_template('crm/analytics.html', months=months,
                           conversion_rate=conversion_rate, total_leads=total_leads,
                           won_leads=won, top_products=top_products)
