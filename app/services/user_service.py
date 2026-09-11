from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password


class UserService:
    """
    Service responsible for user business logic.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = UserRepository(db)

    def register_user(self, user_data: UserCreate) -> User:
        """
        Register a new user.
        """

        existing_username = self.repository.get_by_username(
            user_data.username
        )

        if existing_username:
            raise HTTPException(
                status_code=400,
                detail="Username already exists"
            )

        existing_email = self.repository.get_by_email(
            user_data.email
        )

        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="Email already exists"
            )

        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hash_password(user_data.password)
        )

        self.repository.create(new_user)

        self.db.commit()
        self.db.refresh(new_user)

        return new_user