from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='user')  # admin, manager, user
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

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

class WorkCenter(db.Model):
    __tablename__ = 'workcenters'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    location = db.Column(db.String(100))
    department = db.Column(db.String(50))
    responsible_person = db.Column(db.String(100))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='Active')  # Active / Inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<WorkCenter {self.name}>'

class MaintenanceRequest(db.Model):
    __tablename__ = 'maintenance_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200), nullable=False)
    request_type = db.Column(db.String(20), nullable=False)  # Corrective / Preventive
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'))  # Nullable to allow work center requests
    workcenter_id = db.Column(db.Integer, db.ForeignKey('workcenters.id'))  # Nullable to allow equipment requests
    category = db.Column(db.String(50))
    maintenance_team_id = db.Column(db.Integer, db.ForeignKey('maintenance_teams.id'))
    assigned_technician = db.Column(db.String(100))
    scheduled_date = db.Column(db.DateTime)
    duration_hours = db.Column(db.Float)
    stage = db.Column(db.String(20), default='New')  # New / In Progress / Repaired / Scrap
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    equipment = db.relationship('Equipment', backref='maintenance_requests')
    workcenter = db.relationship('WorkCenter', backref='maintenance_requests')
    maintenance_team = db.relationship('MaintenanceTeam', backref='maintenance_requests')
    
    def __repr__(self):
        return f'<MaintenanceRequest {self.subject}>'