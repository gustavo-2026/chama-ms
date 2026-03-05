"""
Core Banking Service
Microservice for members, contributions, loans, treasury
"""
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, Numeric, func, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os
import jwt
import uuid

SECRET_KEY = "change-me-in-production-min-32-characters"

Base = declarative_base()

app = FastAPI(title="Core Banking Service")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./core_service.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# ============ Models ============

class Member(Base):
    __tablename__ = "members"
    id = Column(String, primary_key=True)
    phone = Column(String, unique=True)
    name = Column(String)
    email = Column(String)
    organization_id = Column(String)
    role = Column(String)
    status = Column(String, default="ACTIVE")
    moto_streak = Column(Integer, default=0)
    trust_score = Column(Integer, default=500) # Base score 500



class Contribution(Base):
    __tablename__ = "contributions"
    id = Column(String, primary_key=True)
    member_id = Column(String)
    amount = Column(Numeric)
    method = Column(String)
    status = Column(String, default="COMPLETED")
    created_at = Column(DateTime, default=datetime.utcnow)


class Loan(Base):
    __tablename__ = "loans"
    id = Column(String, primary_key=True)
    member_id = Column(String)
    principal_amount = Column(Numeric)
    term_months = Column(Integer)
    status = Column(String, default="PENDING")
    approved_by = Column(String, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class LoanRepayment(Base):
    __tablename__ = "loan_repayments"
    id = Column(String, primary_key=True)
    loan_id = Column(String)
    amount = Column(Numeric)
    due_date = Column(DateTime)
    status = Column(String, default="PENDING")  # "PENDING", "COMPLETED"
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)



class AuditEvent(Base):
    __tablename__ = "audit_events"
    id = Column(String, primary_key=True)
    organization_id = Column(String)
    member_id = Column(String)
    action = Column(String)
    resource_id = Column(String, nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ContributionSchedule(Base):
    __tablename__ = "contribution_schedules"
    id = Column(String, primary_key=True)
    organization_id = Column(String)
    amount = Column(Numeric)
    frequency = Column(String)  # e.g., "MONTHLY", "WEEKLY"
    next_due_date = Column(DateTime)
    created_by = Column(String)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)


class SocialFund(Base):
    __tablename__ = "social_funds"
    id = Column(String, primary_key=True)
    organization_id = Column(String)
    member_id = Column(String)
    amount = Column(Numeric)
    reason = Column(String)
    category = Column(String) # "FINE", "GIFT"
    created_at = Column(DateTime, default=datetime.utcnow)


class MarketplaceItem(Base):
    __tablename__ = "marketplace_items"
    id = Column(String, primary_key=True)
    organization_id = Column(String)
    member_id = Column(String)
    title = Column(String)
    description = Column(Text)
    price = Column(Numeric)
    category = Column(String) # "GOODS", "SERVICES"
    status = Column(String, default="ACTIVE") # "ACTIVE", "SOLD"
    created_at = Column(DateTime, default=datetime.utcnow)


class Harambee(Base):
    __tablename__ = "harambees"
    id = Column(String, primary_key=True)
    organization_id = Column(String)
    title = Column(String)
    description = Column(Text)
    goal_amount = Column(Numeric)
    current_amount = Column(Numeric, default=0)
    deadline = Column(DateTime)
    status = Column(String, default="ACTIVE") # "ACTIVE", "COMPLETED"
    created_at = Column(DateTime, default=datetime.utcnow)


class HarambeeContribution(Base):
    __tablename__ = "harambee_contributions"
    id = Column(String, primary_key=True, index=True, default=lambda: f"hcont_{uuid.uuid4().hex[:8]}")
    harambee_id = Column(String, ForeignKey("harambees.id"))
    member_id = Column(String, ForeignKey("members.id"))
    amount = Column(Numeric)
    created_at = Column(DateTime, default=datetime.utcnow)


class InvestmentOpportunity(Base):
    __tablename__ = "investment_opportunities"
    id = Column(String, primary_key=True)
    provider = Column(String) # e.g., "Britam", "NCBA"
    title = Column(String)
    description = Column(Text)
    annual_yield = Column(Float)
    min_amount = Column(Numeric)
    category = Column(String) # "MMF", "T-BILL", "LAND"
    created_at = Column(DateTime, default=datetime.utcnow)


class ChamaInvestment(Base):
    __tablename__ = "chama_investments"
    id = Column(String, primary_key=True)
    organization_id = Column(String)
    opportunity_id = Column(String)
    amount = Column(Numeric)
    status = Column(String, default="ACTIVE") # "ACTIVE", "WITHDRAWN"
    created_at = Column(DateTime, default=datetime.utcnow)


class ShareListing(Base):
    __tablename__ = "share_listings"
    id = Column(String, primary_key=True)
    organization_id = Column(String)
    seller_id = Column(String)
    shares_count = Column(Numeric)
    ask_price = Column(Numeric)
    status = Column(String, default="OPEN") # "OPEN", "SOLD", "CANCELLED"
    created_at = Column(DateTime, default=datetime.utcnow)


