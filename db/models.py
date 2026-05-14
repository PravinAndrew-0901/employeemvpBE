from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, JSON, Enum, Float
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
import enum
from db.database import Base

# --- Enums ---

class CandidateStatus(str, enum.Enum):
    NEW = 'New'
    PROFILE_REVIEWED = 'Profile Reviewed'
    SHORTLISTED = 'Shortlisted'
    REJECTED = 'Rejected'
    DUPLICATE = 'Duplicate'
    CONTACTED = 'Contacted'
    NOT_RESPONDING = 'Not Responding'
    INTERESTED = 'Interested'
    NOT_INTERESTED = 'Not Interested'
    INTERVIEW_SCHEDULED = 'Interview Scheduled'
    INTERVIEW_COMPLETED = 'Interview Completed'
    SELECTED = 'Selected'
    OFFER_RELEASED = 'Offer Released'
    JOINED = 'Joined'
    ON_HOLD = 'On Hold'

class FollowUpType(str, enum.Enum):
    CALL = 'Call'
    EMAIL = 'Email'
    WHATSAPP = 'WhatsApp'
    INTERVIEW = 'Interview'

class EmployeeStatus(str, enum.Enum):
    ACTIVE = 'Active'
    PROBATION = 'Probation'
    ON_LEAVE = 'On Leave'
    TERMINATED = 'Terminated'
    RESIGNED = 'Resigned'
    RETIRED = 'Retired'

class LeaveType(str, enum.Enum):
    SICK = 'Sick Leave'
    CASUAL = 'Casual Leave'
    EARNED = 'Earned Leave'
    MATERNITY = 'Maternity Leave'
    PATERNITY = 'Paternity Leave'
    LOP = 'Loss of Pay'

class LeaveStatus(str, enum.Enum):
    PENDING = 'Pending'
    APPROVED = 'Approved'
    REJECTED = 'Rejected'
    CANCELLED = 'Cancelled'

class TicketPriority(str, enum.Enum):
    LOW = 'Low'
    MEDIUM = 'Medium'
    HIGH = 'High'
    URGENT = 'Urgent'

class TicketStatus(str, enum.Enum):
    OPEN = 'Open'
    IN_PROGRESS = 'In Progress'
    RESOLVED = 'Resolved'
    CLOSED = 'Closed'

# --- RBAC Models ---

class Permission(Base):
    __tablename__ = 'permissions'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    module_name = Column(String(100))
    description = Column(String(255))
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(255))
    is_system_role = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")
    users = relationship("User", back_populates="role")

class RolePermission(Base):
    __tablename__ = 'role_permissions'
    role_id = Column(Integer, ForeignKey('roles.id', ondelete="CASCADE"), primary_key=True)
    permission_id = Column(Integer, ForeignKey('permissions.id', ondelete="CASCADE"), primary_key=True)

# --- Core User Model ---

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    mobile = Column(String(20), unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id', ondelete="SET NULL"), nullable=True)
    is_candidate = Column(Boolean, default=False)
    is_employee = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    role = relationship("Role", back_populates="users")
    employee_profile = relationship("Employee", back_populates="user", uselist=False, foreign_keys='Employee.user_id')
    created_jobs = relationship("Job", back_populates="creator")
    follow_ups = relationship("FollowUp", back_populates="updater")
    assigned_candidates = relationship("Candidate", back_populates="assigned_recruiter", foreign_keys='Candidate.assigned_recruiter_id')

# --- Master Data ---

class Skill(Base):
    __tablename__ = 'skills'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    category = Column(String(100))
    is_active = Column(Boolean, default=True)

class FilterOption(Base):
    __tablename__ = 'filter_options'
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), index=True)
    value = Column(String(255), nullable=False)
    label = Column(String(255))
    sort_order = Column(Integer, default=0)

class Department(Base):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    employees = relationship("Employee", back_populates="department")

class Designation(Base):
    __tablename__ = 'designations'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), unique=True, nullable=False)
    level = Column(Integer) 
    employees = relationship("Employee", back_populates="designation")

# --- Recruitment ---

