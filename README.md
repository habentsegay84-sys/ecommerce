# E-Commerce Backend API

A production-oriented E-Commerce backend API built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**, **Alembic**, and **Docker**.

The project follows a clean layered architecture using:

```
API Layer → Service Layer → Repository Layer → Database
```

This separation improves maintainability, testing, and scalability.

---

# Features

## User Management

* User registration
* User authentication
* JWT-based authorization
* Role-based access control
* Admin and normal user roles

Roles:

* `user`
* `admin`

---

# Product Management

## Customer Features

* View products
* Search products
* Filter by category
* Filter by price range
* Sort products by price
* Pagination
* View product details
* View product ratings

## Admin Features

* Create products
* Update products
* Soft delete products
* Restore deleted products
* Manage product inventory

---

# Category Management

Products are organized into categories.

Features:

* Create categories
* Assign products to categories
* Filter products by category

---

# Shopping Cart

Users can:

* Add products to cart
* Update quantities
* Remove items
* View cart contents

The cart belongs to a specific user.

---

# Order Management

Users can:

* Checkout cart items
* Create orders
* View order history
* View order details
* Track order status

Order workflow:

```
Pending
   ↓
Processing
   ↓
Completed
```

---

# Coupon System

Users can apply discount coupons during checkout.

Features:

* Create coupons
* Validate coupon codes
* Check expiration date
* Apply percentage discounts
* Store used coupon information in orders

Example:

```
SUMMER30 → 30% discount
```

---

# Review System

Users can review products.

Features:

* Add product ratings
* Add comments
* Calculate average rating
* Count reviews

Product responses include:

```
average_rating
review_count
```

---

# Inventory Management

The system tracks stock changes.

Features:

* Update stock
* Validate available quantity
* Record inventory history

Each inventory change stores:

* Product
* Old stock
* New stock
* Change type
* Admin who performed the update
* Timestamp

---

# Payment System

Features:

* Create payments
* Prevent duplicate payments
* Track payment status
* Update order status after successful payment
* Generate transaction references

Payment statuses:

```
pending
processing
successful
failed
```

---

# Architecture

The project uses a layered architecture.

## API Layer

Location:

```
app/api/
```

Responsible for:

* HTTP requests
* Validation
* Authentication
* Returning responses

Example:

```
app/api/products.py
```

---

## Service Layer

Location:

```
app/services/
```

Responsible for:

* Business logic
* Validation rules
* Workflow handling

Examples:

```
product_service.py
order_service.py
payment_service.py
inventory_service.py
```

---

## Repository Layer

Location:

```
app/repositories/
```

Responsible for:

* Database queries
* CRUD operations
* Persistence

Examples:

```
product_repository.py
order_repository.py
payment_repository.py
```

---

# Project Structure

```
app/
│
├── api/
│   ├── products.py
│   ├── orders.py
│   ├── payments.py
│   └── admin/
│
├── services/
│   ├── product_service.py
│   ├── order_service.py
│   ├── payment_service.py
│   └── inventory_service.py
│
├── repositories/
│   ├── product_repository.py
│   ├── order_repository.py
│   └── payment_repository.py
│
├── models/
│   ├── user.py
│   ├── product.py
│   ├── order.py
│   └── payment.py
│
├── schemas/
│
├── database/
│
├── auth/
│
└── main.py
```

---

# Database

Database:

```
PostgreSQL
```

ORM:

```
SQLAlchemy
```

Migration tool:

```
Alembic
```

Main tables:

```
users
categories
products
reviews
carts
cart_items
orders
order_items
coupons
payments
inventory_logs
order_status_history
```

---

# Authentication

Authentication uses:

```
JWT Bearer Token
```

Protected endpoints require:

```
Authorization: Bearer <token>
```

Authorization levels:

User:

* Cart
* Orders
* Payments
* Reviews

Admin:

* Products
* Inventory
* Payments
* Order management

---

# Running the Project

## Clone repository

```bash
git clone <repository-url>
```

Go into project:

```bash
cd ecommerce
```

---

## Create virtual environment

```bash
python -m venv venv
```

Activate:

Windows:

```bash
venv\Scripts\activate
```

---

## Install dependencies

```bash
pip install -r requirements.txt
```

---

## Database migration

Run:

```bash
alembic upgrade head
```

---

## Start server

```bash
uvicorn app.main:app --reload
```

API:

```
http://localhost:8000
```

Swagger documentation:

```
http://localhost:8000/docs
```

---

# Docker

The project uses Docker for containerized development.

Services:

```
FastAPI Application
PostgreSQL Database
```

Run:

```bash
docker compose up
```

---

# Testing

Run tests:

```bash
pytest
```

Current tests cover:

* Authentication
* Products
* Orders
* Payments
* Business logic

---

# Development Workflow

The project follows:

```
Feature
 ↓
Model
 ↓
Migration
 ↓
Repository
 ↓
Service
 ↓
API
 ↓
Test
 ↓
Git Commit
```

---

# Future Improvements

Possible improvements:

* Add refresh tokens
* Add email verification
* Add product images
* Add payment gateway integration
* Add Redis caching
* Add background tasks
* Add CI/CD pipeline
* Deploy using cloud services

---

# Author

Developed as a Computer Science and Engineering backend project.

Technologies:

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* Docker
* Alembic
* JWT Authentication