class ShareBid(Base):
    __tablename__ = "share_bids"
    id = Column(String, primary_key=True)
    status = Column(String, default="PENDING") # "PENDING", "ACCEPTED", "REJECTED"
    created_at = Column(DateTime, default=datetime.utcnow)


class MeetingMinutes(Base):
    __tablename__ = "meeting_minutes"
    id = Column(String, primary_key=True)
    organization_id = Column(String)
    title = Column(String)
    summary = Column(Text)
    attendees = Column(Text) # JSON string of member IDs
    status = Column(String, default="DRAFT") # "DRAFT", "FINALIZED"
    meeting_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class MinuteSignature(Base):
    __tablename__ = "minute_signatures"
    id = Column(String, primary_key=True)
    minute_id = Column(String)
    member_id = Column(String)
    signed_at = Column(DateTime, default=datetime.utcnow)


# ============ Pydantic Models ============

class MemberCreate(BaseModel):
    phone: str
    name: str
    email: Optional[str] = None
    organization_id: str
    role: str = "MEMBER"


class ContributionCreate(BaseModel):
    member_id: str
    amount: float
    method: str = "CASH"


class LoanCreate(BaseModel):
    member_id: str
    principal_amount: float
    term_months: int
    purpose: str
class MarketplaceItemCreate(BaseModel):
    organization_id: str
    member_id: str
    title: str
    description: str
    price: float
    category: str

class ShareListingCreate(BaseModel):
    organization_id: str
    seller_id: str
    shares_count: float
    ask_price: float

class ShareBidCreate(BaseModel):
    listing_id: str
    bidder_id: str
    bid_amount: float

class HarambeeCreate(BaseModel):
    organization_id: str
    title: str
    description: str
    goal_amount: float
    deadline: datetime

class ContributionScheduleCreate(BaseModel):
    organization_id: str
    amount: float
    frequency: str
    next_due_date: datetime

class OTPRequest(BaseModel):
    contact: str

class OTPVerify(BaseModel):
    contact: str
    otp: str

class RepaymentCreate(BaseModel):
    amount: float


# In-memory OTP store
mock_otps = {}
import random

# ============ Helpers ============

def get_current_member(db: Session = Depends(get_db), authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401)
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return db.query(Member).filter(Member.id == payload.get("sub")).first()
    except:
        raise HTTPException(status_code=401)


def require_roles(allowed_roles: List[str]):
    def role_checker(member = Depends(get_current_member)):
        if not member or member.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient role permissions")
        return member
    return role_checker



def log_audit_event(db: Session, organization_id: str, member_id: str, action: str, resource_id: str = None, details: str = None, ip_address: str = None):
    event = AuditEvent(
        id=f"aud_{datetime.utcnow().timestamp()}",
        organization_id=organization_id,
        member_id=member_id,
        action=action,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address
    )
    db.add(event)


# ============ Member Endpoints ============

@app.get("/health")
def health():
    return {"status": "healthy", "service": "core"}

# ============ Auth Endpoints ============

@app.post("/auth/request-otp")
def request_otp(data: OTPRequest, db: Session = Depends(get_db)):
    member = db.query(Member).filter((Member.phone == data.contact) | (Member.email == data.contact)).first()
    if not member:
        raise HTTPException(status_code=404, detail="User not found")
    
    otp = str(random.randint(100000, 999999))
    mock_otps[member.id] = otp
    
    # DEV logging
    print(f"DEV: OTP for {data.contact} ({member.id}) is {otp}")
    
    return {"status": "otp_sent"}

@app.post("/auth/verify-otp")
def verify_otp(data: OTPVerify, db: Session = Depends(get_db)):
    member = db.query(Member).filter((Member.phone == data.contact) | (Member.email == data.contact)).first()
    if not member:
        raise HTTPException(status_code=404, detail="User not found")
        
    expected_otp = mock_otps.get(member.id)
    if not expected_otp or expected_otp != data.otp:
        if data.otp != "123456": # Magic OTP for testing
            raise HTTPException(status_code=401, detail="Invalid OTP")
            
    payload = {
        "sub": member.id,
        "role": member.role,
        "org_id": member.organization_id,
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    mock_otps.pop(member.id, None)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "member": {
            "id": member.id,
            "name": member.name,
            "role": member.role,
            "organization_id": member.organization_id
        }
    }


@app.post("/members", response_model=dict)
def create_member(data: MemberCreate, db: Session = Depends(get_db)):
    member = Member(
        id=f"mem_{datetime.utcnow().timestamp()}",
        phone=data.phone,
        name=data.name,
        email=data.email,
        organization_id=data.organization_id,
        role=data.role
    )
    db.add(member)
    db.commit()
    return {"id": member.id, "status": "created"}


@app.get("/members/{member_id}", response_model=dict)
def get_member(member_id: str, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404)
    return {
        "id": member.id,
        "name": member.name,
        "phone": member.phone,
        "email": member.email,
        "role": member.role,
        "organization_id": member.organization_id
    }


