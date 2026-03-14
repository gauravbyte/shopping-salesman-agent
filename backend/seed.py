"""Seed the database with sample categories and products."""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.database import engine, SessionLocal, Base
from app import models  # noqa: registers all models
from app.models.product import Category, Product
from app.models.user import User
from app.core.security import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Categories
categories_data = [
    {"name": "Electronics", "slug": "electronics"},
    {"name": "Clothing", "slug": "clothing"},
    {"name": "Books", "slug": "books"},
    {"name": "Home & Garden", "slug": "home-garden"},
    {"name": "Sports", "slug": "sports"},
]

categories = {}
for cat_data in categories_data:
    cat = db.query(Category).filter(Category.slug == cat_data["slug"]).first()
    if not cat:
        cat = Category(**cat_data)
        db.add(cat)
        db.flush()
    categories[cat_data["slug"]] = cat

# Products
products_data = [
    {
        "name": "Wireless Headphones",
        "description": "Premium noise-cancelling wireless headphones with 30hr battery life.",
        "price": 79.99,
        "stock": 50,
        "image_url": "https://placehold.co/400x300?text=Headphones",
        "category_slug": "electronics",
    },
    {
        "name": "Smart Watch",
        "description": "Track your fitness, notifications, and more.",
        "price": 199.99,
        "stock": 30,
        "image_url": "https://placehold.co/400x300?text=Smart+Watch",
        "category_slug": "electronics",
    },
    {
        "name": "USB-C Hub",
        "description": "7-in-1 USB-C hub with HDMI, USB 3.0, SD card reader.",
        "price": 39.99,
        "stock": 100,
        "image_url": "https://placehold.co/400x300?text=USB-C+Hub",
        "category_slug": "electronics",
    },
    {
        "name": "Classic T-Shirt",
        "description": "100% cotton unisex classic fit t-shirt.",
        "price": 19.99,
        "stock": 200,
        "image_url": "https://placehold.co/400x300?text=T-Shirt",
        "category_slug": "clothing",
    },
    {
        "name": "Denim Jacket",
        "description": "Vintage wash denim jacket, slim fit.",
        "price": 59.99,
        "stock": 75,
        "image_url": "https://placehold.co/400x300?text=Denim+Jacket",
        "category_slug": "clothing",
    },
    {
        "name": "Running Shoes",
        "description": "Lightweight breathable running shoes with cushioned sole.",
        "price": 89.99,
        "stock": 60,
        "image_url": "https://placehold.co/400x300?text=Running+Shoes",
        "category_slug": "sports",
    },
    {
        "name": "Python Programming",
        "description": "Comprehensive guide to Python 3 programming for all levels.",
        "price": 34.99,
        "stock": 150,
        "image_url": "https://placehold.co/400x300?text=Python+Book",
        "category_slug": "books",
    },
    {
        "name": "The Pragmatic Programmer",
        "description": "Classic software engineering book, 20th anniversary edition.",
        "price": 44.99,
        "stock": 80,
        "image_url": "https://placehold.co/400x300?text=Pragmatic+Programmer",
        "category_slug": "books",
    },
    {
        "name": "Indoor Plant Pot",
        "description": "Minimalist ceramic pot, 6-inch, ideal for succulents.",
        "price": 14.99,
        "stock": 120,
        "image_url": "https://placehold.co/400x300?text=Plant+Pot",
        "category_slug": "home-garden",
    },
    {
        "name": "Yoga Mat",
        "description": "Non-slip eco-friendly yoga mat, 6mm thick.",
        "price": 29.99,
        "stock": 90,
        "image_url": "https://placehold.co/400x300?text=Yoga+Mat",
        "category_slug": "sports",
    },
]

for p_data in products_data:
    slug = p_data.pop("category_slug")
    p_data["category_id"] = categories[slug].id
    if not db.query(Product).filter(Product.name == p_data["name"]).first():
        db.add(Product(**p_data))

# Admin user
if not db.query(User).filter(User.email == "admin@example.com").first():
    db.add(User(
        email="admin@example.com",
        hashed_password=hash_password("admin123"),
        full_name="Admin User",
        is_admin=True,
    ))

db.commit()
db.close()
print("Database seeded successfully.")
print("  Admin: admin@example.com / admin123")