class Candidate(Base):
    __tablename__ = 'candidates'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="SET NULL"), nullable=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    mobile = Column(String(20), unique=True, index=True, nullable=False)
    alternate_mobile = Column(String(20))
    current_location = Column(String(100))
    total_experience = Column(Float)
    skills = Column(JSON)
    cv_file_path = Column(String(500))
    status = Column(Enum(CandidateStatus), default=CandidateStatus.NEW)
    assigned_recruiter_id = Column(Integer, ForeignKey('users.id', ondelete="SET NULL"), nullable=True)
    is_duplicate = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    assigned_recruiter = relationship("User", foreign_keys=[assigned_recruiter_id], back_populates="assigned_candidates")
    applications = relationship("JobApplication", back_populates="candidate")
    employee_record = relationship("Employee", back_populates="candidate_record", uselist=False, foreign_keys='Employee.candidate_id')
    follow_ups = relationship("FollowUp", back_populates="candidate")

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    client_name = Column(String(100))
    skills_required = Column(JSON)
    experience_range = Column(String(50))
    location = Column(String(100))
    work_mode = Column(String(50))
    description = Column(Text)
    status = Column(String(50), default='Open')
    created_by = Column(Integer, ForeignKey('users.id', ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    creator = relationship("User", back_populates="created_jobs")
    applications = relationship("JobApplication", back_populates="job")

class JobApplication(Base):
    __tablename__ = 'job_applications'
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey('jobs.id', ondelete="CASCADE"), nullable=False)
    candidate_id = Column(Integer, ForeignKey('candidates.id', ondelete="CASCADE"), nullable=False)
    status = Column(Enum(CandidateStatus), default=CandidateStatus.NEW)
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    job = relationship("Job", back_populates="applications")
    candidate = relationship("Candidate", back_populates="applications")

# --- Employee Management ---

class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=True)
    employee_code = Column(String(50), unique=True, index=True)
    
    department_id = Column(Integer, ForeignKey('departments.id'))
    designation_id = Column(Integer, ForeignKey('designations.id'))
    reporting_manager_id = Column(Integer, ForeignKey('employees.id'), nullable=True)
    
    joining_date = Column(DateTime(timezone=True), server_default=func.now())
    exit_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(EmployeeStatus), default=EmployeeStatus.PROBATION)
    
    base_salary = Column(Float, default=0.0)
    bank_name = Column(String(100))
    account_number = Column(String(50))
    pan_number = Column(String(20))
    
    user = relationship("User", back_populates="employee_profile", foreign_keys=[user_id])
    candidate_record = relationship("Candidate", back_populates="employee_record", foreign_keys=[candidate_id])
    department = relationship("Department", back_populates="employees")
    designation = relationship("Designation", back_populates="employees")
    
    # Self-referential for manager
    reporting_manager = relationship("Employee", remote_side=[id], backref="subordinates")
    
    leave_requests = relationship("LeaveRequest", back_populates="employee", foreign_keys='LeaveRequest.employee_id')
    leave_balances = relationship("LeaveBalance", back_populates="employee")
    pay_slips = relationship("PaySlip", back_populates="employee")
    tickets = relationship("SupportTicket", back_populates="creator", foreign_keys='SupportTicket.created_by_id')

# --- Attendance & Leave ---

class LeaveBalance(Base):
    __tablename__ = 'leave_balances'
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    leave_type = Column(Enum(LeaveType))
    total_days = Column(Float, default=0.0)
    used_days = Column(Float, default=0.0)
    year = Column(Integer)
    employee = relationship("Employee", back_populates="leave_balances")

class LeaveRequest(Base):
    __tablename__ = 'leave_requests'
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    leave_type = Column(Enum(LeaveType))
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    reason = Column(Text)
    status = Column(Enum(LeaveStatus), default=LeaveStatus.PENDING)
    approved_by_id = Column(Integer, ForeignKey('employees.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    employee = relationship("Employee", back_populates="leave_requests", foreign_keys=[employee_id])
    approver = relationship("Employee", foreign_keys=[approved_by_id])

# --- Payroll ---

class PaySlip(Base):
    __tablename__ = 'pay_slips'
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    month = Column(Integer)
    year = Column(Integer)
    basic_salary = Column(Float)
    allowances = Column(JSON) 
    deductions = Column(JSON) 
    net_salary = Column(Float)
    status = Column(String(50), default='Generated')
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    employee = relationship("Employee", back_populates="pay_slips")

# --- Helpdesk / Tickets ---

class SupportTicket(Base):
    __tablename__ = 'support_tickets'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    priority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM)
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN)
    category = Column(String(100)) 
    created_by_id = Column(Integer, ForeignKey('employees.id'))
    assigned_to_id = Column(Integer, ForeignKey('employees.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    creator = relationship("Employee", foreign_keys=[created_by_id], back_populates="tickets")
    assigned_to = relationship("Employee", foreign_keys=[assigned_to_id])
    comments = relationship("TicketComment", back_populates="ticket")

class TicketComment(Base):
    __tablename__ = 'ticket_comments'
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey('support_tickets.id'))
    commenter_id = Column(Integer, ForeignKey('users.id'))
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    ticket = relationship("SupportTicket", back_populates="comments")
    commenter = relationship("User")

# --- Follow Ups ---

class FollowUp(Base):
    __tablename__ = 'follow_ups'
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id', ondelete="CASCADE"), nullable=False)
    follow_up_date = Column(DateTime(timezone=True), server_default=func.now())
    next_follow_up_date = Column(DateTime(timezone=True))
    type = Column(Enum(FollowUpType))
    remarks = Column(Text)
    updated_by = Column(Integer, ForeignKey('users.id', ondelete="SET NULL"), nullable=True)
    candidate = relationship("Candidate", back_populates="follow_ups")
    updater = relationship("User", back_populates="follow_ups")
