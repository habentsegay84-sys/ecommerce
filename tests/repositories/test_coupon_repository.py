from app.models.coupon import Coupon
from app.repositories.coupon_repository import CouponRepository
from datetime import datetime, timedelta, timezone


def test_get_coupon_by_code(db):
    """
    Verify that a coupon can be retrieved using its unique code.
    """

    coupon = Coupon(
        code="SUMMER30",
        discount_percent=30,
        active=True,
    )

    db.add(coupon)
    db.commit()
    db.refresh(coupon)

    repository = CouponRepository(db)

    result = repository.get_by_code(
        "SUMMER30",
    )

    assert result is not None
    assert result.id == coupon.id
    assert result.code == "SUMMER30"
    assert result.discount_percent == 30

def test_create_coupon(db):
    """
    Verify that the repository persists a new coupon
    and returns the refreshed database object.
    """

    repository = CouponRepository(db)

    coupon = Coupon(
        code="WINTER20",
        discount_percent=20,
        active=True,
    )

    result = repository.create(
        coupon,
    )

    assert result.id is not None
    assert result.code == "WINTER20"
    assert result.discount_percent == 20

    stored_coupon = (
        db.query(Coupon)
        .filter(Coupon.id == result.id)
        .first()
    )

    assert stored_coupon is not None
    assert stored_coupon.code == "WINTER20"

def test_update_coupon(db):
    """
    Verify that the repository persists changes made
    to an existing coupon.
    """

    coupon = Coupon(
        code="SUMMER30",
        discount_percent=30,
        active=True,
    )

    db.add(coupon)
    db.commit()
    db.refresh(coupon)

    repository = CouponRepository(db)

    coupon.discount_percent = 50
    coupon.active = False

    result = repository.update(
        coupon,
    )

    assert result.id == coupon.id
    assert result.discount_percent == 50
    assert result.active is False

    stored_coupon = (
        db.query(Coupon)
        .filter(Coupon.id == coupon.id)
        .first()
    )

    assert stored_coupon.discount_percent == 50
    assert stored_coupon.active is False

def test_list_all_coupons_orders_newest_first(db):
    """
    Verify that coupons are returned in descending creation order.
    """

    first_coupon = Coupon(
        code="FIRST10",
        discount_percent=10,
        active=True,
    )

    db.add(first_coupon)
    db.commit()
    db.refresh(first_coupon)

    second_coupon = Coupon(
        code="SECOND20",
        discount_percent=20,
        active=True,
    )

    db.add(second_coupon)
    db.commit()
    db.refresh(second_coupon)

    repository = CouponRepository(db)

    result = repository.list_all()

    assert len(result) == 2

    assert result[0].id == second_coupon.id
    assert result[1].id == first_coupon.id

def test_get_coupon_by_id(db):
    """
    Verify that a coupon can be retrieved using its primary key.
    """

    coupon = Coupon(
        code="IDTEST20",
        discount_percent=20,
        active=True,
    )

    db.add(coupon)
    db.commit()
    db.refresh(coupon)

    repository = CouponRepository(db)

    result = repository.get_by_id(
        coupon.id,
    )

    assert result is not None
    assert result.id == coupon.id
    assert result.code == "IDTEST20"

def test_delete_coupon(db):
    """
    Verify that an existing coupon can be removed
    from the database.
    """

    coupon = Coupon(
        code="DELETE10",
        discount_percent=10,
        active=True,
    )

    db.add(coupon)
    db.commit()
    db.refresh(coupon)

    repository = CouponRepository(db)

    repository.delete(coupon)

    result = (
        db.query(Coupon)
        .filter(Coupon.id == coupon.id)
        .first()
    )

    assert result is None

def test_get_valid_coupon_returns_active_non_expired_coupon(db):
    """
    Verify that an active, non-expired coupon is returned.
    """

    coupon = Coupon(
        code="VALID20",
        discount_percent=20,
        active=True,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )

    db.add(coupon)
    db.commit()
    db.refresh(coupon)

    repository = CouponRepository(db)

    result = repository.get_valid_coupon(
        "VALID20",
    )

    assert result is not None
    assert result.id == coupon.id
    assert result.code == "VALID20"

def test_get_valid_coupon_returns_none_for_inactive_coupon(db):
    """
    Verify that an inactive coupon is rejected.
    """

    coupon = Coupon(
        code="INACTIVE20",
        discount_percent=20,
        active=False,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )

    db.add(coupon)
    db.commit()
    db.refresh(coupon)

    repository = CouponRepository(db)

    result = repository.get_valid_coupon(
        "INACTIVE20",
    )

    assert result is None

def test_get_valid_coupon_returns_none_for_expired_coupon(db):
    """
    Verify that an expired coupon is rejected.
    """

    coupon = Coupon(
        code="EXPIRED20",
        discount_percent=20,
        active=True,
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),
    )

    db.add(coupon)
    db.commit()
    db.refresh(coupon)

    repository = CouponRepository(db)

    result = repository.get_valid_coupon(
        "EXPIRED20",
    )

    assert result is None

def test_get_valid_coupon_returns_coupon_without_expiration(db):
    """
    Verify that an active coupon with no expiration
    date is considered valid.
    """

    coupon = Coupon(
        code="NOEXPIRY20",
        discount_percent=20,
        active=True,
        expires_at=None,
    )

    db.add(coupon)
    db.commit()
    db.refresh(coupon)

    repository = CouponRepository(db)

    result = repository.get_valid_coupon(
        "NOEXPIRY20",
    )

    assert result is not None
    assert result.id == coupon.id
    assert result.code == "NOEXPIRY20"

