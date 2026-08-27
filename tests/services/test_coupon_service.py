import pytest

from app.models.coupon import Coupon
from app.schemas.coupon import (
    CouponCreate,
    CouponUpdate,
)

from app.services.coupon_service import (
    create_coupon_service,
    list_coupons_service,
    update_coupon_service,
    delete_coupon_service,
)


# ============================================================
# Create coupon
# ============================================================

def test_create_coupon_service_success(db):
    """
    Verify that the service creates a new active coupon
    when the coupon code does not already exist.
    """

    coupon_data = CouponCreate(
        code="SUMMER30",
        discount_percent=30,
    )

    coupon = create_coupon_service(
        db=db,
        coupon_data=coupon_data,
    )

    assert coupon.id is not None
    assert coupon.code == "SUMMER30"
    assert coupon.discount_percent == 30
    assert coupon.active is True


def test_create_coupon_service_rejects_duplicate_code(db):
    """
    Verify that duplicate coupon codes are rejected
    before another coupon is created.
    """

    existing_coupon = Coupon(
        code="SUMMER30",
        discount_percent=30,
        active=True,
    )

    db.add(existing_coupon)
    db.commit()

    coupon_data = CouponCreate(
        code="SUMMER30",
        discount_percent=20,
    )

    with pytest.raises(ValueError) as exc_info:
        create_coupon_service(
            db=db,
            coupon_data=coupon_data,
        )

    assert str(exc_info.value) == "Coupon code already exists."


# ============================================================
# List coupons
# ============================================================

def test_list_coupons_service_success(db):
    """
    Verify that the service returns all coupons.
    """

    coupon_one = Coupon(
        code="SUMMER30",
        discount_percent=30,
        active=True,
    )

    coupon_two = Coupon(
        code="WINTER20",
        discount_percent=20,
        active=True,
    )

    db.add_all(
        [
            coupon_one,
            coupon_two,
        ]
    )

    db.commit()

    coupons = list_coupons_service(
        db=db,
    )

    assert len(coupons) == 2
    assert coupons[0].code in {
        "SUMMER30",
        "WINTER20",
    }


def test_list_coupons_service_empty(db):
    """
    Verify that listing coupons returns an empty list
    when no coupons exist.
    """

    coupons = list_coupons_service(
        db=db,
    )

    assert coupons == []


# ============================================================
# Update coupon
# ============================================================

def test_update_coupon_service_success(db):
    """
    Verify that an existing coupon can be updated.
    """

    coupon = Coupon(
        code="SUMMER30",
        discount_percent=30,
        active=True,
    )

    db.add(coupon)
    db.commit()
    db.refresh(coupon)

    update_data = CouponUpdate(
        discount_percent=40,
    )

    updated_coupon = update_coupon_service(
        db=db,
        coupon_id=coupon.id,
        coupon_data=update_data,
    )

    assert updated_coupon.discount_percent == 40
    assert updated_coupon.code == "SUMMER30"


def test_update_coupon_service_partial_update(db):
    """
    Verify that only fields supplied by the client
    are modified.
    """

    coupon = Coupon(
        code="SUMMER30",
        discount_percent=30,
        active=True,
    )

    db.add(coupon)
    db.commit()
    db.refresh(coupon)

    update_data = CouponUpdate(
        active=False,
    )

    updated_coupon = update_coupon_service(
        db=db,
        coupon_id=coupon.id,
        coupon_data=update_data,
    )

    assert updated_coupon.active is False
    assert updated_coupon.code == "SUMMER30"
    assert updated_coupon.discount_percent == 30


def test_update_coupon_service_missing_coupon(db):
    """
    Verify that updating a nonexistent coupon raises
    the expected business error.
    """

    update_data = CouponUpdate(
        discount_percent=50,
    )

    with pytest.raises(ValueError) as exc_info:
        update_coupon_service(
            db=db,
            coupon_id=9999,
            coupon_data=update_data,
        )

    assert str(exc_info.value) == "Coupon not found."


# ============================================================
# Delete coupon
# ============================================================

def test_delete_coupon_service_success(db):
    """
    Verify that an existing coupon can be deleted.
    """

    coupon = Coupon(
        code="SUMMER30",
        discount_percent=30,
        active=True,
    )

    db.add(coupon)
    db.commit()
    db.refresh(coupon)

    delete_coupon_service(
        db=db,
        coupon_id=coupon.id,
    )

    deleted_coupon = (
        db.query(Coupon)
        .filter(Coupon.id == coupon.id)
        .first()
    )

    assert deleted_coupon is None


def test_delete_coupon_service_missing_coupon(db):
    """
    Verify that deleting a nonexistent coupon raises
    the expected business error.
    """

    with pytest.raises(ValueError) as exc_info:
        delete_coupon_service(
            db=db,
            coupon_id=9999,
        )

    assert str(exc_info.value) == "Coupon not found."