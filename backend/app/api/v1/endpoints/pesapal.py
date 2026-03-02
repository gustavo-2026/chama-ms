"""
Pesapal Integration
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import requests
import hashlib
import jwt

from app.db.database import get_db
from app.models import Member
from app.models.marketplace import MarketplaceOrder, OrderStatus

router = APIRouter()


# ============ Pydantic Models ============

class PesapalConfig:
    """Pesapal settings (stored in config or DB)"""
    def __init__(self):
        from app.core.config import settings
        self.consumer_key = settings.PESAPAL_CONSUMER_KEY
        self.consumer_secret = settings.PESAPAL_CONSUMER_SECRET
        self.callback_url = settings.PESAPAL_CALLBACK_URL
        self.demo = settings.PESAPAL_DEMO


def get_current_member(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.replace("Bearer ", "")
    from app.core.config import settings
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return db.query(Member).filter(Member.id == payload.get("sub")).first()
    except:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_token():
    """Get Pesapal OAuth token"""
    from app.core.config import settings
    
    consumer_key = settings.PESAPAL_CONSUMER_KEY
    consumer_secret = settings.PESAPAL_CONSUMER_SECRET
    
    if not consumer_key or not consumer_secret:
        raise HTTPException(status_code=503, detail="Pesapal not configured")
    
    # Generate token
    url = "https://pay.pesapal.com/Api/PostPaymentGeneralRequest" if not settings.PESAPAL_DEMO else "https://cybqa.pesapal.com/Api/PostPaymentGeneralRequest"
    
    # Create signature
    import secrets
    ref_id = secrets.token_urlsafe(16)
    
    # This is a simplified version - full OAuth needed for production
    return {
        "consumer_key": consumer_key,
        "consumer_secret": consumer_secret,
        "ref_id": ref_id
    }


# ============ Pesapal Endpoints ============

@router.post("/pesapal/order")
def create_pesapal_order(
    amount: float,
    description: str,
    reference: str,  # Order ID
    email: str = None,
    phone: str = None,
    db: Session = Depends(get_db),
    current = Depends(get_current_member)
):
    """Create Pesapal payment order"""
    from app.core.config import settings
    
    consumer_key = settings.PESAPAL_CONSUMER_KEY
    consumer_secret = settings.PESAPAL_CONSUMER_SECRET
    
    if not consumer_key:
        raise HTTPException(status_code=503, detail="Pesapal not configured")
    
    # Get user info
    email = email or current.email
    phone = phone or current.phone
    
    # Generate unique reference
    import secrets
    order_tracking_id = secrets.token_urlsafe(16)
    
    # Build callback URL
    callback_url = f"{settings.PESAPAL_CALLBACK_URL or 'https://your-domain.com'}/api/v1/pesapal/callback?order={reference}"
    
    # Pesapal API URL
    base_url = "https://cybqa.pesapal.com" if settings.PESAPAL_DEMO else "https://pay.pesapal.com"
    
    # Create payment request
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "consumer_key": consumer_key,
        "consumer_secret": consumer_secret,
        "command": "RegisterIPN",
        "description": description,
        "reference_id": reference,
        "email": email,
        "phone_number": phone,
        "amount": str(amount),
        "currency": "KES",
        "callback_url": callback_url,
        "notification_type": "POST"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/PostPaymentOrderRequest",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "order_tracking_id": result.get("order_tracking_id"),
                "redirect_url": result.get("process_url"),
                "message": "Redirect user to Pesapal"
            }
        else:
            return {
                "success": False,
                "error": response.text
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/pesapal/order/{order_tracking_id}")
def check_pesapal_order(
    order_tracking_id: str,
    db: Session = Depends(get_db),
    current = Depends(get_current_member)
):
    """Check Pesapal order status"""
    from app.core.config import settings
    
    consumer_key = settings.PESAPAL_CONSUMER_KEY
    consumer_secret = settings.PESAPAL_CONSUMER_SECRET
    
    base_url = "https://cybqa.pesapal.com" if settings.PESAPAL_DEMO else "https://pay.pesapal.com"
    
    payload = {
        "consumer_key": consumer_key,
        "consumer_secret": consumer_secret,
        "order_tracking_id": order_tracking_id
    }
    
    response = requests.post(
        f"{base_url}/api/QueryPaymentDetails",
        json=payload,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        
        # Update order if paid
        if result.get("status") == "COMPLETED":
            order = db.query(MarketplaceOrder).filter(
                MarketplaceOrder.id == result.get("reference")
            ).first()
            
            if order:
                order.status = OrderStatus.PAID
                order.escrow_status = "HELD"
                order.paid_at = datetime.utcnow()
                order.mpesa_code = order_tracking_id  # Reuse field
                db.commit()
        
        return result
    
    return {"error": response.text}


@router.post("/pesapal/callback")
def pesapal_ipn(
    order_tracking_id: str = None,
    reference: str = None,
    status: str = None,
    db: Session = Depends(get_db)
):
    """Pesapal IPN (Instant Payment Notification)"""
    if status == "COMPLETED":
        order = db.query(MarketplaceOrder).filter(
            MarketplaceOrder.id == reference
        ).first()
        
        if order:
            order.status = OrderStatus.PAID
            order.escrow_status = "HELD"
            order.paid_at = datetime.utcnow()
            order.mpesa_code = order_tracking_id
            db.commit()
    
    return {"status": "received"}


# ============ Unified Checkout ============

@router.get("/providers")
def get_payment_providers(db: Session = Depends(get_db)):
    """List available payment providers"""
    from app.core.config import settings
    
    providers = []
    
    # M-Pesa
    if settings.MPESA_SHORTCODE:
        providers.append({
            "id": "mpesa",
            "name": "M-Pesa",
            "type": "mobile_money",
            "icon": "phone"
        })
    
    # Pesapal
    if settings.PESAPAL_CONSUMER_KEY:
        providers.append({
            "id": "pesapal",
            "name": "Pesapal",
            "type": "card_bank",
            "icon": "card"
        })
    
    return providers


@router.post("/checkout")
def unified_checkout(
    provider: str,  # mpesa or pesapal
    amount: float,
    reference: str,
    description: str = "Payment",
    phone: str = None,
    email: str = None,
    db: Session = Depends(get_db),
    current = Depends(get_current_member)
):
    """Unified checkout with provider selection"""
    
    if provider == "mpesa":
        # Redirect to M-Pesa flow
        from app.api.v1.endpoints.mpesa_stk import initiate_stk_push
        return initiate_stk_push(amount, phone or current.phone, reference, description, db, current)
    
    elif provider == "pesapal":
        return create_pesapal_order(amount, description, reference, email or current.email, phone or current.phone, db, current)
    
    else:
        raise HTTPException(status_code=400, detail="Invalid payment provider")
