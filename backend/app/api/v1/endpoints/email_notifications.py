from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.models import Member, Meeting, Attendance, Organization, Contribution, Loan
from app.core.security import get_current_member
router = APIRouter()
class EmailNotificationCreate(BaseModel):
    subject: str
    body: str
    recipients: List[str]  # Emails
    cc: List[str] = None
    template: str = None  # Use pre-built template
# === EMAIL NOTIFICATIONS ===
@router.post("/email/send")
def send_email(
    email: EmailNotificationCreate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Send email notification (Chair/Treasurer only)"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # In production, integrate with email service (SendGrid, SES, etc.)
    # For now, log and return success
    
    org = db.query(Organization).filter(Organization.id == current.organization_id).first()
    
    return {
        "message": "Email queued for sending",
        "recipients": len(email.recipients),
        "subject": email.subject,
        "from": f"Chama <noreply@{org.slug}.chama.app>" if org else "Chama <noreply@chama.app>"
    }
@router.post("/email/alert")
def send_transaction_alert(
    alert_type: str,  # contribution, loan, repayment
    recipient_phone: str = None,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Send transaction alert email"""
    # In production, trigger based on events
    
    return {
        "message": f"{alert_type} alert sent",
        "recipient": recipient_phone
    }
@router.get("/email/templates")
def list_email_templates(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """List available email templates"""
    return [
        {
            "id": "welcome",
            "name": "Welcome Email",
            "subject": "Welcome to {{chama_name}}",
            "description": "Sent when member joins"
        },
        {
            "id": "contribution_received",
            "name": "Contribution Received",
            "subject": "Contribution Received - {{amount}}",
            "description": "When contribution is recorded"
        },
        {
            "id": "loan_approved",
            "name": "Loan Approved",
            "subject": "Your Loan has been Approved",
            "description": "When loan is approved"
        },
        {
            "id": "loan_due",
            "name": "Loan Due Reminder",
            "subject": "Loan Repayment Due",
            "description": "Reminder before loan due date"
        },
        {
            "id": "meeting_reminder",
            "name": "Meeting Reminder",
            "subject": "Meeting Reminder - {{date}}",
            "description": "Before scheduled meeting"
        },
        {
            "id": "monthly_statement",
            "name": "Monthly Statement",
            "subject": "Your Monthly Statement - {{month}}",
            "description": "Monthly contribution summary"
        }
    ]
# === SCHEDULED REPORTS ===
@router.get("/scheduled-reports")
def list_scheduled_reports(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """List scheduled reports"""
    
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    reports = db.query(ScheduledReport).filter(
        ScheduledReport.organization_id == current.organization_id
    ).all()
    
    return [
        {
            "id": r.id,
            "name": r.name,
            "report_type": r.report_type,
            "frequency": r.frequency,
            "recipients": r.recipients,
            "is_active": r.is_active,
            "last_sent": r.last_sent.isoformat() if r.last_sent else None,
            "next_send": r.next_send.isoformat() if r.next_send else None
        }
        for r in reports
    ]
@router.post("/scheduled-reports")
def create_scheduled_report(
    name: str,
    report_type: str,
    frequency: str,  # daily, weekly, monthly
    recipients: str,  # comma-separated emails
    day_of_week: str = None,  # For weekly: monday, tuesday, etc.
    day_of_month: int = None,  # For monthly: 1-28
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Create scheduled report"""
    
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Calculate next send time
    now = datetime.utcnow()
    next_send = now
    
    if frequency == "daily":
        from datetime import timedelta
        next_send = now + timedelta(days=1)
    elif frequency == "weekly":
        # Simple: next week same time
        from datetime import timedelta
        next_send = now + timedelta(days=7)
    elif frequency == "monthly":
        # Next month same day
        if now.month == 12:
            next_send = now.replace(year=now.year+1, month=1)
        else:
            next_send = now.replace(month=now.month+1)
    
    report = ScheduledReport(
        organization_id=current.organization_id,
        name=name,
        report_type=report_type,
        frequency=frequency,
        day_of_week=day_of_week,
        day_of_month=str(day_of_month) if day_of_month else None,
        recipients=recipients,
        next_send=next_send
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return {
        "id": report.id,
        "name": report.name,
        "next_send": report.next_send.isoformat()
    }
@router.patch("/scheduled-reports/{report_id}/toggle")
def toggle_scheduled_report(
    report_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Enable/disable scheduled report"""
    
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    report = db.query(ScheduledReport).filter(
        ScheduledReport.id == report_id,
        ScheduledReport.organization_id == current.organization_id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report.is_active = not report.is_active
    db.commit()
    
    return {"message": f"Report {'enabled' if report.is_active else 'disabled'}"}
@router.delete("/scheduled-reports/{report_id}")
def delete_scheduled_report(
    report_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Delete scheduled report"""
    
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    report = db.query(ScheduledReport).filter(
        ScheduledReport.id == report_id,
        ScheduledReport.organization_id == current.organization_id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    db.delete(report)
    db.commit()
    
    return {"message": "Scheduled report deleted"}
@router.post("/scheduled-reports/{report_id}/send-now")
def send_report_now(
    report_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Send scheduled report immediately"""
    
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    report = db.query(ScheduledReport).filter(
        ScheduledReport.id == report_id,
        ScheduledReport.organization_id == current.organization_id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # In production, generate and send report
    report.last_sent = datetime.utcnow()
    db.commit()
    
    return {
        "message": "Report sent",
        "recipients": report.recipients.split(",")
    }
