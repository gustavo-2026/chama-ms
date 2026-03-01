from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models import Member
from app.models import LoginHistory, TwoFactorSetting
from app.core.security import get_current_member

router = APIRouter()


class TwoFactorEnableResponse(BaseModel):
    secret: str
    qr_code: str  # URL for QR code
    backup_codes: List[str]


@router.get("/2fa/status")
def get_2fa_status(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Get 2FA status"""
    setting = db.query(TwoFactorSetting).filter(
        TwoFactorSetting.member_id == current.id
    ).first()
    
    return {
        "enabled": setting.enabled if setting else False
    }


@router.post("/2fa/enable")
def enable_2fa(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Enable 2FA for current user"""
    # Generate secret
    import secrets
    secret = secrets.token_hex(20)
    
    # Generate backup codes
    backup_codes = [secrets.token_hex(4) for _ in range(8)]
    
    # Save
    setting = db.query(TwoFactorSetting).filter(
        TwoFactorSetting.member_id == current.id
    ).first()
    
    if setting:
        setting.enabled = True
        setting.secret = secret
        setting.backup_codes = ",".join(backup_codes)
    else:
        setting = TwoFactorSetting(
            member_id=current.id,
            enabled=True,
            secret=secret,
            backup_codes=",".join(backup_codes)
        )
        db.add(setting)
    
    db.commit()
    
    # Generate QR code URL (for authenticator apps)
    qr_url = f"otpauth://totp/Chama:{current.phone}?secret={secret}&issuer=Chama"
    
    return {
        "secret": secret,
        "qr_code": qr_url,
        "backup_codes": backup_codes,
        "message": "Save your backup codes securely!"
    }


@router.post("/2fa/disable")
def disable_2fa(
    code: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Disable 2FA"""
    setting = db.query(TwoFactorSetting).filter(
        TwoFactorSetting.member_id == current.id
    ).first()
    
    if not setting or not setting.enabled:
        raise HTTPException(status_code=400, detail="2FA not enabled")
    
    # Verify code (simplified - in production use proper TOTP validation)
    if code != setting.secret and code not in setting.backup_codes.split(","):
        raise HTTPException(status_code=400, detail="Invalid code")
    
    setting.enabled = False
    db.commit()
    
    return {"message": "2FA disabled"}


@router.get("/login-history")
def get_login_history(
    days: int = 30,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Get login history"""
    since = datetime.utcnow() - timedelta(days=days)
    
    history = db.query(LoginHistory).filter(
        LoginHistory.member_id == current.id,
        LoginHistory.created_at >= since
    ).order_by(LoginHistory.created_at.desc()).limit(50).all()
    
    return [
        {
            "ip_address": h.ip_address,
            "device_info": h.device_info,
            "location": h.location,
            "success": h.success,
            "created_at": h.created_at.isoformat()
        }
        for h in history
    ]


@router.get("/security/logins")
def get_all_login_history(
    days: int = 30,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Get all login history (Chair/Treasurer only)"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    since = datetime.utcnow() - timedelta(days=days)
    
    history = db.query(LoginHistory).filter(
        LoginHistory.created_at >= since
    ).order_by(LoginHistory.created_at.desc()).limit(100).all()
    
    # Get member names
    member_ids = list(set(h.member_id for h in history))
    members = db.query(Member).filter(Member.id.in_(member_ids)).all()
    member_map = {m.id: m.name for m in members}
    
    return [
        {
            "member_name": member_map.get(h.member_id, "Unknown"),
            "ip_address": h.ip_address,
            "device_info": h.device_info,
            "success": h.success,
            "created_at": h.created_at.isoformat()
        }
        for h in history
    ]
