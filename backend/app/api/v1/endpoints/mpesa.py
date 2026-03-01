from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from decimal import Decimal
from app.db.database import get_db
from app.models import Member, Contribution, TransactionStatus
from app.schemas.schemas import STKPushRequest, STKPushResponse, MpesaCallback, B2CRequest, B2CResponse
from app.core.config import settings
import requests
import base64
import datetime

router = APIRouter()


def get_current_member(db: Session = Depends(get_db)):
    member = db.query(Member).first()
    if not member:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return member


def get_mpesa_token():
    """Get M-Pesa access token"""
    if settings.MPESA_ENV == "sandbox":
        base_url = "https://sandbox.safaricom.co.ke"
    else:
        base_url = "https://api.safaricom.co.ke"
    
    credentials = f"{settings.MPESA_CONSUMER_KEY}:{settings.MPESA_CONSUMER_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()
    
    response = requests.get(
        f"{base_url}/oauth/v1/generate?grant_type=client_credentials",
        headers={"Authorization": f"Basic {encoded}"}
    )
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise HTTPException(status_code=500, detail="Failed to get M-Pesa token")


@router.post("/stk-push", response_model=STKPushResponse)
async def stk_push(
    request: STKPushRequest,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Initiate STK Push for contribution"""
    if settings.MPESA_ENV == "sandbox":
        base_url = "https://sandbox.safaricom.co.ke"
    else:
        base_url = "https://api.safaricom.co.ke"
    
    token = get_mpesa_token()
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(
        f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}".encode()
    ).decode()
    
    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": str(int(request.amount)),
        "PartyA": request.phone,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": request.phone,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": "ChamaContribution",
        "TransactionDesc": "Chama Contribution"
    }
    
    response = requests.post(
        f"{base_url}/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        return STKPushResponse(
            checkout_request_id=data.get("CheckoutRequestID", ""),
            merchant_request_id=data.get("MerchantRequestID", ""),
            response_code=data.get("ResponseCode", ""),
            response_description=data.get("ResponseDescription", "")
        )
    else:
        raise HTTPException(
            status_code=500,
            detail=f"STK Push failed: {response.text}"
        )


@router.post("/callback/c2b")
async def c2b_callback(
    callback: MpesaCallback,
    db: Session = Depends(get_db)
):
    """Handle C2B callback"""
    # Find member by phone
    member = db.query(Member).filter(
        Member.phone == callback.phone_number
    ).first()
    
    if member and callback.trans_id:
        # Create transaction record
        transaction = Contribution(
            organization_id=member.organization_id,
            member_id=member.id,
            type="C2B",
            amount=callback.trans_amount or Decimal("0"),
            status=TransactionStatus.COMPLETED,
            mpesa_receipt=callback.trans_id,
            phone=callback.phone_number,
            processed_at=datetime.datetime.utcnow()
        )
        db.add(transaction)
        db.commit()
    
    return {"ResultCode": 0, "ResultDesc": "Accepted"}


@router.post("/callback/b2c")
async def b2c_callback(
    callback: MpesaCallback,
    db: Session = Depends(get_db)
):
    """Handle B2C callback"""
    # Process B2C payment result
    return {"ResultCode": 0, "ResultDesc": "Accepted"}


@router.post("/b2c", response_model=B2CResponse)
async def b2c_payment(
    request: B2CRequest,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Send money to member (dividends, withdrawals)"""
    # Check role permission
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if settings.MPESA_ENV == "sandbox":
        base_url = "https://sandbox.safaricom.co.ke"
    else:
        base_url = "https://api.safaricom.co.ke"
    
    token = get_mpesa_token()
    
    payload = {
        "InitiatorName": "ChamaAPI",
        "SecurityCredential": "encrypted_credential",  # Encrypt in production
        "CommandID": "BusinessPayment",
        "Amount": str(int(request.amount)),
        "PartyA": settings.MPESA_SHORTCODE,
        "PartyB": request.phone,
        "Remarks": request.occasion,
        "QueueTimeOutURL": f"{settings.MPESA_CALLBACK_URL}/timeout",
        "ResultURL": f"{settings.MPESA_CALLBACK_URL}/b2c"
    }
    
    response = requests.post(
        f"{base_url}/mpesa/b2c/v1/sendpayment",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        return B2CResponse(
            conversation_id=data.get("ConversationID", ""),
            originator_conversation_id=data.get("OriginatorConversationID", ""),
            response_code=data.get("ResponseCode", ""),
            response_description=data.get("ResponseDescription", "")
        )
    else:
        raise HTTPException(
            status_code=500,
            detail=f"B2C failed: {response.text}"
        )


@router.get("/transactions")
def list_transactions(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """List M-Pesa transactions"""
    transactions = db.query(Transaction).filter(
        Transaction.organization_id == current.organization_id
    ).order_by(Transaction.created_at.desc()).limit(50).all()
    return transactions
