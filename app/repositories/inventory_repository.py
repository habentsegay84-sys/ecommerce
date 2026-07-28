from sqlalchemy.orm import Session

from app.models.inventory import InventoryLog
from sqlalchemy.orm import joinedload


class InventoryRepository:
    """
    Repository for inventory history.
    """

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create_log(
        self,
        log: InventoryLog,
    ):
        """
        Save an inventory log.
        """

        self.db.add(log)

    def list_logs(self):
        """
        Retrieve inventory logs ordered
        by newest first.
        """

        return (
            self.db.query(InventoryLog)
            .options(
                joinedload(InventoryLog.product)
            )
            .order_by(
                InventoryLog.created_at.desc()
            )
            .all()
        )