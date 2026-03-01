from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.models import Member, PushToken, PushNotification, ScheduledReport
from app.core.security import get_current_member

router = APIRouter()


class PushTokenRegister(BaseModel):
    token: str
    device_type: str = "ios"
    device_name: str = None


class PushNotificationCreate(BaseModel):
    title: str
    body: str
    data: dict = None
    target: str = "all"  # all, member, role
    target_id: str = None
    schedule: str = None  # ISO datetime for scheduled


# === PUSH TOKEN MANAGEMENT ===

@router.post("/push/register")
def register_push_token(
    token_data: PushTokenRegister,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Register push token for current user"""
    # Check if token exists
    existing = db.query(PushToken).filter(
        PushToken.token == token_data.token
    ).first()
    
    if existing:
        # Update
        existing.member_id = current.id
        existing.is_active = True
        existing.last_used = datetime.utcnow()
    else:
        new_token = PushToken(
            member_id=current.id,
            organization_id=current.organization_id,
            token=token_data.token,
            device_type=token_data.device_type,
            device_name=token_data.device_name
        )
        db.add(new_token)
    
    db.commit()
    return {"message": "Push token registered"}


@router.delete("/push/unregister")
def unregister_push_token(
    token: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Unregister push token"""
    token_record = db.query(PushToken).filter(
        PushToken.token == token,
        PushToken.member_id == current.id
    ).first()
    
    if token_record:
        token_record.is_active = False
        db.commit()
    
    return {"message": "Push token unregistered"}


@router.get("/push/tokens")
def list_push_tokens(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """List my push tokens"""
    tokens = db.query(PushToken).filter(
        PushToken.member_id == current.id,
        PushToken.is_active == True
    ).all()
    
    return [
        {
            "id": t.id,
            "device_type": t.device_type,
            "device_name": t.device_name,
            "last_used": t.last_used.isoformat()
        }
        for t in tokens
    ]


# === PUSH NOTIFICATIONS ===

@router.post("/push/send")
def send_push_notification(
    notification: PushNotificationCreate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Send push notification (Chair/Treasurer only)"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get target tokens
    if notification.target == "all":
        tokens = db.query(PushToken).filter(
            PushToken.organization_id == current.organization_id,
            PushToken.is_active == True
        ).all()
    elif notification.target == "role":
        members = db.query(Member).filter(
            Member.organization_id == current.organization_id,
            Member.role == notification.target_id
        ).all()
        member_ids = [m.id for m in members]
        tokens = db.query(PushToken).filter(
            PushToken.member_id.in_(member_ids),
            PushToken.is_active == True
        ).all()
    else:
        tokens = db.query(PushToken).filter(
            PushToken.member_id == notification.target_id,
            PushToken.is_active == True
        ).all()
    
    # Create notification record
    scheduled_for = None
    if notification.schedule:
        scheduled_for = datetime.fromisoformat(notification.schedule)
    
    push_notif = PushNotification(
        organization_id=current.organization_id,
        title=notification.title,
        body=notification.body,
        data=notification.data,
        target=notification.target,
        target_id=notification.target_id,
        scheduled_for=scheduled_for
    )
    db.add(push_notif)
    
    if not scheduled_for:
        # Send immediately (in production, queue this)
        push_notif.sent = True
        push_notif.sent_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "Notification queued",
        "recipients": len(tokens),
        "scheduled": scheduled_for is not None
    }


@router.get("/push/history")
def push_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Get push notification history"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    notifications = db.query(PushNotification).filter(
        PushNotification.organization_id == current.organization_id
    ).order_by(PushNotification.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": n.id,
            "title": n.title,
            "body": n.body,
            "target": n.target,
            "sent": n.sent,
            "scheduled_for": n.scheduled_for.isoformat() if n.scheduled_for else None,
            "sent_at": n.sent_at.isoformat() if n.sent_at else None,
            "created_at": n.created_at.isoformat()
        }
        for n in notifications
    ]


@router.delete("/push/{notification_id}")
def delete_notification(
    notification_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Delete scheduled notification"""
    notification = db.query(PushNotification).filter(
        PushNotification.id == notification_id,
        PushNotification.organization_id == current.organization_id,
        PushNotification.sent == False
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found or already sent")
    
    db.delete(notification)
    db.commit()
    
    return {"message": "Notification deleted"}


# === NOTIFICATION PREFERENCES ===

@router.get("/preferences")
def get_notification_preferences(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Get notification preferences"""
    # In production, store in database
    return {
        "push_enabled": True,
        "sms_enabled": True,
        "email_enabled": True,
        "contribution_alerts": True,
        "loan_alerts": True,
        "meeting_reminders": True,
        "kudos_notifications": True
    }


@router.post("/preferences")
def update_notification_preferences(
    push_enabled: bool = True,
    sms_enabled: bool = True,
    email_enabled: bool = True,
    contribution_alerts: bool = True,
    loan_alerts: bool = True,
    meeting_reminders: bool = True,
    kudos_notifications: bool = True,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Update notification preferences"""
    # In production, store in database
    return {"message": "Preferences updated"}
