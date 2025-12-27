# GearGuard - The Ultimate Maintenance Tracker

GearGuard is a comprehensive maintenance management system designed to streamline equipment and work center maintenance operations. Built with Flask, it provides an intuitive interface for tracking maintenance requests, managing equipment, and organizing work schedules.

## Features

- **Equipment Management**: Track all equipment with detailed information including serial numbers, categories, departments, and maintenance history
- **Work Center Management**: Manage maintenance for work centers and production areas
- **Maintenance Requests**: Create and track maintenance requests with different types (Corrective, Preventive, Predictive)
- **Kanban Board**: Visual workflow management with drag-and-drop functionality
- **Calendar View**: Schedule and visualize maintenance activities
- **Team Management**: Organize maintenance teams and assign technicians
- **Worksheet Management**: Create and manage maintenance worksheets
- **Authentication**: Secure login and registration system with Firebase integration

## Tech Stack

- **Backend**: Python Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML/CSS/JavaScript with Jinja2 templating
- **Authentication**: Firebase Admin SDK

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jayy1506/Gear-Gaurd.git
```

2. Navigate to the project directory:
```bash
cd gearguard
```

3. Install dependencies:
```bash
pip install flask flask-sqlalchemy werkzeug firebase-admin
```

4. Run the application:
```bash
python app.py
```

5. Access the application at `http://127.0.0.1:5000`

## Usage

### Getting Started
- Register a new account or use the demo credentials: `admin@gearguard.com` / `admin123`
- Create equipment or work centers to track
- Add maintenance teams and assign technicians
- Create maintenance requests for equipment or work centers

### Main Modules

#### Equipment Management
- Add, edit, and track all equipment
- Assign to departments and maintenance teams
- Track maintenance history and status

#### Work Center Management
- Create and manage work centers (production lines, stations, etc.)
- Assign to departments and responsible personnel
- Track maintenance activities by work center

#### Maintenance Requests
- Create requests for equipment or work centers
- Track through different stages: New → In Progress → Repaired/Scrap
- Schedule preventive maintenance activities

#### Kanban Board
- Visual workflow management
- Drag and drop requests between stages
- Quick access to request details and actions

#### Calendar View
- Monthly calendar view of scheduled maintenance
- Visualize preventive maintenance activities
- Plan and organize maintenance schedules

## Project Structure

```
gearguard/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── seed.py                # Database seeding script
├── static/                # Static files (CSS, JS)
│   └── style.css          # Main stylesheet
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── dashboard.html     # Kanban board dashboard
│   ├── equipment.html     # Equipment management
│   ├── workcenters.html   # Work center management
│   ├── requests.html      # Maintenance requests
│   ├── teams.html         # Team management
│   ├── calendar.html      # Calendar view
│   ├── worksheets.html    # Worksheet management
│   ├── login.html         # Login page
│   └── register.html      # Registration page
├── firebase_config.py     # Firebase configuration
└── firebase_auth_service.py # Firebase authentication service
```

## Authentication

The system includes Firebase authentication integration that allows users to register and login with email and password. Credentials are securely stored both in Firebase and locally in the SQLite database.

## Database Seeding

The seed.py file creates sample data for demonstration purposes. It includes:
- Sample users (admin and demo)
- Sample maintenance teams
- Sample equipment
- Sample work centers
- Sample maintenance requests

## Team Jay

Created by Team Jay - Dedicated to providing efficient maintenance tracking solutions.

## License

This project is licensed under the MIT License.