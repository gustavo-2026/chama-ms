"""
M-Pesa STK Push Integration
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import requests
import base64
import jwt

from app.db.database import get_db
from app.models import Member
from app.models.mpesa_config import MpesaConfig, MpesaTransaction, ChamaMpesaConfig
from app.models.marketplace import MarketplaceOrder, OrderStatus
from app.core.config import settings

router = APIRouter()


def get_db_session():
    return next(get_db())


def get_current_member(authorization: str = Header(None), db: Session = Depends(get_db_session)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return db.query(Member).filter(Member.id == payload.get("sub")).first()
    except:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_mpesa_token(config: MpesaConfig) -> str:
    """Get M-Pesa access token"""
    import time
    
    # Check cached token
    now = time.time()
    if hasattr(get_mpesa_token, 'cached_token') and hasattr(get_mpesa_token, 'token_expires'):
        if now < get_mpesa_token.token_expires:
            return get_mpesa_token.cached_token
    
    auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate" if config.environment == "sandbox" else "https://api.safaricom.co.ke/oauth/v1/generate"
    
    response = requests.get(
        auth_url,
        params={"grant_type": "client_credentials"},
        auth=(config.consumer_key, config.consumer_secret),
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        # Cache for ~1 hour (tokens last ~1 hour)
        get_mpesa_token.cached_token = token
        get_mpesa_token.token_expires = now + 3500
        return token
    
    raise HTTPException(status_code=500, detail="Failed to get M-Pesa token")


def lipa_na_mpesa_online(config: MpesaConfig, phone: str, amount: int, reference: str, description: str) -> dict:
    """Initiate STK Push"""
    token = get_mpesa_token(config)
    
    # Prepare password (shortcode + passkey + timestamp)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = f"{config.shortcode}{config.passkey}{timestamp}"
    encoded_password = base64.b64encode(password.encode()).decode()
    
    # STK Push endpoint
    stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest" if config.environment == "sandbox" else "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "BusinessShortCode": config.shortcode,
        "Password": encoded_password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerBuyGoodsOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": config.shortcode,
        "PhoneNumber": phone,
        "CallBackURL": settings.MPESA_CALLBACK_URL or "https://your-domain.com/api/v1/mpesa/callback",
        "AccountReference": reference,
        "TransactionDesc": description
    }
    
    response = requests.post(stk_url, json=payload, headers=headers, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        return {
            "success": True,
            "checkout_request_id": result.get("CheckoutRequestID"),
            "response_code": result.get("ResponseCode"),
            "response_description": result.get("ResponseDescription"),
            "merchant_request_id": result.get("MerchantRequestID")
        }
    else:
        return {
            "success": False,
            "error": response.text
        }


def query_stk_status(config: MpesaConfig, checkout_request_id: str) -> dict:
    """Query STK Push status"""
    token = get_mpesa_token(config)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = f"{config.shortcode}{config.passkey}{timestamp}"
    encoded_password = base64.b64encode(password.encode()).decode()
    
    query_url = "https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query" if config.environment == "sandbox" else "https://api.safaricom.co.ke/mpesa/stkpushquery/v1/query"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "BusinessShortCode": config.shortcode,
        "Password": encoded_password,
        "Timestamp": timestamp,
        "CheckoutRequestID": checkout_request_id
    }
    
    response = requests.post(query_url, json=payload, headers=headers, timeout=30)
    
    if response.status_code == 200:
        return response.json()
    return {"error": response.text}


# ============ STK Push Endpoints ============

@router.post("/stk-push")
def initiate_stk_push(
    amount: float,
    phone: str,
    reference: str,  # Order ID or other reference
    description: str = "Payment",
    db: Session = Depends(get_db_session),
    current = Depends(get_current_member)
):
    """Initiate STK Push payment"""
    # Get platform config
    config = db.query(MpesaConfig).first()
    
    if not config:
        raise HTTPException(status_code=503, detail="M-Pesa not configured")
    
    if not config.is_active:
        raise HTTPException(status_code=503, detail="M-Pesa is disabled")
    
    if not config.allow_stk_push:
        raise HTTPException(status_code=403, detail="STK Push not enabled")
    
    # Format phone
    if phone.startswith("0"):
        phone = "254" + phone[1:]
    elif not phone.startswith("254"):
        phone = "254" + phone
    
    # Initiate STK Push
    result = lipa_na_mpesa_online(config, phone, int(amount), reference, description)
    
    if result.get("success"):
        # Create transaction record
        tx = MpesaTransaction(
            transaction_type="STK_PUSH",
            mpesa_code=result.get("checkout_request_id"),
            amount=str(amount),
            phone=phone,
            shortcode=config.shortcode,
            status="PENDING",
            reference_id=reference
        )
        db.add(tx)
        db.commit()
        
        return {
            "success": True,
            "checkout_request_id": result.get("checkout_request_id"),
            "message": "STK push sent to your phone"
        }
    
    return {
        "success": False,
        "error": result.get("error", "Failed to initiate payment")
    }


@router.get("/stk-push/status/{checkout_request_id}")
def check_stk_status(
    checkout_request_id: str,
    db: Session = Depends(get_db_session),
    current = Depends(get_current_member)
):
    """Check STK Push payment status"""
    config = db.query(MpesaConfig).first()
    
    if not config:
        raise HTTPException(status_code=503, detail="M-Pesa not configured")
    
    result = query_stk_status(config, checkout_request_id)
    
    # Update transaction if completed
    tx = db.query(MpesaTransaction).filter(
        MpesaTransaction.mpesa_code == checkout_request_id
    ).first()
    
    if result.get("ResponseCode") == "0":
        if tx:
            tx.status = "COMPLETED"
            db.commit()
        return {"status": "COMPLETED", "message": "Payment successful"}
    
    return {"status": result.get("ResultCode", "PENDING"), "message": result.get("ResultDesc", "Pending")}


@router.post("/callback")
def mpesa_callback(
    Body: dict,
    db: Session = Depends(get_db_session)
):
    """M-Pesa callback URL"""
    try:
        stk_callback = Body.get("stkCallback", {})
        
        checkout_request_id = stk_callback.get("CheckoutRequestID")
        result_code = stk_callback.get("ResultCode")
        result_desc = stk_callback.get("ResultDesc")
        
        # Find transaction
        tx = db.query(MpesaTransaction).filter(
            MpesaTransaction.mpesa_code == checkout_request_id
        ).first()
        
        if result_code == 0:
            # Payment successful
            callback_metadata = stk_callback.get("CallbackMetadata", {})
            
            # Extract M-Pesa receipt number
            mpesa_receipt = None
            amount = None
            phone = None
            
            for item in callback_metadata.get("Item", []):
                if item.get("Name") == "MpesaReceiptNumber":
                    mpesa_receipt = item.get("Value")
                elif item.get("Name") == "Amount":
                    amount = item.get("Value")
                elif item.get("Name") == "PhoneNumber":
                    phone = item.get("Value")
            
            if tx:
                tx.status = "COMPLETED"
                tx.mpesa_code = mpesa_receipt or checkout_request_id
                tx.callback_amount = str(amount)
                tx.completed_at = datetime.utcnow()
                tx.reference_id = mpesa_receipt
                
                # Update marketplace order if applicable
                if tx.reference_id:
                    order = db.query(MarketplaceOrder).filter(
                        MarketplaceOrder.id == tx.reference_id
                    ).first()
                    
                    if order:
                        order.status = OrderStatus.PAID
                        order.escrow_status = "HELD"
                        order.paid_at = datetime.utcnow()
                        order.mpesa_code = mpesa_receipt
            
            return {"status": "success"}
        
        else:
            # Payment failed
            if tx:
                tx.status = "FAILED"
                tx.failure_reason = result_desc
            
            return {"status": "failed", "reason": result_desc}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/b2c")
def initiate_b2c(
    phone: str,
    amount: float,
    remarks: str = "Withdrawal",
    db: Session = Depends(get_db_session),
    current = Depends(get_current_member)
):
    """Initiate B2C payment (disbursement to member)"""
    config = db.query(MpesaConfig).first()
    
    if not config:
        raise HTTPException(status_code=503, detail="M-Pesa not configured")
    
    if not config.allow_b2c:
        raise HTTPException(status_code=403, detail="B2C not enabled")
    
    # Format phone
    if phone.startswith("0"):
        phone = "254" + phone[1:]
    elif not phone.startswith("254"):
        phone = "254" + phone
    
    token = get_mpesa_token(config)
    
    # B2C endpoint
    b2c_url = "https://sandbox.safaricom.co.ke/mpesa/b2c/v1/paymentrequest" if config.environment == "sandbox" else "https://api.safaricom.co.ke/mpesa/b2c/v1/paymentrequest"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "InitiatorName": settings.MPESA_INITIATOR_NAME or "testapi",
        "SecurityCredential": settings.MPESA_B2C_SECURITY or "test",
        "CommandID": "BusinessPayment",
        "Amount": int(amount),
        "PartyA": config.shortcode,
        "PartyB": phone,
        "Remarks": remarks,
        "QueueTimeOutURL": f"{settings.MPESA_CALLBACK_URL or 'https://your-domain.com'}/api/v1/mpesa/b2c-timeout",
        "ResultURL": f"{settings.MPESA_CALLBACK_URL or 'https://your-domain.com'}/api/v1/mpesa/b2c-result"
    }
    
    response = requests.post(b2c_url, json=payload, headers=headers, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        return {"success": True, "conversation_id": result.get("ConversationID")}
    
    return {"success": False, "error": response.text}


# ============ C2B (Paybill/Till) ============

@router.post("/c2b-register")
def register_c2b_urls(
    db: Session = Depends(get_db_session),
    current = Depends(get_current_member)
):
    """Register C2B validation and confirmation URLs"""
    config = db.query(MpesaConfig).first()
    
    if not config:
        raise HTTPException(status_code=503, detail="M-Pesa not configured")
    
    token = get_mpesa_token(config)
    
    register_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl" if config.environment == "sandbox" else "https://api.safaricom.co.ke/mpesa/c2b/v1/registerurl"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "ShortCode": config.shortcode,
        "ResponseType": "Completed",
        "ConfirmationURL": f"{settings.MPESA_CALLBACK_URL or 'https://your-domain.com'}/api/v1/mpesa/c2b-confirm",
        "ValidationURL": f"{settings.MPESA_CALLBACK_URL or 'https://your-domain.com'}/api/v1/mpesa/c2b-validate"
    }
    
    response = requests.post(register_url, json=payload, headers=headers, timeout=30)
    
    return response.json()


@router.post("/c2b-confirm")
def c2b_confirm(
    Body: dict,
    db: Session = Depends(get_db_session)
):
    """C2B confirmation callback"""
    # Handle payment confirmation
    return {"status": "success"}


@router.post("/c2b-validate")
def c2b_validate(
    Body: dict,
    db: Session = Depends(get_db_session)
):
    """C2B validation callback"""
    return {"status": "success", "ResultCode": 0}
