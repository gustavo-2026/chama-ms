from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models import Member, MeetingNotice, Meeting
from app.core.security import get_current_member

router = APIRouter()


class MeetingNoticeCreate(BaseModel):
    meeting_id: str = None
    title: str
    message: str
    meeting_title: str = None
    meeting_date: datetime = None
    location: str = None
    reminder_before: int = 60  # Minutes


class MeetingNoticeResponse(BaseModel):
    id: str
    organization_id: str
    meeting_id: str = None
    author_id: str
    title: str
    message: str
    meeting_title: str = None
    meeting_date: datetime = None
    location: str = None
    reminder_before: int
    sent: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/meeting-notices", response_model=List[MeetingNoticeResponse])
def list_meeting_notices(
    upcoming: bool = False,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """List meeting notices"""
    query = db.query(MeetingNotice).filter(
        MeetingNotice.organization_id == current.organization_id
    )
    
    if upcoming:
        # Get notices for upcoming meetings
        query = query.filter(
            MeetingNotice.meeting_date > datetime.utcnow(),
            MeetingNotice.sent == False
        )
    
    return query.order_by(MeetingNotice.meeting_date.asc()).all()


@router.post("/meeting-notices", response_model=MeetingNoticeResponse, status_code=201)
def create_meeting_notice(
    notice: MeetingNoticeCreate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Create meeting notice (Chair/Treasurer only)"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_notice = MeetingNotice(
        organization_id=current.organization_id,
        meeting_id=notice.meeting_id,
        author_id=current.id,
        title=notice.title,
        message=notice.message,
        meeting_title=notice.meeting_title,
        meeting_date=notice.meeting_date,
        location=notice.location,
        reminder_before=notice.reminder_before,
    )
    db.add(new_notice)
    db.commit()
    db.refresh(new_notice)
    return new_notice


@router.post("/meeting-notices/{notice_id}/send")
def send_meeting_notice(
    notice_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Send meeting notice to members"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    notice = db.query(MeetingNotice).filter(
        MeetingNotice.id == notice_id,
        MeetingNotice.organization_id == current.organization_id
    ).first()
    
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")
    
    if notice.sent:
        raise HTTPException(status_code=400, detail="Notice already sent")
    
    # TODO: Actually send SMS/notification to all members
    
    notice.sent = True
    notice.sent_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Meeting notice sent"}


@router.delete("/meeting-notices/{notice_id}")
def delete_meeting_notice(
    notice_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Delete meeting notice"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    notice = db.query(MeetingNotice).filter(
        MeetingNotice.id == notice_id,
        MeetingNotice.organization_id == current.organization_id
    ).first()
    
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")
    
    db.delete(notice)
    db.commit()
    
    return {"message": "Meeting notice deleted"}
