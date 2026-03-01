from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import csv
import io
import json
from datetime import datetime
from app.db.database import get_db
from app.models import Member, Contribution, Loan, Organization
from app.core.security import get_current_member

router = APIRouter()


# === BULK IMPORT/EXPORT ===

class ImportResult(BaseModel):
    success: int
    failed: int
    errors: List[dict]


@router.post("/import/members-csv", response_model=ImportResult)
async def import_members_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Import members from CSV file"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    content = await file.read()
    decoded = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))
    
    result = ImportResult(success=0, failed=0, errors=[])
    
    for row_num, row in enumerate(reader, start=2):
        try:
            if not row.get('phone') or not row.get('name'):
                result.failed += 1
                result.errors.append({"row": row_num, "error": "Missing phone or name"})
                continue
            
            # Check duplicate
            existing = db.query(Member).filter(
                Member.phone == row['phone'],
                Member.organization_id == current.organization_id
            ).first()
            
            if existing:
                result.failed += 1
                result.errors.append({"row": row_num, "error": f"Phone exists: {row['phone']}"})
                continue
            
            member = Member(
                organization_id=current.organization_id,
                phone=row['phone'],
                name=row['name'],
                role=row.get('role', 'MEMBER'),
                contribution_tier=row.get('tier', 'regular')
            )
            db.add(member)
            result.success += 1
            
        except Exception as e:
            result.failed += 1
            result.errors.append({"row": row_num, "error": str(e)})
    
    db.commit()
    return result


@router.post("/import/members-json", response_model=ImportResult)
async def import_members_json(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Import members from JSON file"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    content = await file.read()
    data = json.loads(content)
    
    if not isinstance(data, list):
        raise HTTPException(status_code=400, detail="JSON must be an array of members")
    
    result = ImportResult(success=0, failed=0, errors=[])
    
    for row_num, row in enumerate(data, start=1):
        try:
            if not row.get('phone') or not row.get('name'):
                result.failed += 1
                result.errors.append({"row": row_num, "error": "Missing phone or name"})
                continue
            
            existing = db.query(Member).filter(
                Member.phone == row['phone'],
                Member.organization_id == current.organization_id
            ).first()
            
            if existing:
                result.failed += 1
                result.errors.append({"row": row_num, "error": f"Phone exists: {row['phone']}"})
                continue
            
            member = Member(
                organization_id=current.organization_id,
                phone=row['phone'],
                name=row['name'],
                role=row.get('role', 'MEMBER'),
                contribution_tier=row.get('tier', row.get('contribution_tier', 'regular'))
            )
            db.add(member)
            result.success += 1
            
        except Exception as e:
            result.failed += 1
            result.errors.append({"row": row_num, "error": str(e)})
    
    db.commit()
    return result


@router.post("/import/contributions")
async def import_contributions(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Import contributions from CSV"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    content = await file.read()
    decoded = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))
    
    result = {"success": 0, "failed": 0, "errors": []}
    
    # Get member phone to ID map
    members = db.query(Member).filter(Member.organization_id == current.organization_id).all()
    phone_to_id = {m.phone: m.id for m in members}
    
    for row_num, row in enumerate(reader, start=2):
        try:
            phone = row.get('phone')
            if not phone or phone not in phone_to_id:
                result["failed"] += 1
                result["errors"].append({"row": row_num, "error": f"Unknown phone: {phone}"})
                continue
            
            contribution = Contribution(
                organization_id=current.organization_id,
                member_id=phone_to_id[phone],
                amount=row.get('amount', '0'),
                method=row.get('method', 'CASH'),
                status=row.get('status', 'COMPLETED'),
                note=row.get('note', '')
            )
            db.add(contribution)
            result["success"] += 1
            
        except Exception as e:
            result["failed"] += 1
            result["errors"].append({"row": row_num, "error": str(e)})
    
    db.commit()
    return result


@router.get("/export/members")
def export_members(
    format: str = "json",
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Export all members"""
    members = db.query(Member).filter(Member.organization_id == current.organization_id).all()
    
    data = [
        {
            "phone": m.phone,
            "name": m.name,
            "role": m.role.value if hasattr(m.role, 'value') else m.role,
            "tier": m.contribution_tier,
            "created_at": m.created_at.isoformat() if m.created_at else None
        }
        for m in members
    ]
    
    if format == "csv":
        output = io.StringIO()
        if data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        return {"data": output.getvalue(), "content_type": "text/csv"}
    
    return {"data": data, "count": len(data)}


@router.get("/export/contributions")
def export_contributions(
    year: int = None,
    format: str = "json",
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Export contributions"""
    query = db.query(Contribution).filter(Contribution.organization_id == current.organization_id)
    
    if year:
        query = query.filter(db.func.extract('year', Contribution.created_at) == year)
    
    contributions = query.all()
    
    # Get member names
    member_ids = list(set(c.member_id for c in contributions))
    members = db.query(Member).filter(Member.id.in_(member_ids)).all()
    member_map = {m.id: m.name for m in members}
    
    data = [
        {
            "member_name": member_map.get(c.member_id, "Unknown"),
            "amount": c.amount,
            "method": c.method.value if hasattr(c.method, 'value') else c.method,
            "status": c.status.value if hasattr(c.status, 'value') else c.status,
            "note": c.note,
            "date": c.created_at.isoformat() if c.created_at else None
        }
        for c in contributions
    ]
    
    if format == "csv":
        output = io.StringIO()
        if data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        return {"data": output.getvalue(), "content_type": "text/csv"}
    
    return {"data": data, "count": len(data)}


@router.get("/export/loans")
def export_loans(
    status: str = None,
    format: str = "json",
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Export loans"""
    query = db.query(Loan).filter(Loan.organization_id == current.organization_id)
    
    if status:
        query = query.filter(Loan.status == status)
    
    loans = query.all()
    
    # Get member names
    member_ids = list(set(l.member_id for l in loans))
    members = db.query(Member).filter(Member.id.in_(member_ids)).all()
    member_map = {m.id: m.name for m in members}
    
    data = [
        {
            "member_name": member_map.get(l.member_id, "Unknown"),
            "amount": l.amount,
            "interest_rate": l.interest_rate,
            "status": l.status.value if hasattr(l.status, 'value') else l.status,
            "purpose": l.purpose,
            "created_at": l.created_at.isoformat() if l.created_at else None
        }
        for l in loans
    ]
    
    if format == "csv":
        output = io.StringIO()
        if data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        return {"data": output.getvalue(), "content_type": "text/csv"}
    
    return {"data": data, "count": len(data)}


@router.get("/import/template")
def download_import_template():
    """Download CSV template for member import"""
    return {
        "filename": "members_import.csv",
        "headers": ["phone", "name", "role", "tier"],
        "required": ["phone", "name"],
        "optional": ["role", "tier"],
        "examples": [
            {"phone": "254712345678", "name": "John Doe", "role": "MEMBER", "tier": "regular"},
            {"phone": "254723456789", "name": "Jane Smith", "role": "TREASURER", "tier": "gold"}
        ],
        "roles": ["MEMBER", "TREASURER", "CHAIR", "AGENT"],
        "tiers": ["regular", "silver", "gold", "platinum"]
    }
