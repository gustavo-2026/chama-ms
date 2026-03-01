from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from decimal import Decimal
from app.db.database import get_db
from app.models import Member, Contribution, Loan, TransactionStatus, LoanStatus
from app.core.security import get_current_member
from io import BytesIO
import base64

router = APIRouter()


def generate_pdf_content(data: dict) -> str:
    """Generate HTML for PDF (using browser print or PDF library)"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{data.get('title', 'Report')}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #333; border-bottom: 2px solid #7C3AED; padding-bottom: 10px; }}
            h2 {{ color: #555; margin-top: 30px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            th {{ background-color: #7C3AED; color: white; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
            .summary-item {{ background: #f5f5f5; padding: 15px; border-radius: 8px; flex: 1; }}
            .summary-label {{ font-size: 12px; color: #666; }}
            .summary-value {{ font-size: 24px; font-weight: bold; color: #333; }}
            .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #999; }}
        </style>
    </head>
    <body>
        <h1>{data.get('title', 'Report')}</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        
        <div class="summary">
            {''.join([f'''
            <div class="summary-item">
                <div class="summary-label">{item['label']}</div>
                <div class="summary-value">{item['value']}</div>
            </div>
            ''' for item in data.get('summary', [])])}
        </div>
        
        {data.get('content', '')}
        
        <div class="footer">
            <p>Chama Treasury Management System</p>
        </div>
    </body>
    </html>
    """
    return html


