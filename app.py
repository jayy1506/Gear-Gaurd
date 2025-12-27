from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User, Equipment, MaintenanceTeam, MaintenanceRequest, WorkCenter
from datetime import datetime
import os
import re
from datetime import datetime as dt
from firebase_auth_service import FirebaseAuthService


def validate_password(password):
    """
    Validate password requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number"
    
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is valid"

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

# Authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Validate email format
        if not FirebaseAuthService.validate_email(email):
            flash('Please enter a valid email address', 'error')
            return render_template('register.html')
        
        # Validate password strength
        is_valid, message = validate_password(password)
        if not is_valid:
            flash(message, 'error')
            return render_template('register.html')
        
        # Check if user already exists in local database
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists', 'error')
            return render_template('register.html')
        
        # Create user via Firebase service
        result = FirebaseAuthService.create_user(email, password, username)
        
        if result['success']:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash(f'Registration failed: {result["error"]}', 'error')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Verify credentials via Firebase service
        result = FirebaseAuthService.verify_password(email, password)
        
        if result['success']:
            # Find or create user in local database
            user = User.query.filter_by(email=email).first()
            if not user:
                # Create local user if doesn't exist
                user = User(username=result['username'], email=email)
                user.set_password(password)  # Store hashed password locally as well
                db.session.add(user)
                db.session.commit()
            
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['firebase_uid'] = result['uid']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

from functools import wraps

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Check if user is logged in
@app.context_processor
def inject_user():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return {'current_user': user}
    return {'current_user': None}

# Routes for Work Centers
@app.route('/workcenters')
@login_required
def workcenters_list():
    workcenters = WorkCenter.query.all()
    return render_template('workcenters.html', workcenters=workcenters)

@app.route('/workcenter/new', methods=['GET', 'POST'])
@login_required
def create_workcenter():
    if request.method == 'POST':
        workcenter = WorkCenter(
            name=request.form['name'],
            code=request.form['code'],
            location=request.form.get('location'),
            department=request.form.get('department'),
            responsible_person=request.form.get('responsible_person'),
            description=request.form.get('description')
        )
        db.session.add(workcenter)
        db.session.commit()
        flash('Work Center created successfully!', 'success')
        return redirect(url_for('workcenters_list'))
    return render_template('workcenter_form.html')

@app.route('/workcenter/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_workcenter(id):
    workcenter = WorkCenter.query.get_or_404(id)
    
    if request.method == 'POST':
        workcenter.name = request.form['name']
        workcenter.code = request.form['code']
        workcenter.location = request.form.get('location')
        workcenter.department = request.form.get('department')
        workcenter.responsible_person = request.form.get('responsible_person')
        workcenter.description = request.form.get('description')
        
        db.session.commit()
        flash('Work Center updated successfully!', 'success')
        return redirect(url_for('workcenters_list'))
    
    return render_template('workcenter_form.html', workcenter=workcenter)

@app.route('/workcenter/<int:id>/delete', methods=['POST'])
@login_required
def delete_workcenter(id):
    workcenter = WorkCenter.query.get_or_404(id)
    db.session.delete(workcenter)
    db.session.commit()
    flash('Work Center deleted successfully!', 'success')
    return redirect(url_for('workcenters_list'))

# Routes for Equipment
@app.route('/')
@login_required
def dashboard():
    return redirect(url_for('kanban_board'))

@app.route('/dashboard')
@login_required
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
@login_required
def equipment_list():
    equipment = Equipment.query.all()
    return render_template('equipment_list.html', equipment=equipment)

@app.route('/equipment/<int:id>')
@login_required
def equipment_detail(id):
    equip = Equipment.query.get_or_404(id)
    # Get maintenance requests for this equipment
    requests = MaintenanceRequest.query.filter_by(equipment_id=id).all()
    return render_template('equipment_detail.html', equipment=equip, requests=requests)

@app.route('/equipment/<int:equip_id>/maintenance_requests')
@login_required
def equipment_maintenance_requests(equip_id):
    equip = Equipment.query.get_or_404(equip_id)
    requests = MaintenanceRequest.query.filter_by(equipment_id=equip_id).all()
    return render_template('equipment_detail.html', equipment=equip, requests=requests)

@app.route('/equipment/new', methods=['GET', 'POST'])
@login_required
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
@login_required
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
@login_required
def maintenance_requests():
    requests = MaintenanceRequest.query.all()
    return render_template('requests_list.html', requests=requests)

@app.route('/request/new', methods=['GET', 'POST'])
@login_required
def create_request():
    if request.method == 'POST':
        # Determine if request is for equipment or work center
        request_for = request.form.get('request_for')  # 'equipment' or 'workcenter'
        
        scheduled_date_str = request.form.get('scheduled_date')
        scheduled_date = None
        if scheduled_date_str:
            try:
                scheduled_date = datetime.strptime(scheduled_date_str, '%Y-%m-%d %H:%M')
            except ValueError:
                # Handle potential parsing errors
                pass
        
        # Create request object
        request_obj = MaintenanceRequest(
            subject=request.form['subject'],
            request_type=request.form['request_type'],
            scheduled_date=scheduled_date,
            duration_hours=float(request.form.get('duration_hours', 0)) if request.form.get('duration_hours') else None,
            stage='New',  # Default stage
            assigned_technician=request.form.get('assigned_technician')
        )
        
        # Set category and maintenance team based on request type
        if request_for == 'equipment' and request.form.get('equipment_id'):
            equipment = Equipment.query.get(request.form['equipment_id'])
            request_obj.equipment_id = request.form['equipment_id']
            request_obj.category = equipment.category if equipment else None
            request_obj.maintenance_team_id = equipment.maintenance_team_id if equipment else None
            if not request_obj.assigned_technician:
                request_obj.assigned_technician = equipment.default_technician if equipment else None
        elif request_for == 'workcenter' and request.form.get('workcenter_id'):
            workcenter = WorkCenter.query.get(request.form['workcenter_id'])
            request_obj.workcenter_id = request.form['workcenter_id']
            request_obj.category = workcenter.department if workcenter else None
            # You can set maintenance team based on workcenter if needed
        
        db.session.add(request_obj)
        db.session.commit()
        
        flash('Maintenance request created successfully!', 'success')
        return redirect(url_for('maintenance_requests'))
    
    equipment_list = Equipment.query.all()
    workcenters_list = WorkCenter.query.all()
    teams = MaintenanceTeam.query.all()
    return render_template('request_form.html', 
                           equipment_list=equipment_list, 
                           workcenters_list=workcenters_list,
                           teams=teams)

@app.route('/request/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_request(id):
    request_obj = MaintenanceRequest.query.get_or_404(id)
    
    if request.method == 'POST':
        # Update the request
        request_obj.subject = request.form['subject']
        request_obj.request_type = request.form['request_type']
        
        # Determine if request is for equipment or work center
        request_for = request.form.get('request_for')  # 'equipment' or 'workcenter'
        
        # Clear both IDs first
        request_obj.equipment_id = None
        request_obj.workcenter_id = None
        
        # Set appropriate ID based on request type
        if request_for == 'equipment' and request.form.get('equipment_id'):
            request_obj.equipment_id = request.form['equipment_id']
            equipment = Equipment.query.get(request_obj.equipment_id)
            request_obj.category = equipment.category if equipment else None
            request_obj.maintenance_team_id = equipment.maintenance_team_id if equipment else None
        elif request_for == 'workcenter' and request.form.get('workcenter_id'):
            request_obj.workcenter_id = request.form['workcenter_id']
            workcenter = WorkCenter.query.get(request_obj.workcenter_id)
            request_obj.category = workcenter.department if workcenter else None
        
        request_obj.assigned_technician = request.form.get('assigned_technician')
        scheduled_date_str = request.form.get('scheduled_date')
        if scheduled_date_str:
            try:
                request_obj.scheduled_date = datetime.strptime(scheduled_date_str, '%Y-%m-%d %H:%M')
            except ValueError:
                request_obj.scheduled_date = None
        else:
            request_obj.scheduled_date = None
        request_obj.duration_hours = float(request.form.get('duration_hours', 0)) if request.form.get('duration_hours') else None
        request_obj.stage = request.form['stage']
        
        # If stage is 'Scrap', update equipment status
        if request_obj.stage == 'Scrap' and request_obj.equipment_id:
            equipment = Equipment.query.get(request_obj.equipment_id)
            if equipment:
                equipment.status = 'Scrapped'
                equipment.notes = f"Marked as scrapped due to maintenance request: {request_obj.subject}"
        
        db.session.commit()
        flash('Maintenance request updated successfully!', 'success')
        return redirect(url_for('maintenance_requests'))
    
    equipment_list = Equipment.query.all()
    workcenters_list = WorkCenter.query.all()
    teams = MaintenanceTeam.query.all()
    return render_template('request_form.html', 
                           request=request_obj, 
                           equipment_list=equipment_list, 
                           workcenters_list=workcenters_list,
                           teams=teams)

@app.route('/request/<int:id>/update_stage', methods=['POST'])
@login_required
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

# Worksheets view
@app.route('/worksheets')
@login_required
def worksheets():
    return render_template('worksheets.html')

@app.route('/worksheet/new', methods=['GET', 'POST'])
@login_required
def create_worksheet():
    # This is a placeholder - worksheets functionality would be implemented here
    flash('Worksheet creation functionality would be implemented here', 'info')
    return redirect(url_for('worksheets'))

# Calendar view for preventive maintenance
@app.route('/calendar')
@login_required
def calendar_view():
    # Get all maintenance requests with scheduled dates
    all_requests = MaintenanceRequest.query.filter(MaintenanceRequest.scheduled_date.isnot(None)).all()
    
    # Group requests by date
    requests_by_date = {}
    for request in all_requests:
        if request.scheduled_date:
            date_key = request.scheduled_date.strftime('%Y-%m-%d')
            if date_key not in requests_by_date:
                requests_by_date[date_key] = []
            requests_by_date[date_key].append(request)
    
    # Get current month/year for calendar
    import calendar
    from datetime import date
    
    today = date.today()
    current_month = today.month
    current_year = today.year
    
    # Generate calendar for current month
    cal = calendar.monthcalendar(current_year, current_month)
    
    return render_template('calendar.html', 
                           requests_by_date=requests_by_date,
                           calendar=cal,
                           current_month=current_month,
                           current_year=current_year,
                           month_name=calendar.month_name[current_month])

@app.route('/teams')
@login_required
def teams_list():
    teams = MaintenanceTeam.query.all()
    return render_template('teams.html', teams=teams)

@app.route('/create_team', methods=['GET', 'POST'])
@login_required
def create_team():
    if request.method == 'POST':
        team = MaintenanceTeam(
            name=request.form['name'],
            members=request.form['members']
        )
        db.session.add(team)
        db.session.commit()
        flash('Team created successfully!', 'success')
        return redirect(url_for('teams_list'))
    return render_template('team_form.html')


# Additional helper routes
@app.route('/equipment/<int:id>/delete', methods=['POST'])
@login_required
def delete_equipment(id):
    equipment = Equipment.query.get_or_404(id)
    db.session.delete(equipment)
    db.session.commit()
    flash('Equipment deleted successfully!', 'success')
    return redirect(url_for('equipment_list'))

@app.route('/request/<int:id>/delete', methods=['POST'])
@login_required
def delete_request(id):
    request_obj = MaintenanceRequest.query.get_or_404(id)
    db.session.delete(request_obj)
    db.session.commit()
    flash('Request deleted successfully!', 'success')
    return redirect(url_for('maintenance_requests'))

if __name__ == '__main__':
    app.run(debug=True)