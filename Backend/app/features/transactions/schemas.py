from typing import List, Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from app.features.transactions.enums import Category, SubCategory, TransactionStatus, AccountType

class TransactionBase(BaseModel):
    amount: Decimal
    currency: str = "INR"
    merchant_name: Optional[str] = None
    category: Category
    sub_category: SubCategory
    status: TransactionStatus = TransactionStatus.PENDING
    account_type: AccountType = AccountType.SAVINGS
    remarks: Optional[str] = None
    tags: Optional[List[str]] = []

class TransactionCreate(TransactionBase):
    raw_content_hash: str

class ManualTransactionCreate(BaseModel):
    amount: Decimal
    currency: str = "INR"
    merchant_name: str
    category: Category
    sub_category: SubCategory
    account_type: AccountType = AccountType.SAVINGS
    remarks: Optional[str] = None

class TransactionUpdate(BaseModel):
    # Used for verification/updates
    category: Optional[Category] = None
    sub_category: Optional[SubCategory] = None
    merchant_name: Optional[str] = None
    status: Optional[TransactionStatus] = None
    remarks: Optional[str] = None
    tags: Optional[List[str]] = None

class TransactionResponse(TransactionBase):
    id: UUID
    user_id: UUID
    raw_content_hash: str
    created_at: datetime

    class Config:
        from_attributes = True

class VerificationRequest(BaseModel):
    category: Category
    sub_category: SubCategory
    merchant_name: str # Confirmed merchant name to save to mapping
    approved: bool # If False -> REJECTED

class CategoriesResponse(BaseModel):
    categories: dict[str, list[str]]
