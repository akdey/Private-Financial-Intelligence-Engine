from typing import Annotated, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends
from app.features.auth.deps import get_current_user
from app.features.auth.models import User
from app.features.transactions import schemas
from app.features.transactions.service import TransactionService

router = APIRouter()

@router.get("/categories", response_model=schemas.CategoriesResponse)
async def get_categories(
    service: Annotated[TransactionService, Depends()]
):
    return {"categories": service.get_categories()}

@router.get("/pending", response_model=List[schemas.TransactionResponse])
async def get_pending_transactions(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[TransactionService, Depends()],
    skip: int = 0,
    limit: int = 100
):
    return await service.get_pending_transactions(user_id=current_user.id, skip=skip, limit=limit)

@router.post("/", response_model=schemas.TransactionResponse)
async def create_manual_transaction(
    data: schemas.ManualTransactionCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[TransactionService, Depends()]
):
    return await service.create_manual_transaction(user_id=current_user.id, data=data)

@router.patch("/{transaction_id}/verify", response_model=schemas.TransactionResponse)
async def verify_transaction(
    transaction_id: UUID,
    verification: schemas.VerificationRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[TransactionService, Depends()]
):
    return await service.verify_transaction(transaction_id=transaction_id, user_id=current_user.id, verification=verification)
