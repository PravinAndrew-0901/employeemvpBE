from sqlalchemy.orm import Session
from db.database import engine, Base, SessionLocal
from db.models import Role, Permission, User, Department, Designation
from core.security import get_password_hash
import sys

def reset_db_production():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 1. Essential Permissions
        print("Seeding Essential Permissions...")
        perms = [
            # Candidate & Recruitment
            Permission(name="view_candidates", module_name="Recruitment", description="Can view candidate list and details"),
            Permission(name="manage_candidates", module_name="Recruitment", description="Can add, edit, and delete candidates"),
            Permission(name="bulk_upload_cv", module_name="Recruitment", description="Can upload ZIP/multiple CV files"),
            Permission(name="manage_jobs", module_name="Recruitment", description="Can create and manage job postings"),
            
            # HR & Employees
            Permission(name="manage_users", module_name="System", description="Can manage system users and staff"),
            Permission(name="view_reports", module_name="Reporting", description="Can access analytics and reports"),
            Permission(name="manage_payroll", module_name="Finance", description="Can process salaries and pay slips"),
            
            # Enterprise Power Modules
            Permission(name="manage_assets", module_name="Operations", description="Can track and assign company assets"),
            Permission(name="manage_expenses", module_name="Finance", description="Can approve/reject expense claims"),
            Permission(name="manage_projects", module_name="Operations", description="Can manage projects and teams"),
            
            # System Admin
            Permission(name="manage_roles", module_name="System", description="Can manage RBAC roles and permissions"),
            Permission(name="manage_settings", module_name="System", description="Can modify global system settings")
        ]
        db.add_all(perms)
        db.commit()

        # 2. Essential Roles
        print("Seeding Core Enterprise Roles...")
        # Super Admin
        admin_role = Role(name="Super Admin", description="Full system access", is_system_role=True)
        # HR Manager
        hr_role = Role(name="HR Manager", description="Manage recruitment and staff lifecycle")
        # Finance Head
        finance_role = Role(name="Finance Head", description="Manage payroll and expenses")
        # Employee
        emp_role = Role(name="Employee", description="Basic staff access for self-service")
        
        db.add_all([admin_role, hr_role, finance_role, emp_role])
        db.commit()

        # Assign all permissions to Super Admin
        all_perms = db.query(Permission).all()
        admin_role.permissions = all_perms
        db.commit()

        # 3. Core Master Data
        print("Seeding Initial Departments & Designations...")
        depts = [
            Department(name="Executive Management", description="C-level and Directors"),
            Department(name="Human Resources", description="Talent and Culture"),
            Department(name="Finance & Accounts", description="Financial operations"),
            Department(name="IT & Engineering", description="Product and Platform"),
            Department(name="Operations", description="General Business Ops")
        ]
        db.add_all(depts)
        db.commit()

        # 4. First Admin User (Production Ready)
        print("Creating Initial Super Admin...")
        admin_user = User(
            name="System Administrator",
            email="admin@corpsuite.com",
            mobile="9999999999",
            password_hash=get_password_hash("admin@123"),
            role_id=admin_role.id,
            is_employee=True
        )
        db.add(admin_user)
        db.commit()

        print("\n" + "="*50)
        print("PRODUCTION DATABASE INITIALIZED SUCCESSFULLY")
        print("="*50)
        print("Login Credentials:")
        print("Email: admin@corpsuite.com")
        print("Password: admin@123")
        print("="*50)

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_db_production()
