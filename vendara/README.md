# Vendara — Full Stack Procurement ERP

A comprehensive procurement and vendor management ERP system built with Python Flask, HTML, CSS, and SQLite. Designed for hackathons with a professional Odoo-inspired design and complete workflow automation.

## 🎨 Design

**Odoo Official Color Scheme:**
- Primary: `#714B67` (Odoo Purple)
- Background: `#1C1C1C` (Dark)
- Accent: `#00A09D` (Odoo Teal)
- Sidebar: `#4B2E4A` (Dark Purple)
- Font: Roboto

## 👥 Role-Based Login System

5 login roles, each with different dashboards and permissions:

1. **Admin** — Full access, system settings, vendor approvals
2. **Purchase Manager** — Approves RFQs, POs, vendors
3. **Requester** — Only raises purchase requisitions
4. **Finance** — Invoice processing & payments only
5. **Vendor** — External portal, submits quotes & invoices

## 📦 Modules

### 1. Vendor Onboarding
- Register vendor with company details, GST, contact, bank info
- Auto-generate Vendor ID
- Admin approval workflow
- Document upload support

### 2. Purchase Requisition
- Requester fills item details, quantity, budget, department, urgency
- Goes to Manager for approval
- Status workflow: Draft → Submitted → Approved → Rejected

### 3. RFQ Management
- Procurement creates RFQ from approved requisition
- Selects vendors from approved list
- Vendors get notified
- Deadline setting
- PDF preview available

### 4. Quotation Comparison Engine
- Vendors submit price, delivery days, warranty
- System auto-ranks by: lowest price, fastest delivery, highest rating
- Side-by-side comparison table
- Savings vs budget shown in green

### 5. Approval Workflow
- Manager sees pending approvals
- Approve / Reject / Request Revision actions
- Every action logged with timestamp + user
- Email notification simulation shown on screen

### 6. Purchase Order Generation
- Auto-generated on approval
- PO number, vendor details, item list, amount, GST breakdown
- Delivery date, terms
- Download as PDF
- Send to vendor button

### 7. Goods Receipt Note (GRN)
- Warehouse logs received qty vs ordered qty
- Condition check
- Auto-flagged if mismatch
- GRN number generated

### 8. Invoice & 3-Way Match
- Vendor uploads invoice
- System checks: PO ✓ vs GRN ✓ vs Invoice ✓
- All match → auto-approve for payment
- Any mismatch → flagged with reason shown clearly

### 9. Vendor Scorecard
- Auto-score vendor after every completed order
- Delivery (on time?), Quality (GRN issues?), Price (vs market?)
- Overall rating updated
- Shown on vendor profile

### 10. Analytics Dashboard
- Monthly spend bar chart
- Savings vs budget donut chart
- Top 5 vendors by spend
- Pending approvals counter
- RFQ to PO conversion rate
- Category-wise spend breakdown

## ⭐ SmartSource AI Advisor

The standout feature — a built-in procurement intelligence panel that:

- **Flags overpriced quotes** — "This quote is 18% above market rate for this item category"
- **Suggests best vendor** — based on past performance score + current quote price
- **Predicts delivery risk** — "Vendor X has missed deadlines 2x in last 3 orders"
- **Budget burn rate alert** — "At current pace, Q1 budget exhausts by Feb 22"
- **Duplicate PO detection** — warns if similar item was purchased recently

Shown as a sidebar panel with insight cards. Uses rule-based logic + mock data to simulate AI. Looks smart, feels real.

## 🔄 Workflow

Every screen has:
- Clear Next Step button
- No dead ends — every action leads somewhere
- Breadcrumb navigation always visible
- Status badges on every record (color coded)
- Confirmation modals before destructive actions

## 🐍 Python Backend (Flask)

- REST API endpoints for all modules
- SQLite database (simple, no setup)
- Session-based login per role
- Mock data pre-seeded for demo
- `/api/vendors`, `/api/rfq`, `/api/po`, `/api/invoices`, `/api/dashboard`

## 📁 Project Structure

```
vendara/
├── app.py                      # Main Flask application
├── seed_data.py                # Mock data seeding script
├── requirements.txt             # Python dependencies
├── README.md                   # This file
├── database/
│   └── schema.sql              # Database schema
├── static/
│   └── style.css               # Odoo-inspired CSS
└── templates/
    ├── base.html               # Base template
    ├── login.html              # Login page
    ├── signup.html             # Signup page
    ├── dashboard.html          # Dashboard
    ├── vendors.html            # Vendor management
    ├── requisitions.html       # Purchase requisitions
    ├── rfqs.html               # RFQ management
    ├── quotations.html         # Quotations & comparison
    ├── pos.html                # Purchase orders
    ├── grns.html               # Goods receipt notes
    ├── invoices.html           # Invoices & 3-way match
    ├── scorecards.html         # Vendor scorecards
    └── analytics.html          # Analytics dashboard
```

## 🚀 Setup Instructions

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. **Navigate to the project directory:**
   ```bash
   cd vendara
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Seed the database with mock data:**
   ```bash
   python seed_data.py
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Access the application:**
   Open your browser and navigate to `http://127.0.0.1:5000`

