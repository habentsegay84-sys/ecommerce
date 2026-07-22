from fastapi import FastAPI
from sqlalchemy import text

from app.database.base import Base
from app.database.db import engine
from app.api.users import router as users_router
from app.api.auth import router as auth_router
from app.api.categories import router as categories_router
from app.api.products import router as products_router
from app.api.cart import router as cart_router
from app.api.orders import router as orders_router
from app.api.admin.products import router as admin_products_router
from app.api.admin.inventory import router as inventory_router
from app.api.admin.inventory import router as admin_inventory_router
from app.api.admin.orders import router as admin_orders_router
from app.api.payments import router as payments_router
from app.api.admin.payments import router as admin_payments_router

import app.models

app = FastAPI()

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(products_router)
app.include_router(cart_router)
app.include_router(orders_router)
app.include_router(admin_products_router)
app.include_router(inventory_router)
app.include_router(admin_inventory_router)
app.include_router(admin_orders_router)
app.include_router(payments_router)
app.include_router(admin_payments_router)

@app.get("/")
def home():
    return {
        "message": "E-Commerce API Running"
    }


@app.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception as e:
        return {
            "status": "error",
            "database": str(e)
        }

