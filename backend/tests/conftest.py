"""Test configuration and shared fixtures."""

import tempfile
from pathlib import Path
from typing import Generator

import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.models.portfolio import Asset, Dividend, Transaction
from app.models.bonds import Bond
from app.models.cash import CashAccount
from app.models.user_settings import UserSettings


@pytest.fixture(name="db_session")
def db_session_fixture() -> Generator[Session, None, None]:
    """
    Yield an in-memory SQLite session for isolated test execution.

    Yields:
        Session: Temporary in-memory database session.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture
def sample_transaction_data() -> dict:
    """
    Return a minimal valid transaction payload for use in tests.

    Returns:
        dict: Sample transaction field values.
    """
    return {
        "date": "2023-01-15T10:30:00",
        "ticker": "AAPL",
        "type": "BUY",
        "quantity": 10.0,
        "price": 150.0,
        "amount": 1500.0,
        "account": "USD",
    }


@pytest.fixture
def sample_dividend_data() -> dict:
    """
    Return a minimal valid dividend payload for use in tests.

    Returns:
        dict: Sample dividend field values.
    """
    return {
        "date": "2023-03-15T00:00:00",
        "ticker": "AAPL",
        "amount": 25.0,
        "currency": "USD",
        "account": "USD",
    }


@pytest.fixture
def excel_file_path() -> Generator[Path, None, None]:
    """
    Create a temporary Excel file with synthetic portfolio data.

    Yields:
        Path: Path to the temporary Excel file.
    """
    import pandas as pd

    temp_dir = Path(tempfile.mkdtemp())
    excel_path = temp_dir / "test_portfolio.xlsx"

    open_positions_data = {
        "Symbol": ["AAPL", "GOOGL"],
        "Volume": [10, 5],
        "Open Time": ["2023-01-15 10:30:00", "2023-02-01 14:20:00"],
        "Open Price": [150.0, 2500.0],
        "Market Price": [155.0, 2600.0],
        "Purchase Value": [1500.0, 12500.0],
    }

    cash_ops_data = {
        "Type": ["Dividend", "Withholding Tax"],
        "Symbol": ["AAPL", "AAPL"],
        "Time": ["2023-03-15 00:00:00", "2023-03-15 00:00:00"],
        "Amount": [30.0, -5.0],
    }

    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        pd.DataFrame(open_positions_data).to_excel(
            writer,
            sheet_name="Open Position",
            index=False,
        )
        pd.DataFrame(cash_ops_data).to_excel(
            writer,
            sheet_name="Cash Operation",
            index=False,
        )

    yield excel_path
