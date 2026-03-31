# MarketHub - Product Marketplace with CRM

A full-featured product marketplace with an integrated CRM (Customer Relationship Management) system, built with Python/Flask and SQLite.

## Features

### Marketplace
- Product browsing with categories, search, and sorting
- Product detail pages with related products
- Shopping cart with quantity management
- Checkout flow with order confirmation
- User registration and authentication (customer/seller roles)

### CRM (Admin Backend)
- **Dashboard** â Key metrics, pipeline overview, recent activity
- **Contacts** â Full contact management with search, CRUD operations
- **Leads & Pipeline** â Kanban-style pipeline board and list view, deal tracking
- **Tasks** â Task management with priorities, due dates, and status filtering
- **Notes** â Quick notes linked to contacts
- **Interactions** â Log emails, calls, and meetings per contact
- **Analytics** â Revenue charts, order trends, lead conversion rates, top products

## Tech Stack

- **Backend:** Python 3, Flask, SQLAlchemy
- **Database:** SQLite
- **Frontend:** HTML5, CSS3 (custom design system, no frameworks)
- **Auth:** Session-based with password hashing

## Quick Start

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/marketplace-crm.git
cd marketplace-crm

# Install dependencies
pip install -r requirements.txt

# Seed the database with sample data
python seed.py

# Run the app
python app.py
```

Visit `http://localhost:5000` in your browser.

## Login Credentials (Demo)

| Role     | Username   | Password     |
|----------|------------|--------------|
| Admin    | admin      | admin123     |
| Seller   | techstore  | seller123    |
| Customer | johndoe    | customer123  |

Log in as **admin** to access the CRM at `/crm`.

## Project Structure

```
marketplace-crm/
âââ app.py              # Flask app factory
âââ models.py           # SQLAlchemy models
âââ seed.py             # Database seeder
âââ requirements.txt
âââ routes/
â   âââ auth.py         # Login, register, logout
â   âââ marketplace.py  # Products, cart, checkout
â   âââ crm.py          # CRM pages (admin only)
â   âââ api.py          # JSON API endpoints
âââ templates/
â   âââ base.html
â   âââ auth/
â   âââ marketplace/
â   âââ crm/
âââ static/
    âââ css/
        âââ style.css
```

## API Endpoints

- `GET /api/products` â List all active products
- `GET /api/contacts` â List contacts (admin)
- `GET /api/leads` â List leads (admin)
- `PUT /api/leads/<id>/stage` â Update lead stage (admin)
- `GET /api/dashboard/stats` â Dashboard statistics (admin)

## License

MIT