# ============ Schedule Endpoints ============

@app.post("/schedules", response_model=dict)
def create_schedule(data: ContributionScheduleCreate, db: Session = Depends(get_db), member = Depends(require_roles(["CHAIR", "ADMIN"]))):
    schedule = ContributionSchedule(
        id=f"sch_{datetime.utcnow().timestamp()}",
        organization_id=data.organization_id,
        amount=data.amount,
        frequency=data.frequency,
        next_due_date=data.next_due_date,
        created_by=member.id
    )
    db.add(schedule)
    log_audit_event(db, data.organization_id, member.id, "CREATE_SCHEDULE", schedule.id, f"Created {data.frequency} schedule for {data.amount}")
    db.commit()
    return {"id": schedule.id, "status": "created"}

@app.get("/schedules/{org_id}", response_model=List[dict])
def list_schedules(org_id: str, db: Session = Depends(get_db)):
    schedules = db.query(ContributionSchedule).filter(
        ContributionSchedule.organization_id == org_id,
        ContributionSchedule.is_active == 1
    ).all()
    return [{
        "id": s.id,
        "amount": float(s.amount),
        "frequency": s.frequency,
        "next_due_date": s.next_due_date.isoformat() if s.next_due_date else None,
        "created_by": s.created_by
    } for s in schedules]

@app.delete("/schedules/{schedule_id}")
def delete_schedule(schedule_id: str, db: Session = Depends(get_db), member = Depends(require_roles(["CHAIR", "ADMIN"]))):
    schedule = db.query(ContributionSchedule).filter(ContributionSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    schedule.is_active = 0
    log_audit_event(db, schedule.organization_id, member.id, "DELETE_SCHEDULE", schedule.id, "Deactivated schedule")
    db.commit()
    return {"status": "deleted"}


@app.post("/schedules/trigger-reminders")
def trigger_reminders(db: Session = Depends(get_db)):
    """
    Finds all active schedules where next_due_date is within next 3 days.
    Returns list of members to ping.
    """
    now = datetime.utcnow()
    upcoming_threshold = now + timedelta(days=3)

    due_schedules = db.query(ContributionSchedule).filter(
        ContributionSchedule.is_active == 1,
        ContributionSchedule.next_due_date <= upcoming_threshold,
        ContributionSchedule.next_due_date > now
    ).all()

    notifications = []
    
    for schedule in due_schedules:
        # Get all active members in the org
        members = db.query(Member).filter(
            Member.organization_id == schedule.organization_id,
            Member.status == "ACTIVE"
        ).all()
        
        for m in members:
            # Here we just return them for the mock, in real life we'd call notification-service
            notifications.append({
                "member_id": m.id,
                "phone": m.phone,
                "email": m.email,
                "message": f"Reminder: Your {schedule.frequency} contribution of {schedule.amount} is due by {schedule.next_due_date.strftime('%Y-%m-%d')}."
            })
            
    return {"reminders_triggered": len(notifications), "notifications": notifications}


@app.get("/members", response_model=List[dict])
def list_members(org_id: str = None, limit: int = 50, db: Session = Depends(get_db)):
    query = db.query(Member)
    if org_id:
        query = query.filter(Member.organization_id == org_id)
    return [{"id": m.id, "name": m.name, "phone": m.phone, "role": m.role} 
            for m in query.limit(limit).all()]


# ============ Contribution Endpoints ============

@app.post("/contributions", response_model=dict)
def create_contribution(data: ContributionCreate, db: Session = Depends(get_db), member = Depends(get_current_member)):
    contrib = Contribution(
        id=f"con_{datetime.utcnow().timestamp()}",
        member_id=data.member_id,
        amount=data.amount,
        method=data.method,
        status="COMPLETED"
    )
    db.add(contrib)
    
    # Update Moto Streak & Trust Score
    member_obj = db.query(Member).filter(Member.id == data.member_id).first()
    if member_obj:
        member_obj.moto_streak += 1
        member_obj.trust_score = min(1000, member_obj.trust_score + 10)
    
    org_id = member.organization_id if member else "UNKNOWN"
    log_audit_event(db, org_id, member.id, "CREATE_CONTRIBUTION", contrib.id, f"Added contribution of {data.amount} for member {data.member_id}")
    
    db.commit()
    return {"id": contrib.id, "status": "created", "new_streak": member_obj.moto_streak if member_obj else 0}


@app.get("/contributions/member/{member_id}", response_model=List[dict])
def get_member_contributions(member_id: str, db: Session = Depends(get_db)):
    contribs = db.query(Contribution).filter(Contribution.member_id == member_id).all()
    return [{"id": c.id, "amount": float(c.amount), "status": c.status, "created_at": c.created_at} 
            for c in contribs]


@app.get("/contributions/organization/{org_id}", response_model=dict)
def get_org_contributions(org_id: str, db: Session = Depends(get_db)):
    members = db.query(Member).filter(Member.organization_id == org_id).all()
    member_ids = [m.id for m in members]
    contribs = db.query(Contribution).filter(Contribution.member_id.in_(member_ids)).all()
    total = sum(float(c.amount) for c in contribs)
    return {"total": total, "count": len(contribs)}


# ============ Loan Endpoints ============

@app.post("/loans", response_model=dict)
def create_loan(data: LoanCreate, db: Session = Depends(get_db), member = Depends(get_current_member)):
    loan = Loan(
        id=f"lon_{datetime.utcnow().timestamp()}",
        member_id=data.member_id,
        principal_amount=data.principal_amount,
        term_months=data.term_months,
        status="PENDING"
    )
    db.add(loan)
    
    org_id = member.organization_id if member else "UNKNOWN"
    log_audit_event(db, org_id, member.id, "CREATE_LOAN", loan.id, f"Requested loan of {data.principal_amount}")
    
    db.commit()
    return {"id": loan.id, "status": "pending"}


@app.get("/loans/{loan_id}", response_model=dict)
def get_loan(loan_id: str, db: Session = Depends(get_db)):
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404)
    return {
        "id": loan.id,
        "member_id": loan.member_id,
        "principal_amount": float(loan.principal_amount),
        "term_months": loan.term_months,
        "status": loan.status,
        "created_at": loan.created_at.isoformat()
    }

