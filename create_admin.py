from db.database import SessionLocal
from db.models import User, Role
from core.security import get_password_hash

def create():
    db = SessionLocal()
    admin_role = db.query(Role).filter(Role.name == "Admin").first()
    if not admin_role:
        print("Admin role not found. Run seed.py first.")
        return
        
    admin_user = db.query(User).filter(User.email == "admin@example.com").first()
    if not admin_user:
        admin_user = User(
            name="System Admin",
            email="admin@example.com",
            mobile="1234567890",
            password_hash=get_password_hash("admin123"),
            role_id=admin_role.id
        )
        db.add(admin_user)
        db.commit()
        print("Admin user created: admin@example.com / admin123")
    else:
        print("Admin user already exists: admin@example.com / admin123")
        
if __name__ == "__main__":
    create()
