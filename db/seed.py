import sys
import os

# Add the parent directory to the python path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from db.database import SessionLocal, engine, Base
from db.models import Role, Permission, RolePermission, Skill, FilterOption
from core.config import settings

def seed_db():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Default Permissions
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
            {"name": "manage_followups", "module_name": "Candidates", "description": "Can manage candidate follow-ups"},
            {"name": "manage_settings", "module_name": "Settings", "description": "Can manage master skills and filters"},
        ]
        
        # Insert permissions if they don't exist
        for p_data in permissions_data:
            perm = db.query(Permission).filter(Permission.name == p_data["name"]).first()
            if not perm:
                perm = Permission(**p_data)
                db.add(perm)
        db.commit()

        # Default Roles
        roles_data = [
            {"name": "Admin", "description": "System Administrator", "is_system_role": True},
            {"name": "HR", "description": "Human Resources Manager", "is_system_role": True},
            {"name": "Employee", "description": "Standard Employee", "is_system_role": True},
        ]
        
        for r_data in roles_data:
            role = db.query(Role).filter(Role.name == r_data["name"]).first()
            if not role:
                role = Role(**r_data)
                db.add(role)
        db.commit()
        
        # Assign all permissions to Admin
        admin_role = db.query(Role).filter(Role.name == "Admin").first()
        all_perms = db.query(Permission).all()
        
        if admin_role:
            for perm in all_perms:
                rp = db.query(RolePermission).filter_by(role_id=admin_role.id, permission_id=perm.id).first()
                if not rp:
                    rp = RolePermission(role_id=admin_role.id, permission_id=perm.id)
                    db.add(rp)
        
        # Seed Initial Skills
        skills_data = [
            {"name": "React", "category": "Frontend"},
            {"name": "Angular", "category": "Frontend"},
            {"name": "Vue.js", "category": "Frontend"},
            {"name": "Python", "category": "Backend"},
            {"name": "FastAPI", "category": "Backend"},
            {"name": "Node.js", "category": "Backend"},
            {"name": "Java", "category": "Backend"},
            {"name": "Flutter", "category": "Mobile"},
            {"name": "React Native", "category": "Mobile"},
            {"name": "Docker", "category": "DevOps"},
            {"name": "AWS", "category": "Cloud"},
            {"name": "Machine Learning", "category": "AI"},
        ]
        for s_data in skills_data:
            if not db.query(Skill).filter_by(name=s_data["name"]).first():
                db.add(Skill(**s_data))

        # Seed Initial Filter Options
        filters_data = [
            {"category": "notice_period", "value": "Immediate", "label": "Immediate Joiner", "sort_order": 1},
            {"category": "notice_period", "value": "15 Days", "label": "15 Days", "sort_order": 2},
            {"category": "notice_period", "value": "30 Days", "label": "30 Days", "sort_order": 3},
            {"category": "notice_period", "value": "45 Days", "label": "45 Days", "sort_order": 4},
            {"category": "notice_period", "value": "60 Days", "label": "2 Months", "sort_order": 5},
            {"category": "notice_period", "value": "90 Days", "label": "3 Months", "sort_order": 6},
            
            {"category": "work_mode", "value": "Remote", "label": "Remote", "sort_order": 1},
            {"category": "work_mode", "value": "Hybrid", "label": "Hybrid", "sort_order": 2},
            {"category": "work_mode", "value": "On-site", "label": "On-site", "sort_order": 3},

            {"category": "experience_range", "value": "0-2", "label": "0-2 Years", "sort_order": 1},
            {"category": "experience_range", "value": "2-5", "label": "2-5 Years", "sort_order": 2},
            {"category": "experience_range", "value": "5-8", "label": "5-8 Years", "sort_order": 3},
            {"category": "experience_range", "value": "8+", "label": "8+ Years", "sort_order": 4},
        ]
        for f_data in filters_data:
            if not db.query(FilterOption).filter_by(category=f_data["category"], value=f_data["value"]).first():
                db.add(FilterOption(**f_data))

        db.commit()
        print("Database seeded successfully with skills and filters.")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
