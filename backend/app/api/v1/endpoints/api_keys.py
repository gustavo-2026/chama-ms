from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import hashlib
import secrets
from app.db.database import get_db
from app.models import Member, APIKey, IPWhitelist

from app.core.security import get_current_member

router = APIRouter()


def hash_api_key(key: str) -> str:
    """Hash an API key using SHA256"""
    return hashlib.sha256(key.encode()).hexdigest()


def generate_api_key() -> tuple[str, str]:
    """Generate a new API key. Returns (plain_key, hashed)"""
    plain = f"chama_{secrets.token_hex(24)}"
    return plain, hash_api_key(plain)


# ============ API KEYS ============

class APIKeyCreate(BaseModel):
    name: str
    permissions: str = "read"
    expires_days: int = 365


class APIKeyResponse(BaseModel):
    id: str
    name: str
    prefix: str
    permissions: str
    expires_at: datetime = None
    last_used: datetime = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/api-keys", response_model=List[APIKeyResponse])
def list_api_keys(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """List API keys (Chair/Treasurer only)"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    keys = db.query(APIKey).filter(
        APIKey.organization_id == current.organization_id
    ).order_by(APIKey.created_at.desc()).all()
    
    return keys


@router.post("/api-keys", response_model=dict)
def create_api_key(
    key_data: APIKeyCreate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Create a new API key (Chair/Treasurer only)"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    plain_key, hashed = generate_api_key()
    
    expires_at = None
    if key_data.expires_days:
        expires_at = datetime.utcnow() + timedelta(days=key_data.expires_days)
    
    api_key = APIKey(
        organization_id=current.organization_id,
        name=key_data.name,
        key_hash=hashed,
        prefix=plain_key[:12],
        permissions=key_data.permissions,
        expires_at=expires_at
    )
    db.add(api_key)
    db.commit()
    
    return {
        "id": api_key.id,
        "name": api_key.name,
        "key": plain_key,  # Only returned ONCE
        "prefix": api_key.prefix,
        "permissions": api_key.permissions,
        "expires_at": expires_at.isoformat() if expires_at else None,
        "message": "Save this key securely - it cannot be retrieved again!"
    }


@router.delete("/api-keys/{key_id}")
def revoke_api_key(
    key_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Revoke an API key"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.organization_id == current.organization_id
    ).first()
    
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    key.is_active = False
    db.commit()
    
    return {"message": "API key revoked"}


@router.post("/api-keys/verify")
def verify_api_key(
    key: str,
    db: Session = Depends(get_db)
):
    """Verify an API key (for service-to-service auth)"""
    key_hash = hash_api_key(key)
    
    api_key = db.query(APIKey).filter(
        APIKey.key_hash == key_hash,
        APIKey.is_active == True
    ).first()
    
    if not api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Check expiration
    if api_key.expires_at and api_key.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="API key expired")
    
    # Update last used
    api_key.last_used = datetime.utcnow()
    db.commit()
    
    return {
        "valid": True,
        "organization_id": api_key.organization_id,
        "permissions": api_key.permissions,
        "name": api_key.name
    }


# ============ IP WHITELISTING ============

class IPWhitelistCreate(BaseModel):
    ip_address: str
    description: str = None


class IPWhitelistResponse(BaseModel):
    id: str
    ip_address: str
    description: str = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/ip-whitelist", response_model=List[IPWhitelistResponse])
def list_ip_whitelist(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """List IP whitelist (Chair/Treasurer only)"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    ips = db.query(IPWhitelist).filter(
        IPWhitelist.organization_id == current.organization_id
    ).order_by(IPWhitelist.created_at.desc()).all()
    
    return ips


@router.post("/ip-whitelist", response_model=IPWhitelistResponse)
def add_ip_whitelist(
    ip_data: IPWhitelistCreate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Add IP to whitelist (Chair/Treasurer only)"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Validate IP format (basic)
    import ipaddress
    try:
        ipaddress.ip_address(ip_data.ip_address)
    except ValueError:
        try:
            ipaddress.ip_network(ip_data.ip_address, strict=False)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid IP address or CIDR")
    
    # Check exists
    existing = db.query(IPWhitelist).filter(
        IPWhitelist.organization_id == current.organization_id,
        IPWhitelist.ip_address == ip_data.ip_address
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="IP already in whitelist")
    
    ip = IPWhitelist(
        organization_id=current.organization_id,
        ip_address=ip_data.ip_address,
        description=ip_data.description
    )
    db.add(ip)
    db.commit()
    db.refresh(ip)
    
    return ip


@router.delete("/ip-whitelist/{ip_id}")
def remove_ip_whitelist(
    ip_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Remove IP from whitelist"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    ip = db.query(IPWhitelist).filter(
        IPWhitelist.id == ip_id,
        IPWhitelist.organization_id == current.organization_id
    ).first()
    
    if not ip:
        raise HTTPException(status_code=404, detail="IP not found")
    
    db.delete(ip)
    db.commit()
    
    return {"message": "IP removed from whitelist"}


@router.patch("/ip-whitelist/{ip_id}/toggle")
def toggle_ip_whitelist(
    ip_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Enable/disable IP in whitelist"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    ip = db.query(IPWhitelist).filter(
        IPWhitelist.id == ip_id,
        IPWhitelist.organization_id == current.organization_id
    ).first()
    
    if not ip:
        raise HTTPException(status_code=404, detail="IP not found")
    
    ip.is_active = not ip.is_active
    db.commit()
    
    return {"message": f"IP {'enabled' if ip.is_active else 'disabled'}"}


@router.post("/ip-whitelist/check")
def check_ip_allowed(
    ip_address: str,
    db: Session = Depends(get_db)
):
    """Check if IP is allowed (for middleware)"""
    # Get all active whitelists
    from app.models import Organization
    
    # For demo, check against all orgs
    all_ips = db.query(IPWhitelist).filter(IPWhitelist.is_active == True).all()
    
    import ipaddress
    try:
        client_ip = ipaddress.ip_address(ip_address)
        
        for whitelist in all_ips:
            network = ipaddress.ip_network(whitelist.ip_address, strict=False)
            if client_ip in network:
                return {"allowed": True, "organization_id": whitelist.organization_id}
    except:
        pass
    
    return {"allowed": False}
