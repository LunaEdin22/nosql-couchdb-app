from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ProductBase(BaseModel):
    name: str = Field(..., example="UltraBook Pro 15")
    category: str = Field(..., example="Laptops")
    price: float = Field(..., gt=0, example=1299.99)
    stock: int = Field(default=10, ge=0, example=25)
    tags: List[str] = Field(default_factory=list, example=["electronics", "computers", "portable"])
    specs: Dict[str, Any] = Field(
        default_factory=dict,
        example={"cpu": "Intel Core i7", "ram_gb": 32, "storage_tb": 1}
    )
    status: str = Field(default="active", example="active")

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    tags: Optional[List[str]] = None
    specs: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class ProductResponse(ProductBase):
    id: str
    rev: str
