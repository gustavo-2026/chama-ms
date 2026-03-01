"""
Enhanced Authentication & User Profile Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timedelta
import secrets
import bcrypt
import pyotp
import aiofiles
import os
import jwt

from app.db.database import get_db
from app.models import Member, LoginHistory, TwoFactorSetting
from app.schemas.schemas import TokenResponse
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.core.config import settings

router = APIRouter()


# ============ Pydantic Models ============

class PasswordLoginRequest(BaseModel):
    username: str
    password: str


class PasswordRegisterRequest(BaseModel):
    email: EmailStr = None
    phone: str
    name: str
    password: str = Field(min_length=6)
    organization_id: str = None


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6)


class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    bio: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    occupation: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None


class ProfileResponse(BaseModel):
    id: str
    phone: str
    name: str
    email: Optional[str] = None
    role: str
    contribution_tier: str
    bio: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    occupation: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    profile_photo_url: Optional[str] = None
    mpesa_linked: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Helper Functions ============

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except:
        return False


def get_current_member_optional(authorization: str = Header(None), db: Session = Depends(get_db)) -> Optional[Member]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        member_id = payload.get("sub")
        member = db.query(Member).filter(Member.id == member_id).first()
        return member
    except:
        return None


def require_member(authorization: str = Header(None), db: Session = Depends(get_db)) -> Member:
    member = get_current_member_optional(authorization, db)
    if not member:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return member


# ============ Authentication Endpoints ============

@router.post("/auth/register-password", response_model=TokenResponse)
async def register_with_password(request: PasswordRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(Member).filter(Member.phone == request.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Phone already registered")
    
    from app.models import Organization, MemberRole
    
    org = db.query(Organization).first()
    if not org:
        org = Organization(name="My Chama", slug="my-chama", phone=request.phone)
        db.add(org)
        db.commit()
        db.refresh(org)
    
    new_member = Member(
        organization_id=org.id,
        phone=request.phone,
        name=request.name,
        user_id=hash_password(request.password),
        role=MemberRole.MEMBER,
    )
    if request.email:
        new_member.email = request.email
    
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    
    access_token = create_access_token(data={"sub": new_member.id, "org": new_member.organization_id})
    refresh_token = create_refresh_token(data={"sub": new_member.id})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/auth/login-password", response_model=TokenResponse)
async def login_with_password(request: PasswordLoginRequest, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.phone == request.username).first()
    
    if not member:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(request.password, member.user_id or ""):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    login_record = LoginHistory(
        member_id=member.id,
        organization_id=member.organization_id,
        success=True
    )
    db.add(login_record)
    db.commit()
    
    access_token = create_access_token(data={"sub": member.id, "org": member.organization_id})
    refresh_token = create_refresh_token(data={"sub": member.id})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/auth/change-password")
async def change_password(request: ChangePasswordRequest, db: Session = Depends(get_db), current: Member = Depends(require_member)):
    if not verify_password(request.old_password, current.user_id or ""):
        raise HTTPException(status_code=400, detail="Current password incorrect")
    
    current.user_id = hash_password(request.new_password)
    db.commit()
    return {"message": "Password changed"}


@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
        member_id = payload.get("sub")
        member = db.query(Member).filter(Member.id == member_id).first()
        if not member:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        access_token = create_access_token(data={"sub": member.id, "org": member.organization_id})
        new_refresh = create_refresh_token(data={"sub": member.id})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    except:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.post("/auth/logout")
async def logout(db: Session = Depends(get_db), current: Member = Depends(get_current_member_optional)):
    if current:
        record = LoginHistory(
            member_id=current.id,
            organization_id=current.organization_id,
            success=True,
            details="logout"
        )
        db.add(record)
        db.commit()
    return {"message": "Logged out"}


# ============ Profile Endpoints ============

@router.get("/profile", response_model=ProfileResponse)
async def get_profile(db: Session = Depends(get_db), current: Member = Depends(require_member)):
    return current


@router.patch("/profile", response_model=ProfileResponse)
async def update_profile(updates: ProfileUpdateRequest, db: Session = Depends(get_db), current: Member = Depends(require_member)):
    if updates.name is not None:
        current.name = updates.name
    if updates.email is not None:
        current.email = updates.email
    if updates.bio is not None:
        current.bio = updates.bio
    if updates.date_of_birth is not None:
        current.date_of_birth = updates.date_of_birth
    if updates.gender is not None:
        current.gender = updates.gender
    if updates.location is not None:
        current.location = updates.location
    if updates.occupation is not None:
        current.occupation = updates.occupation
    if updates.emergency_contact_name is not None:
        current.emergency_contact_name = updates.emergency_contact_name
    if updates.emergency_contact_phone is not None:
        current.emergency_contact_phone = updates.emergency_contact_phone
    
    db.commit()
    db.refresh(current)
    return current


@router.post("/profile/photo")
async def upload_profile_photo(file: UploadFile = File(...), db: Session = Depends(get_db), current: Member = Depends(require_member)):
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, WebP allowed")
    
    upload_dir = "/home/gustavo/.openclaw/workspace/chama/backend/uploads/profile"
    os.makedirs(upload_dir, exist_ok=True)
    
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{current.id}_{secrets.token_hex(8)}.{ext}"
    filepath = os.path.join(upload_dir, filename)
    
    async with aiofiles.open(filepath, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    current.profile_photo_url = f"/uploads/profile/{filename}"
    db.commit()
    
    return {"message": "Photo uploaded", "url": current.profile_photo_url}


@router.get("/profile/login-history")
async def get_login_history(days: int = 30, db: Session = Depends(get_db), current: Member = Depends(require_member)):
    since = datetime.utcnow() - timedelta(days=days)
    history = db.query(LoginHistory).filter(
        LoginHistory.member_id == current.id,
        LoginHistory.created_at >= since
    ).order_by(LoginHistory.created_at.desc()).all()
    
    return [
        {
            "ip_address": h.ip_address,
            "device_info": h.device_info,
            "success": h.success,
            "created_at": h.created_at.isoformat()
        }
        for h in history
    ]


# ============ 2FA Endpoints ============

@router.post("/profile/2fa/enable")
async def enable_2fa(db: Session = Depends(get_db), current: Member = Depends(require_member)):
    secret = pyotp.random_base32()
    
    two_fa = db.query(TwoFactorSetting).filter(TwoFactorSetting.member_id == current.id).first()
    
    if two_fa:
        two_fa.enabled = True
        two_fa.secret = secret
    else:
        two_fa = TwoFactorSetting(member_id=current.id, enabled=True, secret=secret)
        db.add(two_fa)
    
    db.commit()
    
    totp = pyotp.TOTP(secret)
    qr_uri = totp.provisioning_uri(name=current.name, issuer_name="Chama")
    
    return {"secret": secret, "qr_uri": qr_uri}


@router.post("/profile/2fa/disable")
async def disable_2fa(code: str, db: Session = Depends(get_db), current: Member = Depends(require_member)):
    two_fa = db.query(TwoFactorSetting).filter(
        TwoFactorSetting.member_id == current.id,
        TwoFactorSetting.enabled == True
    ).first()
    
    if not two_fa:
        raise HTTPException(status_code=400, detail="2FA not enabled")
    
    totp = pyotp.TOTP(two_fa.secret)
    if not totp.verify(code):
        backup_codes = (two_fa.backup_codes or "").split(",")
        if code not in backup_codes:
            raise HTTPException(status_code=400, detail="Invalid code")
    
    two_fa.enabled = False
    db.commit()
    return {"message": "2FA disabled"}


@router.get("/profile/2fa/status")
async def get_2fa_status(db: Session = Depends(get_db), current: Member = Depends(require_member)):
    two_fa = db.query(TwoFactorSetting).filter(TwoFactorSetting.member_id == current.id).first()
    return {"enabled": two_fa.enabled if two_fa else False}