@router.get("/report/contributions")
async def contributions_report(
    period_month: int = None,
    period_year: int = None,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Generate contributions report"""
    query = db.query(Contribution).filter(
        Contribution.organization_id == current.organization_id,
        Contribution.status == TransactionStatus.COMPLETED
    )
    
    if period_month:
        query = query.filter(Contribution.period_month == period_month)
    if period_year:
        query = query.filter(Contribution.period_year == period_year)
    
    contributions = query.all()
    
    # Group by member
    member_totals = {}
    for c in contributions:
        if c.member_id not in member_totals:
            member_totals[c.member_id] = 0
        member_totals[c.member_id] += float(c.amount)
    
    total = sum(member_totals.values())
    
    # Get member names
    member_ids = list(member_totals.keys())
    members = db.query(Member).filter(Member.id.in_(member_ids)).all()
    member_names = {m.id: m.name for m in members}
    
    # Build table
    rows = []
    for mid, amount in sorted(member_totals.items(), key=lambda x: -x[1]):
        rows.append(f"<tr><td>{member_names.get(mid, 'Unknown')}</td><td>KES {amount:,.2f}</td></tr>")
    
    content = f"""
    <h2>Contribution Details</h2>
    <table>
        <tr><th>Member</th><th>Amount</th></tr>
        {''.join(rows)}
    </table>
    """
    
    html = generate_pdf_content({
        "title": "Contributions Report",
        "summary": [
            {"label": "Total Members", "value": len(member_totals)},
            {"label": "Total Contributions", "value": f"KES {total:,.2f}"}
        ],
        "content": content
    })
    
    return {"html": html, "type": "contributions"}


@router.get("/report/loans")
async def loans_report(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Generate loans report"""
    loans = db.query(Loan).filter(
        Loan.organization_id == current.organization_id
    ).all()
    
    active = [l for l in loans if l.status == LoanStatus.ACTIVE]
    pending = [l for l in loans if l.status == LoanStatus.PENDING]
    paid = [l for l in loans if l.status == LoanStatus.PAID]
    
    total_outstanding = sum(float(l.amount) for l in active)
    total_pending = sum(float(l.amount) for l in pending)
    
    # Get member names
    member_ids = list(set(l.member_id for l in loans))
    members = db.query(Member).filter(Member.id.in_(member_ids)).all()
    member_names = {m.id: m.name for m in members}
    
    rows = []
    for l in loans:
        rows.append(f"<tr><td>{member_names.get(l.member_id, 'Unknown')}</td><td>KES {float(l.amount):,.2f}</td><td>{l.status}</td></tr>")
    
    content = f"""
    <h2>Loan Details</h2>
    <table>
        <tr><th>Member</th><th>Amount</th><th>Status</th></tr>
        {''.join(rows)}
    </table>
    """
    
    html = generate_pdf_content({
        "title": "Loans Report",
        "summary": [
            {"label": "Active Loans", "value": len(active)},
            {"label": "Pending", "value": len(pending)},
            {"label": "Outstanding", "value": f"KES {total_outstanding:,.2f}"}
        ],
        "content": content
    })
    
    return {"html": html, "type": "loans"}


@router.get("/report/treasury")
async def treasury_report(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Generate treasury summary report"""
    org_id = current.organization_id
    
    # Contributions
    contributions = db.query(Contribution).filter(
        Contribution.organization_id == org_id,
        Contribution.status == TransactionStatus.COMPLETED
    ).all()
    total_contributions = sum(float(c.amount) for c in contributions)
    
    # Loans
    loans = db.query(Loan).filter(
        Loan.organization_id == org_id,
        Loan.status == LoanStatus.ACTIVE
    ).all()
    total_loans = sum(float(l.amount) for l in loans)
    
    # Member count
    member_count = db.query(Member).filter(Member.organization_id == org_id).count()
    
    # Available
    available = total_contributions - total_loans
    
    content = f"""
    <h2>Treasury Details</h2>
    <p>This report shows the financial position of the chama as of {datetime.now().strftime('%Y-%m-%d')}.</p>
    """
    
    html = generate_pdf_content({
        "title": "Treasury Summary Report",
        "summary": [
            {"label": "Total Capital", "value": f"KES {total_contributions:,.2f}"},
            {"label": "Available", "value": f"KES {available:,.2f}"},
            {"label": "Locked in Loans", "value": f"KES {total_loans:,.2f}"},
            {"label": "Members", "value": str(member_count)}
        ],
        "content": content
    })
    
    return {"html": html, "type": "treasury"}


@router.get("/report/member/{member_id}")
async def member_statement(
    member_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Generate individual member statement"""
    # Verify member belongs to org
    member = db.query(Member).filter(
        Member.id == member_id,
        Member.organization_id == current.organization_id
    ).first()
    
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Contributions
    contributions = db.query(Contribution).filter(
        Contribution.member_id == member_id,
        Contribution.status == TransactionStatus.COMPLETED
    ).all()
    total_contributed = sum(float(c.amount) for c in contributions)
    
    # Loans
    loans = db.query(Loan).filter(
        Loan.member_id == member_id
    ).all()
    active_loans = [l for l in loans if l.status == LoanStatus.ACTIVE]
    total_borrowed = sum(float(l.amount) for l in loans)
    
    cont_rows = []
    for c in contributions:
        cont_rows.append(f"<tr><td>{c.created_at.strftime('%Y-%m-%d')}</td><td>Contribution</td><td>KES {float(c.amount):,.2f}</td></tr>")
    
    content = f"""
    <h2>Member: {member.name}</h2>
    <p>Phone: {member.phone}</p>
    <p>Role: {member.role}</p>
    
    <h3>Contributions</h3>
    <table>
        <tr><th>Date</th><th>Type</th><th>Amount</th></tr>
        {''.join(cont_rows)}
    </table>
    
    <h3>Loans</h3>
    <p>Total Borrowed: KES {total_borrowed:,.2f}</p>
    <p>Active Loans: {len(active_loans)}</p>
    """
    
    html = generate_pdf_content({
        "title": f"Member Statement - {member.name}",
        "summary": [
            {"label": "Total Contributed", "value": f"KES {total_contributed:,.2f}"},
            {"label": "Total Borrowed", "value": f"KES {total_borrowed:,.2f}"},
            {"label": "Active Loans", "value": str(len(active_loans))}
        ],
        "content": content
    })
    
    return {"html": html, "type": "member_statement"}
