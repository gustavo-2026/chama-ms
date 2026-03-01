from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.database import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/health")
def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@router.get("/health/ready")
def readiness_check(db: Session = Depends(get_db)):
    """Readiness check - includes database"""
    try:
        # Try to query database
        db.execute("SELECT 1")
        db_status = "ready"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "ready" if db_status == "ready" else "not_ready",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health/live")
def liveness_check():
    """Liveness check - is the service running"""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/metrics")
def metrics(db: Session = Depends(get_db)):
    """Basic metrics endpoint (Prometheus format)"""
    try:
        # Get basic stats
        from app.models import Member, Contribution, Loan, Organization
        
        org_count = db.query(Organization).count()
        member_count = db.query(Member).count()
        contribution_count = db.query(Contribution).count()
        loan_count = db.query(Loan).count()
        
        metrics = f"""# HELP chama_organizations_total Total organizations
# TYPE chama_organizations_total gauge
chama_organizations_total {org_count}

# HELP chama_members_total Total members
# TYPE chama_members_total gauge
chama_members_total {member_count}

# HELP chama_contributions_total Total contributions
# TYPE chama_contributions_total counter
chama_contributions_total {contribution_count}

# HELP chama_loans_total Total loans
# TYPE chama_loans_total counter
chama_loans_total {loan_count}
"""
        return metrics
    except Exception as e:
        return f"# Error: {str(e)}"
