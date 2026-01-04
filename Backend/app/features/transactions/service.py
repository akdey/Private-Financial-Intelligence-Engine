from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from fastapi import Depends
from app.features.transactions.models import Transaction, MerchantMapping
from app.features.transactions import schemas
from app.features.transactions.enums import TransactionStatus
from app.core.database import get_db
import logging
logger = logging.getLogger(__name__)

class TransactionService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def get_pending_transactions(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Transaction]:
        stmt = (
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .where(Transaction.status == TransactionStatus.PENDING)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def verify_transaction(self, transaction_id: UUID, user_id: UUID, verification: schemas.VerificationRequest) -> Transaction:
        stmt = select(Transaction).where(Transaction.id == transaction_id, Transaction.user_id == user_id)
        result = await self.db.execute(stmt)
        txn = result.scalar_one_or_none()
        
        if not txn:
            raise HTTPException(status_code=404, detail="Transaction not found")

        if not verification.approved:
            txn.status = TransactionStatus.REJECTED
        else:
            txn.status = TransactionStatus.VERIFIED
            txn.category = verification.category
            txn.sub_category = verification.sub_category
            
            raw_merchant_key = txn.merchant_name 
            txn.merchant_name = verification.merchant_name
            
            mapping_stmt = select(MerchantMapping).where(MerchantMapping.raw_merchant == raw_merchant_key)
            mapping_result = await self.db.execute(mapping_stmt)
            existing_mapping = mapping_result.scalar_one_or_none()
            
            if existing_mapping:
                 existing_mapping.display_name = verification.merchant_name
                 existing_mapping.default_category = verification.category
                 existing_mapping.default_sub_category = verification.sub_category
            else:
                 self.db.add(MerchantMapping(
                     raw_merchant=raw_merchant_key or "UNKNOWN",
                     display_name=verification.merchant_name,
                     default_category=verification.category,
                     default_sub_category=verification.sub_category
                 ))
                 
        await self.db.commit()
        await self.db.refresh(txn)
        return txn

    async def get_merchant_mapping(self, raw_merchant: str) -> Optional[MerchantMapping]:
        stmt = select(MerchantMapping).where(MerchantMapping.raw_merchant == raw_merchant)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_transaction_by_hash(self, content_hash: str) -> Optional[Transaction]:
        stmt = select(Transaction).where(Transaction.raw_content_hash == content_hash)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_transaction(self, txn_data: dict) -> Transaction:
        txn = Transaction(**txn_data)
        self.db.add(txn)
        await self.db.commit()
        return txn

    async def create_manual_transaction(self, user_id: UUID, data: schemas.ManualTransactionCreate) -> Transaction:
        import hashlib
        import time
        import uuid
        
        seed = f"MANUAL-{user_id}-{time.time()}"
        content_hash = hashlib.sha256(seed.encode()).hexdigest()
        
        txn_data = data.model_dump()
        txn_data.update({
            "id": uuid.uuid4(),
            "user_id": user_id,
            "raw_content_hash": content_hash,
            "status": TransactionStatus.VERIFIED
        })
        
        return await self.create_transaction(txn_data)

    def get_categories(self) -> dict:
        from app.features.transactions.enums import CATEGORY_MAP
        return {cat.value: [sub.value for sub in subs] for cat, subs in CATEGORY_MAP.items()}
