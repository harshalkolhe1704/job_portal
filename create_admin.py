from backend.database import SessionLocal
from backend import models, auth
from backend.models import UserRole

def create_admin():
    db = SessionLocal()
    
    email = "admin@jobportal.com"
    password = "admin123"
    
    existing_admin = db.query(models.User).filter(models.User.email == email).first()
    if existing_admin:
        print(f"Admin user already exists: {email}")
    else:
        hashed_password = auth.get_password_hash(password)
        admin_user = models.User(
            email=email,
            hashed_password=hashed_password,
            role=UserRole.admin
        )
        db.add(admin_user)
        db.commit()
        print(f"Admin user created successfully!")
        print(f"Email: {email}")
        print(f"Password: {password}")
        
    db.close()

if __name__ == "__main__":
    create_admin()
