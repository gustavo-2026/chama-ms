from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.models import Member
from app.core.security import get_current_member

router = APIRouter()


class AssetCreate(BaseModel):
    name: str
    description: str = None
    category: str
    purchase_date: datetime = None
    purchase_value: float
    current_value: float = None
    depreciation_rate: float = 0
    location: str = None
    serial_number: str = None
    notes: str = None


class AssetUpdate(BaseModel):
    name: str = None
    description: str = None
    status: str = None
    current_value: float = None
    depreciation_rate: float = None
    location: str = None
    notes: str = None


class AssetResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    description: str = None
    category: str
    status: str
    purchase_date: datetime = None
    purchase_value: float
    current_value: float
    depreciation_rate: float
    location: str = None
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/assets", response_model=List[AssetResponse])
def list_assets(
    category: str = None,
    status: str = "ACTIVE",
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """List all assets"""
    query = db.query(Asset).filter(Asset.organization_id == current.organization_id)
    
    if category:
        query = query.filter(Asset.category == category)
    if status:
        query = query.filter(Asset.status == status)
    
    return query.order_by(Asset.created_at.desc()).all()


@router.get("/assets/{asset_id}", response_model=AssetResponse)
def get_asset(
    asset_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Get asset details"""
    asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.organization_id == current.organization_id
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    return asset


@router.post("/assets", response_model=AssetResponse, status_code=201)
def create_asset(
    asset: AssetCreate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Create asset (Chair/Treasurer only)"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_asset = Asset(
        organization_id=current.organization_id,
        name=asset.name,
        description=asset.description,
        category=asset.category,
        purchase_date=asset.purchase_date,
        purchase_value=asset.purchase_value,
        current_value=asset.current_value or asset.purchase_value,
        depreciation_rate=asset.depreciation_rate,
        location=asset.location,
        serial_number=asset.serial_number,
        notes=asset.notes
    )
    db.add(new_asset)
    db.commit()
    db.refresh(new_asset)
    return new_asset


@router.patch("/assets/{asset_id}", response_model=AssetResponse)
def update_asset(
    asset_id: str,
    asset_update: AssetUpdate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Update asset"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.organization_id == current.organization_id
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Update fields
    for field, value in asset_update.model_dump(exclude_unset=True).items():
        setattr(asset, field, value)
    
    db.commit()
    db.refresh(asset)
    return asset


@router.delete("/assets/{asset_id}")
def delete_asset(
    asset_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Delete asset"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.organization_id == current.organization_id
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    db.delete(asset)
    db.commit()
    
    return {"message": "Asset deleted"}


@router.get("/assets/summary")
def assets_summary(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Get asset summary by category"""
    assets = db.query(Asset).filter(
        Asset.organization_id == current.organization_id,
        Asset.status == AssetStatus.ACTIVE
    ).all()
    
    by_category = {}
    total_value = 0
    
    for asset in assets:
        cat = asset.category.value if hasattr(asset.category, 'value') else asset.category
        value = float(asset.current_value or 0)
        
        if cat not in by_category:
            by_category[cat] = {"count": 0, "total_value": 0}
        
        by_category[cat]["count"] += 1
        by_category[cat]["total_value"] += value
        total_value += value
    
    return {
        "total_assets": len(assets),
        "total_value": total_value,
        "by_category": by_category
    }


@router.post("/assets/{asset_id}/valuation")
def add_valuation(
    asset_id: str,
    value: float,
    notes: str = None,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Add asset valuation"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.organization_id == current.organization_id
    ).first()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Create valuation record
    valuation = AssetValuation(
        asset_id=asset_id,
        value=value,
        notes=notes
    )
    db.add(valuation)
    
    # Update current value
    asset.current_value = value
    db.commit()
    
    return {"message": "Valuation added", "new_value": value}
