import sys
import os

# Add the parent directory to the python path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from db.database import SessionLocal, engine, Base
from db.models import (
    Role, Permission, RolePermission, Skill, FilterOption, 
    Department, Designation, User, Employee, EmployeeStatus,
    SupportTicket, LeaveRequest, LeaveStatus, TicketStatus, TicketPriority, LeaveType
)
from core.security import get_password_hash
from core.config import settings
from datetime import datetime, timedelta

def seed_db():
    print("Creating tables...")
    Base.metadata.drop_all(bind=engine) # Drop first for clean seed
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("Seeding Permissions...")
        permissions_data = [
            {"name": "view_users", "module_name": "Users", "description": "Can view users"},
            {"name": "manage_users", "module_name": "Users", "description": "Can create/edit/delete users"},
            {"name": "view_candidates", "module_name": "Candidates", "description": "Can view candidates"},
            {"name": "edit_candidates", "module_name": "Candidates", "description": "Can edit candidates"},
            {"name": "bulk_upload_cv", "module_name": "Candidates", "description": "Can bulk upload CVs"},
            {"name": "view_jobs", "module_name": "Jobs", "description": "Can view jobs"},
            {"name": "manage_jobs", "module_name": "Jobs", "description": "Can create/edit/delete jobs"},
            {"name": "view_dashboard", "module_name": "Dashboard", "description": "Can view analytics dashboard"},
            {"name": "view_reports", "module_name": "Reports", "description": "Can view and export reports"},
            {"name": "manage_roles", "module_name": "Roles", "description": "Can manage custom roles"},
            {"name": "manage_settings", "module_name": "Settings", "description": "Can manage master skills and filters"},
            {"name": "manage_payroll", "module_name": "Payroll", "description": "Can generate pay slips"},
            {"name": "approve_leaves", "module_name": "Leaves", "description": "Can approve/reject leave requests"},
            {"name": "resolve_tickets", "module_name": "Tickets", "description": "Can assign and resolve support tickets"},
        ]
        
        for p_data in permissions_data:
            perm = Permission(**p_data)
            db.add(perm)
        db.commit()

        print("Seeding Roles...")
        roles_data = [
            {"name": "Admin", "description": "System Administrator", "is_system_role": True},
            {"name": "HR", "description": "Human Resources Manager", "is_system_role": True},
            {"name": "Manager", "description": "Department Manager", "is_system_role": True},
            {"name": "Employee", "description": "Standard Staff", "is_system_role": True},
            {"name": "Finance", "description": "Payroll & Accounts", "is_system_role": True},
            {"name": "Candidate", "description": "External Candidate", "is_system_role": True},
        ]
        
        for r_data in roles_data:
            role = Role(**r_data)
            db.add(role)
        db.commit()
        
        # Assign all permissions to Admin
        admin_role = db.query(Role).filter(Role.name == "Admin").first()
        all_perms = db.query(Permission).all()
        for perm in all_perms:
            rp = RolePermission(role_id=admin_role.id, permission_id=perm.id)
            db.add(rp)
        
        # Assign HR specific perms
        hr_role = db.query(Role).filter(Role.name == "HR").first()
        hr_perm_names = ["view_candidates", "edit_candidates", "view_jobs", "manage_jobs", "approve_leaves", "view_reports"]
        for p in all_perms:
            if p.name in hr_perm_names:
                db.add(RolePermission(role_id=hr_role.id, permission_id=p.id))

        print("Seeding Departments & Designations...")
        depts = [
            Department(name="Information Technology", description="Software development and IT support"),
            Department(name="Human Resources", description="Recruitment and employee relations"),
            Department(name="Finance", description="Accounting and payroll"),
            Department(name="Sales & Marketing", description="Lead generation and sales"),
        ]
        db.add_all(depts)
        db.commit()

        desigs = [
            Designation(title="Software Engineer", level=1),
            Designation(title="Senior Developer", level=2),
            Designation(title="Team Lead", level=3),
            Designation(title="HR Manager", level=4),
            Designation(title="Finance Analyst", level=2),
            Designation(title="CTO", level=5),
        ]
        db.add_all(desigs)
        db.commit()

        print("Seeding Initial Users & Employees...")
        # 1. Admin User
        admin_user = User(
            name="System Admin",
            email="admin@example.com",
            password_hash=get_password_hash("admin123"),
            role_id=admin_role.id
        )
        db.add(admin_user)
        db.commit()

        # 2. Some Employees
        it_dept = db.query(Department).filter_by(name="Information Technology").first()
        se_desig = db.query(Designation).filter_by(title="Software Engineer").first()
        emp_role = db.query(Role).filter_by(name="Employee").first()

        emp_names = ["Alice Johnson", "Bob Smith", "Charlie Davis"]
        for idx, name in enumerate(emp_names):
            u = User(
                name=name,
                email=f"{name.lower().replace(' ', '.')}@example.com",
                password_hash=get_password_hash("password123"),
                role_id=emp_role.id,
                is_employee=True
            )
            db.add(u)
            db.flush()
            
            e = Employee(
                user_id=u.id,
                employee_code=f"EMP{100 + idx}",
                department_id=it_dept.id,
                designation_id=se_desig.id,
                base_salary=50000 + (idx * 5000),
                status=EmployeeStatus.ACTIVE,
                joining_date=datetime.now() - timedelta(days=365)
            )
            db.add(e)
        
        db.commit()

        print("Seeding Skills & Filters...")
        skills = [Skill(name=n, category=c) for n, c in [("React", "Frontend"), ("Python", "Backend"), ("SQL", "Database"), ("Docker", "DevOps")]]
        db.add_all(skills)
        
        filters = [
            FilterOption(category="notice_period", value="Immediate", label="Immediate", sort_order=1),
            FilterOption(category="work_mode", value="Remote", label="Remote", sort_order=1),
        ]
        db.add_all(filters)
        
        print("Seeding Support Tickets & Leaves...")
        first_emp = db.query(Employee).first()
        if first_emp:
            ticket = SupportTicket(
                title="VPN not connecting",
                description="Unable to connect to office VPN since morning.",
                priority=TicketPriority.HIGH,
                status=TicketStatus.OPEN,
                category="IT",
                created_by_id=first_emp.id
            )
            db.add(ticket)
            
            leave = LeaveRequest(
                employee_id=first_emp.id,
                leave_type=LeaveType.SICK,
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=1),
                reason="Feeling unwell",
                status=LeaveStatus.PENDING
            )
            db.add(leave)

        db.commit()
        print("Database seeded successfully with corporate data.")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
