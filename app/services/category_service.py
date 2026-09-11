from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate
from app.repositories.category_repository import CategoryRepository


class CategoryService:
    """
    Service responsible for category business logic.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = CategoryRepository(db)

    def create_category(
        self,
        category_data: CategoryCreate
    ) -> Category:
        """
        Create a new category.
        """

        existing = self.repository.get_by_name(
            category_data.name
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Category already exists"
            )

        new_category = Category(
            name=category_data.name,
            description=category_data.description,
        )

        self.repository.create(new_category)

        self.db.commit()
        self.db.refresh(new_category)

        return new_category