@app.get("/loans/{loan_id}/schedule", response_model=List[dict])
def get_loan_schedule(loan_id: str, db: Session = Depends(get_db)):
    repayments = db.query(LoanRepayment).filter(LoanRepayment.loan_id == loan_id).all()
    if not repayments:
        # Generate on the fly if it was just approved and hasn't been generated
        loan = db.query(Loan).filter(Loan.id == loan_id).first()
        if not loan or loan.status != "APPROVED":
            return []
        # Basic amortization logic (interest-free for now as per simple Chama rules)
        monthly = loan.principal_amount / loan.term_months
        res = []
        for i in range(1, loan.term_months + 1):
            rep = LoanRepayment(
                id=f"rep_{loan_id}_{i}",
                loan_id=loan_id,
                amount=monthly,
                due_date=loan.approved_at + timedelta(days=30*i)
            )
            db.add(rep)
            res.append(rep)
        db.commit()
        repayments = res

    return [{
        "id": r.id,
        "amount": float(r.amount),
        "due_date": r.due_date.isoformat(),
        "status": r.status,
        "paid_at": r.paid_at.isoformat() if r.paid_at else None
    } for r in repayments]

@app.post("/loans/{loan_id}/repay")
def record_repayment(loan_id: str, data: RepaymentCreate, db: Session = Depends(get_db), member = Depends(require_roles(["TREASURER", "ADMIN"]))):
    # Find next pending repayment
    rep = db.query(LoanRepayment).filter(
        LoanRepayment.loan_id == loan_id,
        LoanRepayment.status == "PENDING"
    ).order_by(LoanRepayment.due_date).first()
    
    if not rep:
        raise HTTPException(status_code=400, detail="No pending repayments found")
    
    rep.status = "COMPLETED"
    rep.paid_at = datetime.utcnow()
    
    # Update Trust Score for on-time repayment
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if loan:
        member_obj = db.query(Member).filter(Member.id == loan.member_id).first()
        if member_obj:
            # Check if paid on time
            if rep.paid_at <= rep.due_date:
                member_obj.trust_score = min(1000, member_obj.trust_score + 15)
            else:
                member_obj.trust_score = max(0, member_obj.trust_score - 20)
                member_obj.moto_streak = 0 # Reset streak on late payment

    log_audit_event(db, "ADMIN_ORG", member.id, "RECORD_REPAYMENT", rep.id, f"Repaid KES {data.amount} for loan {loan_id}")
    
    # Check if all repaid
    remaining = db.query(LoanRepayment).filter(
        LoanRepayment.loan_id == loan_id,
        LoanRepayment.status == "PENDING"
    ).count()
    
    if remaining == 0:
        loan.status = "REPAID"
        
    db.commit()
    return {"status": "recorded"}

@app.get("/loans/member/{member_id}", response_model=List[dict])
def get_member_loans(member_id: str, db: Session = Depends(get_db)):
    loans = db.query(Loan).filter(Loan.member_id == member_id).all()
    return [{"id": l.id, "amount": float(l.principal_amount), "status": l.status} 
            for l in loans]


@app.post("/loans/{loan_id}/approve")
def approve_loan(loan_id: str, db: Session = Depends(get_db), member = Depends(require_roles(["CHAIR", "ADMIN"]))):
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404)
    loan.status = "APPROVED"
    loan.approved_by = member.id
    loan.approved_at = datetime.utcnow()
    
    # Audit log
    loan_member = db.query(Member).filter(Member.id == loan.member_id).first()
    org_id = loan_member.organization_id if loan_member else "UNKNOWN"
    log_audit_event(db, org_id, member.id, "APPROVE_LOAN", loan.id, f"Approved loan for {loan.principal_amount}")
    
    db.commit()
    return {"id": loan.id, "status": "approved"}


