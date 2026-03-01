from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.models import Member, Organization
from app.core.security import get_current_member

router = APIRouter()


class FederationCreate(BaseModel):
    name: str
    description: str = None
    region: str = None
    allow_inter_lending: bool = True
    shared_interest_rate: float = 8.0


class FederationResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: str = None
    region: str = None
    allow_inter_lending: bool
    shared_interest_rate: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# === FEDERATION MANAGEMENT ===

@router.get("/federations", response_model=List[FederationResponse])
def list_federations(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """List all federations"""
    return db.query(Federation).filter(Federation.status == "ACTIVE").all()


@router.get("/federations/{federation_id}", response_model=FederationResponse)
def get_federation(
    federation_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Get federation details"""
    federation = db.query(Federation).filter(Federation.id == federation_id).first()
    if not federation:
        raise HTTPException(status_code=404, detail="Federation not found")
    return federation


@router.post("/federations", response_model=FederationResponse)
def create_federation(
    federation: FederationCreate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Create a new federation"""
    # Only super admins or platform can create federations
    # For now, allow any Chair to create
    
    import secrets
    slug = f"{federation.name.lower().replace(' ', '-')}-{secrets.token_hex(4)}"
    
    new_federation = Federation(
        name=federation.name,
        slug=slug,
        description=federation.description,
        region=federation.region,
        allow_inter_lending=federation.allow_inter_lending,
        shared_interest_rate=str(federation.shared_interest_rate)
    )
    db.add(new_federation)
    db.commit()
    db.refresh(new_federation)
    return new_federation


@router.post("/federations/{federation_id}/join")
def join_federation(
    federation_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Join a federation"""
    federation = db.query(Federation).filter(Federation.id == federation_id).first()
    if not federation:
        raise HTTPException(status_code=404, detail="Federation not found")
    
    # Check if already a member
    existing = db.query(FederationMember).filter(
        FederationMember.federation_id == federation_id,
        FederationMember.organization_id == current.organization_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already a member")
    
    member = FederationMember(
        federation_id=federation_id,
        organization_id=current.organization_id,
        role="MEMBER"
    )
    db.add(member)
    db.commit()
    
    return {"message": "Joined federation"}


@router.get("/federations/{federation_id}/members")
def federation_members(
    federation_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """List members of a federation"""
    members = db.query(FederationMember).filter(
        FederationMember.federation_id == federation_id,
        FederationMember.is_active == True
    ).all()
    
    # Get org names
    org_ids = [m.organization_id for m in members]
    orgs = db.query(Organization).filter(Organization.id.in_(org_ids)).all()
    org_map = {o.id: o.name for o in orgs}
    
    return [
        {
            "organization_id": m.organization_id,
            "organization_name": org_map.get(m.organization_id, "Unknown"),
            "role": m.role,
            "joined_at": m.joined_at.isoformat()
        }
        for m in members
    ]


@router.get("/federations/{federation_id}/treasury")
def federation_treasury(
    federation_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Get federation treasury"""
    treasury = db.query(FederationTreasury).filter(
        FederationTreasury.federation_id == federation_id
    ).first()
    
    if not treasury:
        # Create default treasury
        treasury = FederationTreasury(
            federation_id=federation_id,
            total_shares="0",
            total_value="0",
            interest_earned="0"
        )
        db.add(treasury)
        db.commit()
        db.refresh(treasury)
    
    return {
        "federation_id": federation_id,
        "total_shares": treasury.total_shares,
        "total_value": float(treasury.total_value),
        "interest_earned": float(treasury.interest_earned)
    }


@router.get("/my-federations", response_model=List[FederationResponse])
def my_federations(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Get federations my organization belongs to"""
    fed_members = db.query(FederationMember).filter(
        FederationMember.organization_id == current.organization_id,
        FederationMember.is_active == True
    ).all()
    
    fed_ids = [fm.federation_id for fm in fed_members]
    federations = db.query(Federation).filter(Federation.id.in_(fed_ids)).all()
    
    return federations
