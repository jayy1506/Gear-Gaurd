from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Equipment, MaintenanceTeam, MaintenanceRequest
from datetime import datetime
import os
from datetime import datetime as dt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your-secret-key-here'

db.init_app(app)

with app.app_context():
    db.create_all()

@app.context_processor
def inject_now():
    return {'now': dt.utcnow}

# Routes for Equipment
@app.route('/')
def dashboard():
    return redirect(url_for('kanban_board'))

@app.route('/dashboard')
def kanban_board():
    # Get maintenance requests grouped by stage
    new_requests = MaintenanceRequest.query.filter_by(stage='New').all()
    in_progress_requests = MaintenanceRequest.query.filter_by(stage='In Progress').all()
    repaired_requests = MaintenanceRequest.query.filter_by(stage='Repaired').all()
    scrap_requests = MaintenanceRequest.query.filter_by(stage='Scrap').all()
    
    return render_template('dashboard.html', 
                           new_requests=new_requests,
                           in_progress_requests=in_progress_requests,
                           repaired_requests=repaired_requests,
                           scrap_requests=scrap_requests)

@app.route('/equipment')
def equipment_list():
    equipment = Equipment.query.all()
    return render_template('equipment_list.html', equipment=equipment)

@app.route('/equipment/<int:id>')
def equipment_detail(id):
    equip = Equipment.query.get_or_404(id)
    # Get maintenance requests for this equipment
    requests = MaintenanceRequest.query.filter_by(equipment_id=id).all()
    return render_template('equipment_detail.html', equipment=equip, requests=requests)

@app.route('/equipment/<int:equip_id>/maintenance_requests')
def equipment_maintenance_requests(equip_id):
    equip = Equipment.query.get_or_404(equip_id)
    requests = MaintenanceRequest.query.filter_by(equipment_id=equip_id).all()
    return render_template('equipment_detail.html', equipment=equip, requests=requests)

@app.route('/equipment/new', methods=['GET', 'POST'])
def create_equipment():
    if request.method == 'POST':
        equipment = Equipment(
            name=request.form['name'],
            serial_number=request.form['serial_number'],
            category=request.form['category'],
            department=request.form['department'],
            assigned_employee=request.form.get('assigned_employee'),
            maintenance_team_id=request.form.get('maintenance_team_id'),
            default_technician=request.form.get('default_technician'),
            purchase_date=datetime.strptime(request.form['purchase_date'], '%Y-%m-%d').date() if request.form.get('purchase_date') else None,
            warranty_end=datetime.strptime(request.form['warranty_end'], '%Y-%m-%d').date() if request.form.get('warranty_end') else None,
            location=request.form.get('location'),
            notes=request.form.get('notes')
        )
        db.session.add(equipment)
        db.session.commit()
        flash('Equipment created successfully!', 'success')
        return redirect(url_for('equipment_list'))
    
    teams = MaintenanceTeam.query.all()
    return render_template('equipment_form.html', teams=teams)

@app.route('/equipment/<int:id>/edit', methods=['GET', 'POST'])
def edit_equipment(id):
    equipment = Equipment.query.get_or_404(id)
    
    if request.method == 'POST':
        equipment.name = request.form['name']
        equipment.serial_number = request.form['serial_number']
        equipment.category = request.form['category']
        equipment.department = request.form['department']
        equipment.assigned_employee = request.form.get('assigned_employee')
        equipment.maintenance_team_id = request.form.get('maintenance_team_id')
        equipment.default_technician = request.form.get('default_technician')
        equipment.purchase_date = datetime.strptime(request.form['purchase_date'], '%Y-%m-%d').date() if request.form.get('purchase_date') else None
        equipment.warranty_end = datetime.strptime(request.form['warranty_end'], '%Y-%m-%d').date() if request.form.get('warranty_end') else None
        equipment.location = request.form.get('location')
        equipment.notes = request.form.get('notes')
        
        db.session.commit()
        flash('Equipment updated successfully!', 'success')
        return redirect(url_for('equipment_list'))
    
    teams = MaintenanceTeam.query.all()
    return render_template('equipment_form.html', equipment=equipment, teams=teams)

# Routes for Maintenance Requests
@app.route('/requests')
def maintenance_requests():
    requests = MaintenanceRequest.query.all()
    return render_template('requests_list.html', requests=requests)

