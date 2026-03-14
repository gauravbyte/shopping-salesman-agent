from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from . import models  # ensure all models are imported before create_all
from .routers import auth, products, cart, orders, payments

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Shopping Salesman API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(payments.router)


@app.get("/")
def root():
    return {"message": "Shopping Salesman API"}
