from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models import db, Product, Category, Order, OrderItem, User
from datetime import datetime
import uuid

marketplace_bp = Blueprint('marketplace', __name__)

@marketplace_bp.route('/')
def index():
    featured = Product.query.filter_by(featured=True, is_active=True).limit(8).all()
    categories = Category.query.all()
    latest = Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).limit(8).all()
    return render_template('marketplace/index.html', featured=featured, categories=categories, latest=latest)

@marketplace_bp.route('/products')
def products():
    page = request.args.get('page', 1, type=int)
    category_slug = request.args.get('category')
    search = request.args.get('q')
    sort = request.args.get('sort', 'newest')

    query = Product.query.filter_by(is_active=True)
    if category_slug:
        cat = Category.query.filter_by(slug=category_slug).first()
        if cat:
            query = query.filter_by(category_id=cat.id)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))

    if sort == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_high':
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(Product.created_at.desc())

    products = query.paginate(page=page, per_page=12, error_out=False)
    categories = Category.query.all()
    return render_template('marketplace/products.html', products=products, categories=categories,
                           current_category=category_slug, search=search, sort=sort)

@marketplace_bp.route('/product/<slug>')
def product_detail(slug):
    product = Product.query.filter_by(slug=slug, is_active=True).first_or_404()
    related = Product.query.filter(Product.category_id == product.category_id, Product.id != product.id, Product.is_active == True).limit(4).all()
    return render_template('marketplace/product_detail.html', product=product, related=related)

@marketplace_bp.route('/cart')
def cart():
    cart_items = session.get('cart', {})
    products = []
    total = 0
    for pid, qty in cart_items.items():
        p = Product.query.get(int(pid))
        if p:
            subtotal = p.price * qty
            total += subtotal
            products.append({'product': p, 'quantity': qty, 'subtotal': subtotal})
    return render_template('marketplace/cart.html', items=products, total=total)

@marketplace_bp.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    cart = session.get('cart', {})
    qty = request.form.get('quantity', 1, type=int)
    pid = str(product_id)
    cart[pid] = cart.get(pid, 0) + qty
    session['cart'] = cart
    flash('Item added to cart!', 'success')
    return redirect(request.referrer or url_for('marketplace.products'))

@marketplace_bp.route('/cart/update/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    cart = session.get('cart', {})
    qty = request.form.get('quantity', 1, type=int)
    pid = str(product_id)
    if qty <= 0:
        cart.pop(pid, None)
    else:
        cart[pid] = qty
    session['cart'] = cart
    return redirect(url_for('marketplace.cart'))

@marketplace_bp.route('/cart/remove/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    cart.pop(str(product_id), None)
    session['cart'] = cart
    flash('Item removed from cart.', 'info')
    return redirect(url_for('marketplace.cart'))

@marketplace_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        flash('Please log in to checkout.', 'error')
        return redirect(url_for('auth.login'))

    cart_items = session.get('cart', {})
    if not cart_items:
        flash('Your cart is empty.', 'info')
        return redirect(url_for('marketplace.products'))

    if request.method == 'POST':
        order = Order(
            order_number=f"ORD-{uuid.uuid4().hex[:8].upper()}",
            user_id=session['user_id'],
            shipping_address=request.form.get('address'),
            payment_method=request.form.get('payment_method', 'card'),
            status='confirmed'
        )
        total = 0
        for pid, qty in cart_items.items():
            product = Product.query.get(int(pid))
            if product:
                item = OrderItem(product_id=product.id, quantity=qty, price=product.price)
                order.items.append(item)
                total += product.price * qty
                product.stock = max(0, product.stock - qty)
        order.total = total
        db.session.add(order)
        db.session.commit()
        session.pop('cart', None)
        flash(f'Order {order.order_number} placed successfully!', 'success')
        return redirect(url_for('marketplace.order_confirmation', order_id=order.id))

    products = []
    total = 0
    for pid, qty in cart_items.items():
        p = Product.query.get(int(pid))
        if p:
            subtotal = p.price * qty
            total += subtotal
            products.append({'product': p, 'quantity': qty, 'subtotal': subtotal})
    return render_template('marketplace/checkout.html', items=products, total=total)

@marketplace_bp.route('/order/<int:order_id>')
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('marketplace/order_confirmation.html', order=order)
