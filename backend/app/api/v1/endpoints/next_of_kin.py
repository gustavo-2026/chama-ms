from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.db.database import get_db
from app.models import Member, NextOfKin
from app.core.security import get_current_member

router = APIRouter()


class NextOfKinCreate(BaseModel):
    name: str
    relationship: str  # spouse, parent, sibling, child, other
    phone: str = None
    email: str = None
    id_number: str = None
    is_primary: bool = True


class NextOfKinResponse(BaseModel):
    id: str
    member_id: str
    name: str
    relationship: str
    phone: str = None
    email: str = None
    id_number: str = None
    is_primary: bool
    
    class Config:
        from_attributes = True


@router.get("/next-of-kin", response_model=List[NextOfKinResponse])
def list_next_of_kin(
    member_id: str = None,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """List next of kin for members"""
    query = db.query(NextOfKin)
    
    if member_id:
        # Check access
        member = db.query(Member).filter(
            Member.id == member_id,
            Member.organization_id == current.organization_id
        ).first()
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        query = query.filter(NextOfKin.member_id == member_id)
    else:
        # Only show for members user has access to
        query = query.join(Member).filter(Member.organization_id == current.organization_id)
    
    return query.all()


@router.post("/next-of-kin", response_model=NextOfKinResponse, status_code=201)
def create_next_of_kin(
    kin: NextOfKinCreate,
    member_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Add next of kin to a member"""
    # Verify member
    member = db.query(Member).filter(
        Member.id == member_id,
        Member.organization_id == current.organization_id
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # If this is primary, unset other primaries
    if kin.is_primary:
        db.query(NextOfKin).filter(
            NextOfKin.member_id == member_id,
            NextOfKin.is_primary == True
        ).update({"is_primary": False})
    
    new_kin = NextOfKin(
        member_id=member_id,
        name=kin.name,
        relationship=kin.relationship,
        phone=kin.phone,
        email=kin.email,
        id_number=kin.id_number,
        is_primary=kin.is_primary
    )
    db.add(new_kin)
    db.commit()
    db.refresh(new_kin)
    return new_kin


@router.get("/next-of-kin/{kin_id}", response_model=NextOfKinResponse)
def get_next_of_kin(
    kin_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Get next of kin by ID"""
    kin = db.query(NextOfKin).filter(NextOfKin.id == kin_id).first()
    if not kin:
        raise HTTPException(status_code=404, detail="Next of kin not found")
    
    # Verify member belongs to org
    member = db.query(Member).filter(
        Member.id == kin.member_id,
        Member.organization_id == current.organization_id
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Next of kin not found")
    
    return kin


@router.patch("/next-of-kin/{kin_id}", response_model=NextOfKinResponse)
def update_next_of_kin(
    kin_id: str,
    kin: NextOfKinCreate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Update next of kin"""
    existing = db.query(NextOfKin).filter(NextOfKin.id == kin_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Next of kin not found")
    
    # Verify member belongs to org
    member = db.query(Member).filter(
        Member.id == existing.member_id,
        Member.organization_id == current.organization_id
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Next of kin not found")
    
    # If setting as primary, unset others
    if kin.is_primary and not existing.is_primary:
        db.query(NextOfKin).filter(
            NextOfKin.member_id == existing.member_id,
            NextOfKin.is_primary == True
        ).update({"is_primary": False})
    
    for field, value in kin.model_dump().items():
        setattr(existing, field, value)
    
    db.commit()
    db.refresh(existing)
    return existing


@router.delete("/next-of-kin/{kin_id}")
def delete_next_of_kin(
    kin_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Delete next of kin"""
    kin = db.query(NextOfKin).filter(NextOfKin.id == kin_id).first()
    if not kin:
        raise HTTPException(status_code=404, detail="Next of kin not found")
    
    # Verify member belongs to org
    member = db.query(Member).filter(
        Member.id == kin.member_id,
        Member.organization_id == current.organization_id
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Next of kin not found")
    
    db.delete(kin)
    db.commit()
    return {"message": "Next of kin deleted"}
