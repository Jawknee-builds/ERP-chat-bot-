from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Customer(BaseModel):
    id: Optional[str] = Field(None, description="The unique identifier for the customer")
    name: str = Field(..., description="The name of the customer")
    email: Optional[str] = Field(None, description="The email of the customer")
    created_at: Optional[datetime] = Field(None, description="The creation date of the customer")

class Product(BaseModel):
    id: Optional[str] = Field(None, description="The unique identifier for the product")
    name: str = Field(..., description="The name of the product")
    price: Optional[float] = Field(None, description="The price of the product")
    currency: Optional[str] = Field("USD", description="The currency of the price")

class Invoice(BaseModel):
    id: Optional[str] = Field(None, description="The unique identifier for the invoice")
    customer_id: str = Field(..., description="The ID of the customer who owns the invoice")
    total_amount: float = Field(..., description="Total amount of the invoice")
    status: str = Field(..., description="The status of the invoice (e.g., PAID, UNPAID)")
    issued_at: Optional[datetime] = Field(None, description="The date when the invoice was issued")
