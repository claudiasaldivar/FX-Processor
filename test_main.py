import pytest
from fastapi.testclient import TestClient
from decimal import Decimal
from main import app, wallet_service

client = TestClient(app)

class TestAPI:
    
    def setup_method(self):
        wallet_service.wallets.clear()
        wallet_service.transactions.clear()
        wallet_service.transaction_counter = 0