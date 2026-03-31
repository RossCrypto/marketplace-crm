"""Seed the database with sample data for demonstration."""
from app import create_app
from models import db, User, Category, Product, Contact, Lead, Task, Note, Interaction, Order, OrderItem
from datetime import datetime, timedelta
import random

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    # ââ Users ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    admin = User(username='admin', email='admin@markethub.com', role='admin',
                 first_name='Admin', last_name='User')
    admin.set_password('admin123')

    seller1 = User(username='techstore', email='tech@markethub.com', role='seller',
                   first_name='Tech', last_name='Store')
    seller1.set_password('seller123')

    seller2 = User(username='homecraft', email='home@markethub.com', role='seller',
                   first_name='Home', last_name='Craft')
    seller2.set_password('seller123')

    customer1 = User(username='johndoe', email='john@example.com', role='customer',
                     first_name='John', last_name='Doe')
    customer1.set_password('customer123')

    db.session.add_all([admin, seller1, seller2, customer1])
    db.session.commit()

    # ââ Categories âââââââââââââââââââââââââââââââââââââââââââââââââââââ
    categories_data = [
        ('Electronics', 'electronics', 'Gadgets, devices and tech accessories'),
        ('Home & Garden', 'home-garden', 'Furniture, decor and garden supplies'),
        ('Fashion', 'fashion', 'Clothing, shoes and accessories'),
        ('Sports', 'sports', 'Sporting goods and fitness equipment'),
        ('Books', 'books', 'Books, e-books and audiobooks'),
        ('Toys & Games', 'toys-games', 'Toys, board games and puzzles'),
    ]
    categories = []
    for name, slug, desc in categories_data:
        cat = Category(name=name, slug=slug, description=desc)
        categories.append(cat)
        db.session.add(cat)
    db.session.commit()

    # ââ Products âââââââââââââââââââââââââââââââââââââââââââââââââââââââ
    products_data = [
        ('Wireless Bluetooth Headphones', 'wireless-bluetooth-headphones', 'Premium noise-cancelling wireless headphones with 30-hour battery life.', 79.99, 99.99, 50, 0, True),
        ('Smart Watch Pro', 'smart-watch-pro', 'Feature-packed smartwatch with health monitoring and GPS.', 199.99, 249.99, 30, 0, True),
        ('USB-C Hub Adapter', 'usb-c-hub-adapter', '7-in-1 USB-C hub with HDMI, USB 3.0, and SD card reader.', 34.99, None, 100, 0, False),
        ('Mechanical Keyboard RGB', 'mechanical-keyboard-rgb', 'Full-size mechanical keyboard with customisable RGB lighting.', 89.99, 119.99, 40, 0, True),
        ('Portable Speaker', 'portable-speaker', 'Waterproof portable Bluetooth speaker with 360-degree sound.', 49.99, None, 75, 0, False),
        ('Laptop Stand Adjustable', 'laptop-stand-adjustable', 'Ergonomic aluminium laptop stand with adjustable height.', 29.99, None, 60, 1, False),
        ('Ceramic Plant Pot Set', 'ceramic-plant-pot-set', 'Set of 3 minimalist ceramic plant pots in assorted sizes.', 24.99, None, 80, 1, True),
        ('LED Desk Lamp', 'led-desk-lamp', 'Dimmable LED desk lamp with wireless charging base.', 44.99, 59.99, 45, 1, False),
        ('Cotton Throw Blanket', 'cotton-throw-blanket', 'Soft organic cotton throw blanket, machine washable.', 39.99, None, 55, 1, True),
        ('Wall Art Canvas Print', 'wall-art-canvas-print', 'Modern abstract canvas wall art, 60x90cm.', 54.99, 69.99, 25, 1, False),
        ('Running Trainers Ultra', 'running-trainers-ultra', 'Lightweight running shoes with responsive cushioning.', 119.99, 149.99, 35, 2, True),
        ('Denim Jacket Classic', 'denim-jacket-classic', 'Classic fit denim jacket, 100% cotton.', 64.99, None, 40, 2, False),
        ('Leather Wallet Slim', 'leather-wallet-slim', 'Genuine leather slim wallet with RFID protection.', 29.99, None, 90, 2, False),
        ('Yoga Mat Premium', 'yoga-mat-premium', 'Extra thick non-slip yoga mat with carry strap.', 34.99, 44.99, 65, 3, True),
        ('Football Size 5', 'football-size-5', 'Professional match quality football, FIFA approved.', 27.99, None, 100, 3, False),
        ('Resistance Bands Set', 'resistance-bands-set', 'Set of 5 resistance bands with different strengths.', 19.99, None, 120, 3, False),
        ('Python Programming Guide', 'python-programming-guide', 'Comprehensive guide to Python programming for beginners and experts.', 24.99, None, 200, 4, True),
        ('Business Strategy Handbook', 'business-strategy-handbook', 'Essential strategies for growing a successful business.', 18.99, None, 150, 4, False),
        ('Board Game Collection', 'board-game-collection', 'Family board game with 4 classic games in one box.', 32.99, None, 45, 5, True),
        ('Puzzle 1000 Pieces', 'puzzle-1000-pieces', 'High-quality 1000-piece jigsaw puzzle, landscape scene.', 14.99, None, 70, 5, False),
    ]

    products = []
    for name, slug, desc, price, compare, stock, cat_idx, featured in products_data:
        seller = seller1 if cat_idx in [0, 3, 4] else seller2
        p = Product(name=name, slug=slug, description=desc, price=price,
                    compare_price=compare, stock=stock, category_id=categories[cat_idx].id,
                    seller_id=seller.id, featured=featured, is_active=True)
        products.append(p)
        db.session.add(p)
    db.session.commit()

    # ââ CRM Contacts ââââââââââââââââââââââââââââââââââââââââââââââââââ
    contacts_data = [
        ('Sarah', 'Johnson', 'sarah.j@techcorp.com', '+44 7700 900001', 'TechCorp Ltd', 'CTO', 'website'),
        ('Michael', 'Chen', 'mchen@globalretail.com', '+44 7700 900002', 'Global Retail', 'Head of Procurement', 'referral'),
        ('Emma', 'Williams', 'emma.w@startuplab.io', '+44 7700 900003', 'StartupLab', 'Founder', 'social'),
        ('James', 'Taylor', 'james@digitalmedia.co.uk', '+44 7700 900004', 'Digital Media Co', 'Marketing Director', 'email'),
        ('Olivia', 'Brown', 'o.brown@luxurybrands.com', '+44 7700 900005', 'Luxury Brands Inc', 'Buyer', 'website'),
        ('Daniel', 'Wilson', 'dan@innovateuk.org', '+44 7700 900006', 'InnovateUK', 'Programme Manager', 'referral'),
        ('Sophie', 'Davies', 'sophie@ecogoods.co.uk', '+44 7700 900007', 'EcoGoods', 'Operations Lead', 'social'),
        ('Robert', 'Evans', 'robert.e@megastore.com', '+44 7700 900008', 'MegaStore', 'VP of Sales', 'email'),
        ('Charlotte', 'Thomas', 'charlotte@fashionfw.com', '+44 7700 900009', 'Fashion Forward', 'Creative Director', 'website'),
        ('William', 'Roberts', 'will@supplychainpro.com', '+44 7700 900010', 'SupplyChain Pro', 'Logistics Manager', 'referral'),
    ]

    contacts = []
    for fn, ln, email, phone, company, title, source in contacts_data:
        c = Contact(first_name=fn, last_name=ln, email=email, phone=phone,
                    company=company, job_title=title, source=source)
        contacts.append(c)
        db.session.add(c)
    db.session.commit()

    # ââ CRM Leads âââââââââââââââââââââââââââââââââââââââââââââââââââââ
    stages = ['new', 'qualified', 'proposal', 'negotiation', 'won', 'lost']
    leads_data = [
        ('Enterprise Software Bundle', 0, 25000, 'qualified', 40, 30),
        ('Retail Store Partnership', 1, 15000, 'proposal', 60, 45),
        ('Startup Hardware Package', 2, 8500, 'new', 15, 60),
        ('Media Advertising Deal', 3, 12000, 'negotiation', 75, 20),
        ('Luxury Brand Collaboration', 4, 45000, 'won', 100, -10),
        ('Innovation Lab Equipment', 5, 9000, 'new', 10, 90),
        ('Eco-Friendly Product Line', 6, 18000, 'qualified', 35, 50),
        ('MegaStore Wholesale Order', 7, 65000, 'proposal', 55, 40),
        ('Fashion Collection Launch', 8, 22000, 'negotiation', 80, 15),
        ('Supply Chain Optimisation', 9, 11000, 'lost', 0, -5),
        ('Cloud Migration Project', 0, 35000, 'qualified', 45, 55),
        ('Digital Marketing Campaign', 3, 7500, 'new', 20, 70),
    ]

    leads = []
    for title, ci, value, stage, prob, days_offset in leads_data:
        lead = Lead(title=title, contact_id=contacts[ci].id, value=value,
                    stage=stage, probability=prob,
                    expected_close=datetime.utcnow().date() + timedelta(days=days_offset),
                    description=f'Deal with {contacts[ci].company}')
        leads.append(lead)
        db.session.add(lead)
    db.session.commit()

    # ââ CRM Tasks âââââââââââââââââââââââââââââââââââââââââââââââââââââ
    tasks_data = [
        ('Follow up with Sarah on software bundle', 'Send proposal draft and schedule demo call', 0, 'high', 'pending', 3),
        ('Prepare retail partnership presentation', 'Create slides for Global Retail meeting', 1, 'urgent', 'in_progress', 1),
        ('Research startup lab requirements', 'Gather info on hardware needs', 2, 'medium', 'pending', 7),
        ('Send contract to Luxury Brands', 'Final contract review and send', 4, 'high', 'pending', 2),
        ('Review eco-friendly product samples', 'Check quality of new product line samples', 6, 'medium', 'completed', -2),
        ('Call MegaStore for order confirmation', 'Confirm wholesale quantities and delivery dates', 7, 'urgent', 'pending', 0),
        ('Update CRM with Fashion FW contacts', 'Add new contacts from fashion event', 8, 'low', 'pending', 5),
        ('Quarterly pipeline review', 'Prepare pipeline report for management', None, 'high', 'pending', 10),
    ]

    for title, desc, ci, priority, status, days in tasks_data:
        task = Task(title=title, description=desc,
                    contact_id=contacts[ci].id if ci is not None else None,
                    priority=priority, status=status,
                    due_date=datetime.utcnow() + timedelta(days=days))
        if status == 'completed':
            task.completed_at = datetime.utcnow()
        db.session.add(task)
    db.session.commit()

    # ââ CRM Notes âââââââââââââââââââââââââââââââââââââââââââââââââââââ
    notes_data = [
        ('Sarah is very interested in the enterprise bundle. Wants a demo next week.', 0),
        ('Michael mentioned they are reviewing 3 vendors. We need to be competitive on price.', 1),
        ('Emma is bootstrapping - needs flexible payment terms.', 2),
        ('Great call with Olivia. She loves our product quality.', 4),
        ('MegaStore looking to place their largest order ever. High priority.', 7),
    ]

    for content, ci in notes_data:
        note = Note(content=content, contact_id=contacts[ci].id, created_by=admin.id)
        db.session.add(note)
    db.session.commit()

    # ââ CRM Interactions ââââââââââââââââââââââââââââââââââââââââââââââ
    interactions_data = [
        (0, 'email', 'Initial Enquiry', 'Received enquiry about enterprise pricing', 'inbound'),
        (0, 'call', 'Discovery Call', '30-min call discussing requirements', 'outbound'),
        (1, 'meeting', 'On-site Visit', 'Visited Global Retail HQ for product demo', 'outbound'),
        (4, 'email', 'Contract Sent', 'Sent final contract for review', 'outbound'),
        (7, 'call', 'Order Discussion', 'Discussed wholesale pricing and delivery', 'outbound'),
        (3, 'email', 'Marketing Proposal', 'Sent advertising partnership proposal', 'outbound'),
        (8, 'meeting', 'Fashion Show Meeting', 'Met at fashion event to discuss collab', 'outbound'),
    ]

    for ci, itype, subject, body, direction in interactions_data:
        interaction = Interaction(contact_id=contacts[ci].id, type=itype,
                                  subject=subject, body=body, direction=direction,
                                  created_by=admin.id)
        db.session.add(interaction)
    db.session.commit()

    # ââ Sample Orders âââââââââââââââââââââââââââââââââââââââââââââââââ
    statuses = ['confirmed', 'shipped', 'delivered', 'delivered', 'delivered']
    for i in range(8):
        order = Order(
            order_number=f'ORD-{10000+i}',
            user_id=customer1.id,
            status=random.choice(statuses),
            shipping_address='123 High Street, London, UK',
            payment_method='card',
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 90))
        )
        # Add 1-3 random items
        order_products = random.sample(products, random.randint(1, 3))
        total = 0
        for p in order_products:
            qty = random.randint(1, 3)
            item = OrderItem(product_id=p.id, quantity=qty, price=p.price)
            order.items.append(item)
            total += p.price * qty
        order.total = round(total, 2)
        db.session.add(order)
    db.session.commit()

    print('Database seeded successfully!')
    print(f'  Users: {User.query.count()}')
    print(f'  Categories: {Category.query.count()}')
    print(f'  Products: {Product.query.count()}')
    print(f'  Contacts: {Contact.query.count()}')
    print(f'  Leads: {Lead.query.count()}')
    print(f'  Tasks: {Task.query.count()}')
    print(f'  Notes: {Note.query.count()}')
    print(f'  Orders: {Order.query.count()}')
    print()
    print('Login credentials:')
    print('  Admin:    admin / admin123')
    print('  Seller:   techstore / seller123')
    print('  Customer: johndoe / customer123')