# ============ Treasury Endpoints ============

@app.get("/treasury/{org_id}", response_model=dict)
def get_treasury(org_id: str, db: Session = Depends(get_db)):
    # Get members
    members = db.query(Member).filter(Member.organization_id == org_id).all()
    member_ids = [m.id for m in members]
    
    # Contributions
    contribs = db.query(Contribution).filter(Contribution.member_id.in_(member_ids)).all()
    total_in = sum(float(c.amount) for c in contribs)
    
    # Loans
    loans = db.query(Loan).filter(Loan.member_id.in_(member_ids), Loan.status == "APPROVED").all()
    total_loans = sum(float(l.principal_amount) for l in loans)
    
    return {
        "total_contributions": total_in,
        "total_loans_disbursed": total_loans,
        "available": total_in - total_loans,
        "member_count": len(members)
    }


# ============ Proposals ============

class Proposal(Base):
    __tablename__ = "proposals"
    id = Column(String, primary_key=True)
    organization_id = Column(String)
    title = Column(String)
    description = Column(Text)
    proposed_by = Column(String)
    status = Column(String, default="OPEN")  # "OPEN", "APPROVED", "REJECTED", "EXPIRED"
    deadline = Column(DateTime, nullable=True)
    quorum = Column(Integer, default=50) # Percentage
    created_at = Column(DateTime, default=datetime.utcnow)


class Vote(Base):
    __tablename__ = "votes"
    id = Column(String, primary_key=True)
    proposal_id = Column(String)
    member_id = Column(String)
    vote_type = Column(String)

# Create tables
Base.metadata.create_all(bind=engine)


class ProposalCreate(BaseModel):
    organization_id: str
    title: str
    description: str
    deadline_days: int = 7
    quorum: int = 50

@app.post("/proposals", response_model=dict)
def create_proposal(
    data: ProposalCreate,
    db=Depends(get_db),
    member=Depends(get_current_member)
):
    deadline = datetime.utcnow() + timedelta(days=data.deadline_days)
    proposal = Proposal(
        id=f"prp_{datetime.utcnow().timestamp()}",
        organization_id=data.organization_id,
        title=data.title,
        description=data.description,
        proposed_by=member.id,
        deadline=deadline,
        quorum=data.quorum,
        status="OPEN"
    )
    db.add(proposal)
    log_audit_event(db, data.organization_id, member.id, "CREATE_PROPOSAL", proposal.id, f"Created proposal: {data.title}")
    db.commit()
    return {"id": proposal.id, "status": "open", "deadline": deadline.isoformat()}


@app.get("/proposals/{org_id}", response_model=List[dict])
def list_proposals(org_id: str, db: Session = Depends(get_db)):
    props = db.query(Proposal).filter(Proposal.organization_id == org_id).all()
    return [{"id": p.id, "title": p.title, "status": p.status} for p in props]


@app.post("/proposals/{proposal_id}/vote")
def vote_proposal(
    proposal_id: str,
    vote_type: str,
    db=Depends(get_db),
    member=Depends(get_current_member)
):
    vote = Vote(
        id=f"vot_{datetime.utcnow().timestamp()}",
        proposal_id=proposal_id,
        member_id=member.id,
        vote_type=vote_type
    )
    db.add(vote)
    
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    org_id = proposal.organization_id if proposal else "UNKNOWN"
    log_audit_event(db, org_id, member.id, "VOTE_PROPOSAL", proposal_id, f"Voted {vote_type}")

    db.commit()
    return {"status": "voted"}

@app.post("/proposals/{proposal_id}/resolve")
def resolve_proposal(proposal_id: str, db: Session = Depends(get_db), member = Depends(require_roles(["CHAIR", "ADMIN"]))):
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    if proposal.status != "OPEN":
        raise HTTPException(status_code=400, detail="Proposal already resolved")

    # Count votes
    votes = db.query(Vote).filter(Vote.proposal_id == proposal_id).all()
    yes_votes = sum(1 for v in votes if v.vote_type == "YES")
    no_votes = sum(1 for v in votes if v.vote_type == "NO")
    
    # In a real app, we'd check against total members for quorum
    # For now, let's just use a simple majority rule
    if yes_votes > no_votes:
        proposal.status = "APPROVED"
    else:
        proposal.status = "REJECTED"
        
    log_audit_event(db, proposal.organization_id, member.id, "RESOLVE_PROPOSAL", proposal.id, f"Resolved as {proposal.status}. Yes: {yes_votes}, No: {no_votes}")
    db.commit()
    return {"status": proposal.status, "yes": yes_votes, "no": no_votes}


