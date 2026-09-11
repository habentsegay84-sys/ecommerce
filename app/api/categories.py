from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.category import (
    CategoryCreate,
    CategoryResponse,
)
from app.auth.admin import get_current_admin
from app.models.user import User
from app.services.category_service import CategoryService


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
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    service = CategoryService(db)

    return service.create_category(category)