## 🔐 Default Login Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@vendara.com | admin123 |
| Purchase Manager | manager@vendara.com | manager123 |
| Requester | requester@vendara.com | requester123 |
| Finance | finance@vendara.com | finance123 |
| Vendor | techcorp@vendor.com | vendor123 |

## 📋 Hackathon Workflow

1. **Login** as Requester
2. **Create Requisition** → Submit for approval
3. **Login** as Purchase Manager
4. **Approve Requisition** → Create RFQ
5. **Select Vendors** → Send RFQ
6. **Login** as Vendor
7. **Submit Quotation** for RFQ
8. **Login** as Purchase Manager
9. **Compare Quotations** → Generate PO
10. **Login** as Warehouse/Manager
11. **Create GRN** when goods received
12. **Login** as Vendor
13. **Upload Invoice**
14. **Login** as Finance
15. **3-Way Match** → Process payment
16. **Create Scorecard** for vendor
17. **View Analytics** dashboard

## 🎯 Database Schema

### Tables

1. **users** — User authentication and role management
2. **vendors** — Vendor information and contact details
3. **requisitions** — Purchase requisitions
4. **rfqs** — Request for Quotation details
5. **rfq_vendors** — Vendor assignments to RFQs
6. **quotations** — Vendor quotations for RFQs
7. **approvals** — Approval decisions and remarks
8. **purchase_orders** — Purchase order generation
9. **grns** — Goods receipt notes
10. **invoices** — Invoice management with 3-way match
11. **vendor_scorecards** — Vendor performance tracking
12. **analytics** — Analytics data storage
13. **notifications** — Email notification simulation

See `database/schema.sql` for complete table definitions.

## 🔌 REST API Endpoints

- `GET /api/vendors` — Get all vendors
- `GET /api/requisitions` — Get all requisitions
- `GET /api/rfqs` — Get all RFQs
- `GET /api/pos` — Get all purchase orders
- `GET /api/invoices` — Get all invoices
- `GET /api/dashboard` — Get dashboard statistics

## 🎨 UI Design Notes

- **Professional ERP design** inspired by Odoo
- **Dark theme** with white card surfaces
- **Purple primary color** (#714B67)
- **Teal accent color** (#00A09D) for success actions
- **Responsive layout** for mobile and desktop
- **Modern tables** with status badges
- **Clean typography** using Roboto font
- **No Bootstrap** — pure custom CSS
- **Handcrafted look** — no generic templates

## 🐛 Troubleshooting

### Database Issues
If you encounter database errors, delete the `vendara.db` file and run `python seed_data.py` again.

### Port Already in Use
If port 5000 is already in use, modify the port in `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)
```

### Dependencies Issues
If you encounter dependency issues, try:
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## 📝 Features in Detail

### Authentication
- User registration with role selection
- Secure password hashing using SHA256
- Session-based authentication
- Role-based access control
- Login/logout functionality

### Dashboard
- Real-time statistics cards
- SmartSource AI Advisor panel
- Recent activity feed
- Pending approvals counter
- Role-based navigation

### Vendor Management
- Add new vendors with complete details
- Approval workflow for new vendors
- Search and filter vendors
- Status management (pending, approved, active, rejected)

### Purchase Requisition
- Create requisitions with item details
- Submit for approval workflow
- Approve/Reject by Purchase Manager
- Status tracking (draft, submitted, approved, rejected)

### RFQ Management
- Create RFQ from approved requisition
- Select vendors from approved list
- Set deadlines
- Send RFQ to vendors
- PDF preview simulation

### Quotation Comparison
- Side-by-side comparison table
- Auto-ranking by price, delivery, rating
- Best price highlight
- Generate PO from selected quotation

### Purchase Orders
- Auto-generate from approved quotation
- GST calculation
- PDF download simulation
- Send to vendor
- Status tracking

### Goods Receipt Notes
- Log received quantity
- Condition check
- Auto-flag mismatches
- GRN number generation

### Invoice & 3-Way Match
- Vendor invoice upload
- Automatic 3-way matching (PO vs GRN vs Invoice)
- Mismatch detection
- Payment processing

### Vendor Scorecard
- Auto-score after completed orders
- Delivery, Quality, Price scores
- Overall rating calculation
- Vendor profile integration

### Analytics Dashboard
- Monthly spend trend chart
- Top vendors by spend
- Category-wise breakdown
- Savings vs budget visualization
- Conversion rate tracking

## 🏆 Hackathon Tips

1. **Start with the workflow** — Follow the complete procurement cycle
2. **Try different roles** — Experience the system from each user perspective
3. **Use the AI Advisor** — Check the smart insights on the dashboard
4. **Test the 3-way match** — Upload invoices and see the matching logic
5. **Explore the analytics** — View the visualizations and charts

## 📄 License

This project is created for hackathon purposes. Feel free to use and modify as needed.

## 👥 Team

Vendara — Full Stack Procurement ERP
Built for hackathon demonstration
