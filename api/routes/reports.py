from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from api.dependencies import get_db, check_permission
from db.models import Candidate, User
import pandas as pd
import os
import tempfile
import uuid

router = APIRouter()

@router.get("/candidates/export")
def export_candidates(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("view_candidates"))
):
    """
    Export all candidates to Excel file.
    """
    candidates = db.query(Candidate).all()
    
    data = []
    for c in candidates:
        data.append({
            "Candidate Id": c.id,
            "Candidate Name": c.full_name,
            "Email": c.email,
            "Mobile": c.mobile,
            "Skills": ", ".join(c.skills) if c.skills else "",
            "Experience": c.total_experience,
            "Location": c.current_location,
            "Applied Role": c.applied_role,
            "Source": c.source,
            "Status": c.status.value if c.status else "",
            "Assigned Recruiter": c.assigned_recruiter.name if c.assigned_recruiter else "",
            "Remarks": c.remarks
        })
        
    df = pd.DataFrame(data)
    
    # Create temp file
    temp_file = os.path.join(tempfile.gettempdir(), f"candidates_report_{uuid.uuid4().hex}.xlsx")
    df.to_excel(temp_file, index=False)
    
    return FileResponse(
        temp_file, 
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        filename="Candidates_Report.xlsx"
    )
