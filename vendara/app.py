"""
Vendara — Full Stack Procurement ERP
Flask Application with SQLite Database
5-Role Authentication System
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import hashlib
from datetime import datetime, date, timedelta
import random

# Initialize Flask Application
app = Flask(__name__)

# Secret Key for Session Management
app.secret_key = 'vendara_secret_key_2024'

# SQLite Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vendara.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# ==================== UTILITY FUNCTIONS ====================

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verify password against hash"""
    return hash_password(password) == hashed

def is_logged_in():
    """Check if user is logged in"""
    return 'user_id' in session

def login_required(f):
    """Decorator to require login for routes"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    """Decorator to require specific role"""
    from functools import wraps
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not is_logged_in():
                flash('Please login to access this page.', 'warning')
                return redirect(url_for('login'))
            if session.get('user_role') not in allowed_roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def generate_vendor_id():
    """Generate unique vendor ID"""
    return 'VND' + datetime.now().strftime('%Y%m%d') + str(random.randint(1000, 9999))

def generate_requisition_number():
    """Generate unique requisition number"""
    return 'REQ' + datetime.now().strftime('%Y%m%d') + str(random.randint(1000, 9999))

def generate_rfq_number():
    """Generate unique RFQ number"""
    return 'RFQ' + datetime.now().strftime('%Y%m%d') + str(random.randint(1000, 9999))

def generate_po_number():
    """Generate unique PO number"""
    return 'PO' + datetime.now().strftime('%Y%m%d') + str(random.randint(1000, 9999))

def generate_grn_number():
    """Generate unique GRN number"""
    return 'GRN' + datetime.now().strftime('%Y%m%d') + str(random.randint(1000, 9999))

def generate_invoice_number():
    """Generate unique invoice number"""
    return 'INV' + datetime.now().strftime('%Y%m%d') + str(random.randint(1000, 9999))

# ==================== DATABASE MODELS ====================

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    company_name = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Vendor(db.Model):
    __tablename__ = 'vendors'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.String(50), unique=True, nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    gst_number = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text)
    bank_name = db.Column(db.String(100))
    bank_account = db.Column(db.String(50))
    ifsc_code = db.Column(db.String(20))
    documents = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approver = db.relationship('User', backref='approved_vendors')

class Requisition(db.Model):
    __tablename__ = 'requisitions'
    id = db.Column(db.Integer, primary_key=True)
    requisition_number = db.Column(db.String(50), unique=True, nullable=False)
    item_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    estimated_budget = db.Column(db.Float, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    urgency = db.Column(db.String(20), default='normal')
    requested_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='draft')
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    requester = db.relationship('User', foreign_keys=[requested_by], backref='requisitions')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_requisitions')

class RFQ(db.Model):
    __tablename__ = 'rfqs'
    id = db.Column(db.Integer, primary_key=True)
    rfq_number = db.Column(db.String(50), unique=True, nullable=False)
    requisition_id = db.Column(db.Integer, db.ForeignKey('requisitions.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    deadline = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='open')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    requisition = db.relationship('Requisition', backref='rfqs')
    creator = db.relationship('User', backref='created_rfqs')

class RFQVendor(db.Model):
    __tablename__ = 'rfq_vendors'
    id = db.Column(db.Integer, primary_key=True)
    rfq_id = db.Column(db.Integer, db.ForeignKey('rfqs.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    sent_at = db.Column(db.DateTime)
    rfq = db.relationship('RFQ', backref='rfq_vendors')
    vendor = db.relationship('Vendor', backref='rfq_vendors')

class Quotation(db.Model):
    __tablename__ = 'quotations'
    id = db.Column(db.Integer, primary_key=True)
    rfq_id = db.Column(db.Integer, db.ForeignKey('rfqs.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    delivery_days = db.Column(db.Integer, nullable=False)
    warranty = db.Column(db.Text)
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    submitted_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    rfq = db.relationship('RFQ', backref='quotations')
    vendor = db.relationship('Vendor', backref='quotations')

class Approval(db.Model):
    __tablename__ = 'approvals'
    id = db.Column(db.Integer, primary_key=True)
    module_type = db.Column(db.String(20), nullable=False)
    module_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(20), nullable=False)
    remarks = db.Column(db.Text)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    approved_at = db.Column(db.DateTime, default=datetime.utcnow)
    approver = db.relationship('User', backref='approvals')

class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'
    id = db.Column(db.Integer, primary_key=True)
    po_number = db.Column(db.String(50), unique=True, nullable=False)
    quotation_id = db.Column(db.Integer, db.ForeignKey('quotations.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    item_name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    gst_amount = db.Column(db.Float, nullable=False)
    grand_total = db.Column(db.Float, nullable=False)
    delivery_date = db.Column(db.Date, nullable=False)
    payment_terms = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    quotation = db.relationship('Quotation', backref='purchase_orders')
    vendor = db.relationship('Vendor', backref='purchase_orders')
    creator = db.relationship('User', backref='created_pos')

class GRN(db.Model):
    __tablename__ = 'grns'
    id = db.Column(db.Integer, primary_key=True)
    grn_number = db.Column(db.String(50), unique=True, nullable=False)
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    received_quantity = db.Column(db.Integer, nullable=False)
    ordered_quantity = db.Column(db.Integer, nullable=False)
    condition_check = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    received_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    received_at = db.Column(db.DateTime, default=datetime.utcnow)
    remarks = db.Column(db.Text)
    po = db.relationship('PurchaseOrder', backref='grns')
    receiver = db.relationship('User', backref='received_grns')

class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    grn_id = db.Column(db.Integer, db.ForeignKey('grns.id'))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    tax = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    po_match = db.Column(db.String(20), default='pending')
    grn_match = db.Column(db.String(20), default='pending')
    invoice_match = db.Column(db.String(20), default='pending')
    overall_status = db.Column(db.String(20), default='pending')
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    uploaded_at = db.Column(db.DateTime)
    processed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    processed_at = db.Column(db.DateTime)
    remarks = db.Column(db.Text)
    po = db.relationship('PurchaseOrder', backref='invoices')
    grn = db.relationship('GRN', backref='invoices')
    vendor = db.relationship('Vendor', backref='invoices')
    uploader = db.relationship('User', foreign_keys=[uploaded_by], backref='uploaded_invoices')
    processor = db.relationship('User', foreign_keys=[processed_by], backref='processed_invoices')

class VendorScorecard(db.Model):
    __tablename__ = 'vendor_scorecards'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    delivery_score = db.Column(db.Integer)
    quality_score = db.Column(db.Integer)
    price_score = db.Column(db.Integer)
    overall_score = db.Column(db.Float)
    rated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rated_at = db.Column(db.DateTime, default=datetime.utcnow)
    remarks = db.Column(db.Text)
    vendor = db.relationship('Vendor', backref='scorecards')
    po = db.relationship('PurchaseOrder', backref='scorecards')
    rater = db.relationship('User', backref='rated_scorecards')

class Analytics(db.Model):
    __tablename__ = 'analytics'
    id = db.Column(db.Integer, primary_key=True)
    metric_type = db.Column(db.String(50), nullable=False)
    metric_value = db.Column(db.Float, nullable=False)
    metric_date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(100))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    vendor = db.relationship('Vendor', backref='analytics')

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), default='info')
    is_read = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='notifications')

# Create all tables
with app.app_context():
    db.create_all()

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/')
def index():
    """Redirect to login or dashboard based on login status"""
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and verify_password(password, user.password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email
            session['user_role'] = user.role
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user registration"""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'requester')
        company_name = request.form.get('company_name', '')
        
        existing_user = User.query.filter_by(email=email).first()
        
        if existing_user:
            flash('Email already exists!', 'danger')
        else:
            hashed_password = hash_password(password)
            new_user = User(
                name=name,
                email=email,
                password=hashed_password,
                role=role,
                company_name=company_name
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    """Handle user logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ==================== DASHBOARD ROUTE ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """Display role-based dashboard"""
    role = session.get('user_role')
    role_display = role.replace('_', ' ').title() if role else ''
    
    # Check for deadline reminders (auto-trigger on dashboard load)
    check_deadline_reminders()
    
    # Get statistics based on role
    total_vendors = Vendor.query.count()
    total_requisitions = Requisition.query.count()
    total_rfqs = RFQ.query.count()
    total_quotations = Quotation.query.count()
    total_pos = PurchaseOrder.query.count()
    total_invoices = Invoice.query.count()
    
    # Get pending approvals
    pending_requisitions = Requisition.query.filter_by(status='submitted').count()
    pending_rfqs = RFQ.query.filter_by(status='open').count()
    pending_quotations = Quotation.query.filter_by(status='pending').count()
    pending_invoices = Invoice.query.filter_by(overall_status='pending').count()
    
    # Get recent activities
    recent_requisitions = Requisition.query.order_by(Requisition.created_at.desc()).limit(3).all()
    recent_rfqs = RFQ.query.order_by(RFQ.created_at.desc()).limit(3).all()
    
    recent_activities = []
    for r in recent_requisitions:
        recent_activities.append({
            'type': 'Requisition',
            'name': r.item_name,
            'status': r.status,
            'created_at': r.created_at
        })
    for r in recent_rfqs:
        recent_activities.append({
            'type': 'RFQ',
            'name': r.title,
            'status': r.status,
            'created_at': r.created_at
        })
    
    recent_activities.sort(key=lambda x: x['created_at'], reverse=True)
    recent_activities = recent_activities[:5]
    
    # Get AI Advisor insights
    ai_insights = get_ai_insights()
    
    # Get user notifications
    user_notifications = Notification.query.filter_by(user_id=session['user_id']).order_by(Notification.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html',
                         role=role,
                         role_display=role_display,
                         total_vendors=total_vendors,
                         total_requisitions=total_requisitions,
                         total_rfqs=total_rfqs,
                         total_quotations=total_quotations,
                         total_pos=total_pos,
                         total_invoices=total_invoices,
                         pending_requisitions=pending_requisitions,
                         pending_rfqs=pending_rfqs,
                         pending_quotations=pending_quotations,
                         pending_invoices=pending_invoices,
                         recent_activities=recent_activities,
                         ai_insights=ai_insights,
                         notifications=user_notifications)

def get_ai_insights():
    """Generate AI Advisor insights using rule-based logic"""
    insights = []
    
    # Check for overpriced quotations
    quotations = Quotation.query.filter_by(status='pending').all()
    for q in quotations:
        if q.price > 100000:  # Threshold for expensive items
            insights.append({
                'type': 'warning',
                'title': 'High Price Alert',
                'message': f'Quotation from vendor {q.vendor.company_name} is ₹{q.price:.0f} - review pricing'
            })
    
    # Check for pending approvals
    pending_count = Requisition.query.filter_by(status='submitted').count()
    if pending_count > 5:
        insights.append({
            'type': 'danger',
            'title': 'Approval Backlog',
            'message': f'{pending_count} requisitions awaiting approval - action needed'
        })
    
    # Check for vendor performance
    vendors = Vendor.query.filter_by(status='active').all()
    for v in vendors:
        scorecards = VendorScorecard.query.filter_by(vendor_id=v.id).all()
        if scorecards:
            avg_score = sum([s.overall_score or 0 for s in scorecards]) / len(scorecards)
            if avg_score < 3:
                insights.append({
                    'type': 'warning',
                    'title': 'Vendor Performance Alert',
                    'message': f'{v.company_name} has low performance score ({avg_score:.1f}/5)'
                })
    
    # Budget alert simulation
    insights.append({
        'type': 'info',
        'title': 'Budget Status',
        'message': 'Q1 budget at 65% utilization - on track'
    })
    
    return insights[:5]  # Return top 5 insights

# ==================== AUTOMATION FUNCTIONS ====================

def auto_create_rfq(requisition_id, created_by):
    """Automatically create RFQ from approved requisition with auto-selected vendors"""
    requisition = Requisition.query.get_or_404(requisition_id)
    
    # Auto-select vendors based on category matching
    matching_vendors = Vendor.query.filter_by(status='active').all()
    
    # If requisition has department info, try to match with vendor category
    category_keywords = {
        'IT': ['electronics', 'computers', 'software', 'it'],
        'HR': ['office', 'furniture', 'supplies'],
        'Operations': ['machinery', 'equipment', 'raw materials'],
        'Finance': ['software', 'services', 'consulting']
    }
    
    selected_vendors = []
    dept_lower = requisition.department.lower()
    
    for vendor in matching_vendors:
        vendor_cat_lower = vendor.category.lower()
        # Check if vendor category matches department keywords
        for dept, keywords in category_keywords.items():
            if dept.lower() in dept_lower:
                if any(keyword in vendor_cat_lower for keyword in keywords):
                    selected_vendors.append(vendor)
                    break
        
        # If no match found, include top 5 vendors by default
        if not selected_vendors and len(matching_vendors) <= 5:
            selected_vendors = matching_vendors
    
    # Limit to top 5 vendors
    selected_vendors = selected_vendors[:5] if selected_vendors else matching_vendors[:5]
    
    # Calculate deadline (7 days from now)
    deadline = datetime.now() + timedelta(days=7)
    
    # Create RFQ
    rfq_number = generate_rfq_number()
    new_rfq = RFQ(
        rfq_number=rfq_number,
        requisition_id=requisition_id,
        title=f"RFQ for {requisition.item_name}",
        description=requisition.description or f"Purchase requisition for {requisition.item_name}",
        deadline=deadline.date(),
        status='sent',
        created_by=created_by
    )
    db.session.add(new_rfq)
    db.session.commit()
    
    # Add selected vendors to RFQ
    for vendor in selected_vendors:
        rfq_vendor = RFQVendor(
            rfq_id=new_rfq.id,
            vendor_id=vendor.id,
            status='sent',
            sent_at=datetime.utcnow()
        )
        db.session.add(rfq_vendor)
        
        # Auto-notify vendor
        create_notification(
            user_id=vendor.id,
            title=f'New RFQ: {rfq_number}',
            message=f'You have been invited to submit a quotation for {requisition.item_name}. Deadline: {deadline.strftime("%Y-%m-%d")}',
            type='info'
        )
    
    db.session.commit()
    
    # Notify admin
    create_notification(
        user_id=created_by,
        title='RFQ Auto-Created',
        message=f'RFQ {rfq_number} auto-created for requisition {requisition.requisition_number} and sent to {len(selected_vendors)} vendors',
        type='success'
    )
    
    return new_rfq

def auto_update_rfq_status(rfq_id):
    """Automatically update RFQ status based on quotations received"""
    rfq = RFQ.query.get_or_404(rfq_id)
    rfq_vendors = RFQVendor.query.filter_by(rfq_id=rfq_id).all()
    
    # Count quotations submitted
    quotations_count = Quotation.query.filter_by(rfq_id=rfq_id).count()
    total_vendors = len(rfq_vendors)
    
    # Update status based on quotations
    if quotations_count == 0:
        rfq.status = 'sent'
    elif quotations_count < total_vendors:
        rfq.status = 'in_review'
    elif quotations_count == total_vendors:
        rfq.status = 'review_complete'
    
    db.session.commit()
    return rfq.status

def create_notification(user_id, title, message, type='info'):
    """Create notification for user"""
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=type
    )
    db.session.add(notification)
    db.session.commit()

def check_deadline_reminders():
    """Check for RFQs approaching deadline and send reminders"""
    tomorrow = datetime.now() + timedelta(days=1)
    upcoming_rfqs = RFQ.query.filter(
        RFQ.deadline <= tomorrow.date(),
        RFQ.deadline >= datetime.now().date(),
        RFQ.status == 'sent'
    ).all()
    
    for rfq in upcoming_rfqs:
        rfq_vendors = RFQVendor.query.filter_by(rfq_id=rfq.id, status='sent').all()
        
        for rv in rfq_vendors:
            # Check if vendor has already submitted quotation
            existing_quotation = Quotation.query.filter_by(
                rfq_id=rfq.id,
                vendor_id=rv.vendor_id
            ).first()
            
            if not existing_quotation:
                # Send reminder notification
                create_notification(
                    user_id=rv.vendor_id,
                    title='RFQ Deadline Reminder',
                    message=f'RFQ {rfq.rfq_number} deadline is tomorrow ({rfq.deadline}). Please submit your quotation.',
                    type='warning'
                )

# ==================== VENDOR ONBOARDING ROUTES ====================

@app.route('/vendors')
@login_required
def vendors():
    """Display all vendors with approval workflow"""
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    
    query = Vendor.query
    if search:
        query = query.filter(
            (Vendor.company_name.like(f'%{search}%')) |
            (Vendor.category.like(f'%{search}%')) |
            (Vendor.email.like(f'%{search}%'))
        )
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    vendors = query.order_by(Vendor.created_at.desc()).all()
    return render_template('vendors.html', vendors=vendors, search=search, status_filter=status_filter)

@app.route('/vendors/register', methods=['GET', 'POST'])
@login_required
def register_vendor():
    """Register new vendor"""
    if request.method == 'POST':
        vendor_id = generate_vendor_id()
        company_name = request.form['company_name']
        gst_number = request.form['gst_number']
        category = request.form['category']
        contact_person = request.form['contact_person']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form.get('address', '')
        bank_name = request.form.get('bank_name', '')
        bank_account = request.form.get('bank_account', '')
        ifsc_code = request.form.get('ifsc_code', '')
        documents = request.form.get('documents', '')
        
        new_vendor = Vendor(
            vendor_id=vendor_id,
            company_name=company_name,
            gst_number=gst_number,
            category=category,
            contact_person=contact_person,
            email=email,
            phone=phone,
            address=address,
            bank_name=bank_name,
            bank_account=bank_account,
            ifsc_code=ifsc_code,
            documents=documents,
            status='pending'
        )
        db.session.add(new_vendor)
        db.session.commit()
        flash('Vendor registered successfully! Pending approval.', 'success')
        return redirect(url_for('vendors'))
    
    return render_template('vendors.html', action='register')

@app.route('/vendors/approve/<int:vendor_id>')
@login_required
@role_required('admin')
def approve_vendor(vendor_id):
    """Approve vendor registration"""
    vendor = Vendor.query.get_or_404(vendor_id)
    vendor.status = 'active'
    vendor.approved_by = session['user_id']
    vendor.approved_at = datetime.utcnow()
    db.session.commit()
    flash('Vendor approved successfully!', 'success')
    return redirect(url_for('vendors'))

@app.route('/vendors/reject/<int:vendor_id>')
@login_required
@role_required('admin')
def reject_vendor(vendor_id):
    """Reject vendor registration"""
    vendor = Vendor.query.get_or_404(vendor_id)
    vendor.status = 'rejected'
    vendor.approved_by = session['user_id']
    vendor.approved_at = datetime.utcnow()
    db.session.commit()
    flash('Vendor rejected.', 'warning')
    return redirect(url_for('vendors'))

# ==================== PURCHASE REQUISITION ROUTES ====================

@app.route('/requisitions')
@login_required
def requisitions():
    """Display all requisitions"""
    role = session.get('user_role')
    
    if role == 'requester':
        requisitions = Requisition.query.filter_by(requested_by=session['user_id']).order_by(Requisition.created_at.desc()).all()
    else:
        requisitions = Requisition.query.order_by(Requisition.created_at.desc()).all()
    
    return render_template('requisitions.html', requisitions=requisitions, role=role)

@app.route('/requisitions/create', methods=['GET', 'POST'])
@login_required
def create_requisition():
    """Create new purchase requisition"""
    if request.method == 'POST':
        requisition_number = generate_requisition_number()
        item_name = request.form['item_name']
        description = request.form.get('description', '')
        quantity = request.form['quantity']
        unit = request.form['unit']
        estimated_budget = request.form['estimated_budget']
        department = request.form['department']
        urgency = request.form.get('urgency', 'normal')
        
        new_requisition = Requisition(
            requisition_number=requisition_number,
            item_name=item_name,
            description=description,
            quantity=int(quantity),
            unit=unit,
            estimated_budget=float(estimated_budget),
            department=department,
            urgency=urgency,
            requested_by=session['user_id'],
            status='draft'
        )
        db.session.add(new_requisition)
        db.session.commit()
        flash('Requisition created successfully!', 'success')
        return redirect(url_for('requisitions'))
    
    return render_template('requisitions.html', action='create')

@app.route('/requisitions/submit/<int:requisition_id>')
@login_required
def submit_requisition(requisition_id):
    """Submit requisition for approval"""
    requisition = Requisition.query.get_or_404(requisition_id)
    requisition.status = 'submitted'
    db.session.commit()
    flash('Requisition submitted for approval!', 'success')
    return redirect(url_for('requisitions'))

@app.route('/requisitions/approve/<int:requisition_id>')
@login_required
@role_required('purchase_manager')
def approve_requisition(requisition_id):
    """Approve requisition and auto-create RFQ"""
    requisition = Requisition.query.get_or_404(requisition_id)
    requisition.status = 'approved'
    requisition.approved_by = session['user_id']
    requisition.approved_at = datetime.utcnow()
    
    # Add approval record
    approval = Approval(
        module_type='requisition',
        module_id=requisition_id,
        action='approve',
        approved_by=session['user_id']
    )
    db.session.add(approval)
    db.session.commit()
    
    # Auto-create RFQ with vendor selection
    auto_create_rfq(requisition_id, session['user_id'])
    
    flash('Requisition approved! RFQ auto-created and sent to vendors.', 'success')
    return redirect(url_for('requisitions'))

@app.route('/requisitions/reject/<int:requisition_id>')
@login_required
@role_required('purchase_manager')
def reject_requisition(requisition_id):
    """Reject requisition"""
    requisition = Requisition.query.get_or_404(requisition_id)
    requisition.status = 'rejected'
    requisition.approved_by = session['user_id']
    requisition.approved_at = datetime.utcnow()
    
    # Add approval record
    approval = Approval(
        module_type='requisition',
        module_id=requisition_id,
        action='reject',
        approved_by=session['user_id']
    )
    db.session.add(approval)
    db.session.commit()
    flash('Requisition rejected.', 'warning')
    return redirect(url_for('requisitions'))

# ==================== RFQ MANAGEMENT ROUTES ====================

@app.route('/rfqs')
@login_required
def rfqs():
    """Display all RFQs"""
    rfqs = RFQ.query.order_by(RFQ.created_at.desc()).all()
    return render_template('rfqs.html', rfqs=rfqs, action='view')

@app.route('/rfqs/create/<int:requisition_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'purchase_manager')
def create_rfq(requisition_id):
    """Create RFQ from approved requisition"""
    requisition = Requisition.query.get_or_404(requisition_id)
    
    if request.method == 'POST':
        rfq_number = generate_rfq_number()
        title = request.form['title']
        description = request.form.get('description', '')
        deadline = request.form['deadline']
        vendor_ids = request.form.getlist('vendor_ids')
        
        new_rfq = RFQ(
            rfq_number=rfq_number,
            requisition_id=requisition_id,
            title=title,
            description=description,
            deadline=datetime.strptime(deadline, '%Y-%m-%d').date(),
            created_by=session['user_id']
        )
        db.session.add(new_rfq)
        db.session.commit()
        
        # Add vendors to RFQ
        for vendor_id in vendor_ids:
            rfq_vendor = RFQVendor(
                rfq_id=new_rfq.id,
                vendor_id=int(vendor_id),
                status='sent',
                sent_at=datetime.utcnow()
            )
            db.session.add(rfq_vendor)
        
        db.session.commit()
        flash('RFQ created and sent to vendors!', 'success')
        return redirect(url_for('rfqs'))
    
    # Get approved vendors
    vendors = Vendor.query.filter_by(status='active').all()
    return render_template('rfqs.html', action='create', requisition=requisition, vendors=vendors)

# ==================== QUOTATION ROUTES ====================

@app.route('/quotations')
@login_required
def quotations():
    """Display all quotations"""
    role = session.get('user_role')
    
    if role == 'vendor':
        quotations = Quotation.query.filter_by(vendor_id=session.get('vendor_id')).order_by(Quotation.created_at.desc()).all()
    else:
        quotations = Quotation.query.order_by(Quotation.created_at.desc()).all()
    
    return render_template('quotations.html', quotations=quotations, role=role)

@app.route('/quotations/submit', methods=['GET', 'POST'])
@login_required
@role_required('vendor')
def submit_quotation():
    """Submit quotation for RFQ"""
    if request.method == 'POST':
        rfq_id = request.form['rfq_id']
        price = request.form['price']
        delivery_days = request.form['delivery_days']
        warranty = request.form.get('warranty', '')
        notes = request.form.get('notes', '')
        
        new_quotation = Quotation(
            rfq_id=int(rfq_id),
            vendor_id=session.get('vendor_id'),
            price=float(price),
            delivery_days=int(delivery_days),
            warranty=warranty,
            notes=notes,
            status='submitted',
            submitted_at=datetime.utcnow()
        )
        db.session.add(new_quotation)
        db.session.commit()
        
        # Auto-update RFQ status
        auto_update_rfq_status(int(rfq_id))
        
        flash('Quotation submitted successfully!', 'success')
        return redirect(url_for('quotations'))
    
    # Get RFQs where vendor is invited
    rfq_vendors = RFQVendor.query.filter_by(vendor_id=session.get('vendor_id'), status='sent').all()
    rfqs = [rv.rfq for rv in rfq_vendors]
    return render_template('quotations.html', action='submit', rfqs=rfqs)

@app.route('/quotations/compare/<int:rfq_id>')
@login_required
def compare_quotations(rfq_id):
    """Compare quotations for RFQ with auto-ranking"""
    quotations = Quotation.query.filter_by(rfq_id=rfq_id).order_by(Quotation.price.asc()).all()
    
    # Auto-rank quotations
    ranked_quotations = []
    for i, q in enumerate(quotations):
        rank = i + 1
        score = 5 - i  # Simple scoring based on price rank
        ranked_quotations.append({
            'quotation': q,
            'rank': rank,
            'score': score
        })
    
    rfq = RFQ.query.get_or_404(rfq_id)
    return render_template('quotations.html', action='compare', quotations=ranked_quotations, rfq=rfq)

# ==================== PURCHASE ORDER ROUTES ====================

@app.route('/pos')
@login_required
def purchase_orders():
    """Display all purchase orders"""
    pos = PurchaseOrder.query.order_by(PurchaseOrder.created_at.desc()).all()
    return render_template('pos.html', pos=pos, action='view')

@app.route('/pos/generate/<int:quotation_id>')
@login_required
@role_required('admin', 'purchase_manager')
def generate_po(quotation_id):
    """Generate purchase order from approved quotation"""
    quotation = Quotation.query.get_or_404(quotation_id)
    rfq = quotation.rfq
    requisition = rfq.requisition
    
    # Check if PO already exists
    existing_po = PurchaseOrder.query.filter_by(quotation_id=quotation_id).first()
    if existing_po:
        flash('PO already generated for this quotation!', 'warning')
        return redirect(url_for('purchase_orders'))
    
    # Calculate amounts
    quantity = requisition.quantity
    unit_price = quotation.price
    total_amount = quantity * unit_price
    gst_amount = total_amount * 0.18  # 18% GST
    grand_total = total_amount + gst_amount
    
    # Generate PO
    new_po = PurchaseOrder(
        po_number=generate_po_number(),
        quotation_id=quotation_id,
        vendor_id=quotation.vendor_id,
        item_name=requisition.item_name,
        quantity=quantity,
        unit=requisition.unit,
        unit_price=unit_price,
        total_amount=total_amount,
        gst_amount=gst_amount,
        grand_total=grand_total,
        delivery_date=datetime.now() + datetime.timedelta(days=quotation.delivery_days),
        payment_terms='Net 30 days',
        status='pending',
        created_by=session['user_id']
    )
    db.session.add(new_po)
    db.session.commit()
    
    # Update quotation status
    quotation.status = 'approved'
    db.session.commit()
    
    flash('Purchase Order generated successfully!', 'success')
    return redirect(url_for('purchase_orders'))

# ==================== GRN ROUTES ====================

@app.route('/grns')
@login_required
def grns():
    """Display all GRNs"""
    grns = GRN.query.order_by(GRN.received_at.desc()).all()
    return render_template('grns.html', grns=grns, action='view')

@app.route('/grns/create/<int:po_id>', methods=['GET', 'POST'])
@login_required
def create_grn(po_id):
    """Create GRN for received goods"""
    po = PurchaseOrder.query.get_or_404(po_id)
    
    if request.method == 'POST':
        received_quantity = request.form['received_quantity']
        condition_check = request.form.get('condition_check', '')
        remarks = request.form.get('remarks', '')
        
        # Check for mismatch
        status = 'accepted'
        if int(received_quantity) != po.quantity:
            status = 'flagged'
        
        new_grn = GRN(
            grn_number=generate_grn_number(),
            po_id=po_id,
            received_quantity=int(received_quantity),
            ordered_quantity=po.quantity,
            condition_check=condition_check,
            status=status,
            received_by=session['user_id'],
            remarks=remarks
        )
        db.session.add(new_grn)
        db.session.commit()
        
        flash('GRN created successfully!', 'success')
        return redirect(url_for('grns'))
    
    return render_template('grns.html', action='create', po=po)

# ==================== INVOICE ROUTES ====================

@app.route('/invoices')
@login_required
def invoices():
    """Display all invoices"""
    role = session.get('user_role')
    
    if role == 'vendor':
        invoices = Invoice.query.filter_by(vendor_id=session.get('vendor_id')).order_by(Invoice.uploaded_at.desc()).all()
    elif role == 'finance':
        invoices = Invoice.query.order_by(Invoice.uploaded_at.desc()).all()
    else:
        invoices = Invoice.query.order_by(Invoice.uploaded_at.desc()).all()
    
    return render_template('invoices.html', invoices=invoices, role=role)

@app.route('/invoices/upload', methods=['GET', 'POST'])
@login_required
@role_required('vendor')
def upload_invoice():
    """Upload invoice for PO"""
    if request.method == 'POST':
        po_id = request.form['po_id']
        amount = request.form['amount']
        tax = request.form['tax']
        
        po = PurchaseOrder.query.get_or_404(po_id)
        
        total_amount = float(amount) + float(tax)
        
        new_invoice = Invoice(
            invoice_number=generate_invoice_number(),
            po_id=po_id,
            vendor_id=po.vendor_id,
            amount=float(amount),
            tax=float(tax),
            total_amount=total_amount,
            uploaded_by=session['user_id'],
            uploaded_at=datetime.utcnow()
        )
        db.session.add(new_invoice)
        db.session.commit()
        
        # Perform 3-way match
        perform_3way_match(new_invoice.id)
        
        flash('Invoice uploaded and 3-way match performed!', 'success')
        return redirect(url_for('invoices'))
    
    # Get POs for vendor
    pos = PurchaseOrder.query.filter_by(vendor_id=session.get('vendor_id'), status='acknowledged').all()
    return render_template('invoices.html', action='upload', pos=pos)

def perform_3way_match(invoice_id):
    """Perform 3-way match: PO vs GRN vs Invoice"""
    invoice = Invoice.query.get_or_404(invoice_id)
    po = invoice.po
    grn = GRN.query.filter_by(po_id=po.id).first()
    
    # PO match
    if invoice.amount <= po.total_amount * 1.05:  # Allow 5% variance
        invoice.po_match = 'matched'
    else:
        invoice.po_match = 'mismatch'
    
    # GRN match
    if grn and grn.status == 'accepted':
        invoice.grn_match = 'matched'
    else:
        invoice.grn_match = 'mismatch'
    
    # Invoice match
    if invoice.po_match == 'matched' and invoice.grn_match == 'matched':
        invoice.invoice_match = 'matched'
        invoice.overall_status = 'approved'
    else:
        invoice.invoice_match = 'mismatch'
        invoice.overall_status = 'flagged'
    
    invoice.processed_by = session.get('user_id')
    invoice.processed_at = datetime.utcnow()
    db.session.commit()

# ==================== VENDOR SCORECARD ROUTES ====================

@app.route('/scorecards')
@login_required
def scorecards():
    """Display vendor scorecards"""
    scorecards = VendorScorecard.query.order_by(VendorScorecard.rated_at.desc()).all()
    return render_template('scorecards.html', scorecards=scorecards)

@app.route('/scorecards/create/<int:po_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'purchase_manager')
def create_scorecard(po_id):
    """Create vendor scorecard"""
    po = PurchaseOrder.query.get_or_404(po_id)
    
    if request.method == 'POST':
        delivery_score = request.form['delivery_score']
        quality_score = request.form['quality_score']
        price_score = request.form['price_score']
        remarks = request.form.get('remarks', '')
        
        overall_score = (int(delivery_score) + int(quality_score) + int(price_score)) / 3
        
        new_scorecard = VendorScorecard(
            vendor_id=po.vendor_id,
            po_id=po_id,
            delivery_score=int(delivery_score),
            quality_score=int(quality_score),
            price_score=int(price_score),
            overall_score=overall_score,
            rated_by=session['user_id'],
            remarks=remarks
        )
        db.session.add(new_scorecard)
        db.session.commit()
        
        flash('Scorecard created successfully!', 'success')
        return redirect(url_for('scorecards'))
    
    return render_template('scorecards.html', action='create', po=po)

# ==================== ANALYTICS ROUTES ====================

@app.route('/analytics')
@login_required
def analytics():
    """Display analytics dashboard"""
    # Get monthly spend data
    monthly_spend = db.session.query(
        db.func.strftime('%Y-%m', PurchaseOrder.created_at).label('month'),
        db.func.sum(PurchaseOrder.grand_total).label('total')
    ).group_by('month').order_by('month').all()
    
    # Get top vendors by spend
    vendor_spend = db.session.query(
        Vendor.company_name,
        db.func.sum(PurchaseOrder.grand_total).label('total')
    ).join(PurchaseOrder).group_by(Vendor.id).order_by(db.desc('total')).limit(5).all()
    
    # Get category-wise spend
    category_spend = db.session.query(
        Vendor.category,
        db.func.sum(PurchaseOrder.grand_total).label('total')
    ).join(PurchaseOrder).group_by(Vendor.category).all()
    
    return render_template('analytics.html',
                         monthly_spend=monthly_spend,
                         vendor_spend=vendor_spend,
                         category_spend=category_spend)

# ==================== NOTIFICATION ROUTES ====================

@app.route('/notifications/mark-read/<int:notification_id>')
@login_required
def mark_notification_read(notification_id):
    """Mark notification as read"""
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id == session['user_id']:
        notification.is_read = 1
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/notifications/mark-all-read')
@login_required
def mark_all_notifications_read():
    """Mark all notifications as read for current user"""
    Notification.query.filter_by(user_id=session['user_id']).update({'is_read': 1})
    db.session.commit()
    return redirect(url_for('dashboard'))

# ==================== REST API ENDPOINTS ====================

@app.route('/api/vendors', methods=['GET'])
def api_vendors():
    """API: Get all vendors"""
    vendors = Vendor.query.all()
    return jsonify([{
        'id': v.id,
        'vendor_id': v.vendor_id,
        'company_name': v.company_name,
        'category': v.category,
        'status': v.status
    } for v in vendors])

@app.route('/api/requisitions', methods=['GET'])
def api_requisitions():
    """API: Get all requisitions"""
    requisitions = Requisition.query.all()
    return jsonify([{
        'id': r.id,
        'requisition_number': r.requisition_number,
        'item_name': r.item_name,
        'quantity': r.quantity,
        'status': r.status
    } for r in requisitions])

@app.route('/api/rfqs', methods=['GET'])
def api_rfqs():
    """API: Get all RFQs"""
    rfqs = RFQ.query.all()
    return jsonify([{
        'id': r.id,
        'rfq_number': r.rfq_number,
        'title': r.title,
        'status': r.status
    } for r in rfqs])

@app.route('/api/pos', methods=['GET'])
def api_pos():
    """API: Get all POs"""
    pos = PurchaseOrder.query.all()
    return jsonify([{
        'id': p.id,
        'po_number': p.po_number,
        'vendor_id': p.vendor_id,
        'grand_total': p.grand_total,
        'status': p.status
    } for p in pos])

@app.route('/api/invoices', methods=['GET'])
def api_invoices():
    """API: Get all invoices"""
    invoices = Invoice.query.all()
    return jsonify([{
        'id': i.id,
        'invoice_number': i.invoice_number,
        'total_amount': i.total_amount,
        'overall_status': i.overall_status
    } for i in invoices])

@app.route('/api/dashboard', methods=['GET'])
def api_dashboard():
    """API: Get dashboard statistics"""
    return jsonify({
        'total_vendors': Vendor.query.count(),
        'total_requisitions': Requisition.query.count(),
        'total_rfqs': RFQ.query.count(),
        'total_quotations': Quotation.query.count(),
        'total_pos': PurchaseOrder.query.count(),
        'total_invoices': Invoice.query.count()
    })

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('base.html', error='Page not found'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors"""
    return render_template('base.html', error='Internal server error'), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    app.run(debug=True)
