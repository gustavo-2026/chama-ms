from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.models import Member, Organization, SuperAdmin, PlatformSettings, Organization, Contribution, Loan
from app.core.security import get_current_member

router = APIRouter()

# Note: In production, use proper dependency injection for super admin auth


class PlatformStatsResponse(BaseModel):
    total_organizations: int
    total_members: int
    total_contributions: float
    total_loans: float
    recorded_at: datetime


# === SUPER ADMIN ===

def require_super_admin(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Require super admin privileges - placeholder"""
    # In production, check for super admin role/session
    # For now, any CHAIR can access these endpoints
    if current.role != "CHAIR":
        raise HTTPException(status_code=403, detail="Super admin access required")
    return current


@router.get("/admin/stats", response_model=PlatformStatsResponse)
def platform_stats(
    db: Session = Depends(get_db),
    current: Member = Depends(require_super_admin)
):
    """Get platform-wide statistics"""
    total_orgs = db.query(Organization).count()
    total_members = db.query(Member).count()
    
    contributions = db.query(Contribution).filter(Contribution.status == "COMPLETED").all()
    total_contributions = sum(float(c.amount) for c in contributions)
    
    loans = db.query(Loan).filter(Loan.status.in_(["ACTIVE", "PAID"])).all()
    total_loans = sum(float(l.amount) for l in loans)
    
    return {
        "total_organizations": total_orgs,
        "total_members": total_members,
        "total_contributions": total_contributions,
        "total_loans": total_loans,
        "recorded_at": datetime.utcnow()
    }


@router.get("/admin/organizations")
def all_organizations(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current: Member = Depends(require_super_admin)
):
    """List all organizations on platform"""
    orgs = db.query(Organization).offset(offset).limit(limit).all()
    
    result = []
    for org in orgs:
        member_count = db.query(Member).filter(Member.organization_id == org.id).count()
        result.append({
            "id": org.id,
            "name": org.name,
            "phone": org.phone,
            "email": org.email,
            "member_count": member_count,
            "created_at": org.created_at.isoformat() if org.created_at else None
        })
    
    return result


@router.get("/admin/organizations/{org_id}")
def organization_details(
    org_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(require_super_admin)
):
    """Get detailed organization info"""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    members = db.query(Member).filter(Member.organization_id == org_id).all()
    
    contributions = db.query(Contribution).filter(
        Contribution.organization_id == org_id,
        Contribution.status == "COMPLETED"
    ).all()
    
    loans = db.query(Loan).filter(Loan.organization_id == org_id).all()
    
    return {
        "organization": {
            "id": org.id,
            "name": org.name,
            "slug": org.slug,
            "phone": org.phone,
            "email": org.email,
            "created_at": org.created_at.isoformat() if org.created_at else None
        },
        "stats": {
            "total_members": len(members),
            "total_contributions": sum(float(c.amount) for c in contributions),
            "active_loans": len([l for l in loans if l.status == "ACTIVE"]),
            "total_loans_disbursed": sum(float(l.amount) for l in loans)
        },
        "members": [
            {"id": m.id, "name": m.name, "phone": m.phone, "role": m.role}
            for m in members[:10]  # Preview
        ]
    }


@router.patch("/admin/organizations/{org_id}/status")
def toggle_organization_status(
    org_id: str,
    active: bool,
    db: Session = Depends(get_db),
    current: Member = Depends(require_super_admin)
):
    """Activate or deactivate an organization"""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # In production, would add is_active field
    return {"message": f"Organization {org.name} status: {active}"}


@router.get("/admin/settings")
def platform_settings(
    db: Session = Depends(get_db),
    current: Member = Depends(require_super_admin)
):
    """Get platform settings"""
    settings = db.query(PlatformSettings).all()
    return {s.key: s.value for s in settings}


@router.post("/admin/settings")
def update_platform_setting(
    key: str,
    value: str,
    description: str = None,
    db: Session = Depends(get_db),
    current: Member = Depends(require_super_admin)
):
    """Update platform setting"""
    setting = db.query(PlatformSettings).filter(PlatformSettings.key == key).first()
    
    if setting:
        setting.value = value
        if description:
            setting.description = description
    else:
        setting = PlatformSettings(key=key, value=value, description=description)
        db.add(setting)
    
    db.commit()
    return {"message": "Setting updated"}


@router.get("/admin/audit")
def platform_audit(
    days: int = 30,
    limit: int = 100,
    db: Session = Depends(get_db),
    current: Member = Depends(require_super_admin)
):
    """Platform-wide audit log (simplified)"""
    # In production, would have a proper audit log table
    
    # Recent organizations
    orgs = db.query(Organization).order_by(Organization.created_at.desc()).limit(limit).all()
    
    # Recent members
    members = db.query(Member).order_by(Member.created_at.desc()).limit(limit).all()
    
    return {
        "recent_organizations": [
            {"id": o.id, "name": o.name, "created_at": o.created_at.isoformat()}
            for o in orgs[:20]
        ],
        "recent_members": [
            {"id": m.id, "name": m.name, "org_id": m.organization_id, "created_at": m.created_at.isoformat()}
            for m in members[:20]
        ]
    }