@app.get("/proposals/{proposal_id}/results", response_model=dict)
def get_proposal_results(proposal_id: str, db: Session = Depends(get_db)):
    votes = db.query(Vote).filter(Vote.proposal_id == proposal_id).all()
    return {
        "approve": sum(1 for v in votes if v.vote_type == "APPROVE"),
        "reject": sum(1 for v in votes if v.vote_type == "REJECT"),
        "abstain": sum(1 for v in votes if v.vote_type == "ABSTAIN")
    }


# ============ Audit Endpoints ============

@app.get("/audit/{org_id}", response_model=List[dict])
def list_audit_events(org_id: str, limit: int = 100, db: Session = Depends(get_db)):
    events = db.query(AuditEvent).filter(AuditEvent.organization_id == org_id).order_by(AuditEvent.created_at.desc()).limit(limit).all()
    return [{
        "id": e.id,
        "member_id": e.member_id,
        "action": e.action,
        "resource_id": e.resource_id,
        "details": e.details,
        "ip_address": e.ip_address,
        "created_at": e.created_at
    } for e in events]


@app.get("/reports/{org_id}/financial")
def get_financial_report(org_id: str, db: Session = Depends(get_db)):
    # Calculate totals
    total_contributions = db.query(func.sum(Contribution.amount)).filter(
        Contribution.organization_id == org_id,
        Contribution.status == "COMPLETED"
    ).scalar() or 0
    
    total_loans = db.query(func.sum(Loan.principal_amount)).filter(
        Loan.organization_id == org_id,
        Loan.status != "REJECTED"
    ).scalar() or 0
    
    # Member count
    member_count = db.query(Member).filter(Member.organization_id == org_id).count()
    
    # Audit events count
    audit_count = db.query(AuditEvent).filter(AuditEvent.organization_id == org_id).count()

    return {
        "organization_id": org_id,
        "generated_at": datetime.utcnow().isoformat(),
        "summary": {
            "total_contributions": float(total_contributions),
            "total_loans_disbursed": float(total_loans),
            "member_count": member_count,
            "activity_log_entries": audit_count,
            "net_balance": float(total_contributions) - float(total_loans)
        },
        "status": "Generated mockup financial statement"
    }


@app.get("/reports/{org_id}/wrapped")
def get_chama_wrapped(org_id: str, db: Session = Depends(get_db)):
    """Annual performance recap for the Chama"""
    total_savings = db.query(func.sum(Contribution.amount)).filter(Contribution.organization_id == org_id).scalar() or 0
    top_member = db.query(Member).filter(Member.organization_id == org_id).order_by(Member.moto_streak.desc()).first()
    loan_count = db.query(Loan).filter(Loan.organization_id == org_id).count()
    
    return {
        "year": datetime.utcnow().year,
        "total_savings": float(total_savings),
        "top_contributor": top_member.name if top_member else "None",
        "top_streak": top_member.moto_streak if top_member else 0,
        "loans_given": loan_count,
        "group_vibe": "MOTO 🔥" if total_savings > 100000 else "UPKEEPING 📈",
        "fun_fact": f"Your group is in the top 10% of Chamas in {org_id} region!"
    }


@app.get("/members/{member_id}/credit-score")
def get_member_credit_score(member_id: str, db: Session = Depends(get_db)):
    """Calculate an alternative credit score based on chama behavior"""
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
        
    # Calculate score base
    # Formula: (Trust Score * 0.6) + (Streak * 20) + (100 if active)
    score = (member.trust_score * 0.6) + (member.moto_streak * 20)
    
    # Cap at 850 (typical credit score max)
    final_score = min(850, score + 300) 
    
    tier = "EXCELLENT" if final_score > 750 else "GOOD" if final_score > 600 else "FAIR"
    
    return {
        "member_id": member_id,
        "name": member.name,
        "credit_score": int(final_score),
        "tier": tier,
        "factors": [
            "Consistent on-time contributions",
            f"Active {member.moto_streak} week streak",
            "High internal trust score"
        ]
    }

@app.get("/social-fund/{org_id}", response_model=dict)
def get_social_fund(org_id: str, db: Session = Depends(get_db)):
    fines = db.query(SocialFund).filter(
        SocialFund.organization_id == org_id,
        SocialFund.category == "FINE"
    ).all()
    total = sum(float(f.amount) for f in fines)
    return {
        "organization_id": org_id,
        "total_fines": total,
        "items": [{"id": f.id, "reason": f.reason, "amount": float(f.amount)} for f in fines]
    }

@app.post("/social-fund/fine")
def record_fine(org_id: str, member_id: str, amount: float, reason: str, db: Session = Depends(get_db), member_auth = Depends(require_roles(["CHAIR", "ADMIN"]))):
    fine = SocialFund(
        id=f"fin_{datetime.utcnow().timestamp()}",
        organization_id=org_id,
        member_id=member_id,
        amount=amount,
        reason=reason,
        category="FINE"
    )
    db.add(fine)
    log_audit_event(db, org_id, member_auth.id, "RECORD_FINE", fine.id, f"Fined {member_id} KES {amount} for {reason}")
    db.commit()
    return {"status": "recorded"}


