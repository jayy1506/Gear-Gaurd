from models import db, User, Equipment, MaintenanceTeam, MaintenanceRequest, WorkCenter
from datetime import datetime, timedelta
from app import app

def seed_data():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create initial admin user
        admin_user = User(username='admin', email='admin@gearguard.com')
        admin_user.set_password('admin123')
        admin_user.role = 'admin'
        db.session.add(admin_user)
        
        # Create another demo user
        demo_user = User(username='demo', email='demo@gearguard.com')
        demo_user.set_password('demo123')
        demo_user.role = 'user'
        db.session.add(demo_user)
        
        # Create 3 maintenance teams
        team1 = MaintenanceTeam(name="Mechanical Team", members="John Smith, Mike Johnson, Sarah Davis")
        team2 = MaintenanceTeam(name="Electrical Team", members="Robert Wilson, Lisa Brown, Tom Anderson")
        team3 = MaintenanceTeam(name="IT Team", members="Amanda Taylor, Chris Lee, David Miller")
        
        db.session.add_all([team1, team2, team3])
        
        # Create 3 work centers
        wc1 = WorkCenter(
            name="Assembly Line 1",
            code="AL1",
            location="Factory Floor A",
            department="Production",
            responsible_person="Mike Johnson",
            description="Main assembly line for product manufacturing",
            status="Active"
        )
        
        wc2 = WorkCenter(
            name="Painting Station",
            code="PS1",
            location="Factory Floor B",
            department="Production",
            responsible_person="Sarah Williams",
            description="Automated painting and coating station",
            status="Active"
        )
        
        wc3 = WorkCenter(
            name="Quality Control Lab",
            code="QCL",
            location="Building C",
            department="Quality",
            responsible_person="Robert Taylor",
            description="Quality testing and inspection lab",
            status="Active"
        )
        
        db.session.add_all([wc1, wc2, wc3])
        db.session.commit()
        
        # Create 8 equipment records
        equipment_data = [
            {
                "name": "Production Line Conveyor",
                "serial_number": "PLC-001",
                "category": "Mechanical",
                "department": "Production",
                "assigned_employee": "John Smith",
                "maintenance_team_id": team1.id,
                "default_technician": "John Smith",
                "purchase_date": datetime(2020, 5, 15),
                "warranty_end": datetime(2023, 5, 15),
                "location": "Factory Floor A",
                "status": "Active"
            },
            {
                "name": "HVAC System",
                "serial_number": "HVAC-002",
                "category": "Electrical",
                "department": "Admin",
                "assigned_employee": "Lisa Brown",
                "maintenance_team_id": team2.id,
                "default_technician": "Lisa Brown",
                "purchase_date": datetime(2019, 8, 22),
                "warranty_end": datetime(2022, 8, 22),
                "location": "Building A",
                "status": "Active"
            },
            {
                "name": "Server Rack",
                "serial_number": "SR-003",
                "category": "IT",
                "department": "IT",
                "assigned_employee": "Chris Lee",
                "maintenance_team_id": team3.id,
                "default_technician": "Chris Lee",
                "purchase_date": datetime(2021, 3, 10),
                "warranty_end": datetime(2024, 3, 10),
                "location": "Server Room",
                "status": "Active"
            },
            {
                "name": "Industrial Press",
                "serial_number": "IP-004",
                "category": "Mechanical",
                "department": "Production",
                "assigned_employee": "Mike Johnson",
                "maintenance_team_id": team1.id,
                "default_technician": "Mike Johnson",
                "purchase_date": datetime(2018, 11, 5),
                "warranty_end": datetime(2021, 11, 5),
                "location": "Factory Floor B",
                "status": "Active"
            },
            {
                "name": "Backup Generator",
                "serial_number": "BG-005",
                "category": "Electrical",
                "department": "Admin",
                "assigned_employee": "Robert Wilson",
                "maintenance_team_id": team2.id,
                "default_technician": "Robert Wilson",
                "purchase_date": datetime(2020, 1, 30),
                "warranty_end": datetime(2023, 1, 30),
                "location": "Generator Room",
                "status": "Active"
            },
            {
                "name": "Network Switch",
                "serial_number": "NS-006",
                "category": "IT",
                "department": "IT",
                "assigned_employee": "Amanda Taylor",
                "maintenance_team_id": team3.id,
                "default_technician": "Amanda Taylor",
                "purchase_date": datetime(2022, 7, 12),
                "warranty_end": datetime(2025, 7, 12),
                "location": "IT Closet",
                "status": "Active"
            },
            {
                "name": "Assembly Robot",
                "serial_number": "AR-007",
                "category": "Mechanical",
                "department": "Production",
                "assigned_employee": "Sarah Davis",
                "maintenance_team_id": team1.id,
                "default_technician": "Sarah Davis",
                "purchase_date": datetime(2021, 9, 18),
                "warranty_end": datetime(2024, 9, 18),
                "location": "Assembly Line",
                "status": "Active"
            },
            {
                "name": "UPS System",
                "serial_number": "UPS-008",
                "category": "Electrical",
                "department": "IT",
                "assigned_employee": "Tom Anderson",
                "maintenance_team_id": team2.id,
                "default_technician": "Tom Anderson",
                "purchase_date": datetime(2019, 12, 5),
                "warranty_end": datetime(2022, 12, 5),
                "location": "Server Room",
                "status": "Active"
            }
        ]
        
        for equip_data in equipment_data:
            equipment = Equipment(**equip_data)
            db.session.add(equipment)
        
        db.session.commit()
        
        # Create sample maintenance requests (all stages)
        request_data = [
            {
                "subject": "Belt replacement for Conveyor",
                "request_type": "Corrective",
                "equipment_id": 1,
                "category": "Mechanical",
                "maintenance_team_id": team1.id,
                "assigned_technician": "John Smith",
                "stage": "New",
                "created_at": datetime.now() - timedelta(days=1)
            },
            {
                "subject": "HVAC filter cleaning",
                "request_type": "Preventive",
                "equipment_id": 2,
                "category": "Electrical",
                "maintenance_team_id": team2.id,
                "assigned_technician": "Lisa Brown",
                "scheduled_date": datetime.now() + timedelta(days=7),
                "stage": "New",
                "created_at": datetime.now() - timedelta(days=2)
            },
            {
                "subject": "Server rack cooling check",
                "request_type": "Preventive",
                "equipment_id": 3,
                "category": "IT",
                "maintenance_team_id": team3.id,
                "assigned_technician": "Chris Lee",
                "scheduled_date": datetime.now() + timedelta(days=14),
                "stage": "In Progress",
                "created_at": datetime.now() - timedelta(days=3)
            },
            {
                "subject": "Press hydraulic system repair",
                "request_type": "Corrective",
                "equipment_id": 4,
                "category": "Mechanical",
                "maintenance_team_id": team1.id,
                "assigned_technician": "Mike Johnson",
                "stage": "In Progress",
                "created_at": datetime.now() - timedelta(days=1)
            },
            {
                "subject": "Generator routine maintenance",
                "request_type": "Preventive",
                "equipment_id": 5,
                "category": "Electrical",
                "maintenance_team_id": team2.id,
                "assigned_technician": "Robert Wilson",
                "scheduled_date": datetime.now() + timedelta(days=30),
                "stage": "Repaired",
                "duration_hours": 4.5,
                "created_at": datetime.now() - timedelta(days=5)
            },
            {
                "subject": "Network switch firmware update",
                "request_type": "Corrective",
                "equipment_id": 6,
                "category": "IT",
                "maintenance_team_id": team3.id,
                "assigned_technician": "Amanda Taylor",
                "stage": "Repaired",
                "duration_hours": 2.0,
                "created_at": datetime.now() - timedelta(days=4)
            },
            {
                "subject": "Robot calibration",
                "request_type": "Preventive",
                "equipment_id": 7,
                "category": "Mechanical",
                "maintenance_team_id": team1.id,
                "assigned_technician": "Sarah Davis",
                "scheduled_date": datetime.now() - timedelta(days=1),
                "stage": "Scrap",
                "created_at": datetime.now() - timedelta(days=10)
            },
            {
                "subject": "UPS battery replacement",
                "request_type": "Corrective",
                "equipment_id": 8,
                "category": "Electrical",
                "maintenance_team_id": team2.id,
                "assigned_technician": "Tom Anderson",
                "stage": "New",
                "created_at": datetime.now() - timedelta(days=2)
            }
        ]
        
        for req_data in request_data:
            request = MaintenanceRequest(**req_data)
            db.session.add(request)
        
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_data()