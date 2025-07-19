from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Dict, List, Optional
from datetime import datetime
import uvicorn

from wallet_service import WalletService, Transaction, TransactionType

app = FastAPI(title="FX Payment Processor", version="1.0.0")

wallet_service = WalletService()

class FundRequest(BaseModel):
    currency: str = Field(..., min_length=3, max_length=3)
    amount: Decimal = Field(..., gt=0)


class ConvertRequest(BaseModel):
    from_currency: str = Field(..., min_length=3, max_length=3)
    to_currency: str = Field(..., min_length=3, max_length=3)
    amount: Decimal = Field(..., gt=0)


class WithdrawRequest(BaseModel):
    currency: str = Field(..., min_length=3, max_length=3)
    amount: Decimal = Field(..., gt=0)


class TransactionResponse(BaseModel):
    id: str
    user_id: str
    type: str
    currency: str
    amount: Decimal
    timestamp: datetime
    description: str
    from_currency: Optional[str] = None
    to_currency: Optional[str] = None
    exchange_rate: Optional[Decimal] = None


class ReconciliationResponse(BaseModel):
    current_balances: Dict[str, Decimal]
    calculated_balances: Dict[str, Decimal]
    balanced: bool
