from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, JSON, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from db.database import Base

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

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    mobile = Column(String(20), unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id', ondelete="SET NULL"), nullable=True)
    is_candidate = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    role = relationship("Role", back_populates="users")
    assigned_candidates = relationship("Candidate", back_populates="assigned_recruiter", foreign_keys='Candidate.assigned_recruiter_id')
    created_jobs = relationship("Job", back_populates="creator")
    follow_ups = relationship("FollowUp", back_populates="updater")

class Skill(Base):
    __tablename__ = 'skills'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    category = Column(String(100)) # e.g. Frontend, Backend, AI
    is_active = Column(Boolean, default=True)

class FilterOption(Base):
    __tablename__ = 'filter_options'
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), index=True) # e.g. notice_period, experience_range, work_mode
    value = Column(String(255), nullable=False)
    label = Column(String(255))
    sort_order = Column(Integer, default=0)

class Candidate(Base):
    __tablename__ = 'candidates'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="SET NULL"), nullable=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    mobile = Column(String(20), unique=True, index=True, nullable=False)
    alternate_mobile = Column(String(20))
    current_location = Column(String(100))
    preferred_location = Column(String(100))
    total_experience = Column(Float)
    relevant_experience = Column(Float)
    current_company = Column(String(100))
    current_designation = Column(String(100))
    skills = Column(JSON)  
    current_ctc = Column(String(50))
    expected_ctc = Column(String(50))
    notice_period = Column(String(50))
    cv_file_path = Column(String(500))
    status = Column(Enum(CandidateStatus), default=CandidateStatus.NEW)
    source = Column(String(100))
    applied_role = Column(String(100))
    linkedin_url = Column(String(255))
    portfolio_url = Column(String(255))
    remarks = Column(Text)
    assigned_recruiter_id = Column(Integer, ForeignKey('users.id', ondelete="SET NULL"), nullable=True)
    is_duplicate = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    assigned_recruiter = relationship("User", foreign_keys=[assigned_recruiter_id], back_populates="assigned_candidates")
    follow_ups = relationship("FollowUp", back_populates="candidate")
    applications = relationship("JobApplication", back_populates="candidate")

class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    client_name = Column(String(100))
    skills_required = Column(JSON)
    experience_range = Column(String(50))
    location = Column(String(100))
    work_mode = Column(String(50))
    budget = Column(String(50))
    number_of_positions = Column(Integer)
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
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    job = relationship("Job", back_populates="applications")
    candidate = relationship("Candidate", back_populates="applications")

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
