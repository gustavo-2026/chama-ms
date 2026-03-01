from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models import Organization, Member, MemberRole
from app.schemas.schemas import OrganizationCreate, OrganizationResponse, MemberResponse

router = APIRouter()


@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(
    org: OrganizationCreate,
    db: Session = Depends(get_db)
):
    """Create a new chama/organization"""
    # Check if slug exists
    existing = db.query(Organization).filter(Organization.slug == org.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subdomain already taken"
        )
    
    new_org = Organization(
        name=org.name,
        slug=org.slug,
        phone=org.phone,
        email=org.email,
        primary_color=org.primary_color,
    )
    db.add(new_org)
    db.commit()
    db.refresh(new_org)
    
    # Create first member as CHAIR
    first_member = Member(
        organization_id=new_org.id,
        phone=org.phone,
        name="Founder",
        role=MemberRole.CHAIR,
    )
    db.add(first_member)
    db.commit()
    
    return new_org


@router.get("/{org_id}", response_model=OrganizationResponse)
def get_organization(
    org_id: str,
    db: Session = Depends(get_db)
):
    """Get organization by ID"""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@router.get("/by-slug/{slug}", response_model=OrganizationResponse)
def get_organization_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """Get organization by slug"""
    org = db.query(Organization).filter(Organization.slug == slug).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org
