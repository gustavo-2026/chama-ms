from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models import Member, AuditLog
from app.core.security import get_current_member

router = APIRouter()


class AuditLogResponse(BaseModel):
    id: str
    member_id: str
    action: str
    resource: str
    resource_id: str = None
    changes: dict = None
    details: str = None
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/audit-logs", response_model=List[AuditLogResponse])
def list_audit_logs(
    action: str = None,
    resource: str = None,
    member_id: str = None,
    days: int = 30,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """List audit logs (Chair/Treasurer only)"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    query = db.query(AuditLog).filter(
        AuditLog.organization_id == current.organization_id
    )
    
    if action:
        query = query.filter(AuditLog.action == action)
    if resource:
        query = query.filter(AuditLog.resource == resource)
    if member_id:
        query = query.filter(AuditLog.member_id == member_id)
    if days:
        since = datetime.utcnow() - timedelta(days=days)
        query = query.filter(AuditLog.created_at >= since)
    
    return query.order_by(desc(AuditLog.created_at)).offset(offset).limit(limit).all()


@router.get("/audit-logs/summary")
def audit_logs_summary(
    days: int = 30,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Get audit log summary"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    since = datetime.utcnow() - timedelta(days=days)
    
    logs = db.query(AuditLog).filter(
        AuditLog.organization_id == current.organization_id,
        AuditLog.created_at >= since
    ).all()
    
    # Count by action
    by_action = {}
    by_resource = {}
    
    for log in logs:
        by_action[log.action] = by_action.get(log.action, 0) + 1
        by_resource[log.resource] = by_resource.get(log.resource, 0) + 1
    
    # Recent activity
    recent = logs[:10]
    
    return {
        "period_days": days,
        "total_events": len(logs),
        "by_action": by_action,
        "by_resource": by_resource,
        "recent": [
            {
                "action": l.action,
                "resource": l.resource,
                "resource_id": l.resource_id,
                "created_at": l.created_at.isoformat()
            }
            for l in recent
        ]
    }


@router.get("/audit-logs/export")
def export_audit_logs(
    start_date: str = None,
    end_date: str = None,
    format: str = "json",
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Export audit logs"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    query = db.query(AuditLog).filter(
        AuditLog.organization_id == current.organization_id
    )
    
    if start_date:
        query = query.filter(AuditLog.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(AuditLog.created_at <= datetime.fromisoformat(end_date))
    
    logs = query.order_by(desc(AuditLog.created_at)).all()
    
    # Get member names
    member_ids = list(set(l.member_id for l in logs))
    members = db.query(Member).filter(Member.id.in_(member_ids)).all()
    member_map = {m.id: m.name for m in members}
    
    data = [
        {
            "timestamp": l.created_at.isoformat(),
            "user": member_map.get(l.member_id, "Unknown"),
            "action": l.action,
            "resource": l.resource,
            "resource_id": l.resource_id,
            "changes": l.changes,
            "details": l.details,
            "ip_address": l.ip_address
        }
        for l in logs
    ]
    
    if format == "csv":
        import io
        import csv
        output = io.StringIO()
        if data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        return {"data": output.getvalue(), "content_type": "text/csv"}
    
    return {"data": data, "count": len(data)}


# Helper function to log actions (call from other endpoints)
def log_audit(
    db: Session,
    organization_id: str,
    member_id: str,
    action: str,
    resource: str,
    resource_id: str = None,
    changes: dict = None,
    details: str = None,
    ip_address: str = None,
    user_agent: str = None
):
    """Log an audit event"""
    log = AuditLog(
        organization_id=organization_id,
        member_id=member_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        changes=changes,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.add(log)
    db.commit()
