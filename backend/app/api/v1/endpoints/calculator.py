from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from decimal import Decimal

router = APIRouter()


class LoanCalculatorRequest(BaseModel):
    principal: Decimal
    interest_rate: Decimal  # Annual rate in %
    term_months: int
    repayment_frequency: str = "monthly"  # weekly, biweekly, monthly


class AmortizationEntry(BaseModel):
    period: int
    payment: float
    principal: float
    interest: float
    balance: float


class LoanCalculatorResponse(BaseModel):
    principal: float
    interest_rate: float
    term_months: int
    monthly_payment: float
    total_interest: float
    total_payment: float
    amortization: List[AmortizationEntry]


@router.post("/loan-calculator", response_model=LoanCalculatorResponse)
def calculate_loan(request: LoanCalculatorRequest):
    """Calculate loan amortization schedule"""
    P = float(request.principal)
    annual_rate = float(request.interest_rate) / 100
    n = request.term_months
    
    # Monthly interest rate
    r = annual_rate / 12
    
    if r == 0:
        # No interest case
        monthly_payment = P / n
    else:
        # Standard amortization formula
        monthly_payment = P * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    
    # Generate amortization schedule
    balance = P
    amortization = []
    total_interest = 0
    
    for period in range(1, n + 1):
        interest_payment = balance * r
        principal_payment = monthly_payment - interest_payment
        balance -= principal_payment
        
        if balance < 0:
            balance = 0
        
        amortization.append(AmortizationEntry(
            period=period,
            payment=round(monthly_payment, 2),
            principal=round(principal_payment, 2),
            interest=round(interest_payment, 2),
            balance=round(balance, 2)
        ))
        
        total_interest += interest_payment
    
    return LoanCalculatorResponse(
        principal=P,
        interest_rate=annual_rate * 100,
        term_months=n,
        monthly_payment=round(monthly_payment, 2),
        total_interest=round(total_interest, 2),
        total_payment=round(P + total_interest, 2),
        amortization=amortization
    )


@router.get("/loan-eligibility")
def check_eligibility(
    contribution_amount: float,
    months_member: int,
    existing_loans: float = 0
):
    """Check basic loan eligibility"""
    # Simple eligibility rules
    # 1. Must be member for at least 3 months
    # 2. Contribution should be at least 1000 KES
    # 3. No existing defaulted loans
    
    eligible = True
    reasons = []
    
    if months_member < 3:
        eligible = False
        reasons.append("Must be member for at least 3 months")
    
    if contribution_amount < 1000:
        eligible = False
        reasons.append("Monthly contribution should be at least KES 1,000")
    
    if existing_loans > 0:
        # In production, check loan status
        pass
    
    # Calculate max loan amount (3x annual contribution)
    max_loan = contribution_amount * 12 * 3
    
    return {
        "eligible": eligible,
        "reasons": reasons,
        "suggested_max_loan": max_loan
    }


@router.get("/interest-rates")
def get_interest_rates():
    """Get standard interest rates"""
    return {
        "standard": 10,  # 10% per year
        "emergency": 15,  # 15% for emergency loans
        "members": {
            "regular": 10,
            "silver": 8,
            "gold": 6
        }
    }
