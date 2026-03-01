from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.database import get_db
from app.models import Member, Contribution, Loan, Proposal
from app.core.security import get_current_member

router = APIRouter()


@router.get("/search")
def global_search(
    q: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Full-text search across all entities"""
    if not q or len(q) < 2:
        return {"error": "Query must be at least 2 characters"}
    
    org_id = current.organization_id
    results = {"members": [], "contributions": [], "loans": [], "proposals": []}
    
    # Search members
    members = db.query(Member).filter(
        Member.organization_id == org_id,
        or_(
            Member.name.ilike(f"%{q}%"),
            Member.phone.ilike(f"%{q}%")
        )
    ).limit(10).all()
    results["members"] = [
        {"id": m.id, "name": m.name, "phone": m.phone, "role": m.role}
        for m in members
    ]
    
    # Search contributions
    contributions = db.query(Contribution).filter(
        Contribution.organization_id == org_id,
        Contribution.note.ilike(f"%{q}%")
    ).limit(10).all()
    results["contributions"] = [
        {"id": c.id, "amount": float(c.amount), "note": c.note}
        for c in contributions
    ]
    
    # Search loans
    loans = db.query(Loan).filter(
        Loan.organization_id == org_id,
        or_(
            Loan.purpose.ilike(f"%{q}%")
        )
    ).limit(10).all()
    results["loans"] = [
        {"id": l.id, "amount": float(l.amount), "purpose": l.purpose, "status": l.status}
        for l in loans
    ]
    
    # Search proposals
    proposals = db.query(Proposal).filter(
        Proposal.organization_id == org_id,
        or_(
            Proposal.title.ilike(f"%{q}%"),
            Proposal.description.ilike(f"%{q}%")
        )
    ).limit(10).all()
    results["proposals"] = [
        {"id": p.id, "title": p.title, "status": p.status}
        for p in proposals
    ]
    
    return results
