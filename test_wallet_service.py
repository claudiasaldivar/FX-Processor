import pytest
from decimal import Decimal
from wallet_service import WalletService, TransactionType


class TestWalletService:

    def setup_method(self):
        self.wallet_service = WalletService()

    def test_fund_wallet_success(self):
        user_id = "user123"
        currency = "USD"
        amount = Decimal("1000")
        
        result = self.wallet_service.fund_wallet(user_id, currency, amount)
        
        assert result["success"] is True
        assert result["new_balance"] == Decimal("1000")
        
        balances = self.wallet_service.get_balances(user_id)
        assert balances[currency] == Decimal("1000")