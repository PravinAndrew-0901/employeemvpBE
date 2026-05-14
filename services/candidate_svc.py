from sqlalchemy.orm import Session
from db.models import Candidate, CandidateStatus
from schemas.candidate import CandidateCreate
from services.cv_parser import parse_cv_and_get_skills
import os
import zipfile
import io
from fastapi import UploadFile

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

async def process_single_pdf(db: Session, filename: str, content: bytes, current_user_id: int):
    """Helper to process a single PDF content and create a candidate"""
    if len(content) > 5 * 1024 * 1024:
        return {"filename": filename, "status": "failed", "reason": "File size exceeds 5MB limit."}
        
    # Save file
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Handle potential filename collisions
    counter = 1
    base_name, extension = os.path.splitext(filename)
    while os.path.exists(file_path):
        file_path = os.path.join(UPLOAD_DIR, f"{base_name}_{counter}{extension}")
        counter += 1
        
    with open(file_path, "wb") as f:
        f.write(content)
        
    skills = parse_cv_and_get_skills(content, filename)
    
    # Create a dummy candidate
    # In a real app, we'd extract email and name from CV content using AI/NLP
    candidate_name = os.path.basename(file_path).split('.')[0]
    db_candidate = Candidate(
        full_name=candidate_name,
        email=f"{candidate_name.lower().replace(' ', '_')}@example.com",
        mobile="0000000000",
        cv_file_path=file_path,
        skills=skills,
        assigned_recruiter_id=current_user_id
    )
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return {"filename": filename, "status": "success", "id": db_candidate.id}

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
        if file.content_type == "application/zip" or file.filename.endswith('.zip'):
            # Handle ZIP extraction
            try:
                content = await file.read()
                with zipfile.ZipFile(io.BytesIO(content)) as z:
                    for zip_info in z.infolist():
                        if zip_info.is_dir():
                            continue
                        
                        # Only process PDF files inside ZIP
                        if not zip_info.filename.lower().endswith('.pdf'):
                            continue
                        
                        # Skip files in __MACOSX or other hidden folders
                        if zip_info.filename.startswith('__MACOSX/') or os.path.basename(zip_info.filename).startswith('.'):
                            continue
                            
                        with z.open(zip_info) as zf:
                            pdf_content = zf.read()
                            res = await process_single_pdf(db, os.path.basename(zip_info.filename), pdf_content, current_user_id)
                            results.append(res)
            except Exception as e:
                results.append({"filename": file.filename, "status": "failed", "reason": f"Zip error: {str(e)}"})
        
        elif file.content_type == "application/pdf" or file.filename.endswith('.pdf'):
            # Handle individual PDF
            content = await file.read()
            res = await process_single_pdf(db, file.filename, content, current_user_id)
            results.append(res)
        
        else:
            results.append({"filename": file.filename, "status": "failed", "reason": "Invalid file type. Only PDF or ZIP allowed."})
            
    return results
