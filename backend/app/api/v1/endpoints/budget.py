from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from pydantic import BaseModel
from datetime import datetime
from app.db.database import get_db
from app.models import Member
from app.models import BudgetCategory, Budget, Expense
from app.core.security import get_current_member

router = APIRouter()


# ============ BUDGET CATEGORIES ============

class BudgetCategoryCreate(BaseModel):
    name: str
    description: str = None


class BudgetCategoryResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    description: str = None
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/budget-categories", response_model=List[BudgetCategoryResponse])
def list_categories(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """List budget categories"""
    return db.query(BudgetCategory).filter(
        BudgetCategory.organization_id == current.organization_id
    ).all()


@router.post("/budget-categories", response_model=BudgetCategoryResponse)
def create_category(
    category: BudgetCategoryCreate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Create budget category (Chair/Treasurer only)"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_category = BudgetCategory(
        organization_id=current.organization_id,
        name=category.name,
        description=category.description
    )
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


# ============ BUDGETS ============

class BudgetCreate(BaseModel):
    year: str
    month: str
    category: str
    planned: float


class BudgetResponse(BaseModel):
    id: str
    organization_id: str
    year: str
    month: str
    category: str
    planned: float
    actual: float
    
    class Config:
        from_attributes = True


@router.get("/budgets", response_model=List[BudgetResponse])
def list_budgets(
    year: str = None,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """List budgets"""
    query = db.query(Budget).filter(
        Budget.organization_id == current.organization_id
    )
    if year:
        query = query.filter(Budget.year == year)
    return query.all()


@router.post("/budgets", response_model=BudgetResponse)
def create_budget(
    budget: BudgetCreate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Create budget (Chair/Treasurer only)"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_budget = Budget(
        organization_id=current.organization_id,
        year=budget.year,
        month=budget.month,
        category=budget.category,
        planned=budget.planned
    )
    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)
    return new_budget


@router.get("/budgets/vs-actual")
def budget_vs_actual(
    year: str = None,
    month: str = None,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Budget vs Actual report"""
    budgets = db.query(Budget).filter(
        Budget.organization_id == current.organization_id
    )
    if year:
        budgets = budgets.filter(Budget.year == year)
    if month:
        budgets = budgets.filter(Budget.month == month)
    
    results = []
    for b in budgets.all():
        results.append({
            "category": b.category,
            "planned": float(b.planned),
            "actual": float(b.actual),
            "variance": float(b.planned) - float(b.actual),
            "variance_pct": round((float(b.planned) - float(b.actual)) / float(b.planned) * 100, 1) if b.planned > 0 else 0
        })
    
    return results


# ============ EXPENSES ============

class ExpenseCreate(BaseModel):
    category_id: str = None
    description: str
    amount: float
    receipt_url: str = None


class ExpenseResponse(BaseModel):
    id: str
    organization_id: str
    member_id: str
    category_id: str = None
    description: str
    amount: float
    receipt_url: str = None
    approved: str
    date: datetime
    
    class Config:
        from_attributes = True


@router.get("/expenses", response_model=List[ExpenseResponse])
def list_expenses(
    approved: str = None,
    category_id: str = None,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """List expenses"""
    query = db.query(Expense).filter(
        Expense.organization_id == current.organization_id
    )
    if approved:
        query = query.filter(Expense.approved == approved)
    if category_id:
        query = query.filter(Expense.category_id == category_id)
    return query.order_by(Expense.date.desc()).all()


@router.post("/expenses", response_model=ExpenseResponse)
def create_expense(
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Create expense claim"""
    new_expense = Expense(
        organization_id=current.organization_id,
        member_id=current.id,
        category_id=expense.category_id,
        description=expense.description,
        amount=expense.amount,
        receipt_url=expense.receipt_url
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense


@router.patch("/expenses/{expense_id}/approve")
def approve_expense(
    expense_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Approve expense (Chair/Treasurer only)"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.organization_id == current.organization_id
    ).first()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    expense.approved = "APPROVED"
    expense.approved_by = current.id
    expense.approved_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Expense approved"}


@router.patch("/expenses/{expense_id}/reject")
def reject_expense(
    expense_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Reject expense"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.organization_id == current.organization_id
    ).first()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    expense.approved = "REJECTED"
    db.commit()
    
    return {"message": "Expense rejected"}
