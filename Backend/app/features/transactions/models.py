import uuid
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import String, ForeignKey, Numeric, ARRAY, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.features.transactions.enums import Category, SubCategory, TransactionStatus, AccountType
from app.features.auth.models import User

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    raw_content_hash: Mapped[str] = mapped_column(String, unique=True, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    currency: Mapped[str] = mapped_column(String, default="INR")
    merchant_name: Mapped[str] = mapped_column(String, nullable=True)
    category: Mapped[Category] = mapped_column(String) # Storing as String for simplicity in DB, handled as Enum in Pydantic usually, or use SQLAlchemy Enum type. Using String is often safer for migrations.
    sub_category: Mapped[SubCategory] = mapped_column(String)
    status: Mapped[TransactionStatus] = mapped_column(String, default=TransactionStatus.PENDING)
    account_type: Mapped[AccountType] = mapped_column(String, default=AccountType.SAVINGS)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship()

class MerchantMapping(Base):
    __tablename__ = "merchant_mappings"

    raw_merchant: Mapped[str] = mapped_column(String, primary_key=True) # Assuming raw_merchant is unique enough or use UUID
    display_name: Mapped[str] = mapped_column(String)
    default_category: Mapped[Category] = mapped_column(String)
    default_sub_category: Mapped[SubCategory] = mapped_column(String)