@app.route('/request/new', methods=['GET', 'POST'])
def create_request():
    if request.method == 'POST':
        # Get equipment to auto-populate fields
        equipment = Equipment.query.get(request.form['equipment_id'])
        
        request_obj = MaintenanceRequest(
            subject=request.form['subject'],
            request_type=request.form['request_type'],
            equipment_id=request.form['equipment_id'],
            category=equipment.category if equipment else None,
            maintenance_team_id=equipment.maintenance_team_id if equipment else None,
            assigned_technician=request.form.get('assigned_technician') or equipment.default_technician if equipment else None,
            scheduled_date=datetime.strptime(request.form['scheduled_date'], '%Y-%m-%d %H:%M') if request.form.get('scheduled_date') else None,
            duration_hours=float(request.form.get('duration_hours', 0)) if request.form.get('duration_hours') else None,
            stage='New'  # Default stage
        )
        
        db.session.add(request_obj)
        db.session.commit()
        
        flash('Maintenance request created successfully!', 'success')
        return redirect(url_for('maintenance_requests'))
    
    equipment_list = Equipment.query.all()
    teams = MaintenanceTeam.query.all()
    return render_template('request_form.html', equipment_list=equipment_list, teams=teams)

@app.route('/request/<int:id>/edit', methods=['GET', 'POST'])
def edit_request(id):
    request_obj = MaintenanceRequest.query.get_or_404(id)
    
    if request.method == 'POST':
        # Update the request
        request_obj.subject = request.form['subject']
        request_obj.request_type = request.form['request_type']
        request_obj.equipment_id = request.form['equipment_id']
        
        # Auto-populate fields based on equipment
        equipment = Equipment.query.get(request_obj.equipment_id)
        request_obj.category = equipment.category if equipment else None
        request_obj.maintenance_team_id = equipment.maintenance_team_id if equipment else None
        
        request_obj.assigned_technician = request.form.get('assigned_technician')
        request_obj.scheduled_date = datetime.strptime(request.form['scheduled_date'], '%Y-%m-%d %H:%M') if request.form.get('scheduled_date') else None
        request_obj.duration_hours = float(request.form.get('duration_hours', 0)) if request.form.get('duration_hours') else None
        request_obj.stage = request.form['stage']
        
        # If stage is 'Scrap', update equipment status
        if request_obj.stage == 'Scrap':
            equipment = Equipment.query.get(request_obj.equipment_id)
            if equipment:
                equipment.status = 'Scrapped'
                equipment.notes = f"Marked as scrapped due to maintenance request: {request_obj.subject}"
        
        db.session.commit()
        flash('Maintenance request updated successfully!', 'success')
        return redirect(url_for('maintenance_requests'))
    
    equipment_list = Equipment.query.all()
    teams = MaintenanceTeam.query.all()
    return render_template('request_form.html', request=request_obj, equipment_list=equipment_list, teams=teams)

@app.route('/request/<int:id>/update_stage', methods=['POST'])
def update_request_stage(id):
    request_obj = MaintenanceRequest.query.get_or_404(id)
    new_stage = request.form['stage']
    
    # Update stage
    request_obj.stage = new_stage
    
    # If stage is 'Scrap', update equipment status
    if new_stage == 'Scrap':
        equipment = Equipment.query.get(request_obj.equipment_id)
        if equipment:
            equipment.status = 'Scrapped'
            equipment.notes = f"Marked as scrapped due to maintenance request: {request_obj.subject}"
    
    db.session.commit()
    flash('Request stage updated successfully!', 'success')
    return redirect(url_for('kanban_board'))

# Calendar view for preventive maintenance
@app.route('/calendar')
def calendar_view():
    # Get only preventive maintenance requests
    preventive_requests = MaintenanceRequest.query.filter_by(request_type='Preventive').all()
    return render_template('calendar.html', requests=preventive_requests)

# Additional helper routes
@app.route('/equipment/<int:id>/delete', methods=['POST'])
def delete_equipment(id):
    equipment = Equipment.query.get_or_404(id)
    db.session.delete(equipment)
    db.session.commit()
    flash('Equipment deleted successfully!', 'success')
    return redirect(url_for('equipment_list'))

@app.route('/request/<int:id>/delete', methods=['POST'])
def delete_request(id):
    request_obj = MaintenanceRequest.query.get_or_404(id)
    db.session.delete(request_obj)
    db.session.commit()
    flash('Request deleted successfully!', 'success')
    return redirect(url_for('maintenance_requests'))

if __name__ == '__main__':
    app.run(debug=True)