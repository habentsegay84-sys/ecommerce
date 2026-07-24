from fastapi import Depends, HTTPException

from app.auth.dependencies import get_current_user
from app.models.user import User


def get_current_admin(
    current_user: User = Depends(get_current_user),
):
    """
    Ensure the authenticated user has administrator privileges.
    """

    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    return current_user