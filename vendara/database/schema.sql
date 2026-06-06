-- Vendara - Full Stack Procurement ERP
-- SQLite Database Schema for 10 Modules

-- Users Table: 5-role authentication system
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'purchase_manager', 'requester', 'finance', 'vendor')),
    company_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vendors Table: Vendor onboarding with approval workflow
CREATE TABLE IF NOT EXISTS vendors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_id TEXT UNIQUE NOT NULL,
    company_name TEXT NOT NULL,
    gst_number TEXT NOT NULL,
    category TEXT NOT NULL,
    contact_person TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    address TEXT,
    bank_name TEXT,
    bank_account TEXT,
    ifsc_code TEXT,
    documents TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'active', 'inactive')),
    approved_by INTEGER,
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (approved_by) REFERENCES users(id)
);

-- Purchase Requisitions Table: Requester raises requisitions
CREATE TABLE IF NOT EXISTS requisitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requisition_number TEXT UNIQUE NOT NULL,
    item_name TEXT NOT NULL,
    description TEXT,
    quantity INTEGER NOT NULL,
    unit TEXT NOT NULL,
    estimated_budget REAL NOT NULL,
    department TEXT NOT NULL,
    urgency TEXT DEFAULT 'normal' CHECK (urgency IN ('low', 'normal', 'high', 'critical')),
    requested_by INTEGER NOT NULL,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'submitted', 'approved', 'rejected')),
    approved_by INTEGER,
    approved_at TIMESTAMP,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (requested_by) REFERENCES users(id),
    FOREIGN KEY (approved_by) REFERENCES users(id)
);

-- RFQs Table: Procurement creates RFQ from approved requisition
CREATE TABLE IF NOT EXISTS rfqs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rfq_number TEXT UNIQUE NOT NULL,
    requisition_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    deadline DATE NOT NULL,
    status TEXT DEFAULT 'open' CHECK (status IN ('open', 'closed', 'cancelled')),
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (requisition_id) REFERENCES requisitions(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- RFQ Vendors Table: Vendors assigned to RFQ
CREATE TABLE IF NOT EXISTS rfq_vendors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rfq_id INTEGER NOT NULL,
    vendor_id INTEGER NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'responded', 'declined')),
    sent_at TIMESTAMP,
    FOREIGN KEY (rfq_id) REFERENCES rfqs(id),
    FOREIGN KEY (vendor_id) REFERENCES vendors(id)
);

-- Quotations Table: Vendors submit quotations
CREATE TABLE IF NOT EXISTS quotations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rfq_id INTEGER NOT NULL,
    vendor_id INTEGER NOT NULL,
    price REAL NOT NULL,
    delivery_days INTEGER NOT NULL,
    warranty TEXT,
    notes TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'submitted', 'approved', 'rejected')),
    submitted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rfq_id) REFERENCES rfqs(id),
    FOREIGN KEY (vendor_id) REFERENCES vendors(id)
);

-- Approvals Table: Approval workflow with audit trail
CREATE TABLE IF NOT EXISTS approvals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_type TEXT NOT NULL CHECK (module_type IN ('requisition', 'rfq', 'quotation', 'po', 'invoice')),
    module_id INTEGER NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('approve', 'reject', 'request_revision')),
    remarks TEXT,
    approved_by INTEGER NOT NULL,
    approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (approved_by) REFERENCES users(id)
);

-- Purchase Orders Table: PO generation
CREATE TABLE IF NOT EXISTS purchase_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    po_number TEXT UNIQUE NOT NULL,
    quotation_id INTEGER NOT NULL,
    vendor_id INTEGER NOT NULL,
    item_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit TEXT NOT NULL,
    unit_price REAL NOT NULL,
    total_amount REAL NOT NULL,
    gst_amount REAL NOT NULL,
    grand_total REAL NOT NULL,
    delivery_date DATE NOT NULL,
    payment_terms TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'acknowledged', 'partial', 'completed', 'cancelled')),
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (quotation_id) REFERENCES quotations(id),
    FOREIGN KEY (vendor_id) REFERENCES vendors(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Goods Receipt Notes Table: GRN for received goods
CREATE TABLE IF NOT EXISTS grns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grn_number TEXT UNIQUE NOT NULL,
    po_id INTEGER NOT NULL,
    received_quantity INTEGER NOT NULL,
    ordered_quantity INTEGER NOT NULL,
    condition_check TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected', 'flagged')),
    received_by INTEGER NOT NULL,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    remarks TEXT,
    FOREIGN KEY (po_id) REFERENCES purchase_orders(id),
    FOREIGN KEY (received_by) REFERENCES users(id)
);

-- Invoices Table: Vendor invoices with 3-way match
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number TEXT UNIQUE NOT NULL,
    po_id INTEGER NOT NULL,
    grn_id INTEGER,
    vendor_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    tax REAL NOT NULL,
    total_amount REAL NOT NULL,
    po_match TEXT DEFAULT 'pending' CHECK (po_match IN ('pending', 'matched', 'mismatch')),
    grn_match TEXT DEFAULT 'pending' CHECK (grn_match IN ('pending', 'matched', 'mismatch')),
    invoice_match TEXT DEFAULT 'pending' CHECK (invoice_match IN ('pending', 'matched', 'mismatch')),
    overall_status TEXT DEFAULT 'pending' CHECK (overall_status IN ('pending', 'approved', 'rejected', 'flagged')),
    uploaded_by INTEGER,
    uploaded_at TIMESTAMP,
    processed_by INTEGER,
    processed_at TIMESTAMP,
    remarks TEXT,
    FOREIGN KEY (po_id) REFERENCES purchase_orders(id),
    FOREIGN KEY (grn_id) REFERENCES grns(id),
    FOREIGN KEY (vendor_id) REFERENCES vendors(id),
    FOREIGN KEY (uploaded_by) REFERENCES users(id),
    FOREIGN KEY (processed_by) REFERENCES users(id)
);

-- Vendor Scorecards Table: Performance tracking
CREATE TABLE IF NOT EXISTS vendor_scorecards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_id INTEGER NOT NULL,
    po_id INTEGER NOT NULL,
    delivery_score INTEGER CHECK (delivery_score BETWEEN 1 AND 5),
    quality_score INTEGER CHECK (quality_score BETWEEN 1 AND 5),
    price_score INTEGER CHECK (price_score BETWEEN 1 AND 5),
    overall_score REAL,
    rated_by INTEGER NOT NULL,
    rated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    remarks TEXT,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id),
    FOREIGN KEY (po_id) REFERENCES purchase_orders(id),
    FOREIGN KEY (rated_by) REFERENCES users(id)
);

-- Analytics Data Table: Store aggregated analytics data
CREATE TABLE IF NOT EXISTS analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_type TEXT NOT NULL,
    metric_value REAL NOT NULL,
    metric_date DATE NOT NULL,
    category TEXT,
    vendor_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id)
);

-- Notifications Table: Email notification simulation
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    type TEXT DEFAULT 'info' CHECK (type IN ('info', 'success', 'warning', 'danger')),
    is_read INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Insert default admin user
INSERT INTO users (name, email, password, role) VALUES 
('Admin User', 'admin@vendara.com', 'admin123', 'admin')
ON CONFLICT(email) DO NOTHING;
