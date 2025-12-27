import firebase_admin
from firebase_admin import auth as firebase_auth
from models import db, User
import re

class FirebaseAuthService:
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def create_user(email, password, display_name=None):
        """Create a new user in Firebase and local database"""
        try:
            # In a real implementation, this would create the user in Firebase
            # user_record = firebase_auth.create_user(
            #     email=email,
            #     password=password,
            #     display_name=display_name
            # )
            
            # For demo purposes, we'll simulate the Firebase user creation
            # and create a local database entry
            user = User(username=display_name or email.split('@')[0], 
                       email=email)
            user.set_password(password)  # Using the local password hashing
            db.session.add(user)
            db.session.commit()
            
            return {
                'uid': f'demo_user_{email.split("@")[0]}',
                'email': email,
                'display_name': display_name or email.split('@')[0],
                'success': True
            }
        except Exception as e:
            print(f"Error creating user: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def verify_password(email, password):
        """Verify user credentials (simulating Firebase auth)"""
        try:
            # In a real implementation, this would use Firebase auth
            # decoded_token = firebase_auth.verify_id_token(id_token)
            # For demo purposes, we'll check against our local database
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                return {
                    'uid': f'demo_user_{email.split("@")[0]}',
                    'email': email,
                    'username': user.username,
                    'role': user.role,
                    'success': True
                }
            return {'success': False, 'error': 'Invalid credentials'}
        except Exception as e:
            print(f"Error verifying password: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_user_by_token(token):
        """Get user info from token (simulating Firebase auth)"""
        # In a real implementation, this would verify the Firebase token
        # For demo purposes, we'll return a mock user
        return {
            'uid': 'demo_user',
            'email': 'demo@example.com',
            'username': 'demo_user',
            'role': 'user',
            'success': True
        }