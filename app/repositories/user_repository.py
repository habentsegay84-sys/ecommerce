from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """
    Repository responsible for user database operations.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        """
        Retrieve a user by ID.
        """
        return (
            self.db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    def get_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by email.
        """
        return (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )

    def get_by_username(self, username: str) -> User | None:
        """
        Retrieve a user by username.
        """
        return (
            self.db.query(User)
            .filter(User.username == username)
            .first()
        )

    def create(self, user: User) -> User:
        """
        Add a new user to the current transaction.
        """
        self.db.add(user)
        self.db.flush()
        return user