"""
Vendara - Mock Data Seeding Script
Run this script to populate the database with sample data for demonstration
"""

from app import app, db, User, Vendor, Requisition, RFQ, RFQVendor, Quotation, PurchaseOrder, GRN, Invoice, VendorScorecard, Analytics
from datetime import datetime, timedelta
import hashlib

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def seed_data():
    """Seed the database with mock data"""
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create Users (5 roles)
        users = [
            User(name='Admin User', email='admin@vendara.com', password=hash_password('admin123'), role='admin'),
            User(name='John Manager', email='manager@vendara.com', password=hash_password('manager123'), role='purchase_manager'),
            User(name='Alice Requester', email='requester@vendara.com', password=hash_password('requester123'), role='requester'),
            User(name='Bob Finance', email='finance@vendara.com', password=hash_password('finance123'), role='finance'),
            User(name='TechCorp', email='techcorp@vendor.com', password=hash_password('vendor123'), role='vendor', company_name='TechCorp Solutions'),
        ]
        for user in users:
            db.session.add(user)
        db.session.commit()
        
        # Get vendor user
        vendor_user = User.query.filter_by(email='techcorp@vendor.com').first()
        
        # Create Vendors
        vendors = [
            Vendor(vendor_id='VND20240101001', company_name='TechCorp Solutions', gst_number='29ABCDE1234F1Z5', category='Electronics', contact_person='Raj Kumar', email='raj@techcorp.com', phone='9876543210', address='Bangalore, India', bank_name='HDFC Bank', bank_account='1234567890', ifsc_code='HDFC0001234', status='active', approved_by=1, approved_at=datetime.utcnow()),
            Vendor(vendor_id='VND20240101002', company_name='Office Supplies Inc', gst_number='29FGHIJ5678K2L6', category='Office Supplies', contact_person='Priya Sharma', email='priya@officesupplies.com', phone='9876543211', address='Mumbai, India', bank_name='ICICI Bank', bank_account='0987654321', ifsc_code='ICIC0001234', status='active', approved_by=1, approved_at=datetime.utcnow()),
            Vendor(vendor_id='VND20240101003', company_name='Industrial Equipment Ltd', gst_number='29LMNOP9012M3N7', category='Industrial', contact_person='Amit Patel', email='amit@industrial.com', phone='9876543212', address='Pune, India', bank_name='SBI', bank_account='1122334455', ifsc_code='SBIN0001234', status='active', approved_by=1, approved_at=datetime.utcnow()),
            Vendor(vendor_id='VND20240101004', company_name='Furniture World', gst_number='29QRSTU3456O4P8', category='Furniture', contact_person='Sneha Reddy', email='sneha@furniture.com', phone='9876543213', address='Hyderabad, India', bank_name='Axis Bank', bank_account='5566778899', ifsc_code='UTIB0001234', status='pending'),
        ]
        for vendor in vendors:
            db.session.add(vendor)
        db.session.commit()
        
        # Create Requisitions
        requisitions = [
            Requisition(requisition_number='REQ20240101001', item_name='Laptops', description='Dell Latitude 5520 for IT team', quantity=10, unit='pcs', estimated_budget=750000, department='IT', urgency='high', requested_by=3, status='approved', approved_by=2, approved_at=datetime.utcnow()),
            Requisition(requisition_number='REQ20240101002', item_name='Office Chairs', description='Ergonomic chairs for conference room', quantity=20, unit='pcs', estimated_budget=200000, department='HR', urgency='normal', requested_by=3, status='approved', approved_by=2, approved_at=datetime.utcnow()),
            Requisition(requisition_number='REQ20240101003', item_name='Industrial Motors', description='High torque motors for production line', quantity=5, unit='pcs', estimated_budget=500000, department='Production', urgency='critical', requested_by=3, status='submitted'),
        ]
        for req in requisitions:
            db.session.add(req)
        db.session.commit()
        
        # Create RFQs
        rfqs = [
            RFQ(rfq_number='RFQ20240101001', requisition_id=1, title='Laptops for IT Team', description='Dell Latitude 5520, i7, 16GB RAM, 512GB SSD', deadline=datetime.now() + timedelta(days=7), status='open', created_by=2),
            RFQ(rfq_number='RFQ20240101002', requisition_id=2, title='Office Chairs for Conference Room', description='Ergonomic chairs with lumbar support', deadline=datetime.now() + timedelta(days=5), status='open', created_by=2),
        ]
        for rfq in rfqs:
            db.session.add(rfq)
        db.session.commit()
        
        # Assign vendors to RFQs
        rfq_vendors = [
            RFQVendor(rfq_id=1, vendor_id=1, status='sent', sent_at=datetime.utcnow()),
            RFQVendor(rfq_id=1, vendor_id=2, status='sent', sent_at=datetime.utcnow()),
            RFQVendor(rfq_id=2, vendor_id=2, status='sent', sent_at=datetime.utcnow()),
            RFQVendor(rfq_id=2, vendor_id=4, status='sent', sent_at=datetime.utcnow()),
        ]
        for rv in rfq_vendors:
            db.session.add(rv)
        db.session.commit()
        
        # Create Quotations
        quotations = [
            Quotation(rfq_id=1, vendor_id=1, price=72000, delivery_days=7, warranty='3 years', notes='Best price guaranteed', status='submitted', submitted_at=datetime.utcnow()),
            Quotation(rfq_id=1, vendor_id=2, price=75000, delivery_days=10, warranty='2 years', notes='Standard warranty', status='submitted', submitted_at=datetime.utcnow()),
            Quotation(rfq_id=2, vendor_id=2, price=9500, delivery_days=5, warranty='5 years', notes='Bulk discount available', status='submitted', submitted_at=datetime.utcnow()),
        ]
        for quote in quotations:
            db.session.add(quote)
        db.session.commit()
        
        # Create Purchase Orders (from approved quotations)
        total_amount = 72000 * 10
        gst_amount = total_amount * 0.18
        grand_total = total_amount + gst_amount
        
        pos = [
            PurchaseOrder(po_number='PO20240101001', quotation_id=1, vendor_id=1, item_name='Laptops', quantity=10, unit='pcs', unit_price=72000, total_amount=total_amount, gst_amount=gst_amount, grand_total=grand_total, delivery_date=datetime.now() + timedelta(days=7), payment_terms='Net 30 days', status='acknowledged', created_by=2),
        ]
        for po in pos:
            db.session.add(po)
        db.session.commit()
        
        # Create GRNs
        grns = [
            GRN(grn_number='GRN20240101001', po_id=1, received_quantity=10, ordered_quantity=10, condition_check='All items in good condition', status='accepted', received_by=2, remarks='Received on time'),
        ]
        for grn in grns:
            db.session.add(grn)
        db.session.commit()
        
        # Create Invoices
        invoices = [
            Invoice(invoice_number='INV20240101001', po_id=1, grn_id=1, vendor_id=1, amount=720000, tax=129600, total_amount=849600, po_match='matched', grn_match='matched', invoice_match='matched', overall_status='approved', uploaded_by=5, uploaded_at=datetime.utcnow(), processed_by=4, processed_at=datetime.utcnow()),
        ]
        for invoice in invoices:
            db.session.add(invoice)
        db.session.commit()
        
        # Create Vendor Scorecards
        scorecards = [
            VendorScorecard(vendor_id=1, po_id=1, delivery_score=5, quality_score=5, price_score=4, overall_score=4.67, rated_by=2, remarks='Excellent vendor, delivered on time'),
        ]
        for scorecard in scorecards:
            db.session.add(scorecard)
        db.session.commit()
        
        # Create Analytics Data
        analytics_data = [
            Analytics(metric_type='monthly_spend', metric_value=849600, metric_date=datetime.now().date(), category='Electronics', vendor_id=1),
            Analytics(metric_type='monthly_spend', metric_value=500000, metric_date=datetime.now().date() - timedelta(days=30), category='Office Supplies', vendor_id=2),
            Analytics(metric_type='monthly_spend', metric_value=750000, metric_date=datetime.now().date() - timedelta(days=60), category='Industrial', vendor_id=3),
        ]
        for analytic in analytics_data:
            db.session.add(analytic)
        db.session.commit()
        
        print("✅ Mock data seeded successfully!")
        print("\n📝 Login Credentials:")
        print("  Admin: admin@vendara.com / admin123")
        print("  Purchase Manager: manager@vendara.com / manager123")
        print("  Requester: requester@vendara.com / requester123")
        print("  Finance: finance@vendara.com / finance123")
        print("  Vendor: techcorp@vendor.com / vendor123")

if __name__ == '__main__':
    seed_data()
