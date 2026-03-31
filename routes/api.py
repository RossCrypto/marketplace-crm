from flask import Blueprint, jsonify, request, session
from models import db, Product, Contact, Lead, Task, Order

api_bp = Blueprint('api', __name__)

@api_bp.route('/products')
def get_products():
    products = Product.query.filter_by(is_active=True).all()
    return jsonify([p.to_dict() for p in products])

@api_bp.route('/contacts')
def get_contacts():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    contacts = Contact.query.all()
    return jsonify([c.to_dict() for c in contacts])

@api_bp.route('/leads')
def get_leads():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    leads = Lead.query.all()
    return jsonify([l.to_dict() for l in leads])

@api_bp.route('/leads/<int:id>/stage', methods=['PUT'])
def api_update_stage(id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    lead = Lead.query.get_or_404(id)
    data = request.get_json()
    lead.stage = data.get('stage', lead.stage)
    db.session.commit()
    return jsonify(lead.to_dict())

@api_bp.route('/dashboard/stats')
def dashboard_stats():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify({
        'total_contacts': Contact.query.count(),
        'total_leads': Lead.query.count(),
        'open_leads': Lead.query.filter(Lead.stage.notin_(['won', 'lost'])).count(),
        'pipeline_value': db.session.query(db.func.sum(Lead.value)).filter(Lead.stage.notin_(['won', 'lost'])).scalar() or 0,
        'total_orders': Order.query.count(),
        'total_revenue': db.session.query(db.func.sum(Order.total)).scalar() or 0,
        'pending_tasks': Task.query.filter(Task.status.in_(['pending', 'in_progress'])).count()
    })
