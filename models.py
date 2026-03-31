from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# ââ Users ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='customer')  # customer, seller, admin
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    avatar_url = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    products = db.relationship('Product', backref='seller', lazy=True)
    orders = db.relationship('Order', backref='customer', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id, 'username': self.username, 'email': self.email,
            'role': self.role, 'first_name': self.first_name,
            'last_name': self.last_name, 'phone': self.phone,
            'created_at': self.created_at.isoformat()
        }

# ââ Products âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text)
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    compare_price = db.Column(db.Float)
    stock = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(256))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_active = db.Column(db.Boolean, default=True)
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order_items = db.relationship('OrderItem', backref='product', lazy=True)

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'slug': self.slug,
            'description': self.description, 'price': self.price,
            'compare_price': self.compare_price, 'stock': self.stock,
            'image_url': self.image_url, 'category': self.category.name if self.category else None,
            'seller': self.seller.username if self.seller else None,
            'is_active': self.is_active, 'featured': self.featured,
            'created_at': self.created_at.isoformat()
        }

# ââ Orders âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, shipped, delivered, cancelled
    total = db.Column(db.Float, default=0)
    shipping_address = db.Column(db.Text)
    payment_method = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship('OrderItem', backref='order', lazy=True)

    def to_dict(self):
        return {
            'id': self.id, 'order_number': self.order_number,
            'status': self.status, 'total': self.total,
            'items': [i.to_dict() for i in self.items],
            'created_at': self.created_at.isoformat()
        }

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id, 'product_name': self.product.name if self.product else '',
            'quantity': self.quantity, 'price': self.price
        }

# ââ CRM: Contacts âââââââââââââââââââââââââââââââââââââââââââââââââââââ
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    company = db.Column(db.String(100))
    job_title = db.Column(db.String(100))
    source = db.Column(db.String(50))  # website, referral, social, email, other
    status = db.Column(db.String(20), default='active')  # active, inactive
    notes_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    leads = db.relationship('Lead', backref='contact', lazy=True)
    notes = db.relationship('Note', backref='contact', lazy=True)
    tasks = db.relationship('Task', backref='contact', lazy=True)
    interactions = db.relationship('Interaction', backref='contact', lazy=True)

    def to_dict(self):
        return {
            'id': self.id, 'first_name': self.first_name,
            'last_name': self.last_name or '', 'email': self.email,
            'phone': self.phone, 'company': self.company,
            'job_title': self.job_title, 'source': self.source,
            'status': self.status, 'created_at': self.created_at.isoformat()
        }

# ââ CRM: Leads & Pipeline âââââââââââââââââââââââââââââââââââââââââââââ
class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'))
    value = db.Column(db.Float, default=0)
    stage = db.Column(db.String(30), default='new')  # new, qualified, proposal, negotiation, won, lost
    probability = db.Column(db.Integer, default=10)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    expected_close = db.Column(db.Date)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assignee = db.relationship('User', backref='assigned_leads')

    def to_dict(self):
        return {
            'id': self.id, 'title': self.title, 'value': self.value,
            'stage': self.stage, 'probability': self.probability,
            'contact_name': f"{self.contact.first_name} {self.contact.last_name or ''}" if self.contact else '',
            'contact_id': self.contact_id,
            'assigned_to': self.assignee.username if self.assignee else '',
            'expected_close': self.expected_close.isoformat() if self.expected_close else '',
            'created_at': self.created_at.isoformat()
        }

# ââ CRM: Tasks âââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'))
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    priority = db.Column(db.String(10), default='medium')  # low, medium, high, urgent
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, cancelled
    due_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    assignee = db.relationship('User', backref='tasks')

    def to_dict(self):
        return {
            'id': self.id, 'title': self.title, 'description': self.description,
            'priority': self.priority, 'status': self.status,
            'contact_name': f"{self.contact.first_name} {self.contact.last_name or ''}" if self.contact else '',
            'due_date': self.due_date.isoformat() if self.due_date else '',
            'created_at': self.created_at.isoformat()
        }

# ââ CRM: Notes âââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship('User', backref='notes')

    def to_dict(self):
        return {
            'id': self.id, 'content': self.content,
            'contact_name': f"{self.contact.first_name} {self.contact.last_name or ''}" if self.contact else '',
            'author': self.author.username if self.author else '',
            'created_at': self.created_at.isoformat()
        }

# ââ CRM: Interactions (Email Integration) âââââââââââââââââââââââââââââ
class Interaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'))
    type = db.Column(db.String(20))  # email, call, meeting, note
    subject = db.Column(db.String(200))
    body = db.Column(db.Text)
    direction = db.Column(db.String(10))  # inbound, outbound
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship('User', backref='interactions')

    def to_dict(self):
        return {
            'id': self.id, 'type': self.type, 'subject': self.subject,
            'body': self.body, 'direction': self.direction,
            'contact_name': f"{self.contact.first_name} {self.contact.last_name or ''}" if self.contact else '',
            'created_at': self.created_at.isoformat()
        }
