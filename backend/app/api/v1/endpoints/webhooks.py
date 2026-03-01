from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.db.database import get_db
from app.models import Member
from app.core.security import get_current_member
import requests
import uuid

router = APIRouter()

# In-memory webhook store (use database in production)
webhooks = {}


class WebhookCreate(BaseModel):
    url: str
    events: List[str]  # contribution.created, loan.approved, etc.
    secret: Optional[str] = None


class WebhookResponse(BaseModel):
    id: str
    url: str
    events: List[str]
    active: bool


@router.get("/webhooks", response_model=List[WebhookResponse])
def list_webhooks(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """List webhooks (Chair/Treasurer only)"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    org_webhooks = [w for w in webhooks.values() if w["org_id"] == current.organization_id]
    return [
        WebhookResponse(
            id=w["id"],
            url=w["url"],
            events=w["events"],
            active=w["active"]
        )
        for w in org_webhooks
    ]


@router.post("/webhooks", response_model=WebhookResponse)
def create_webhook(
    webhook: WebhookCreate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Create a webhook (Chair/Treasurer only)"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Validate URL
    if not webhook.url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid URL")
    
    webhook_id = f"wh_{uuid.uuid4().hex[:12]}"
    
    webhooks[webhook_id] = {
        "id": webhook_id,
        "org_id": current.organization_id,
        "url": webhook.url,
        "events": webhook.events,
        "secret": webhook.secret,
        "active": True
    }
    
    return WebhookResponse(
        id=webhook_id,
        url=webhook.url,
        events=webhook.events,
        active=True
    )


@router.delete("/webhooks/{webhook_id}")
def delete_webhook(
    webhook_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Delete a webhook"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    webhook = webhooks.get(webhook_id)
    if not webhook or webhook["org_id"] != current.organization_id:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    del webhooks[webhook_id]
    return {"message": "Webhook deleted"}


# Trigger webhook function (call this when events happen)
def trigger_webhook(org_id: str, event: str, data: dict):
    """Trigger webhooks for an event"""
    import hmac
    import hashlib
    import json
    
    for webhook in webhooks.values():
        if webhook["org_id"] != org_id:
            continue
        
        if event not in webhook["events"]:
            continue
        
        if not webhook["active"]:
            continue
        
        # Prepare payload
        payload = {
            "event": event,
            "data": data
        }
        
        # Sign payload
        if webhook["secret"]:
            signature = hmac.new(
                webhook["secret"].encode(),
                json.dumps(payload).encode(),
                hashlib.sha256
            ).hexdigest()
            headers = {
                "Content-Type": "application/json",
                "X-Chama-Signature": signature,
                "X-Chama-Event": event
            }
        else:
            headers = {"Content-Type": "application/json"}
        
        # Send webhook (fire and forget)
        try:
            requests.post(webhook["url"], json=payload, headers=headers, timeout=5)
        except Exception:
            pass  # Log error in production


# Events to support:
# - contribution.created
# - contribution.updated
# - loan.created
# - loan.approved
# - loan.rejected
# - loan.repaid
# - member.added
# - member.removed
# - dividend.disbursed
# - proposal.passed
# - proposal.rejected
