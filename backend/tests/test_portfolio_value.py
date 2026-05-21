"""Tests for PROJ-16: portfolio value endpoint (GET /portfolio/value)."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.portfolio import Transaction
from app.repositories.portfolio import TransactionRepository
from app.schemas.portfolio import PortfolioValueResponse


def _register_and_login(client: TestClient) -> str:
    """Register a test user and return a JWT token."""
    client.post(
        "/auth/register",
        json={"email": "value_test@test.com", "password": "Pass1234!"},
    )
    res = client.post(
        "/auth/login",
        json={"email": "value_test@test.com", "password": "Pass1234!"},
    )
    return res.json()["access_token"]


# ---------------------------------------------------------------------------
# Unit: TransactionRepository.get_account_values
# ---------------------------------------------------------------------------


def test_get_account_values_empty_db(db_session: Session) -> None:
    """Returns empty dict when no transactions exist."""
    repo = TransactionRepository(db_session)
    assert repo.get_account_values() == {}


def test_get_account_values_single_buy(db_session: Session) -> None:
    """Returns correct value for a single BUY transaction."""
    db_session.add(
        Transaction(
            ticker="CDR", type="BUY", quantity=10.0, amount=1000.0, account="PLN"
        )
    )
    db_session.commit()

    repo = TransactionRepository(db_session)
    result = repo.get_account_values()
    assert result == {"PLN": 1000.0}


def test_get_account_values_multiple_accounts(db_session: Session) -> None:
    """Aggregates values per account independently."""
    db_session.add_all(
        [
            Transaction(
                ticker="CDR", type="BUY", quantity=10.0, amount=1000.0, account="PLN"
            ),
            Transaction(
                ticker="PKN", type="BUY", quantity=5.0, amount=500.0, account="PLN"
            ),
            Transaction(
                ticker="AAPL", type="BUY", quantity=2.0, amount=800.0, account="IKE"
            ),
            Transaction(
                ticker="MSFT", type="BUY", quantity=1.0, amount=1200.0, account="USD"
            ),
        ]
    )
    db_session.commit()

    repo = TransactionRepository(db_session)
    result = repo.get_account_values()
    assert result == {"PLN": 1500.0, "IKE": 800.0, "USD": 1200.0}


def test_get_account_values_sell_reduces_value(db_session: Session) -> None:
    """A SELL transaction reduces the net value for the account."""
    db_session.add_all(
        [
            Transaction(
                ticker="CDR", type="BUY", quantity=10.0, amount=1000.0, account="PLN"
            ),
            Transaction(
                ticker="CDR", type="SELL", quantity=4.0, amount=500.0, account="PLN"
            ),
        ]
    )
    db_session.commit()

    repo = TransactionRepository(db_session)
    result = repo.get_account_values()
    assert result == {"PLN": 500.0}


def test_get_account_values_null_amount_ignored(db_session: Session) -> None:
    """Transactions with NULL amount do not contribute to the total."""
    db_session.add_all(
        [
            Transaction(
                ticker="CDR", type="BUY", quantity=10.0, amount=1000.0, account="PLN"
            ),
            Transaction(
                ticker="PKN", type="BUY", quantity=5.0, amount=None, account="PLN"
            ),
        ]
    )
    db_session.commit()

    repo = TransactionRepository(db_session)
    result = repo.get_account_values()
    assert result == {"PLN": 1000.0}


# ---------------------------------------------------------------------------
# Integration: GET /portfolio/value
# ---------------------------------------------------------------------------


def test_portfolio_value_unauthenticated(client: TestClient) -> None:
    """Returns 401 when no bearer token is supplied."""
    res = client.get("/portfolio/value")
    assert res.status_code == 401


def test_portfolio_value_empty_database(client: TestClient) -> None:
    """Returns empty accounts and zero total when no transactions exist."""
    token = _register_and_login(client)
    res = client.get(
        "/portfolio/value",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    body = PortfolioValueResponse(**res.json())
    assert body.accounts == {}
    assert body.total == 0.0


def test_portfolio_value_returns_per_account_values(
    client: TestClient, db_session: Session
) -> None:
    """Returns accurate per-account values after inserting transactions."""
    db_session.add_all(
        [
            Transaction(
                ticker="CDR", type="BUY", quantity=10.0, amount=2000.0, account="PLN"
            ),
            Transaction(
                ticker="AAPL", type="BUY", quantity=1.0, amount=1500.0, account="IKE"
            ),
            Transaction(
                ticker="MSFT", type="BUY", quantity=2.0, amount=3000.0, account="USD"
            ),
        ]
    )
    db_session.commit()

    token = _register_and_login(client)
    res = client.get(
        "/portfolio/value",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    body = PortfolioValueResponse(**res.json())
    assert body.accounts.get("PLN") == pytest.approx(2000.0)
    assert body.accounts.get("IKE") == pytest.approx(1500.0)
    assert body.accounts.get("USD") == pytest.approx(3000.0)
    assert body.total == pytest.approx(6500.0)


def test_portfolio_value_total_matches_account_sum(
    client: TestClient, db_session: Session
) -> None:
    """Total field equals the sum of all per-account values."""
    db_session.add_all(
        [
            Transaction(
                ticker="CDR", type="BUY", quantity=5.0, amount=750.0, account="PLN"
            ),
            Transaction(
                ticker="CDR", type="SELL", quantity=2.0, amount=200.0, account="PLN"
            ),
            Transaction(
                ticker="AAPL", type="BUY", quantity=3.0, amount=900.0, account="IKE"
            ),
        ]
    )
    db_session.commit()

    token = _register_and_login(client)
    res = client.get(
        "/portfolio/value",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    body = PortfolioValueResponse(**res.json())
    assert body.total == pytest.approx(sum(body.accounts.values()))
    assert body.accounts.get("PLN") == pytest.approx(550.0)
    assert body.accounts.get("IKE") == pytest.approx(900.0)
