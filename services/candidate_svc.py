from sqlalchemy.orm import Session
from db.models import Candidate, CandidateStatus
from schemas.candidate import CandidateCreate
from services.cv_parser import parse_cv_and_get_skills
import os
from fastapi import UploadFile

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

async def create_candidate(db: Session, candidate_in: CandidateCreate, cv_file: UploadFile, current_user_id: int):
    # Check duplicate
    duplicate = db.query(Candidate).filter(
        (Candidate.email == candidate_in.email) | (Candidate.mobile == candidate_in.mobile)
    ).first()
    
    is_duplicate = False
    if duplicate:
        is_duplicate = True
        
    # Read file
    content = await cv_file.read()
    
    # Save file
    file_path = os.path.join(UPLOAD_DIR, cv_file.filename)
    with open(file_path, "wb") as f:
        f.write(content)
        
    # Extract skills if not provided
    skills = candidate_in.skills
    if not skills:
        skills = parse_cv_and_get_skills(content, cv_file.filename)
        
    db_candidate = Candidate(
        full_name=candidate_in.full_name,
        email=candidate_in.email,
        mobile=candidate_in.mobile,
        current_location=candidate_in.current_location,
        total_experience=candidate_in.total_experience,
        current_ctc=candidate_in.current_ctc,
        expected_ctc=candidate_in.expected_ctc,
        notice_period=candidate_in.notice_period,
        source=candidate_in.source,
        skills=skills,
        cv_file_path=file_path,
        is_duplicate=is_duplicate,
        assigned_recruiter_id=current_user_id
    )
    
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate

async def bulk_upload_cvs(db: Session, files: list[UploadFile], current_user_id: int):
    results = []
    for file in files:
        if file.content_type != "application/pdf":
            results.append({"filename": file.filename, "status": "failed", "reason": "Invalid file type. Only PDF allowed."})
            continue
            
        content = await file.read()
        if len(content) > 5 * 1024 * 1024:
            results.append({"filename": file.filename, "status": "failed", "reason": "File size exceeds 5MB limit."})
            continue
            
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(content)
            
        skills = parse_cv_and_get_skills(content, file.filename)
        # Create a dummy candidate since we only have CV in bulk upload MVP
        # In a real app, we'd extract email and name from CV
        db_candidate = Candidate(
            full_name=file.filename.split('.')[0],
            email=f"{file.filename.split('.')[0]}@example.com",
            mobile="0000000000",
            cv_file_path=file_path,
            skills=skills,
            assigned_recruiter_id=current_user_id
        )
        db.add(db_candidate)
        db.commit()
        results.append({"filename": file.filename, "status": "success", "id": db_candidate.id})
        
    return results
