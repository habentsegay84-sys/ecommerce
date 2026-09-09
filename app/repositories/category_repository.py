from sqlalchemy.orm import Session

from app.models.category import Category


class CategoryRepository:
    """
    Repository responsible for category database operations.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, category_id: int) -> Category | None:
        """
        Retrieve a category by its ID.
        """
        return (
            self.db.query(Category)
            .filter(Category.id == category_id)
            .first()
        )