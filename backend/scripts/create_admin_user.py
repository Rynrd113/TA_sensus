# backend/scripts/create_admin_user.py
"""
Script untuk membuat user admin pertama
Run this script to create initial admin user
"""

import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.session import get_db
from models.user import User
from models.base import Base
from database.engine import engine
from core.auth import PasswordManager

# Create tables
Base.metadata.create_all(bind=engine)

def create_admin_user():
    db = next(get_db())
    
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("❌ Admin user already exists!")
            return
        
        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@hospital.com",
            full_name="System Administrator",
            hashed_password=PasswordManager.hash_password("admin123"),
            employee_id="ADM001",
            department="IT",
            position="System Administrator",
            phone="+62-123-456-7890",
            roles=["admin"],
            is_active=True,
            is_verified=True
        )
        
        db.add(admin_user)
        db.commit()
        
        print("✅ Admin user created successfully!")
        print("📝 Login credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Email: admin@hospital.com")
        print("⚠️  Please change the password after first login!")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {str(e)}")
        db.rollback()
        
    finally:
        db.close()

def create_sample_users():
    """Create sample users for testing"""
    db = next(get_db())
    
    sample_users = [
        {
            "username": "dr_john",
            "email": "john.doe@hospital.com", 
            "full_name": "Dr. John Doe",
            "employee_id": "DOC001",
            "department": "Internal Medicine",
            "position": "Senior Doctor",
            "phone": "+62-123-456-7891",
            "roles": ["doctor"],
            "password": "doctor123"
        },
        {
            "username": "nurse_mary",
            "email": "mary.smith@hospital.com",
            "full_name": "Mary Smith",
            "employee_id": "NUR001", 
            "department": "General Ward",
            "position": "Head Nurse",
            "phone": "+62-123-456-7892",
            "roles": ["nurse"],
            "password": "nurse123"
        },
        {
            "username": "viewer_bob",
            "email": "bob.wilson@hospital.com",
            "full_name": "Bob Wilson",
            "employee_id": "VIE001",
            "department": "Management",
            "position": "Data Analyst", 
            "phone": "+62-123-456-7893",
            "roles": ["viewer"],
            "password": "viewer123"
        }
    ]
    
    try:
        for user_data in sample_users:
            # Check if user already exists
            existing_user = db.query(User).filter(User.username == user_data["username"]).first()
            if existing_user:
                print(f"⚠️  User {user_data['username']} already exists, skipping...")
                continue
            
            password = user_data.pop("password")
            user = User(
                **user_data,
                hashed_password=PasswordManager.hash_password(password),
                is_active=True,
                is_verified=True
            )
            
            db.add(user)
            db.commit()
            
            print(f"✅ Created user: {user_data['username']} ({user_data['full_name']})")
        
        print("\n📋 Sample users created:")
        print("   Username: dr_john     | Password: doctor123  | Role: doctor")
        print("   Username: nurse_mary  | Password: nurse123   | Role: nurse") 
        print("   Username: viewer_bob  | Password: viewer123  | Role: viewer")
        
    except Exception as e:
        print(f"❌ Error creating sample users: {str(e)}")
        db.rollback()
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🏥 Creating initial users for Sensus RS system...")
    print("=" * 50)
    
    create_admin_user()
    print()
    create_sample_users()
    
    print("\n🎉 User creation completed!")
    print("💡 You can now login to the system with any of the created users.")