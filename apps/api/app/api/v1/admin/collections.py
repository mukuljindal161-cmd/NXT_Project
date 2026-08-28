import re
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Collection, User
from app.schemas import CollectionCreate, CollectionUpdate, CollectionResponse
from app.dependencies import require_admin

router = APIRouter(prefix="/admin/collections", tags=["Admin Collections"])


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-')


@router.get("", response_model=List[CollectionResponse])
def list_collections(
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    return db.query(Collection).order_by(Collection.name.asc()).all()


@router.post("", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
def create_collection(
    payload: CollectionCreate,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    slug = payload.slug or slugify(payload.name)
    existing = db.query(Collection).filter(Collection.slug == slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Collection with slug '{slug}' already exists."
        )

    col = Collection(
        name=payload.name,
        slug=slug,
        description=payload.description,
        department=payload.department,
        is_active=True
    )
    db.add(col)
    db.commit()
    db.refresh(col)
    return col


@router.get("/{collection_id}", response_model=CollectionResponse)
def get_collection(
    collection_id: UUID,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    col = db.query(Collection).filter(Collection.id == collection_id).first()
    if not col:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")
    return col


@router.patch("/{collection_id}", response_model=CollectionResponse)
def update_collection(
    collection_id: UUID,
    payload: CollectionUpdate,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    col = db.query(Collection).filter(Collection.id == collection_id).first()
    if not col:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")

    if payload.name is not None:
        col.name = payload.name
    if payload.description is not None:
        col.description = payload.description
    if payload.department is not None:
        col.department = payload.department
    if payload.is_active is not None:
        col.is_active = payload.is_active

    db.commit()
    db.refresh(col)
    return col


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collection(
    collection_id: UUID,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    col = db.query(Collection).filter(Collection.id == collection_id).first()
    if not col:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")
    db.delete(col)
    db.commit()
    return None
