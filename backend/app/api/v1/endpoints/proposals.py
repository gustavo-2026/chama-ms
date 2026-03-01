from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models import Member, Proposal, Vote, ProposalStatus
from app.schemas.schemas import ProposalCreate, ProposalUpdate, ProposalResponse, VoteRequest, VoteResponse

router = APIRouter()


def get_current_member(db: Session = Depends(get_db)):
    member = db.query(Member).first()
    if not member:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return member


@router.get("/", response_model=List[ProposalResponse])
def list_proposals(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """List all proposals"""
    proposals = db.query(Proposal).filter(
        Proposal.organization_id == current.organization_id
    ).order_by(Proposal.created_at.desc()).all()
    return proposals


@router.post("/", response_model=ProposalResponse, status_code=status.HTTP_201_CREATED)
def create_proposal(
    proposal: ProposalCreate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Create a new proposal"""
    new_proposal = Proposal(
        organization_id=current.organization_id,
        title=proposal.title,
        description=proposal.description,
        proposal_type=proposal.proposal_type,
        status=ProposalStatus.DRAFT,
    )
    db.add(new_proposal)
    db.commit()
    db.refresh(new_proposal)
    return new_proposal


@router.patch("/{proposal_id}", response_model=ProposalResponse)
def update_proposal(
    proposal_id: str,
    update: ProposalUpdate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Update proposal status"""
    proposal = db.query(Proposal).filter(
        Proposal.id == proposal_id,
        Proposal.organization_id == current.organization_id
    ).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    # Check role for publishing
    if update.status == ProposalStatus.PUBLISHED:
        if current.role not in ["TREASURER", "CHAIR"]:
            raise HTTPException(status_code=403, detail="Not authorized to publish")
        proposal.voting_starts = datetime.utcnow()
        proposal.voting_ends = datetime.utcnow() + timedelta(days=3)  # 3 days voting
    
    if update.status:
        proposal.status = update.status
    if update.voting_starts:
        proposal.voting_starts = update.voting_starts
    if update.voting_ends:
        proposal.voting_ends = update.voting_ends
    
    db.commit()
    db.refresh(proposal)
    return proposal


@router.post("/{proposal_id}/vote", response_model=VoteResponse)
def vote(
    proposal_id: str,
    vote: VoteRequest,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Cast a vote on a proposal"""
    proposal = db.query(Proposal).filter(
        Proposal.id == proposal_id,
        Proposal.organization_id == current.organization_id
    ).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    # Check voting period
    if proposal.status != ProposalStatus.VOTING:
        raise HTTPException(status_code=400, detail="Voting is not open")
    
    now = datetime.utcnow()
    if now < (proposal.voting_starts or now) or now > (proposal.voting_ends or now):
        raise HTTPException(status_code=400, detail="Voting period has ended")
    
    # Check if already voted
    existing = db.query(Vote).filter(
        Vote.proposal_id == proposal_id,
        Vote.member_id == current.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already voted")
    
    # Record vote
    new_vote = Vote(
        proposal_id=proposal_id,
        member_id=current.id,
        choice=vote.choice
    )
    db.add(new_vote)
    
    # Check if voting should close (all members voted)
    member_count = db.query(Member).filter(
        Member.organization_id == current.organization_id
    ).count()
    vote_count = db.query(Vote).filter(Vote.proposal_id == proposal_id).count()
    
    if vote_count >= member_count:
        # Count votes
        yes_count = db.query(Vote).filter(
            Vote.proposal_id == proposal_id,
            Vote.choice == "YES"
        ).count()
        
        # Majority passes
        if yes_count > (member_count / 2):
            proposal.status = ProposalStatus.PASSED
        else:
            proposal.status = ProposalStatus.REJECTED
    
    db.commit()
    db.refresh(new_vote)
    return new_vote
