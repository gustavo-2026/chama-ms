from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime
from app.db.database import get_db
from app.models import Member, Announcement, AnnouncementRead
from app.core.security import get_current_member

router = APIRouter()


class AnnouncementCreate(BaseModel):
    title: str
    content: str
    priority: str = "normal"  # low, normal, high, urgent
    target_all: bool = True
    target_roles: str = None  # Comma-separated roles
    pinned: bool = False


class AnnouncementResponse(BaseModel):
    id: str
    organization_id: str
    author_id: str
    title: str
    content: str
    priority: str
    target_all: bool
    target_roles: str = None
    pinned: bool
    published: bool
    published_at: datetime = None
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/announcements", response_model=List[AnnouncementResponse])
def list_announcements(
    published_only: bool = True,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """List announcements"""
    query = db.query(Announcement).filter(
        Announcement.organization_id == current.organization_id
    )
    
    if published_only:
        query = query.filter(Announcement.published == True)
    
    return query.order_by(Announcement.pinned.desc(), Announcement.created_at.desc()).limit(50).all()


@router.post("/announcements", response_model=AnnouncementResponse, status_code=201)
def create_announcement(
    announcement: AnnouncementCreate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Create announcement (Chair/Treasurer only)"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_announcement = Announcement(
        organization_id=current.organization_id,
        author_id=current.id,
        title=announcement.title,
        content=announcement.content,
        priority=announcement.priority,
        target_all=announcement.target_all,
        target_roles=announcement.target_roles,
        pinned=announcement.pinned,
    )
    db.add(new_announcement)
    db.commit()
    db.refresh(new_announcement)
    return new_announcement


@router.patch("/announcements/{announcement_id}/publish")
def publish_announcement(
    announcement_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Publish announcement"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    announcement = db.query(Announcement).filter(
        Announcement.id == announcement_id,
        Announcement.organization_id == current.organization_id
    ).first()
    
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    announcement.published = True
    announcement.published_at = datetime.utcnow()
    db.commit()
    
    # TODO: Send notifications to members
    
    return {"message": "Announcement published"}


@router.patch("/announcements/{announcement_id}/unpublish")
def unpublish_announcement(
    announcement_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Unpublish announcement"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    announcement = db.query(Announcement).filter(
        Announcement.id == announcement_id,
        Announcement.organization_id == current.organization_id
    ).first()
    
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    announcement.published = False
    announcement.published_at = None
    db.commit()
    
    return {"message": "Announcement unpublished"}


@router.delete("/announcements/{announcement_id}")
def delete_announcement(
    announcement_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Delete announcement"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    announcement = db.query(Announcement).filter(
        Announcement.id == announcement_id,
        Announcement.organization_id == current.organization_id
    ).first()
    
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    db.delete(announcement)
    db.commit()
    
    return {"message": "Announcement deleted"}


@router.post("/announcements/{announcement_id}/read")
def mark_announcement_read(
    announcement_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Mark announcement as read"""
    announcement = db.query(Announcement).filter(
        Announcement.id == announcement_id,
        Announcement.organization_id == current.organization_id
    ).first()
    
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    # Check if already read
    existing = db.query(AnnouncementRead).filter(
        AnnouncementRead.announcement_id == announcement_id,
        AnnouncementRead.member_id == current.id
    ).first()
    
    if not existing:
        read = AnnouncementRead(
            announcement_id=announcement_id,
            member_id=current.id
        )
        db.add(read)
        db.commit()
    
    return {"message": "Marked as read"}
