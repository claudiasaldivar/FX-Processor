# FX Payment Processor

A simplified multi-currency wallet system that allows users to fund wallets, convert between currencies, withdraw funds, and view balances.

## Features

- **Fund Wallet**: Add money to user wallets in different currencies
- **Currency Conversion**: Convert between USD and MXN using fixed exchange rates
- **Withdraw Funds**: Remove money from wallets with balance validation
- **View Balances**: Check current wallet balances across all currencies
- **Transaction History**: Track all wallet operations (bonus feature)
- **Reconciliation**: Validate wallet integrity (bonus feature)

## Tech Stack

- **Python**: 3.11+
- **Web Framework**: Flask/FastAPI
- **Storage**: In-memory (Python dictionaries)
- **Testing**: pytest
- **Development**: Test-Driven Development (TDD)

## Setup Instructions

### Prerequisites

- Python 3.11 or newer
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone <https://github.com/claudiasaldivar/FX-Processor.git>
cd FX-Processor
```

2. Create a virtual env:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

