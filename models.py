from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class MaintenanceTeam(db.Model):
    __tablename__ = 'maintenance_teams'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    members = db.Column(db.Text)  # Comma-separated list of technician names
    
    def __repr__(self):
        return f'<MaintenanceTeam {self.name}>'

class Equipment(db.Model):
    __tablename__ = 'equipment'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Mechanical / Electrical / IT
    department = db.Column(db.String(50), nullable=False)  # Production / Admin / IT
    assigned_employee = db.Column(db.String(100))
    maintenance_team_id = db.Column(db.Integer, db.ForeignKey('maintenance_teams.id'))
    default_technician = db.Column(db.String(100))
    purchase_date = db.Column(db.Date)
    warranty_end = db.Column(db.Date)
    location = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Active')  # Active / Scrapped
    notes = db.Column(db.Text)
    
    # Relationship
    maintenance_team = db.relationship('MaintenanceTeam', backref='equipment_list')
    
    def __repr__(self):
        return f'<Equipment {self.name}>'

class MaintenanceRequest(db.Model):
    __tablename__ = 'maintenance_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200), nullable=False)
    request_type = db.Column(db.String(20), nullable=False)  # Corrective / Preventive
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    category = db.Column(db.String(50))  # Auto-filled from equipment
    maintenance_team_id = db.Column(db.Integer, db.ForeignKey('maintenance_teams.id'))  # Auto-filled from equipment
    assigned_technician = db.Column(db.String(100))
    scheduled_date = db.Column(db.DateTime)
    duration_hours = db.Column(db.Float)
    stage = db.Column(db.String(20), default='New')  # New / In Progress / Repaired / Scrap
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    equipment = db.relationship('Equipment', backref='maintenance_requests')
    maintenance_team = db.relationship('MaintenanceTeam', backref='maintenance_requests')
    
    def __repr__(self):
        return f'<MaintenanceRequest {self.subject}>'