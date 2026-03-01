from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import gzip
import base64
from app.db.database import get_db
from app.models import Member, Organization, Contribution, Loan, Proposal
from app.core.security import get_current_member

router = APIRouter()


class BackupResponse(BaseModel):
    organization_id: str
    created_at: datetime
    version: str
    tables: List[str]


@router.get("/backup", response_model=BackupResponse)
def create_backup(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Create a full backup of organization data"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    org_id = current.organization_id
    
    # Backup all tables
    data = {}
    
    # Organizations
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if org:
        data["organization"] = {
            "id": org.id,
            "name": org.name,
            "slug": org.slug,
            "phone": org.phone,
            "email": org.email,
            "created_at": org.created_at.isoformat() if org.created_at else None
        }
    
    # Members
    members = db.query(Member).filter(Member.organization_id == org_id).all()
    data["members"] = [
        {
            "id": m.id,
            "phone": m.phone,
            "name": m.name,
            "role": m.role.value if hasattr(m.role, 'value') else m.role,
            "contribution_tier": m.contribution_tier,
            "created_at": m.created_at.isoformat() if m.created_at else None
        }
        for m in members
    ]
    
    # Contributions
    contributions = db.query(Contribution).filter(Contribution.organization_id == org_id).all()
    data["contributions"] = [
        {
            "id": c.id,
            "member_id": c.member_id,
            "amount": c.amount,
            "method": c.method.value if hasattr(c.method, 'value') else c.method,
            "status": c.status.value if hasattr(c.status, 'value') else c.status,
            "note": c.note,
            "created_at": c.created_at.isoformat() if c.created_at else None
        }
        for c in contributions
    ]
    
    # Loans
    loans = db.query(Loan).filter(Loan.organization_id == org_id).all()
    data["loans"] = [
        {
            "id": l.id,
            "member_id": l.member_id,
            "amount": l.amount,
            "interest_rate": l.interest_rate,
            "status": l.status.value if hasattr(l.status, 'value') else l.status,
            "purpose": l.purpose,
            "created_at": l.created_at.isoformat() if l.created_at else None
        }
        for l in loans
    ]
    
    # Proposals
    proposals = db.query(Proposal).filter(Proposal.organization_id == org_id).all()
    data["proposals"] = [
        {
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "proposal_type": p.proposal_type,
            "status": p.status.value if hasattr(p.status, 'value') else p.status,
            "created_at": p.created_at.isoformat() if p.created_at else None
        }
        for p in proposals
    ]
    
    # Compress
    json_data = json.dumps(data)
    compressed = gzip.compress(json_data.encode('utf-8'))
    encoded = base64.b64encode(compressed).decode('utf-8')
    
    return {
        "organization_id": org_id,
        "created_at": datetime.utcnow().isoformat(),
        "version": "1.0",
        "tables": list(data.keys()),
        "record_counts": {
            "members": len(data.get("members", [])),
            "contributions": len(data.get("contributions", [])),
            "loans": len(data.get("loans", [])),
            "proposals": len(data.get("proposals", []))
        },
        "backup_data": encoded
    }


@router.get("/backup/download")
def download_backup(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Download backup as JSON file"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    org_id = current.organization_id
    
    # Get all data
    members = db.query(Member).filter(Member.organization_id == org_id).all()
    contributions = db.query(Contribution).filter(Contribution.organization_id == org_id).all()
    loans = db.query(Loan).filter(Loan.organization_id == org_id).all()
    
    data = {
        "exported_at": datetime.utcnow().isoformat(),
        "organization_id": org_id,
        "members": [{"phone": m.phone, "name": m.name, "role": m.role} for m in members],
        "contributions": [{"member_id": c.member_id, "amount": c.amount, "date": c.created_at.isoformat()} for c in contributions],
        "loans": [{"member_id": l.member_id, "amount": l.amount, "status": l.status} for l in loans]
    }
    
    return {
        "filename": f"chama_backup_{org_id}_{datetime.utcnow().strftime('%Y%m%d')}.json",
        "content": json.dumps(data, indent=2),
        "content_type": "application/json"
    }


@router.post("/restore")
def restore_backup(
    backup_data: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Restore from backup (Chair only)"""
    if current.role != "CHAIR":
        raise HTTPException(status_code=403, detail="Only CHAIR can restore")
    
    try:
        # Decode
        decoded = base64.b64decode(backup_data)
        decompressed = gzip.decompress(decoded)
        data = json.loads(decompressed)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid backup format: {str(e)}")
    
    # Verify organization
    if data.get("organization_id") != current.organization_id:
        raise HTTPException(status_code=403, detail="Backup doesn't match your organization")
    
    restored = {"members": 0, "contributions": 0, "loans": 0}
    
    # Restore members (skip existing)
    for m in data.get("members", []):
        existing = db.query(Member).filter(
            Member.phone == m["phone"],
            Member.organization_id == current.organization_id
        ).first()
        
        if not existing:
            member = Member(
                organization_id=current.organization_id,
                phone=m["phone"],
                name=m["name"],
                role=m.get("role", "MEMBER")
            )
            db.add(member)
            restored["members"] += 1
    
    db.commit()
    
    return {
        "message": "Restore complete",
        "restored": restored,
        "note": "Only new records were added. Existing data was preserved."
    }


@router.get("/restore/validate")
def validate_backup(
    backup_data: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Validate backup data without restoring"""
    try:
        decoded = base64.b64decode(backup_data)
        decompressed = gzip.decompress(decoded)
        data = json.loads(decompressed)
        
        return {
            "valid": True,
            "organization_id": data.get("organization_id"),
            "version": data.get("version"),
            "tables": list(data.keys()),
            "record_counts": {
                "members": len(data.get("members", [])),
                "contributions": len(data.get("contributions", [])),
                "loans": len(data.get("loans", []))
            }
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }
