from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models import Member, Organization
from app.schemas.schemas import MemberCreate, MemberUpdate, MemberResponse

router = APIRouter()


def get_current_member(db: Session = Depends(get_db)):
    """Placeholder - implement proper auth"""
    # For now, return first member or raise
    member = db.query(Member).first()
    if not member:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return member


@router.get("/", response_model=List[MemberResponse])
def list_members(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """List all members in the organization"""
    members = db.query(Member).filter(
        Member.organization_id == current.organization_id
    ).all()
    return members


@router.post("/", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(
    member: MemberCreate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Add a new member to the organization"""
    # Check if phone already exists
    existing = db.query(Member).filter(Member.phone == member.phone).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )
    
    new_member = Member(
        organization_id=current.organization_id,
        phone=member.phone,
        name=member.name,
        role=member.role,
        contribution_tier=member.contribution_tier,
        mpesa_linked=member.mpesa_linked,
        mpesa_phone=member.mpesa_phone,
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member


@router.get("/{member_id}", response_model=MemberResponse)
def get_member(
    member_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Get member by ID"""
    member = db.query(Member).filter(
        Member.id == member_id,
        Member.organization_id == current.organization_id
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


@router.patch("/{member_id}", response_model=MemberResponse)
def update_member(
    member_id: str,
    update: MemberUpdate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Update member details"""
    member = db.query(Member).filter(
        Member.id == member_id,
        Member.organization_id == current.organization_id
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(member, field, value)
    
    db.commit()
    db.refresh(member)
    return member


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(
    member_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Remove a member from the organization"""
    member = db.query(Member).filter(
        Member.id == member_id,
        Member.organization_id == current.organization_id
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    db.delete(member)
    db.commit()
    return None
