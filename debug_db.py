from backend.database import SessionLocal
from backend import models

def check_users():
    db = SessionLocal()
    users = db.query(models.User).all()
    print(f"Found {len(users)} users.")
    for u in users:
        print(f"ID: {u.id}, Email: {u.email}, Role: {u.role}")
        if u.role == models.UserRole.employer:
            if u.employer_profile:
                print(f"  - Employer Profile: OK (Company: {u.employer_profile.company_name})")
            else:
                print(f"  - Employer Profile: MISSING!")
        elif u.role == models.UserRole.seeker:
            if u.seeker_profile:
                print(f"  - Seeker Profile: OK (Name: {u.seeker_profile.full_name})")
            else:
                print(f"  - Seeker Profile: MISSING!")
    db.close()

if __name__ == "__main__":
    check_users()
