from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from app.models import ProductCreate, ProductResponse, ProductUpdate
from app import database

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure CouchDB database exists
    database.ensure_database_exists()
    yield

app = FastAPI(
    title="NoSQL Cloud Store API (Apache CouchDB)",
    description="A high-performance NoSQL Document Database API built with FastAPI, Apache CouchDB, and deployed via automated CI/CD pipelines.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["General"])
def read_root():
    return {
        "status": "Online",
        "service": "NoSQL Cloud Store API",
        "database": "Apache CouchDB (Document NoSQL)",
        "docs_url": "/docs",
        "health_url": "/health"
    }

@app.get("/health", tags=["General"])
def health_check():
    db_ok = database.ensure_database_exists(max_retries=2, delay=1)
    if not db_ok:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="CouchDB service unreachable"
        )
    return {"status": "healthy", "database": "connected"}

@app.get("/products", response_model=List[ProductResponse], tags=["Products"])
def list_products(limit: int = Query(50, ge=1, le=100), skip: int = Query(0, ge=0)):
    return database.get_all_documents(limit=limit, skip=skip)

@app.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, tags=["Products"])
def create_product(product: ProductCreate):
    return database.create_document(product.model_dump())

@app.get("/products/{product_id}", response_model=ProductResponse, tags=["Products"])
def get_product(product_id: str):
    product = database.get_document_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID '{product_id}' not found")
    return product

@app.put("/products/{product_id}", response_model=ProductResponse, tags=["Products"])
def update_product(product_id: str, product_update: ProductUpdate):
    update_data = {k: v for k, v in product_update.model_dump().items() if v is not None}
    updated = database.update_document(product_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Product with ID '{product_id}' not found")
    return updated

@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Products"])
def delete_product(product_id: str):
    success = database.delete_document(product_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Product with ID '{product_id}' not found")
    return None

@app.get("/products/category/{category_name}", response_model=List[ProductResponse], tags=["Products"])
def query_by_category(category_name: str, limit: int = Query(50, ge=1, le=100)):
    return database.find_by_category(category_name, limit=limit)

@app.post("/products/seed", tags=["Seeding"])
def seed_sample_data():
    sample_products = [
        {
            "name": "MacBook Pro 16",
            "category": "Laptops",
            "price": 2499.00,
            "stock": 15,
            "tags": ["apple", "laptop", "m3-max", "workstation"],
            "specs": {"cpu": "M3 Max", "ram_gb": 64, "storage_tb": 2, "screen": "Liquid Retina XDR"},
            "status": "active"
        },
        {
            "name": "Dell XPS 15",
            "category": "Laptops",
            "price": 1899.99,
            "stock": 20,
            "tags": ["dell", "laptop", "windows", "creator"],
            "specs": {"cpu": "Intel Core i9", "ram_gb": 32, "storage_tb": 1, "screen": "OLED 3.5K"},
            "status": "active"
        },
        {
            "name": "Sony WH-1000XM5",
            "category": "Audio",
            "price": 399.99,
            "stock": 45,
            "tags": ["sony", "audio", "anc", "bluetooth"],
            "specs": {"battery_hours": 30, "driver_mm": 30, "codec": ["LDAC", "AAC", "SBC"]},
            "status": "active"
        },
        {
            "name": "Logitech MX Master 3S",
            "category": "Accessories",
            "price": 99.99,
            "stock": 70,
            "tags": ["logitech", "mouse", "ergonomic", "productivity"],
            "specs": {"dpi": 8000, "sensor": "Darkfield", "rechargeable": True},
            "status": "active"
        }
    ]
    
    created = []
    for item in sample_products:
        res = database.create_document(item)
        created.append(res)
        
    return {"message": "Database seeded successfully", "inserted_count": len(created), "items": created}
