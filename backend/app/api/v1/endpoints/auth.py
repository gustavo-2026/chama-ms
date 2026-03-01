from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import Member
from app.schemas.schemas import PhoneLoginRequest, PhoneLoginResponse, VerifyOTPRequest, TokenResponse
from app.core.security import create_access_token, create_refresh_token
from app.core.config import settings

router = APIRouter()


def generate_otp() -> str:
    """Generate 6-digit OTP"""
    import random
    return str(random.randint(100000, 999999))


def send_otp_via_sms(phone: str, otp: str) -> bool:
    """Send OTP via SMS (Africa's Talking or similar)"""
    if not settings.AT_API_KEY:
        # No SMS service configured - log for development
        print(f"[DEV] OTP for {phone}: {otp}")
        return True
    
    try:
        import africastalking as AT
        AT.initialize(settings.AT_USERNAME, settings.AT_API_KEY)
        sms = AT.SMS
        message = f"Your Chama verification code is: {otp}"
        sms.send(message, [phone])
        return True
    except Exception as e:
        print(f"Failed to send SMS: {e}")
        return False


def store_otp(phone: str, otp: str) -> None:
    """Store OTP (use Redis in production)"""
    import time
    # In production, use Redis:
    # redis.setex(f"otp:{phone}", 300, otp)
    global otp_store
    if not hasattr(router, 'otp_store'):
        router.otp_store = {}
    router.otp_store[phone] = {
        "otp": otp,
        "expires": time.time() + 300  # 5 minutes
    }


def get_stored_otp(phone: str) -> str | None:
    """Get stored OTP (use Redis in production)"""
    import time
    global otp_store
    if not hasattr(router, 'otp_store'):
        return None
    stored = router.otp_store.get(phone)
    if not stored:
        return None
    if time.time() > stored["expires"]:
        del router.otp_store[phone]
        return None
    return stored["otp"]


def clear_otp(phone: str) -> None:
    """Clear stored OTP"""
    global otp_store
    if hasattr(router, 'otp_store') and phone in router.otp_store:
        del router.otp_store[phone]


@router.post("/login", response_model=PhoneLoginResponse)
async def login(request: PhoneLoginRequest, db: Session = Depends(get_db)):
    """Request OTP for phone number"""
    phone = request.phone
    
    # Check if member exists
    member = db.query(Member).filter(Member.phone == phone).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phone number not registered. Contact chama admin."
        )
    
    # Generate OTP
    otp = generate_otp()
    
    # Store OTP
    store_otp(phone, otp)
    
    # Send OTP via SMS
    if not send_otp_via_sms(phone, otp):
        # In development, still return success
        if settings.DEBUG:
            pass
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to send OTP"
            )
    
    return PhoneLoginResponse(
        message="OTP sent to your phone",
        temp_token=f"temp_{phone}"
    )


@router.post("/verify-phone", response_model=TokenResponse)
async def verify_phone(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    """Verify OTP and return JWT tokens"""
    phone = request.phone
    otp = request.otp
    
    # Verify OTP
    stored_otp = get_stored_otp(phone)
    if not stored_otp or stored_otp != otp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP"
        )
    
    # Find member
    member = db.query(Member).filter(Member.phone == phone).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    # Generate tokens
    access_token = create_access_token(data={"sub": member.id, "org": member.organization_id})
    refresh_token = create_refresh_token(data={"sub": member.id})
    
    # Clear OTP
    clear_otp(phone)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    """Refresh access token using refresh token"""
    from app.core.security import decode_token
    
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        member_id = payload.get("sub")
        if not member_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Generate new access token
        access_token = create_access_token(data={"sub": member_id})
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
