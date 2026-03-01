from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import csv
import io
from app.db.database import get_db
from app.models import Member
from app.core.security import get_current_member

router = APIRouter()


class MemberImport(BaseModel):
    phone: str
    name: str
    role: str = "MEMBER"
    contribution_tier: str = "regular"


@router.post("/import/members")
async def import_members(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Import members from CSV"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Read CSV
    content = await file.read()
    decoded = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))
    
    results = {"success": 0, "failed": 0, "errors": []}
    
    for row in reader:
        try:
            # Validate required fields
            if not row.get('phone') or not row.get('name'):
                results["failed"] += 1
                results["errors"].append(f"Missing phone or name: {row}")
                continue
            
            # Check if exists
            existing = db.query(Member).filter(
                Member.phone == row['phone'],
                Member.organization_id == current.organization_id
            ).first()
            
            if existing:
                results["failed"] += 1
                results["errors"].append(f"Phone already exists: {row['phone']}")
                continue
            
            # Create member
            member = Member(
                organization_id=current.organization_id,
                phone=row['phone'],
                name=row['name'],
                role=row.get('role', 'MEMBER'),
                contribution_tier=row.get('contribution_tier', 'regular')
            )
            db.add(member)
            results["success"] += 1
            
        except Exception as e:
            results["failed"] += 1
            results["errors"].append(f"Error: {str(e)}")
    
    db.commit()
    return results


@router.get("/export/template")
def download_template():
    """Download CSV template for member import"""
    return {
        "filename": "members_import_template.csv",
        "headers": ["phone", "name", "role", "contribution_tier"],
        "example": [
            {"phone": "254712345678", "name": "John Doe", "role": "MEMBER", "contribution_tier": "regular"},
            {"phone": "254723456789", "name": "Jane Smith", "role": "TREASURER", "contribution_tier": "gold"}
        ]
    }
