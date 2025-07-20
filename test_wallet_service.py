import pytest
from decimal import Decimal
from wallet_service import WalletService, TransactionType


class TestWalletService:

    def setup_method(self):
        self.wallet_service = WalletService()