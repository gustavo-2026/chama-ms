from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from pydantic import BaseModel
from app.db.database import get_db
from app.models import Meeting, Attendance, Member

router = APIRouter()


# Schemas
class MeetingCreate(BaseModel):
    title: str
    description: str = None
    scheduled_at: datetime
    location: str = None


class MeetingResponse(BaseModel):
    id: str
    organization_id: str
    title: str
    description: str = None
    scheduled_at: datetime
    location: str = None
    status: str
    
    class Config:
        from_attributes = True


class AttendanceMark(BaseModel):
    member_id: str
    present: bool = False
    excused: bool = False
    notes: str = None


class AttendanceResponse(BaseModel):
    id: str
    meeting_id: str
    member_id: str
    present: bool
    excused: bool
    notes: str = None
    
    class Config:
        from_attributes = True


def get_current_member(db: Session = Depends(get_db)):
    member = db.query(Member).first()
    if not member:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return member


@router.post("/meetings", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
def create_meeting(
    meeting: MeetingCreate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Schedule a new meeting"""
    new_meeting = Meeting(
        organization_id=current.organization_id,
        title=meeting.title,
        description=meeting.description,
        scheduled_at=meeting.scheduled_at,
        location=meeting.location,
    )
    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)
    return new_meeting


@router.get("/meetings", response_model=List[MeetingResponse])
def list_meetings(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """List all meetings"""
    meetings = db.query(Meeting).filter(
        Meeting.organization_id == current.organization_id
    ).order_by(Meeting.scheduled_at.desc()).all()
    return meetings


@router.post("/meetings/{meeting_id}/attendance", status_code=status.HTTP_201_CREATED)
def mark_attendance(
    meeting_id: str,
    attendance: AttendanceMark,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Mark attendance for a member"""
    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id,
        Meeting.organization_id == current.organization_id
    ).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Verify member belongs to org
    member = db.query(Member).filter(
        Member.id == attendance.member_id,
        Member.organization_id == current.organization_id
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Check if already marked
    existing = db.query(Attendance).filter(
        Attendance.meeting_id == meeting_id,
        Attendance.member_id == attendance.member_id
    ).first()
    
    if existing:
        existing.present = attendance.present
        existing.excused = attendance.excused
        existing.notes = attendance.notes
    else:
        new_attendance = Attendance(
            meeting_id=meeting_id,
            member_id=attendance.member_id,
            present=attendance.present,
            excused=attendance.excused,
            notes=attendance.notes,
        )
        db.add(new_attendance)
    
    db.commit()
    return {"message": "Attendance marked"}


@router.get("/meetings/{meeting_id}/attendance")
def get_meeting_attendance(
    meeting_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Get attendance for a meeting"""
    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id,
        Meeting.organization_id == current.organization_id
    ).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    attendance = db.query(Attendance).filter(
        Attendance.meeting_id == meeting_id
    ).all()
    
    # Get member details
    member_ids = [a.member_id for a in attendance]
    members = db.query(Member).filter(Member.id.in_(member_ids)).all()
    member_map = {m.id: m.name for m in members}
    
    return [
        {
            "member_id": a.member_id,
            "member_name": member_map.get(a.member_id, "Unknown"),
            "present": a.present,
            "excused": a.excused,
            "notes": a.notes,
        }
        for a in attendance
    ]
