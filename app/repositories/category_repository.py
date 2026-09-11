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

    def get_by_name(self, name: str) -> Category | None:
        """
        Retrieve a category by name.
        """
        return (
            self.db.query(Category)
            .filter(Category.name == name)
            .first()
        )

    def create(self, category: Category) -> Category:
        """
        Add a new category to the current transaction.
        """
        self.db.add(category)
        self.db.flush()
        return category