@app.get("/marketplace/{org_id}")
def get_marketplace_items(org_id: str, db: Session = Depends(get_db)):
    """Browse items in the group marketplace"""
    items = db.query(MarketplaceItem, Member.name).join(
        Member, MarketplaceItem.member_id == Member.id
    ).filter(
        MarketplaceItem.organization_id == org_id,
        MarketplaceItem.status == "ACTIVE"
    ).all()
    
    return [
        {
            "id": i.MarketplaceItem.id,
            "title": i.MarketplaceItem.title,
            "description": i.MarketplaceItem.description,
            "price": float(i.MarketplaceItem.price),
            "category": i.MarketplaceItem.category,
            "seller_name": i.name,
            "member_id": i.MarketplaceItem.member_id,
            "created_at": i.MarketplaceItem.created_at
        } for i in items
    ]


@app.post("/marketplace/item")
def create_marketplace_item(item: MarketplaceItemCreate, db: Session = Depends(get_db)):
    """Post a new item to Soko"""
    new_item = MarketplaceItem(
        id=f"item_{datetime.utcnow().timestamp()}",
        **item.dict()
    )
    db.add(new_item)
    db.commit()
    return {"id": new_item.id, "status": "posted"}


@app.patch("/marketplace/items/{item_id}/status")
def update_item_status(item_id: str, status: str, db: Session = Depends(get_db)):
    """Mark item as sold or back to active"""
    item = db.query(MarketplaceItem).filter(MarketplaceItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.status = status
    db.commit()
    return {"status": "updated"}


@app.get("/harambees/{org_id}")
def get_harambees(org_id: str, db: Session = Depends(get_db)):
    """List all harambees for an organization"""
    return db.query(Harambee).filter(Harambee.organization_id == org_id).all()


@app.post("/harambees")
def create_harambee(harambee: HarambeeCreate, db: Session = Depends(get_db)):
    """Start a new emergency fund drive"""
    new_h = Harambee(
        id=f"har_{datetime.utcnow().timestamp()}",
        **harambee.dict()
    )
    db.add(new_h)
    db.commit()
    return {"id": new_h.id, "status": "started"}


@app.post("/harambees/{harambee_id}/contribute")
def contribute_to_harambee(harambee_id: str, member_id: str, amount: float, db: Session = Depends(get_db)):
    """Record a contribution to a harambee"""
    harambee = db.query(Harambee).filter(Harambee.id == harambee_id).first()
    if not harambee:
        raise HTTPException(status_code=404, detail="Harambee not found")
        
    contribution = HarambeeContribution(
        id=f"hcon_{datetime.utcnow().timestamp()}",
        harambee_id=harambee_id,
        member_id=member_id,
        amount=amount
    )
    
    harambee.current_amount += amount
    db.add(contribution)
    db.commit()
    return {"status": "success", "new_total": float(harambee.current_amount)}


@app.get("/investments/opportunities")
def get_investment_opportunities(db: Session = Depends(get_db)):
    """Browse verified MMFs and T-Bills"""
    # Seeding mock data if empty
    opps = db.query(InvestmentOpportunity).all()
    if not opps:
        mock_opps = [
            InvestmentOpportunity(id="opp_1", provider="Britam", title="Money Market Fund", description="Daily interest, high liquidity", annual_yield=12.5, min_amount=5000, category="MMF"),
            InvestmentOpportunity(id="opp_2", provider="NCBA", title="Fixed Deposit", description="Guaranteed returns for 1 year", annual_yield=11.0, min_amount=100000, category="FIXED"),
            InvestmentOpportunity(id="opp_3", provider="CBK", title="Infrastructure Bond", description="Tax-free government bond", annual_yield=14.2, min_amount=50000, category="T-BOND")
        ]
        db.add_all(mock_opps)
        db.commit()
        opps = db.query(InvestmentOpportunity).all()
    return opps


@app.post("/investments/invest")
def invest_group_funds(org_id: str, opp_id: str, amount: float, db: Session = Depends(get_db)):
    """Commit group wallet funds to an investment"""
    opp = db.query(InvestmentOpportunity).filter(InvestmentOpportunity.id == opp_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    investment = ChamaInvestment(
        id=f"inv_{datetime.utcnow().timestamp()}",
        organization_id=org_id,
        opportunity_id=opp_id,
        amount=amount
    )
    db.add(investment)
    # Log audit event
    log_audit_event(db, org_id, "SYSTEM", "INVEST_FUNDS", opp_id, f"Invested KES {amount} in {opp.title}")
    db.commit()
    return {"status": "invested", "id": investment.id}


@app.get("/investments/portfolio/{org_id}")
def get_group_portfolio(org_id: str, db: Session = Depends(get_db)):
    """List all active investments for a Chama"""
    investments = db.query(ChamaInvestment, InvestmentOpportunity).join(
        InvestmentOpportunity, ChamaInvestment.opportunity_id == InvestmentOpportunity.id
    ).filter(ChamaInvestment.organization_id == org_id).all()
    
    return [
        {
            "id": i.ChamaInvestment.id,
            "title": i.InvestmentOpportunity.title,
            "provider": i.InvestmentOpportunity.provider,
            "amount": float(i.ChamaInvestment.amount),
            "yield": i.InvestmentOpportunity.annual_yield,
            "status": i.ChamaInvestment.status,
            "created_at": i.ChamaInvestment.created_at
        } for i in investments
    ]


@app.get("/bourse/{org_id}")
def get_bourse_listings(org_id: str, db: Session = Depends(get_db)):
    """List open share listings for a Chama"""
    listings = db.query(ShareListing, Member.name).join(
        Member, ShareListing.seller_id == Member.id
    ).filter(
        ShareListing.organization_id == org_id,
        ShareListing.status == "OPEN"
    ).all()
    
    return [
        {
            "id": l.ShareListing.id,
            "seller_name": l.name,
            "shares": float(l.ShareListing.shares_count),
            "ask_price": float(l.ShareListing.ask_price),
            "created_at": l.ShareListing.created_at
        } for l in listings
    ]


@app.post("/bourse/list")
def list_shares_for_sale(data: ShareListingCreate, db: Session = Depends(get_db)):
    """Member wants to exit/sell their stake"""
    listing = ShareListing(
        id=f"sl_{datetime.utcnow().timestamp()}",
        **data.dict()
    )
    db.add(listing)
    db.commit()
    return {"id": listing.id, "status": "listed"}


@app.post("/bourse/bid")
def place_bid_on_shares(data: ShareBidCreate, db: Session = Depends(get_db)):
    """Another member wants to buy the shares"""
    bid = ShareBid(
        id=f"bid_{datetime.utcnow().timestamp()}",
        **data.dict()
    )
    db.add(bid)
    db.commit()
    return {"id": bid.id, "status": "bid_placed"}


@app.patch("/bourse/bids/{bid_id}/accept")
def accept_share_bid(bid_id: str, db: Session = Depends(get_db)):
    """Seller accepts the bid, transferring the 'stake'"""
    bid = db.query(ShareBid).filter(ShareBid.id == bid_id).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")
        
    listing = db.query(ShareListing).filter(ShareListing.id == bid.listing_id).first()
    listing.status = "SOLD"
    bid.status = "ACCEPTED"
    
    # In a real app, this would trigger ledger transfers
    db.commit()
    return {"status": "transferred"}


@app.get("/meetings/minutes/{org_id}")
def get_meeting_minutes(org_id: str, db: Session = Depends(get_db)):
    """Fetch all past meeting minutes"""
    return db.query(MeetingMinutes).filter(MeetingMinutes.organization_id == org_id).all()


@app.post("/meetings/minutes")
def create_meeting_minutes(org_id: str, title: str, summary: str, attendees: List[str], db: Session = Depends(get_db)):
    """Admins/Secretaries log minutes of the meeting"""
    import json
    new_m = MeetingMinutes(
        id=f"min_{datetime.utcnow().timestamp()}",
        organization_id=org_id,
        title=title,
        summary=summary,
        attendees=json.dumps(attendees)
    )
    db.add(new_m)
    db.commit()
    return {"id": new_m.id, "status": "saved"}


@app.post("/meetings/minutes/{minute_id}/sign")
def sign_meeting_minutes(minute_id: str, member_id: str, db: Session = Depends(get_db)):
    """Members digitally sign the minutes via OTP (logic simplified here)"""
    sig = MinuteSignature(
        id=f"sig_{datetime.utcnow().timestamp()}",
        minute_id=minute_id,
        member_id=member_id
    )
    db.add(sig)
    db.commit()
    return {"status": "signed"}


@app.get("/members/{member_id}/summary")
def get_member_portal_summary(member_id: str, db: Session = Depends(get_db)):
    """Personalized view for a member's own data"""
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
        
    contributions = db.query(Contribution).filter(Contribution.member_id == member_id).all()
    loans = db.query(Loan).filter(Loan.member_id == member_id).all()
    
    return {
        "member": {
            "name": member.name,
            "role": member.role,
            "trust_score": member.trust_score,
            "moto_streak": member.streak_count
        },
        "stats": {
            "total_contributed": sum(c.amount for c in contributions),
            "active_loans_count": len([l for l in loans if l.status == 'APPROVED']),
            "outstanding_loan_balance": sum(l.principal_amount for l in loans if l.status == 'APPROVED')
        },
        "recent_activity": contributions[-5:] # Last 5 contributions
    }


@app.post("/webhooks/whatsapp")
async def whatsapp_bot_webhook(data: dict):
    """Mock endpoint for WhatsApp/Telegram bot interactions"""
    # Logic to parse "Balance?", "My Loans?", etc.
    message = data.get("message", "").lower()
    if "balance" in message:
        return {"reply": "Your current Chama balance is KES 45,200. Type 'Statement' for details."}
    return {"reply": "Habari! I am your Chama AI Bot. Ask me about your balance, loans, or next meeting."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
