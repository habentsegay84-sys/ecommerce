from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.category import Category
from app.schemas.category import (
    CategoryCreate,
    CategoryResponse,
)

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=201,
)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
):
    existing = (
        db.query(Category)
        .filter(Category.name == category.name)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Category already exists"
        )

    new_category = Category(
        name=category.name,
        description=category.description,
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category