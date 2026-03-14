# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack ecommerce app: **FastAPI + SQLite** backend, **React + Vite** frontend. Designed with a clean service layer for future LangChain/LangGraph agent integration.

## Architecture

```
shopping-salesman-agent/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, router registration
│   │   ├── database.py          # SQLAlchemy engine + session factory
│   │   ├── dependencies.py      # get_db, get_current_user, get_current_admin
│   │   ├── core/
│   │   │   ├── config.py        # Settings via pydantic-settings (.env)
│   │   │   └── security.py      # bcrypt hashing, JWT encode/decode
│   │   ├── models/              # SQLAlchemy ORM models (User, Product, Category, Cart, Order)
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── services/            # Business logic (LangGraph agents hook here)
│   │   ├── routers/             # auth, products, cart, orders
│   │   └── ai/                  # Placeholder for LangChain/LangGraph agents
│   ├── requirements.txt
│   ├── seed.py                  # Seeds DB with 10 products, 5 categories, admin user
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── api/client.js        # Axios with JWT interceptor
    │   ├── context/             # AuthContext, CartContext
    │   ├── components/          # Navbar, ProductCard, ProtectedRoute
    │   └── pages/               # Home, Products, ProductDetail, Cart, Checkout, Orders, Login, Register
    ├── package.json
    ├── vite.config.js           # Proxy /api → localhost:8000
    └── index.html
```

## Dev Commands

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload     # API on :8000, Swagger at /docs
python seed.py                     # seed DB (admin@example.com / admin123)

# Frontend
cd frontend
npm install
npm run dev                        # dev server on :5173
```

## Key Conventions

- **JWT auth**: OAuth2PasswordBearer; token stored in `localStorage`; `get_current_user` dependency injects user
- **Admin**: `get_current_admin` dependency; seed creates `admin@example.com / admin123`
- **Service layer**: All business logic in `app/services/` — this is where LangChain tools plug in
- **Vite proxy**: `/api/*` → `http://localhost:8000/*` (strips `/api` prefix)
- **DB**: SQLite for dev (`shop.db`); change `DATABASE_URL` in `.env` for PostgreSQL migration
- **Cart**: One cart per user, created on first access; items cleared on order placement
- **Order creation**: Atomic — validates stock, snapshots price, decrements stock, clears cart

## LangGraph Integration Points (future)

- `backend/app/ai/` — add agent graphs here
- Service layer methods → LangChain `Tool` definitions
- New router `routers/ai.py` for agent endpoints
- No restructuring needed
