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


@app.post("/wallets/{user_id}/fund")
async def fund_wallet(user_id: str, request: FundRequest):
    try:
        result = wallet_service.fund_wallet(user_id, request.currency, request.amount)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/wallets/{user_id}/convert")
async def convert_currency(user_id: str, request: ConvertRequest):
    try:
        result = wallet_service.convert_currency(
            user_id, 
            request.from_currency, 
            request.to_currency, 
            request.amount
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/wallets/{user_id}/withdraw")
async def withdraw_funds(user_id: str, request: WithdrawRequest):
    try:
        result = wallet_service.withdraw_funds(user_id, request.currency, request.amount)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/wallets/{user_id}/balances")
async def get_balances(user_id: str) -> Dict[str, Decimal]:
    return wallet_service.get_balances(user_id)

@app.get("/")
async def root():
    return {"message": "FX Payment Processor is running"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)