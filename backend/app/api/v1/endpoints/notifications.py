from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.db.database import get_db
from app.models import Notification, Member, NotificationType, NotificationChannel

router = APIRouter()


class NotificationCreate(BaseModel):
    member_id: str = None  # null for broadcast
    type: NotificationType = NotificationType.GENERAL
    title: str
    message: str
    channel: NotificationChannel = NotificationChannel.IN_APP


class NotificationResponse(BaseModel):
    id: str
    organization_id: str
    member_id: str = None
    type: NotificationType
    title: str
    message: str
    channel: NotificationChannel
    read: bool
    created_at: str
    
    class Config:
        from_attributes = True


def get_current_member(db: Session = Depends(get_db)):
    member = db.query(Member).first()
    if not member:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return member


@router.get("/", response_model=List[NotificationResponse])
def list_notifications(
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """List notifications for current member"""
    query = db.query(Notification).filter(
        Notification.organization_id == current.organization_id,
        (Notification.member_id == current.id) | (Notification.member_id == None)  # noqa
    )
    
    if unread_only:
        query = query.filter(Notification.read == False)
    
    notifications = query.order_by(Notification.created_at.desc()).limit(50).all()
    return notifications


@router.post("/", status_code=201)
def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Send a notification (Chair/Treasurer only)"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_notif = Notification(
        organization_id=current.organization_id,
        member_id=notification.member_id,
        type=notification.type,
        title=notification.title,
        message=notification.message,
        channel=notification.channel,
    )
    db.add(new_notif)
    db.commit()
    
    # TODO: Send SMS via Africa's Talking if channel is SMS
    
    return {"message": "Notification sent", "id": new_notif.id}


@router.patch("/{notification_id}/read")
def mark_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Mark notification as read"""
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.organization_id == current.organization_id
    ).first()
    
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notif.read = True
    db.commit()
    
    return {"message": "Marked as read"}


@router.patch("/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Mark all notifications as read"""
    db.query(Notification).filter(
        Notification.organization_id == current.organization_id,
        Notification.member_id == current.id,
        Notification.read == False
    ).update({"read": True})
    db.commit()
    
    return {"message": "All marked as read"}
