from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class TransactionType(Enum):
    FUND = "fund"
    CONVERT = "convert"
    WITHDRAW = "withdraw"


@dataclass
class Transaction:
    id: str
    user_id: str
    type: TransactionType
    currency: str
    amount: Decimal
    timestamp: datetime
    description: str
    from_currency: Optional[str] = None
    to_currency: Optional[str] = None
    exchange_rate: Optional[Decimal] = None


class WalletService:
    def __init__(self):
        self.wallets: Dict[str, Dict[str, Decimal]] = {}
        self.transactions: Dict[str, List[Transaction]] = {}
        self.fx_rates = {
            ("USD", "MXN"): Decimal("18.70"),
            ("MXN", "USD"): Decimal("0.053")
        }
        self.transaction_counter = 0
    
    def _get_precision(self, currency: str) -> int:
        return 2  # Standard for USD and MXN
    
    def _round_amount(self, amount: Decimal, currency: str) -> Decimal:
        precision = self._get_precision(currency)
        return amount.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)
    
    def _ensure_wallet_exists(self, user_id: str):
        if user_id not in self.wallets:
            self.wallets[user_id] = {}
        if user_id not in self.transactions:
            self.transactions[user_id] = []
    
    def _get_balance(self, user_id: str, currency: str) -> Decimal:
        self._ensure_wallet_exists(user_id)
        return self.wallets[user_id].get(currency, Decimal("0"))
    
    def _set_balance(self, user_id: str, currency: str, amount: Decimal):
        self._ensure_wallet_exists(user_id)
        rounded_amount = self._round_amount(amount, currency)
        if rounded_amount == Decimal("0"):
            self.wallets[user_id].pop(currency, None)
        else:
            self.wallets[user_id][currency] = rounded_amount
    
    def _add_transaction(self, user_id: str, transaction: Transaction):
        self._ensure_wallet_exists(user_id)
        self.transactions[user_id].append(transaction)
    
    def _generate_transaction_id(self) -> str:
        self.transaction_counter += 1
        return f"tx_{self.transaction_counter:06d}"
    
    def fund_wallet(self, user_id: str, currency: str, amount: Decimal) -> Dict:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        current_balance = self._get_balance(user_id, currency)
        new_balance = current_balance + amount
        self._set_balance(user_id, currency, new_balance)
        
        transaction = Transaction(
            id=self._generate_transaction_id(),
            user_id=user_id,
            type=TransactionType.FUND,
            currency=currency,
            amount=amount,
            timestamp=datetime.now(),
            description=f"Funded {amount} {currency}"
        )
        self._add_transaction(user_id, transaction)
        
        return {"success": True, "new_balance": new_balance}
    
    def convert_currency(self, user_id: str, from_currency: str, to_currency: str, amount: Decimal) -> Dict:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        if from_currency == to_currency:
            raise ValueError("Cannot convert to same currency")

        rate_key = (from_currency, to_currency)
        if rate_key not in self.fx_rates:
            raise ValueError(f"Exchange rate not available for {from_currency} to {to_currency}")
        
        exchange_rate = self.fx_rates[rate_key]
        
        current_balance = self._get_balance(user_id, from_currency)
        if current_balance < amount:
            raise ValueError(f"Insufficient balance. Available: {current_balance} {from_currency}")
        
        converted_amount = self._round_amount(amount * exchange_rate, to_currency)
        
        new_from_balance = current_balance - amount
        self._set_balance(user_id, from_currency, new_from_balance)
        
        current_to_balance = self._get_balance(user_id, to_currency)
        new_to_balance = current_to_balance + converted_amount
        self._set_balance(user_id, to_currency, new_to_balance)
        
        transaction = Transaction(
            id=self._generate_transaction_id(),
            user_id=user_id,
            type=TransactionType.CONVERT,
            currency=from_currency,
            amount=amount,
            timestamp=datetime.now(),
            description=f"Converted {amount} {from_currency} to {converted_amount} {to_currency}",
            from_currency=from_currency,
            to_currency=to_currency,
            exchange_rate=exchange_rate
        )
        self._add_transaction(user_id, transaction)
        
        return {
            "success": True,
            "converted_amount": converted_amount,
            "exchange_rate": exchange_rate,
            "from_balance": new_from_balance,
            "to_balance": new_to_balance
        }
    
    def withdraw_funds(self, user_id: str, currency: str, amount: Decimal) -> Dict:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        current_balance = self._get_balance(user_id, currency)
        if current_balance < amount:
            raise ValueError(f"Insufficient balance. Available: {current_balance} {currency}")
        
        new_balance = current_balance - amount
        self._set_balance(user_id, currency, new_balance)
        
        transaction = Transaction(
            id=self._generate_transaction_id(),
            user_id=user_id,
            type=TransactionType.WITHDRAW,
            currency=currency,
            amount=amount,
            timestamp=datetime.now(),
            description=f"Withdrew {amount} {currency}"
        )
        self._add_transaction(user_id, transaction)
        
        return {"success": True, "new_balance": new_balance}
    
    def get_balances(self, user_id: str) -> Dict[str, Decimal]:
        self._ensure_wallet_exists(user_id)
        return dict(self.wallets[user_id])
    
    def get_transactions(self, user_id: str) -> List[Transaction]:
        self._ensure_wallet_exists(user_id)
        return self.transactions[user_id].copy()
    
    def reconcile_balances(self, user_id: str) -> Dict:
        transactions = self.get_transactions(user_id)
        calculated_balances = {}
        
        for transaction in transactions:
            if transaction.type == TransactionType.FUND:
                currency = transaction.currency
                calculated_balances[currency] = calculated_balances.get(currency, Decimal("0")) + transaction.amount
            
            elif transaction.type == TransactionType.WITHDRAW:
                currency = transaction.currency
                calculated_balances[currency] = calculated_balances.get(currency, Decimal("0")) - transaction.amount
            
            elif transaction.type == TransactionType.CONVERT:
                from_currency = transaction.from_currency
                to_currency = transaction.to_currency
                
                calculated_balances[from_currency] = calculated_balances.get(from_currency, Decimal("0")) - transaction.amount
                
                converted_amount = self._round_amount(transaction.amount * transaction.exchange_rate, to_currency)
                calculated_balances[to_currency] = calculated_balances.get(to_currency, Decimal("0")) + converted_amount
        
        for currency in calculated_balances:
            calculated_balances[currency] = self._round_amount(calculated_balances[currency], currency)
        
        calculated_balances = {k: v for k, v in calculated_balances.items() if v > 0}
        
        current_balances = self.get_balances(user_id)
        
        return {
            "current_balances": current_balances,
            "calculated_balances": calculated_balances,
            "balanced": current_balances == calculated_balances
        }
    
    def update_fx_rates(self, new_rates: Dict[tuple, Decimal]):
        self.fx_rates.update(new_rates)