from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum


# ============== ENUMS ==============


class MemberRole(str, Enum):
    MEMBER = "MEMBER"
    TREASURER = "TREASURER"
    CHAIR = "CHAIR"
    AGENT = "AGENT"


class ContributionMethod(str, Enum):
    CASH = "CASH"
    MPESA = "MPESA"
    BANK = "BANK"


class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class LoanStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ACTIVE = "ACTIVE"
    PAID = "PAID"


class ProposalStatus(str, Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    VOTING = "VOTING"
    PASSED = "PASSED"
    REJECTED = "REJECTED"


# ============== AUTH ==============


class PhoneLoginRequest(BaseModel):
    phone: str = Field(..., min_length=10, max_length=15)


class PhoneLoginResponse(BaseModel):
    message: str
    temp_token: Optional[str] = None


class VerifyOTPRequest(BaseModel):
    phone: str
    otp: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ============== ORGANIZATION ==============


class OrganizationBase(BaseModel):
    name: str
    phone: str
    email: Optional[EmailStr] = None
    primary_color: str = "#7C3AED"


class OrganizationCreate(OrganizationBase):
    slug: str


class OrganizationResponse(OrganizationBase):
    id: str
    slug: str
    logo_url: Optional[str] = None
    shortcode: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============== MEMBER ==============


class MemberBase(BaseModel):
    phone: str
    name: str
    role: MemberRole = MemberRole.MEMBER
    contribution_tier: str = "regular"
    mpesa_linked: bool = False
    mpesa_phone: Optional[str] = None


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[MemberRole] = None
    contribution_tier: Optional[str] = None
    mpesa_linked: Optional[bool] = None
    mpesa_phone: Optional[str] = None


class MemberResponse(MemberBase):
    id: str
    organization_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============== CONTRIBUTION ==============


class ContributionBase(BaseModel):
    amount: Decimal = Field(..., gt=0)
    method: ContributionMethod = ContributionMethod.CASH
    period_month: Optional[int] = Field(None, ge=1, le=12)
    period_year: Optional[int] = Field(None, ge=2020)
    note: Optional[str] = None


class ContributionCreate(ContributionBase):
    member_id: str


class ContributionResponse(ContributionBase):
    id: str
    organization_id: str
    member_id: str
    status: TransactionStatus
    mpesa_receipt: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ContributionSummary(BaseModel):
    total_contributions: Decimal
    member_count: int
    this_month: Decimal
    pending: Decimal


# ============== LOAN ==============


class LoanBase(BaseModel):
    amount: Decimal = Field(..., gt=0)
    interest_rate: Decimal = Field(default=10.00, ge=0, le=100)
    purpose: Optional[str] = None


class LoanCreate(LoanBase):
    member_id: str


class LoanResponse(LoanBase):
    id: str
    organization_id: str
    member_id: str
    status: LoanStatus
    created_at: datetime
    approved_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class LoanRepaymentCreate(BaseModel):
    amount: Decimal = Field(..., gt=0)
    method: ContributionMethod = ContributionMethod.MPESA


class LoanRepaymentResponse(BaseModel):
    id: str
    loan_id: str
    amount: Decimal
    method: ContributionMethod
    status: TransactionStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============== TREASURY ==============


class TreasurySummary(BaseModel):
    total_capital: Decimal
    available: Decimal
    locked_in_loans: Decimal
    pending_contributions: Decimal
    member_count: int
    active_loans: int


class DividendDisburseRequest(BaseModel):
    period_month: int = Field(..., ge=1, le=12)
    period_year: int = Field(..., ge=2020)


# ============== PROPOSALS ==============


class ProposalBase(BaseModel):
    title: str
    description: str
    proposal_type: str


class ProposalCreate(ProposalBase):
    pass


class ProposalUpdate(BaseModel):
    status: Optional[ProposalStatus] = None
    voting_starts: Optional[datetime] = None
    voting_ends: Optional[datetime] = None


class ProposalResponse(ProposalBase):
    id: str
    organization_id: str
    status: ProposalStatus
    created_at: datetime
    voting_starts: Optional[datetime] = None
    voting_ends: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class VoteRequest(BaseModel):
    choice: str = Field(..., pattern="^(YES|NO|ABSTAIN)$")


class VoteResponse(BaseModel):
    id: str
    proposal_id: str
    member_id: str
    choice: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============== MPESA ==============


class STKPushRequest(BaseModel):
    phone: str
    amount: Decimal = Field(..., gt=0)


class STKPushResponse(BaseModel):
    checkout_request_id: str
    merchant_request_id: str
    response_code: str
    response_description: str


class MpesaCallback(BaseModel):
    # C2B / STK callback fields
    transaction_type: Optional[str] = None
    trans_id: Optional[str] = None
    trans_time: Optional[str] = None
    trans_amount: Optional[Decimal] = None
    business_shortcode: Optional[str] = None
    bill_ref_number: Optional[str] = None
    invoice_number: Optional[str] = None
    account_number: Optional[str] = None
    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    org_account_balance: Optional[str] = None


class B2CRequest(BaseModel):
    phone: str
    amount: Decimal = Field(..., gt=0)
    occasion: Optional[str] = "Dividend disbursement"


class B2CResponse(BaseModel):
    conversation_id: str
    originator_conversation_id: str
    response_code: str
    response_description: str
