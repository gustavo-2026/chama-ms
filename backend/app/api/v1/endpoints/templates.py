from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.db.database import get_db
from app.models import Member, ChamaTemplate
from app.core.security import get_current_member

router = APIRouter()


class TemplateCreate(BaseModel):
    name: str
    description: str = None
    category: str = "general"
    settings: Dict[str, Any] = {}
    features: Dict[str, bool] = {}
    primary_color: str = "#7C3AED"
    logo_url: str = None
    is_public: bool = True


class TemplateResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: str = None
    category: str
    settings: dict
    features: dict
    primary_color: str
    is_public: bool
    usage_count: str
    
    class Config:
        from_attributes = True


# === CHAMA TEMPLATES ===

@router.get("/templates", response_model=List[TemplateResponse])
def list_templates(
    category: str = None,
    featured: bool = False,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """List available chama templates"""
    query = db.query(ChamaTemplate)
    
    if category:
        query = query.filter(ChamaTemplate.category == category)
    if featured:
        query = query.filter(ChamaTemplate.is_featured == True)
    else:
        query = query.filter(ChamaTemplate.is_public == True)
    
    return query.order_by(ChamaTemplate.usage_count.desc()).all()


@router.get("/templates/{template_id}", response_model=TemplateResponse)
def get_template(
    template_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Get template details"""
    template = db.query(ChamaTemplate).filter(ChamaTemplate.id == template_id).first()
    
    if not template:
        # Check if slug
        template = db.query(ChamaTemplate).filter(ChamaTemplate.slug == template_id).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return template


@router.post("/templates", response_model=TemplateResponse)
def create_template(
    template: TemplateCreate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Create a new chama template"""
    import secrets
    slug = f"{template.name.lower().replace(' ', '-')}-{secrets.token_hex(4)}"
    
    new_template = ChamaTemplate(
        name=template.name,
        slug=slug,
        description=template.description,
        category=template.category,
        settings=template.settings,
        features=template.features,
        primary_color=template.primary_color,
        logo_url=template.logo_url,
        is_public=template.is_public
    )
    db.add(new_template)
    db.commit()
    db.refresh(new_template)
    
    return new_template


@router.patch("/templates/{template_id}", response_model=TemplateResponse)
def update_template(
    template_id: str,
    template_update: TemplateCreate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Update template"""
    # Only platform admins can update
    if current.role != "CHAIR":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    template = db.query(ChamaTemplate).filter(ChamaTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    for field, value in template_update.model_dump().items():
        if value is not None:
            setattr(template, field, value)
    
    db.commit()
    db.refresh(template)
    return template


@router.delete("/templates/{template_id}")
def delete_template(
    template_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Delete template"""
    if current.role != "CHAIR":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    template = db.query(ChamaTemplate).filter(ChamaTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db.delete(template)
    db.commit()
    
    return {"message": "Template deleted"}


@router.post("/templates/seed")
def seed_default_templates(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Seed default templates"""
    if current.role != "CHAIR":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    created = 0
    for slug, config in DEFAULT_TEMPLATES.items():
        # Check if exists
        existing = db.query(ChamaTemplate).filter(ChamaTemplate.slug == slug).first()
        if existing:
            continue
        
        template = ChamaTemplate(
            name=config["name"],
            slug=slug,
            description=config["description"],
            category=config.get("category", "general"),
            settings=config.get("settings", {}),
            features=config.get("features", {}),
            primary_color=config.get("primary_color", "#7C3AED"),
            is_public=True,
            is_featured=True
        )
        db.add(template)
        created += 1
    
    db.commit()
    return {"message": f"Created {created} default templates"}


@router.get("/templates/{template_id}/config")
def get_template_config(
    template_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Get full template configuration for creating a chama"""
    template = db.query(ChamaTemplate).filter(ChamaTemplate.id == template_id).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Increment usage
    template.usage_count = str(int(template.usage_count or 0) + 1)
    db.commit()
    
    return {
        "name": template.name,
        "description": template.description,
        "category": template.category,
        "settings": template.settings,
        "features": template.features,
        "branding": {
            "primary_color": template.primary_color,
            "logo_url": template.logo_url
        }
    }


@router.get("/templates/categories")
def list_categories():
    """List available template categories"""
    return [
        {"id": "savings", "name": "Savings Group", "description": "Regular chama for saving"},
        {"id": "investment", "name": "Investment Club", "description": "Focus on group investments"},
        {"id": "welfare", "name": "Welfare Group", "description": "Emergency support and mutual aid"},
        {"id": "business", "name": "Business Chama", "description": "Entrepreneurs and business owners"},
        {"id": "general", "name": "General", "description": "General purpose"}
    ]
