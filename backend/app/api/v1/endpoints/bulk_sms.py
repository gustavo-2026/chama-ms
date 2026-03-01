from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.models import Member, Meeting, Attendance
from app.core.security import get_current_member

router = APIRouter()


class BulkSMSCreate(BaseModel):
    message: str
    recipients: List[str] = None  # Phone numbers, if None send to all members
    roles: List[str] = None  # Filter by roles: MEMBER, TREASURER, etc.


class BulkSMSResponse(BaseModel):
    id: str
    message: str
    total_recipients: int
    status: str
    created_at: datetime


# === BULK SMS ===

@router.post("/sms/send", response_model=BulkSMSResponse)
def send_bulk_sms(
    sms: BulkSMSCreate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Send bulk SMS (Chair/Treasurer only)"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get recipients
    if sms.recipients:
        recipients = sms.recipients
    elif sms.roles:
        members = db.query(Member).filter(
            Member.organization_id == current.organization_id,
            Member.role.in_(sms.roles)
        ).all()
        recipients = [m.phone for m in members]
    else:
        # All members
        members = db.query(Member).filter(
            Member.organization_id == current.organization_id
        ).all()
        recipients = [m.phone for m in members]
    
    # In production, send via Africa's Talking or similar
    # For now, return success
    
    return {
        "id": f"sms_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "message": sms.message,
        "total_recipients": len(recipients),
        "status": "queued",
        "created_at": datetime.utcnow()
    }


@router.get("/sms/history")
def sms_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Get SMS sending history"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # In production, query from SMS provider
    # For now, return sample
    return {
        "messages": [],
        "total_sent": 0
    }


@router.get("/sms/balance")
def check_sms_balance(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Check SMS credit balance"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # In production, query Africa's Talking API
    return {
        "balance": 1000,  # Placeholder
        "currency": "KES"
    }


@router.get("/sms/templates")
def list_sms_templates(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """List pre-built SMS templates"""
    return [
        {
            "id": "meeting_reminder",
            "name": "Meeting Reminder",
            "template": "Reminder: {{chama}} meeting on {{date}} at {{location}}. Please confirm attendance.",
            "variables": ["chama", "date", "location"]
        },
        {
            "id": "contribution_reminder",
            "name": "Contribution Reminder",
            "template": "Hello {{name}}, this is a reminder that your contribution of KES {{amount}} is due. Please pay via M-Pesa to {{shortcode}}.",
            "variables": ["name", "amount", "shortcode"]
        },
        {
            "id": "loan_due",
            "name": "Loan Due Reminder",
            "template": "Hello {{name}}, your loan repayment of KES {{amount}} is due on {{date}}. Please pay to avoid penalties.",
            "variables": ["name", "amount", "date"]
        },
        {
            "id": "welcome",
            "name": "Welcome Message",
            "template": "Welcome to {{chama}}! Your member number is {{member_id}}. Contact {{contact}} for any questions.",
            "variables": ["chama", "member_id", "contact"]
        },
        {
            "id": "general",
            "name": "General Announcement",
            "template": "{{message}}",
            "variables": ["message"]
        }
    ]


@router.post("/sms/send-template")
def send_sms_template(
    template_id: str,
    variables: dict,
    roles: List[str] = None,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Send SMS using a template"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    templates = {
        "meeting_reminder": "Reminder: chama meeting on {date} at {location}. Please confirm attendance.",
        "contribution_reminder": "Hello {name}, this is a reminder that your contribution of KES {amount} is due.",
        "loan_due": "Hello {name}, your loan repayment of KES {amount} is due on {date}.",
        "welcome": "Welcome to {chama}! Your member number is {member_id}.",
    }
    
    if template_id not in templates:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Build message
    try:
        message = templates[template_id].format(**variables)
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing variable: {e}")
    
    # Get recipients
    if roles:
        members = db.query(Member).filter(
            Member.organization_id == current.organization_id,
            Member.role.in_(roles)
        ).all()
    else:
        members = db.query(Member).filter(
            Member.organization_id == current.organization_id
        ).all()
    
    # In production, send via Africa's Talking
    return {
        "message": message,
        "recipients": len(members),
        "status": "queued"
    }


@router.get("/sms/opt-outs")
def get_opt_outs(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Get list of members who opted out of SMS"""
    # In production, track opt-outs
    return {
        "opt_outs": [],
        "total": 0
    }


@router.post("/sms/opt-out")
def opt_out_sms(
    phone: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Opt out from SMS notifications"""
    # In production, record opt-out
    return {"message": "Opted out of SMS notifications"}


@router.post("/sms/opt-in")
def opt_in_sms(
    phone: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Opt in to SMS notifications"""
    # In production, remove opt-out
    return {"message": "Opted in to SMS notifications"}
